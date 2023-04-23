import datetime
import io
import logging
import os
import re
from typing import Tuple, List

import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart, Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, \
    CallbackQuery, Message, ParseMode, BotCommand, ChatActions
from aiogram.utils import executor

import admin_client
from activity.activity import Activity
from course.course import Course
from course.join_code.join_code import CourseJoinCode
from factory import get_teacher_factory, get_join_code_factory, get_course_factory, get_lesson_factory, \
    get_activity_factory, get_activity_record_factory, get_teacher_activity_link_factory, \
    get_course_teacher_link_factory, get_excel_report_persistence_factory
from lesson.lesson import Lesson
from links.teacher_telegram_link import TeacherTelegramLink
from middleware import TypingMiddleware, FSMFinishMiddleware
from report.excel.excel_report_generator import ReportGenerator
from state_groups import MarkActivitySG, AddCourseSG, AddLessonSG, AddActivitySG, AddJoinCodeSG, RemoveCourseSG, \
    RemoveLessonSG, RemoveActivitySG, JoinCodesListSG, RemoveJoinCodeSG, ReportSG, EditCourseSG
from teacher.teacher import Teacher

logging.basicConfig(level=logging.INFO)

bot = Bot(token=os.environ.get('BOT_TOKEN'))
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(TypingMiddleware())
dp.middleware.setup(FSMFinishMiddleware(dispatcher=dp))

TEACHER_COMMANDS = [
    BotCommand('start', 'Начать работу'),
    BotCommand('mark_activity', 'Отметить активность'),
    BotCommand('cancel', 'Отменить текущую операцию'),
    BotCommand('help', 'Помощь по командам'),
]
MANAGER_HELP_MESSAGE = md.text(
    md.text('Список команд:'),
    md.text('/generate_report - получить отчет по всем курсам'),
    md.text('/join_codes - список кодов подключения к курсу'),
    md.text('/add_join_code - добавить код подключения к курсу'),
    md.text('/add_course - добавить курс'),
    md.text('/add_lesson - добавить урок в курс'),
    md.text('/add_activity - добавить активность в урок по курсу'),
    md.text('/remove_join_code - удалить код подключения к курсу'),
    md.text('/remove_course - удалить курс'),
    md.text('/remove_lesson - удалить урок'),
    md.text('/remove_activity - удалить активность'),
    md.text('/start КОД - подключиться к курсу'),
    md.text('/mark_activity - отметить активность'),
    sep='\n',
)
TEACHER_HELP_PAGE = md.text(
    md.text('Список команд:'),
    md.text('/start КОД - подключиться к курсу'),
    md.text('/mark_activity - отметить активность'),
    md.text('/help - помощь по командам'),
    sep='\n',
)


def only_for_manager(func):
    """Декоратор для команд, доступных только менеджерам бота"""

    async def wrapper(message_or_callback: types.Message, state: FSMContext):
        tf = await get_teacher_factory()
        teacher: Teacher = await tf.load(teacher_id=message_or_callback.from_user.id)
        if not await teacher.is_manager:
            await message_or_callback.answer('Команда доступна только менеджерам бота')
            return
        return await func(message_or_callback, state)

    return wrapper


@dp.message_handler(CommandStart())
async def start_command(message: types.Message):
    """Обработка команды /start, перехода по ссылке подключения и нажатия на кнопку запуска бота.
    Функционал подключения к курсу.
    """
    await bot.set_my_commands(TEACHER_COMMANDS)

    parameter_value = message.get_args()
    if parameter_value:
        join_code: CourseJoinCode = await (await get_join_code_factory()).load(code=parameter_value)
        join_code_course = await join_code.course
        join_code_activated_by = await join_code.activated_by
        if join_code_course is None:
            text = f'Кода "{parameter_value}" не существует'
        elif join_code_activated_by is not None:
            text = f'Код "{parameter_value}" уже активирован'
        else:
            course_title = await join_code_course.name
            telegram_id = message.from_user.id
            teacher = await (await get_teacher_factory()).load(teacher_id=telegram_id)
            await teacher.register()
            await join_code.activate(teacher=teacher)
            text = f'Ты успешно подключен к курсу "{course_title}"!'
    else:
        text = await help_page(message.from_user.id)

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    button_my_courses = KeyboardButton('Мои курсы')
    keyboard.add(button_my_courses)

    await message.reply(text, reply_markup=keyboard)


async def help_page(teacher_id: int):
    """Обработка команды /help для вывода списка доступных команд"""
    tf = await get_teacher_factory()
    teacher: Teacher = await tf.load(teacher_id=teacher_id)
    if await teacher.is_manager:
        return MANAGER_HELP_MESSAGE
    return TEACHER_HELP_PAGE


@dp.message_handler(Command('help'), state='*')
async def help_command(message: types.Message):
    """Обработка команды /help для вывода списка доступных команд"""
    await message.answer(await help_page(message.from_user.id))


async def my_courses(message: types.Message, state: FSMContext):
    """Обработка сообщения "Мои курсы" для запроса списка курсов и последующей отметки активности"""
    telegram_id = message.from_user.id
    teacher = await (await get_teacher_factory()).load(teacher_id=telegram_id)
    if not await teacher.registered:
        await message.reply("Пройди по спeциальной ссылкe или ввeди /start КОД_АКТИВАЦИИ")
        return

    keyboard = InlineKeyboardMarkup()
    courses = await teacher.courses
    for course in courses:
        course_name = await course.name
        button = InlineKeyboardButton(course_name, callback_data=f'course_{course.id}')
        keyboard.add(button)

    if len(courses) == 0:
        await message.reply(
            "У тебя нет курсов. Добавь курс по коду от менеджера с помощью команды /start КОД_АКТИВАЦИИ"
        )
        await state.finish()
    else:
        await message.reply("Выберите курс", reply_markup=keyboard)
        await state.set_state(MarkActivitySG.choose_course)


@dp.message_handler(text='Мои курсы')
async def msg_my_courses(message: types.Message, state: FSMContext):
    """Обработка сообщения "Мои курсы" для запроса списка курсов и последующей отметки активности"""
    await my_courses(message, state)


@dp.message_handler(Command('mark_activity'))
async def cmd_mark_activity(message: types.Message, state: FSMContext):
    """Обработка команды /mark_activity для отметки активности"""
    await my_courses(message, state)


async def choose_lesson(callback_query: CallbackQuery):
    """Обработка выбора урока"""
    course_id = int(callback_query.data.split('_')[1])
    course: Course = await (await get_course_factory()).load(course_id=course_id)

    keyboard = InlineKeyboardMarkup()
    lessons: Tuple[Lesson] = await course.lessons
    for lesson in lessons:
        lesson_date_from = await lesson.date_from
        lesson_date_to = await lesson.date_to
        lesson_date_from_str = lesson_date_from.strftime("%d.%m.%Y")
        lesson_date_to_str = lesson_date_to.strftime("%d.%m.%Y")
        lesson_topic = await lesson.topic or 'Тема не указана'
        lesson_label = f"{lesson_date_from_str}-{lesson_date_to_str}: {lesson_topic}"
        button = InlineKeyboardButton(lesson_label, callback_data=f'lesson_{lesson.id}')
        keyboard.add(button)

    if len(lessons) == 0:
        await callback_query.message.reply(text="У курса нет уроков")
        return False
    else:
        await callback_query.message.reply(text="Выберите урок", reply_markup=keyboard)
        return True


@dp.callback_query_handler(lambda c: re.match(r'^course_\d+$', c.data), state=MarkActivitySG.choose_course)
async def callback_mark_activity_choose_course(callback_query: CallbackQuery, state: FSMContext):
    """Обработчик кнопки выбора курса для отметки активности"""
    result = await choose_lesson(callback_query)
    if result:
        await state.set_state(MarkActivitySG.choose_lesson)
    else:
        await state.finish()
    await callback_query.answer()


async def choose_activity(callback_query: CallbackQuery):
    """Обработка выбора активности"""
    lesson_id = int(callback_query.data.split('_')[1])
    lesson: Lesson = await (await get_lesson_factory()).load(lesson_id=lesson_id)

    keyboard = InlineKeyboardMarkup()
    activities: Tuple[Activity] = await lesson.activities
    for activity in activities:
        activity_topic = await activity.name
        button = InlineKeyboardButton(activity_topic, callback_data=f'activity_{activity.id}')
        keyboard.add(button)

    if len(activities) == 0:
        await callback_query.message.reply(text="У урока нет активностей")
        return False
    else:
        await callback_query.message.reply(text="Выберите активность", reply_markup=keyboard)
        return True


@dp.callback_query_handler(lambda c: re.match(r'^lesson_\d+$', c.data), state=MarkActivitySG.choose_lesson)
async def callback_mark_activity_choose_lesson(callback_query: CallbackQuery, state: FSMContext):
    """Обработчик кнопки выбора урока для отметки активности"""
    result = await choose_activity(callback_query)
    if result:
        await state.set_state(MarkActivitySG.choose_activity)
    else:
        await state.finish()

    await callback_query.answer()


@dp.callback_query_handler(lambda c: re.match(r'^activity_\d+$', c.data), state=MarkActivitySG.choose_activity)
async def callback_mark_activity_choose_activity(callback_query: CallbackQuery, state: FSMContext):
    """Обработчик кнопки выбора активности для отметки активности, предлагает сохранить комментарий для менеджера"""
    activity_id = int(callback_query.data.split('_')[1])
    async with state.proxy() as data:
        data["activity_id"] = activity_id

    keyboard = InlineKeyboardMarkup()
    button = InlineKeyboardButton("Пропустить", callback_data=f'no_comment')
    keyboard.add(button)

    await callback_query.message.reply(
        "Вы можете отправить комментарий для менеджера к отметке активности.",
        reply_markup=keyboard
    )
    await callback_query.answer()

    await state.set_state(MarkActivitySG.choose_comment)


@dp.callback_query_handler(lambda c: re.match(r'^no_comment$', c.data), state=MarkActivitySG.choose_comment)
async def callback_mark_activity_no_comment(callback_query: CallbackQuery, state: FSMContext):
    """Преподаватель решил не указывать комментарий для менеджера к активности, предлагаем указать количество часов"""
    async with state.proxy() as data:
        data["mark_activity_comment"] = None

    message = callback_query.message

    await message.answer(admin_client.messages.SET_HOURS_SUGGESTION)

    await callback_query.answer()

    await state.set_state(MarkActivitySG.choose_hours)


@dp.message_handler(state=MarkActivitySG.choose_comment)
async def msg_mark_activity_hours(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data["mark_activity_comment"] = message.text

    await message.answer(admin_client.messages.SET_HOURS_SUGGESTION)

    await state.set_state(MarkActivitySG.choose_hours)


@dp.message_handler(state=MarkActivitySG.choose_hours)
async def msg_mark_activity_hours(message: Message, state: FSMContext):
    """Обработчик сообщения с указанием количества часов по активности"""
    try:
        hours = float(message.text.replace(',', '.').strip())
    except ValueError:
        await message.answer("К сожалению, мне не удалось распознать число. Пожалуйста, попробуйте ещё раз.")
        return

    async with state.proxy() as data:
        af = await get_activity_factory()
        activity: Activity = await af.load(activity_id=data["activity_id"])
        lesson: Lesson = await activity.lesson
        course: Course = await lesson.course
        arf = await get_activity_record_factory()
        tf = await get_teacher_factory()
        teacher: Teacher = await tf.load(teacher_id=message.from_user.id)
        await arf.create(
            teacher_id=teacher.id, activity_id=activity.id, hours=hours, comment=data["mark_activity_comment"]
        )

        await message.answer(
            "✅ Записал.\n"
            f"▪ Курс - {md.hitalic(await course.name_quoted)}\n"
            f"▪ Тема урока - {md.hitalic(await lesson.topic_quoted or 'НЕ УКАЗАНА')}\n"
            f"▪ {md.hunderline((await lesson.date_from).strftime(admin_client.constants.DATE_FORMAT))}"
            f"-{md.hunderline((await lesson.date_to).strftime(admin_client.constants.DATE_FORMAT))}\n"
            f"▪ Активность - {md.hitalic(await activity.name_quoted)}\n"
            f"▪ {'Добавлено' if hours >= 0 else 'Убрано'} часов - {md.hitalic(abs(hours))}\n",
            parse_mode=ParseMode.HTML
        )

    await state.finish()


@dp.message_handler(Command("cancel"), state='*')
async def cmd_cancel(message: Message, state: FSMContext):
    """Обработчик команды отмены, работает из любого состояния"""
    help_msg = await help_page(message.from_user.id)
    await message.answer(help_msg)
    await state.finish()


@dp.message_handler(Command("add_course"))
@only_for_manager
async def cmd_add_course(message: Message, state: FSMContext):
    """Обработчик команды добавления курса /add_course"""
    await message.answer(
        "Хорошо, давайте добавим новый курс. Если передумаете, пишите /cancel. Как будет называться новый курс?"
    )
    await state.set_state(AddCourseSG.get_name)


@dp.message_handler(state=AddCourseSG.get_name)
@only_for_manager
async def msg_set_course_name(message: Message, state: FSMContext):
    """Обработчик сообщения с названием курса процесса создания курса"""
    async with state.proxy() as data:
        data["course_name"] = message.text
    await state.set_state(AddCourseSG.get_description)

    keyboard = InlineKeyboardMarkup()
    button_skip = InlineKeyboardButton("Пропустить", callback_data=f'no_description')
    keyboard.add(button_skip)

    await message.answer(
        "Укажите описание курса",
        reply_markup=keyboard
    )


@dp.callback_query_handler(lambda c: re.match(r'^no_description$', c.data), state=AddCourseSG.get_description)
@only_for_manager
async def create_course_no_description(callback_query: CallbackQuery, state: FSMContext):
    """Обработчик нажатия кнопки "Пропустить", ветка, где курс создается без описания процесса создания курса"""
    message = callback_query.message
    async with state.proxy() as data:
        cf = await get_course_factory()
        course = await cf.create(name=data["course_name"], description=None)
        await message.answer(f"Курс {md.hbold(await course.name)} добавлен!", parse_mode=ParseMode.HTML)
        kb_yes_no = InlineKeyboardMarkup()
        kb_yes_no.add(
            InlineKeyboardButton("Да", callback_data=f'yes_add_lessons_{course.id}'),
            InlineKeyboardButton("Нет", callback_data=f'no_add_lessons_{course.id}')
        )
        await message.answer(
            "Добавить уроки в курс? "
            "Вы всегда сможете добавить уроки позже, но не забудьте сделать это до начала сбора активности!",
            reply_markup=kb_yes_no
        )
    await callback_query.answer()
    await state.finish()


@dp.message_handler(state=AddCourseSG.get_description)
@only_for_manager
async def msg_set_course_desc(message: Message, state: FSMContext):
    """Обработчик сообщения с описанием нового курса процесса создания курса"""
    description = message.text
    async with state.proxy() as data:
        cf = await get_course_factory()
        course = await cf.create(name=data["course_name"], description=description)
        await message.answer(
            md.text(
                f"Курс {md.hbold(await course.name)} добавлен, описание:",
                md.hcode(description),
                sep='\n'
            ),
            parse_mode=ParseMode.HTML
        )
        kb_yes_no = InlineKeyboardMarkup()
        kb_yes_no.add(
            InlineKeyboardButton("Да", callback_data=f'yes_add_lessons_{course.id}'),
            InlineKeyboardButton("Нет", callback_data=f'no_add_lessons_{course.id}')
        )
        await message.answer(
            "Добавить уроки в курс? "
            "Вы всегда сможете добавить уроки позже, но не забудьте сделать это до начала сбора активности!",
            reply_markup=kb_yes_no
        )
    await state.finish()


@dp.callback_query_handler(lambda c: re.match(r'^(yes|no)_add_lessons_\d+$', c.data))
@only_for_manager
async def callback_add_lessons(callback_query: CallbackQuery, state: FSMContext):
    """Обработчик кнопок "Да" и "Нет" в процессе создания курса"""
    message = callback_query.message
    action = callback_query.data.split('_')[0]
    course_id = int(callback_query.data.split('_')[3])
    if action == 'yes':
        keyboard = InlineKeyboardMarkup()
        button_skip = InlineKeyboardButton("Не указывать", callback_data=f'no_topic')
        keyboard.add(button_skip)
        await message.answer(
            "Хорошо, давайте добавим уроки. Если передумаете, пишите /cancel. "
            "Какая тема будет у нового урока?",
            reply_markup=keyboard
        )
        await state.set_state(AddLessonSG.choose_topic)
        async with state.proxy() as data:
            data["course_id"] = course_id
    else:
        await message.answer("Хорошо, курс создан.")
        await callback_query.answer()
        await state.finish()


@dp.message_handler(Command("add_lesson"))
@only_for_manager
async def cmd_add_lesson(message: Message, state: FSMContext):
    """Команда добавления урока /add_lesson"""
    result = await choose_course(message)
    if result:
        await state.set_state(AddLessonSG.choose_course)
    else:
        await state.finish()


@dp.callback_query_handler(lambda c: re.match(r'^course_\d+$', c.data), state=AddLessonSG.choose_course)
@only_for_manager
async def callback_add_lesson_choose_course(callback_query: CallbackQuery, state: FSMContext):
    """Обработчик кнопки выбора курса в процессе добавления урока"""
    course_id = int(callback_query.data.split('_')[1])
    async with state.proxy() as data:
        data["course_id"] = course_id

    keyboard = InlineKeyboardMarkup()
    button_skip = InlineKeyboardButton("Не указывать", callback_data=f'no_topic')
    keyboard.add(button_skip)

    await callback_query.message.reply(text="Какая тема будет у нового урока?", reply_markup=keyboard)
    await callback_query.answer()

    await state.set_state(AddLessonSG.choose_topic)


@dp.callback_query_handler(lambda c: re.match(r'^no_topic$', c.data), state=AddLessonSG.choose_topic)
@only_for_manager
async def callback_add_lesson_no_topic(callback_query: CallbackQuery, state: FSMContext):
    """Обработчик кнопки "Не указывать" [тему] для урока в процессе создания урока, предлагаем выбрать период"""
    async with state.proxy() as data:
        data["lesson_topic"] = None

    message = callback_query.message
    await message.answer(admin_client.messages.SET_PERIOD_SUGGESTION, parse_mode=ParseMode.HTML)
    await callback_query.answer()

    await state.set_state(AddLessonSG.choose_period)


@dp.message_handler(state=AddLessonSG.choose_topic)
@only_for_manager
async def msg_set_lesson_topic(message: Message, state: FSMContext):
    """Обработчик темы прислал урока в процессе создания урока, предлагаем выбрать период"""
    async with state.proxy() as data:
        data["lesson_topic"] = message.text

    await message.answer(admin_client.messages.SET_PERIOD_SUGGESTION, parse_mode=ParseMode.HTML)

    await state.set_state(AddLessonSG.choose_period)


@dp.message_handler(state=AddLessonSG.choose_period)
@only_for_manager
async def msg_set_lesson_period(message: Message, state: FSMContext):
    """Пользователь прислал период сбора активности по уроку"""
    async with state.proxy() as data:
        dates = re.sub(r"\s", '', message.text).split(admin_client.constants.PERIOD_DELIMITER)
        if len(dates) < 2:
            await message.answer(
                "❗ К сожалению, мне не удалось распознать период. Возможно, вы забыли знак минуса между датами или "
                "написали только одну дату. Пожалуйста, попробуйте заново. "
                f"Укажите {md.hbold('2')} даты в формате ДД.ММ.ГГГГ, разделенные знаком минуса, например "
                f"{md.hcode('10.03.2023-15.03.2023')}",
                parse_mode=ParseMode.HTML
            )
        elif len(dates) > 2:
            await message.answer(
                "❗ К сожалению, мне не удалось распознать период. Ваше сообщение содержит больше одного знака минуса. "
                "Пожалуйста, попробуйте заново. "
                f"Укажите {md.hbold('2')} даты в формате ДД.ММ.ГГГГ, разделенные знаком минуса, например "
                f"{md.hcode('10.03.2023-15.03.2023')}",
                parse_mode=ParseMode.HTML
            )
        else:
            dates_parsed = []
            for date, date_kind in zip(dates, ("начала", "конца")):
                try:
                    dates_parsed.append(datetime.datetime.strptime(date, admin_client.constants.DATE_FORMAT))
                except ValueError:
                    await message.answer(
                        f"❗ К сожалению, мне не удалось распознать дату {date_kind} \"{date}\" "
                        "Пожалуйста, попробуйте указать период заново. Обратите внимание - формат даты ДД.ММ.ГГГГ. "
                        f"Например, {md.hcode('10.03.2023-15.03.2023')}",
                        parse_mode=ParseMode.HTML
                    )
                    return
            if dates_parsed[1] < dates_parsed[0]:
                await message.answer(
                    f"❗ Дата завершения раньше даты начала, укажите период заново!",
                    parse_mode=ParseMode.HTML
                )
                return
            data["lesson_dates"] = dates_parsed

        lf = await get_lesson_factory()
        date_from, date_to = data["lesson_dates"]
        new_lesson = await lf.create(
            course_id=data["course_id"], topic=data["lesson_topic"], date_from=date_from, date_to=date_to
        )
        await message.answer(
            "📚 Урок создан успешно.\n"
            f"▪ Курс - {md.hitalic(await (await new_lesson.course).name_quoted)}\n"
            f"▪ Тема - {md.hitalic(await new_lesson.topic_quoted or 'НЕ УКАЗАНА')}\n"
            f"▪ Сбор активности с "
            f"{md.hunderline((await new_lesson.date_from).strftime(admin_client.constants.DATE_FORMAT))} "
            f"до "
            f"{md.hunderline((await new_lesson.date_to).strftime(admin_client.constants.DATE_FORMAT))} "
            f"(обе даты включительно)",
            parse_mode=ParseMode.HTML
        )
        kb_yes_no = InlineKeyboardMarkup()
        kb_yes_no.add(
            InlineKeyboardButton("Да", callback_data=f"lesson_{new_lesson.id}_yes"),
            InlineKeyboardButton("Нет", callback_data=f"lesson_{new_lesson.id}_no")
        )
        # Предлагаем добавить активность
        await message.answer(
            "📝 Хотите добавить активность к уроку? Если да, нажмите кнопку \"Да\". Если нет, нажмите кнопку \"Нет\". "
            "Вы всегда сможете добавить активность позже, но не забудьте сделать это до начала сбора активности!",
            reply_markup=kb_yes_no
        )

    await state.finish()


@dp.callback_query_handler(lambda c: re.match(r'^lesson_\d+_(yes|no)$', c.data))
@only_for_manager
async def callback_add_activity_to_lesson(call: CallbackQuery, state: FSMContext):
    """Пользователь нажал на кнопку добавления активности к уроку"""
    lesson_id = int(call.data.split("_")[1])
    lf = await get_lesson_factory()
    lesson = await lf.load(lesson_id)
    if not lesson:
        await call.answer("❗Произошла ошибка, попробуйте еще раз")
        return
    if call.data.endswith("yes"):
        await call.message.answer("📝 Введите название активности")
        await state.set_state(AddActivitySG.choose_name)
        await state.update_data(new_activity_lesson_id=lesson_id)
    else:
        await call.message.answer("👌 Окей, вы всегда сможете добавить активность позже")
        await call.message.answer("👋 До свидания!")
        await state.finish()


@dp.message_handler(Command("add_activity"))
@only_for_manager
async def cmd_add_activity(message: Message, state: FSMContext):
    """Команда добавления активности /add_activity"""
    result = await choose_course(message)
    if result:
        await state.set_state(AddActivitySG.choose_course)
    else:
        await state.finish()


@dp.callback_query_handler(lambda c: re.match(r'^course_\d+$', c.data), state=AddActivitySG.choose_course)
@only_for_manager
async def callback_add_course_chosen(callback_query: CallbackQuery, state: FSMContext):
    """Пользователь выбрал курс в процессе добавления активности"""
    result = await choose_lesson(callback_query)
    if result:
        await state.set_state(AddActivitySG.choose_lesson)
    else:
        await state.finish()
    await callback_query.answer()


@dp.callback_query_handler(lambda c: re.match(r'^lesson_\d+$', c.data), state=AddActivitySG.choose_lesson)
@only_for_manager
async def callback_add_activity_lesson_chosen(callback_query: CallbackQuery, state: FSMContext):
    """Обработчик выбора урока в процессе добавления активности"""
    lesson_id = int(callback_query.data.split('_')[1])

    async with state.proxy() as data:
        data["new_activity_lesson_id"] = lesson_id

    await callback_query.message.reply(text="Какое будет название у новой активности?")
    await callback_query.answer()

    await state.set_state(AddActivitySG.choose_name)


@dp.message_handler(state=AddActivitySG.choose_name)
@only_for_manager
async def msg_set_activity_name(message: Message, state: FSMContext):
    """Обработчик имени активности в процессе добавления новой активности"""
    activity_name = message.text
    async with state.proxy() as data:
        af = await get_activity_factory()
        activity = await af.create(name=activity_name, lesson_id=data["new_activity_lesson_id"])
        lesson = await activity.lesson
        await message.answer(
            "📚 Активность создана успешно.\n"
            f"▪ Курс - {md.hitalic(await (await activity.course).name_quoted)}\n"
            f"▪ Тема урока - {md.hitalic(await lesson.topic_quoted or 'НЕ УКАЗАНА')}\n"
            f"▪ Активность - {md.hitalic(await activity.name_quoted)}\n"
            f"▪ Сбор активности с "
            f"{md.hunderline((await lesson.date_from).strftime(admin_client.constants.DATE_FORMAT))} "
            f"до "
            f"{md.hunderline((await lesson.date_to).strftime(admin_client.constants.DATE_FORMAT))} "
            f"(обе даты включительно)",
            parse_mode=ParseMode.HTML
        )
        kb_yes_no = InlineKeyboardMarkup()
        kb_yes_no.add(
            InlineKeyboardButton("Да", callback_data=f"lesson_{lesson.id}_yes"),
            InlineKeyboardButton("Нет", callback_data=f"lesson_{lesson.id}_no")
        )
        await message.answer(
            "Хотите добавить еще одну активность к этому уроку?",
            reply_markup=kb_yes_no
        )

    await state.finish()


@dp.message_handler(Command("join_codes"))
@only_for_manager
async def cmd_join_codes(message: Message, state: FSMContext):
    """Команда просмотра кодов подключения к курсу /join_codes"""
    result = await choose_course(message)
    if result:
        await state.set_state(JoinCodesListSG.choose_course)
    else:
        await state.finish()


@dp.callback_query_handler(lambda c: re.match(r'^course_\d+$', c.data), state=JoinCodesListSG.choose_course)
@only_for_manager
async def callback_join_codes_course_chosen(callback_query: CallbackQuery, state: FSMContext):
    """Пользователь выбрал курс для просмотра кодов подключения"""
    course_id = int(callback_query.data.split('_')[1])
    async with state.proxy() as data:
        data["course_id"] = course_id

    await callback_query.message.answer("🔎 Поиск кодов...")
    cf = await get_course_factory()
    course = await cf.load(course_id)
    jcf = await get_join_code_factory()
    join_codes = await jcf.load_by_course(course=course)
    if not join_codes:
        await callback_query.message.answer("❗Коды подключения к курсу не найдены")
        await state.finish()
        return

    unactivated_codes_msg = "\n".join(
            [
                f"▪ {md.hcode(join_code.code)} - {md.hitalic(await join_code.comment or 'БЕЗ ПРИМЕЧАНИЯ')}"
                for join_code in join_codes if await join_code.activated_by is None
            ]
        ) or "НЕТ"

    tg_teacher_link: TeacherTelegramLink = TeacherTelegramLink(callback_query.bot)
    activated_codes = []
    for join_code in join_codes:
        if await join_code.activated_by is None:
            continue
        code = md.hcode(join_code.code)
        comment = md.hitalic(await join_code.comment_quoted or 'БЕЗ ПРИМЕЧАНИЯ')
        activated_by: Teacher = await join_code.activated_by
        full_name = await tg_teacher_link.get_full_name(activated_by)
        url = f'tg://user?id={activated_by.id}'
        activated_codes.append(f"▪ {code} - {comment} (активировал {md.hlink(full_name, url)})")
    activated_codes_msg = "\n".join(activated_codes) or "НЕТ"

    await callback_query.message.answer(
        md.text(
            f"🔑 Список кодов подключения к курсу {await course.name_quoted}",
            "",
            "Не активированные:",
            unactivated_codes_msg,
            "Активированные:",
            activated_codes_msg,
            sep="\n"
        ),
        parse_mode=ParseMode.HTML
    )
    await state.finish()


@dp.message_handler(Command(["remove_code", "remove_join_code"]))
@only_for_manager
async def cmd_remove_join_code(message: Message, state: FSMContext):
    """Команда удаления кода подключения к курсу /remove_code"""
    result = await choose_course(message)
    if result:
        await state.set_state(RemoveJoinCodeSG.choose_course)
    else:
        await state.finish()


@dp.callback_query_handler(lambda c: re.match(r'^course_\d+$', c.data), state=RemoveJoinCodeSG.choose_course)
@only_for_manager
async def callback_remove_join_code_course_chosen(callback_query: CallbackQuery, state: FSMContext):
    """Пользователь выбрал курс для удаления одноразового кода"""
    course_id = int(callback_query.data.split('_')[1])
    async with state.proxy() as data:
        data["course_id"] = course_id

    await callback_query.message.answer("🔎 Поиск кодов...")
    cf = await get_course_factory()
    course = await cf.load(course_id)
    jcf = await get_join_code_factory()
    active_join_codes = [code for code in await jcf.load_by_course(course=course) if await code.activated_by is None]
    if not active_join_codes:
        await callback_query.message.answer("❗Активные коды подключения к курсу не найдены")
        await state.finish()
        return

    active_codes_labels: List[str] = []
    kb = InlineKeyboardMarkup()
    for join_code in active_join_codes:
        code = md.hcode(join_code.code)
        comment = md.hitalic(await join_code.comment_quoted or 'БЕЗ ПРИМЕЧАНИЯ')
        active_codes_labels.append(f"▪ {code} - {comment}")
        kb.add(InlineKeyboardButton(f"{join_code.code}", callback_data=f"join_code_{join_code.code}"))

    await callback_query.message.answer(
        md.text(
            f"🔑 Список активных кодов подключения к курсу {await course.name_quoted}",
            "",
            "Выберите код для удаления:",
            *active_codes_labels,
            sep="\n"
        ),
        reply_markup=kb,
        parse_mode=ParseMode.HTML
    )
    await state.set_state(RemoveJoinCodeSG.choose_code)


@dp.callback_query_handler(lambda c: re.match(r'^join_code_.+$', c.data), state=RemoveJoinCodeSG.choose_code)
@only_for_manager
async def callback_remove_join_code_code_chosen(callback_query: CallbackQuery, state: FSMContext):
    """Пользователь выбрал код для удаления"""
    code = callback_query.data.split('_')[2]
    jcf = await get_join_code_factory()
    join_code = await jcf.load(code)
    if join_code is None:
        await callback_query.message.answer("❗Код не найден")
        await state.finish()
        return

    if await join_code.activated_by is not None:
        await callback_query.message.answer("❗Код уже активирован")
        await state.finish()
        return

    await callback_query.message.answer(
        md.text(
            f"🔑 Удаление кода {md.hcode(join_code.code)}",
            "",
            f"Код будет удален из базы данных. Действительно удалить?",
            sep="\n"
        ),
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton("Да", callback_data=f"confirm_remove_join_code_{join_code.code}"),
            InlineKeyboardButton("Нет", callback_data=f"cancel_remove_join_code_{join_code.code}")
        ),
        parse_mode=ParseMode.HTML
    )
    await state.set_state(RemoveJoinCodeSG.confirm)


@dp.callback_query_handler(lambda c: re.match(r'^confirm_remove_join_code_.+$', c.data), state=RemoveJoinCodeSG.confirm)
@only_for_manager
async def callback_remove_join_code_confirm(callback_query: CallbackQuery, state: FSMContext):
    """Пользователь подтвердил удаление кода"""
    code = callback_query.data.split('_')[4]
    jcf = await get_join_code_factory()
    join_code = await jcf.load(code)

    if not await join_code.is_issued:
        await callback_query.message.answer("❗Код не найден")
        await state.finish()
        return

    await join_code.delete()
    await callback_query.message.answer("✅ Код удален")
    await state.finish()


@dp.callback_query_handler(lambda c: re.match(r'^cancel_remove_join_code_.+$', c.data), state=RemoveJoinCodeSG.confirm)
@only_for_manager
async def callback_remove_join_code_cancel(callback_query: CallbackQuery, state: FSMContext):
    """Пользователь отменил удаление кода"""
    await callback_query.message.answer("❌ Удаление кода отменено")
    await state.finish()


@dp.message_handler(Command(["add_code", "add_join_code"]))
@only_for_manager
async def cmd_add_join_code(message: Message, state: FSMContext):
    """Команда добавления кода подключения к курсу /add_code"""
    result = await choose_course(message)
    if result:
        await state.set_state(AddJoinCodeSG.choose_course)
    else:
        await state.finish()


@dp.callback_query_handler(lambda c: re.match(r'^course_\d+$', c.data), state=AddJoinCodeSG.choose_course)
@only_for_manager
async def callback_add_join_code_course_chosen(callback_query: CallbackQuery, state: FSMContext):
    """Пользователь выбрал курс для создания одноразового кода, предлагает задать комментарий к новому коду"""
    course_id = int(callback_query.data.split('_')[1])
    async with state.proxy() as data:
        data["new_join_code_course_id"] = course_id

    keyboard = InlineKeyboardMarkup()
    button_skip = InlineKeyboardButton("Не указывать", callback_data=f'no_comment')
    keyboard.add(button_skip)

    await callback_query.message.reply(
        "Укажите примечание к коду. Например, можете написать кому планируете отправить этот код, "
        f"чтобы в будущем понять кто не подключился к курсу. Примечание {md.hbold('не будет')} видно преподавателю.",
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )
    await callback_query.answer()

    await state.set_state(AddJoinCodeSG.choose_description)


async def create_code(message: Message, state: FSMContext):
    async with state.proxy() as data:
        cf = await get_course_factory()
        course = await cf.load(course_id=data["new_join_code_course_id"])
        code_f = await get_join_code_factory()
        new_code = await code_f.create(course=course, comment=data["new_join_code_comment"])

    await message.answer(
        "📚 Код создан успешно.\n"
        f"▪ Курс - {md.hitalic(await course.name_quoted)}\n"
        f"▪ Код - {md.hcode(new_code.code)}\n"
        f"▪ Примечание - {md.hitalic(await new_code.comment_quoted or 'НЕ УКАЗАНО')}\n"
        f"Вы можете отправить преподавателю код для подключения или переслать следующее сообщение со специальной "
        f"ссылкой, по которой можно подключиться к курсу.",
        parse_mode=ParseMode.HTML
    )

    bot_info = await dp.bot.get_me()
    magic_link = f"https://t.me/{bot_info.username}?start={new_code.code}"

    await message.answer(
        f"Для подключения к курсу {await course.name_quoted} нажмите -> {md.hlink('ПОДКЛЮЧИТЬСЯ', magic_link)}",
        parse_mode=ParseMode.HTML
    )


@dp.callback_query_handler(lambda c: re.match(r'^no_comment$', c.data), state=AddJoinCodeSG.choose_description)
@only_for_manager
async def callback_add_join_code_no_description(callback_query: CallbackQuery, state: FSMContext):
    """Пользователь решил не указывать тему для урока, предлагаем выбрать период"""
    async with state.proxy() as data:
        data["new_join_code_comment"] = None

    message = callback_query.message

    await create_code(message=message, state=state)

    await callback_query.answer()

    await state.finish()


@dp.message_handler(state=AddJoinCodeSG.choose_description)
@only_for_manager
async def msg_set_join_code_description(message: Message, state: FSMContext):
    """Пользователь прислал примечание к новому коду"""
    async with state.proxy() as data:
        data["new_join_code_comment"] = message.text

    await create_code(message=message, state=state)

    await state.finish()


@dp.message_handler(Command("remove_course"))
@only_for_manager
async def cmd_remove_course(message: Message, state: FSMContext):
    """Команда удаления курса /remove_course"""
    keyboard = InlineKeyboardMarkup()
    cf = await get_course_factory()
    courses = await cf.get_all()
    for course in courses:
        course_name = await course.name
        button = InlineKeyboardButton(course_name, callback_data=f'course_{course.id}')
        keyboard.add(button)

    if len(courses) == 0:
        await message.reply("В системе нет ни одного курса.")
        await state.finish()
    else:
        await message.reply("Выберите курс для удаления:", reply_markup=keyboard)
        await state.set_state(RemoveCourseSG.choose_course)


@dp.callback_query_handler(lambda c: re.match(r'^course_\d+$', c.data), state=RemoveCourseSG.choose_course)
@only_for_manager
async def callback_remove_course_course_chosen(callback_query: CallbackQuery, state: FSMContext):
    """Пользователь выбрал курс для удаления"""
    course_id = int(callback_query.data.split('_')[1])
    async with state.proxy() as data:
        data["remove_course_course_id"] = course_id

    await callback_query.message.reply(
        "Вы уверены что хотите удалить курс? Все уроки, коды подключения и преподаватели будут удалены безвозвратно.",
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton("Да, удалить", callback_data=f'yes'),
            InlineKeyboardButton("Нет, отменить", callback_data=f'no')
        )
    )
    await callback_query.answer()

    await state.set_state(RemoveCourseSG.confirm)


@dp.callback_query_handler(lambda c: re.match(r'^(yes|no)$', c.data), state=RemoveCourseSG.confirm)
@only_for_manager
async def callback_remove_course_confirm_yes(callback_query: CallbackQuery, state: FSMContext):
    """Пользователь подтвердил удаление курса"""
    async with state.proxy() as data:
        course_id = data["remove_course_course_id"]

    if callback_query.data == 'yes':
        cf = await get_course_factory()
        course = await cf.load(course_id=course_id)
        await course.delete()

        await callback_query.message.reply("Курс успешно удален.")
    else:
        await callback_query.message.reply("Удаление курса отменено.")

    await callback_query.answer()

    await state.finish()


async def choose_course(message: Message) -> bool:
    """Выбор курса пользователем"""
    keyboard = InlineKeyboardMarkup()
    cf = await get_course_factory()
    courses = await cf.get_all()
    for course in courses:
        course_name = await course.name
        button = InlineKeyboardButton(course_name, callback_data=f'course_{course.id}')
        keyboard.add(button)
    if len(courses) == 0:
        await message.reply("В системе нет ни одного курса.")
        return False
    else:
        await message.reply("Выберите курс:", reply_markup=keyboard)
        return True


@dp.message_handler(Command("remove_lesson"))
@only_for_manager
async def cmd_remove_lesson(message: Message, state: FSMContext):
    """Команда удаления урока /remove_lesson"""
    result = await choose_course(message)
    if result:
        await state.set_state(RemoveLessonSG.choose_course)
    else:
        await state.finish()


@dp.callback_query_handler(lambda c: re.match(r'^course_\d+$', c.data), state=RemoveLessonSG.choose_course)
@only_for_manager
async def callback_remove_lesson_course_chosen(callback_query: CallbackQuery, state: FSMContext):
    """Пользователь выбрал курс для удаления урока"""
    course_id = int(callback_query.data.split('_')[1])
    async with state.proxy() as data:
        data["remove_lesson_course_id"] = course_id

    result = await choose_lesson(callback_query)
    if result:
        await state.set_state(RemoveLessonSG.choose_lesson)
    else:
        await state.finish()

    await callback_query.answer()


@dp.callback_query_handler(lambda c: re.match(r'^lesson_\d+$', c.data), state=RemoveLessonSG.choose_lesson)
@only_for_manager
async def callback_remove_lesson_lesson_chosen(callback_query: CallbackQuery, state: FSMContext):
    """Пользователь выбрал урок для удаления"""
    lesson_id = int(callback_query.data.split('_')[1])
    async with state.proxy() as data:
        data["remove_lesson_lesson_id"] = lesson_id

    await callback_query.message.reply(
        "Вы уверены что хотите удалить урок? Все коды подключения и преподаватели будут удалены безвозвратно.",
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton("Да, удалить", callback_data=f'yes'),
            InlineKeyboardButton("Нет, отменить", callback_data=f'no')
        )
    )
    await callback_query.answer()

    await state.set_state(RemoveLessonSG.confirm)


@dp.callback_query_handler(lambda c: re.match(r'^(yes|no)$', c.data), state=RemoveLessonSG.confirm)
@only_for_manager
async def callback_remove_lesson_confirm_yes(callback_query: CallbackQuery, state: FSMContext):
    """Пользователь подтвердил удаление урока"""
    async with state.proxy() as data:
        lesson_id = data["remove_lesson_lesson_id"]

    if callback_query.data == 'yes':
        lf = await get_lesson_factory()
        lesson = await lf.load(lesson_id=lesson_id)
        await lesson.delete()

        await callback_query.message.reply("Урок успешно удален.")
    else:
        await callback_query.message.reply("Удаление урока отменено.")

    await callback_query.answer()

    await state.finish()


@dp.message_handler(Command("remove_activity"))
@only_for_manager
async def cmd_remove_activity(message: Message, state: FSMContext):
    """Команда удаления активности /remove_activity"""
    result = await choose_course(message)
    if result:
        await state.set_state(RemoveActivitySG.choose_course)
    else:
        await state.finish()


@dp.callback_query_handler(lambda c: re.match(r'^course_\d+$', c.data), state=RemoveActivitySG.choose_course)
@only_for_manager
async def callback_remove_activity_course_chosen(callback_query: CallbackQuery, state: FSMContext):
    """Пользователь выбрал курс для удаления активности"""
    course_id = int(callback_query.data.split('_')[1])
    async with state.proxy() as data:
        data["remove_activity_course_id"] = course_id

    result = await choose_lesson(callback_query)
    if result:
        await state.set_state(RemoveActivitySG.choose_lesson)
    else:
        await state.finish()

    await callback_query.answer()


@dp.callback_query_handler(lambda c: re.match(r'^lesson_\d+$', c.data), state=RemoveActivitySG.choose_lesson)
@only_for_manager
async def callback_remove_activity_lesson_chosen(callback_query: CallbackQuery, state: FSMContext):
    """Пользователь выбрал урок для удаления активности"""
    lesson_id = int(callback_query.data.split('_')[1])
    async with state.proxy() as data:
        data["remove_activity_lesson_id"] = lesson_id

    result = await choose_activity(callback_query)
    if result:
        await state.set_state(RemoveActivitySG.choose_activity)
    else:
        await state.finish()

    await callback_query.answer()


@dp.callback_query_handler(lambda c: re.match(r'^activity_\d+$', c.data), state=RemoveActivitySG.choose_activity)
@only_for_manager
async def callback_remove_activity_activity_chosen(callback_query: CallbackQuery, state: FSMContext):
    """Пользователь выбрал активность для удаления"""
    activity_id = int(callback_query.data.split('_')[1])
    async with state.proxy() as data:
        data["remove_activity_activity_id"] = activity_id

    await callback_query.message.reply(
        "Вы уверены что хотите удалить активность? Все коды подключения и преподаватели будут удалены безвозвратно.",
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton("Да, удалить", callback_data=f'yes'),
            InlineKeyboardButton("Нет, отменить", callback_data=f'no')
        )
    )
    await callback_query.answer()

    await state.set_state(RemoveActivitySG.confirm)


@dp.callback_query_handler(lambda c: re.match(r'^(yes|no)$', c.data), state=RemoveActivitySG.confirm)
@only_for_manager
async def callback_remove_activity_confirm_yes(callback_query: CallbackQuery, state: FSMContext):
    """Пользователь подтвердил удаление активности"""
    async with state.proxy() as data:
        activity_id = data["remove_activity_activity_id"]

    if callback_query.data == 'yes':
        af = await get_activity_factory()
        activity = await af.load(activity_id=activity_id)
        await activity.delete()

        await callback_query.message.reply("Активность успешно удалена.")
    else:
        await callback_query.message.reply("Удаление активности отменено.")

    await callback_query.answer()

    await state.finish()


@dp.message_handler(Command(["report", "generate_report"]))
@only_for_manager
async def cmd_report(message: Message, state: FSMContext):
    """Команда получения отчета /generate_report"""
    kb_list_or_new = InlineKeyboardMarkup().add(
        InlineKeyboardButton("Список отчетов", callback_data=f'list'),
        InlineKeyboardButton("Создать отчет", callback_data=f'new')
    )
    await message.reply("Выберите действие:", reply_markup=kb_list_or_new)
    await state.set_state(ReportSG.choose_action)


@dp.callback_query_handler(lambda c: re.match(r'^new$', c.data), state=ReportSG.choose_action)
@only_for_manager
async def callback_report_new(callback_query: CallbackQuery, state: FSMContext):
    """Пользователь выбрал создание отчета"""
    await callback_query.answer()
    await callback_query.bot.send_chat_action(callback_query.message.chat.id, ChatActions.UPLOAD_DOCUMENT)
    cf = await get_course_factory()
    teacher_tg_link = TeacherTelegramLink(bot=callback_query.bot)
    teacher_activity_link = await (await get_teacher_activity_link_factory()).create()
    course_teacher_link = await (await get_course_teacher_link_factory()).create()
    generator = ReportGenerator(
        course_factory=cf,
        teacher_tg_link=teacher_tg_link,
        teacher_activity_link=teacher_activity_link,
        course_teacher_link=course_teacher_link,
    )

    workbook = await generator.generate_report()
    excel_persistence_factory = await get_excel_report_persistence_factory()
    excel_persistence = await excel_persistence_factory.create(workbook=workbook)

    bytes_stream = io.BytesIO()
    workbook.save(bytes_stream)
    bytes_stream.seek(0)

    created_at = await excel_persistence.created_at
    filename = f"courses_report_{created_at.strftime('%d.%m.%Y_%H-%M-%S')}.xlsx"

    await callback_query.message.answer_document(types.InputFile(bytes_stream, filename))
    await state.finish()


@dp.callback_query_handler(lambda c: re.match(r'^list$', c.data), state=ReportSG.choose_action)
@only_for_manager
async def callback_report_list(callback_query: CallbackQuery, state: FSMContext):
    """Пользователь выбрал список отчетов"""
    await callback_query.answer()

    excel_persistence_factory = await get_excel_report_persistence_factory()
    reports = await excel_persistence_factory.get_all()

    if not reports:
        await callback_query.message.reply("Список отчетов пуст.")
        await state.finish()
        return

    kb_reports = InlineKeyboardMarkup()
    for report in reports:
        kb_reports.add(
            InlineKeyboardButton(
                (await report.created_at).strftime('%d.%m.%Y %H:%M:%S'),
                callback_data=f'report_{report.id}'
            )
        )

    await callback_query.message.reply("Выберите отчет:", reply_markup=kb_reports)
    await state.set_state(ReportSG.choose_report)


@dp.callback_query_handler(lambda c: re.match(r'^report_\d+$', c.data), state=ReportSG.choose_report)
@only_for_manager
async def callback_report_chosen(callback_query: CallbackQuery, state: FSMContext):
    """Пользователь выбрал отчет"""
    await callback_query.answer()
    await callback_query.bot.send_chat_action(callback_query.message.chat.id, ChatActions.UPLOAD_DOCUMENT)

    report_id = int(callback_query.data.split('_')[1])
    excel_persistence_factory = await get_excel_report_persistence_factory()
    report = await excel_persistence_factory.load(report_id=report_id)

    bytes_stream = io.BytesIO()
    workbook = await report.get_workbook()
    workbook.save(bytes_stream)
    bytes_stream.seek(0)

    created_at = await report.created_at
    filename = f"courses_report_{created_at.strftime('%d.%m.%Y_%H-%M-%S')}.xlsx"

    await callback_query.message.answer_document(types.InputFile(bytes_stream, filename))
    await state.finish()


@dp.message_handler(Command("edit_course"))
@only_for_manager
async def cmd_edit_course(message: Message, state: FSMContext):
    """Команда редактирования курса /edit_course"""
    await choose_course(message)
    await state.set_state(EditCourseSG.choose_course)


@dp.callback_query_handler(lambda c: re.match(r'^course_\d+$', c.data), state=EditCourseSG.choose_course)
@only_for_manager
async def callback_edit_course_chosen(callback_query: CallbackQuery, state: FSMContext):
    """Пользователь выбрал курс для редактирования"""
    await callback_query.answer()
    course_id = int(callback_query.data.split('_')[1])
    await state.update_data(course_id=course_id)
    kb_edit_course = InlineKeyboardMarkup()
    kb_edit_course.add(
        InlineKeyboardButton("Изменить название", callback_data=f'edit_name'),
        InlineKeyboardButton("Изменить описание", callback_data=f'edit_description'),
    )
    await callback_query.message.reply("Выберите действие:", reply_markup=kb_edit_course)
    await state.set_state(EditCourseSG.choose_action)


@dp.callback_query_handler(
    lambda c: re.match(r'^(edit_name|edit_description)$', c.data), state=EditCourseSG.choose_action
)
@only_for_manager
async def callback_edit_course_action(callback_query: CallbackQuery, state: FSMContext):
    """Пользователь выбрал действие для редактирования курса"""
    await callback_query.answer()
    action = callback_query.data
    course_id = (await state.get_data())['course_id']
    course = await (await get_course_factory()).load(course_id=course_id)
    info_msg = md.text(
        md.text("Название: ", md.hbold(await course.name)),
        md.text("Описание: ", md.hcode(await course.description)),
        sep='\n',
    )
    await callback_query.message.reply(info_msg, parse_mode=ParseMode.HTML)
    if action == 'edit_name':
        await callback_query.message.reply("Введите новое название курса:")
        await state.set_state(EditCourseSG.edit_name)
    elif action == 'edit_description':
        await callback_query.message.reply("Введите новое описание курса:")
        await state.set_state(EditCourseSG.edit_description)


@dp.message_handler(state=EditCourseSG.edit_name)
@only_for_manager
async def edit_course_name(message: Message, state: FSMContext):
    """Пользователь ввел новое название курса"""
    course_id = (await state.get_data())['course_id']
    course = await (await get_course_factory()).load(course_id=course_id)
    await course.set_name(message.text)
    await message.reply(f"Название курса изменено:\n{md.hbold(message.text)}", parse_mode=ParseMode.HTML)
    await state.finish()


@dp.message_handler(state=EditCourseSG.edit_description)
@only_for_manager
async def edit_course_description(message: Message, state: FSMContext):
    """Пользователь ввел новое описание курса"""
    course_id = (await state.get_data())['course_id']
    course = await (await get_course_factory()).load(course_id=course_id)
    await course.set_description(message.text)
    await message.reply(f"Описание курса изменено:\n{md.hcode(message.text)}", parse_mode=ParseMode.HTML)
    await state.finish()


@dp.message_handler(lambda message: message.text.startswith('/'))
async def unknown_command(message: types.Message):
    await message.reply(
        "Неизвестная команда. Помощь по командам /help."
    )


@dp.callback_query_handler()
async def unknown_handler(callback_query: CallbackQuery):
    await callback_query.answer("Ошибка")
    await callback_query.message.reply(
        "Кнопка устарела. Помощь по командам /help."
    )


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False)
