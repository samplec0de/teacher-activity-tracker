import datetime
import logging
import re
from typing import Tuple

import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart, Command
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, \
    CallbackQuery, Message, ParseMode, BotCommand
from aiogram.utils import executor

import admin_client
from activity.activity import Activity
from activity.activity_factory import ActivityFactory
from activity.record.pg_activity_record_factory import ActivityRecordFactory
from course.course import Course
from course.course_factory import CourseFactory
from course.join_code.join_code import CourseJoinCode
from course.join_code.join_code_factory import CourseJoinCodeFactory
from database import get_pool
from lesson.lesson import Lesson
from lesson.lesson_factory import LessonFactory
from teacher.teacher import Teacher
from teacher.teacher_factory import TeacherFactory

logging.basicConfig(level=logging.INFO)

bot = Bot(token='5952854813:AAFemh5A5MbK_EBZB8p7BBjDnYvWpjav-Eo')
dp = Dispatcher(bot, storage=MemoryStorage())

TEACHER_COMMANDS = [
    BotCommand('start', 'Начать работу'),
    BotCommand('mark_activity', 'Отметить активность'),
]

join_code_factory = None
teacher_factory = None
course_factory = None
lesson_factory = None
activity_factory = None
activity_record_factory = None


class MarkActivitySG(StatesGroup):
    """Группа состояний aiogram процесса отметки активности"""
    choose_course = State()
    choose_lesson = State()
    choose_activity = State()
    choose_comment = State()
    choose_hours = State()


class AddCourseSG(StatesGroup):
    """Группа состояний aiogram процесса добавления курса"""
    get_name = State()
    get_description = State()


class AddLessonSG(StatesGroup):
    """Группа состояний aiogram процесса добавления урока в курс"""
    choose_course = State()
    choose_topic = State()
    choose_period = State()


class AddActivitySG(StatesGroup):
    """Группа состояний aiogram процесса добавления активности в урок по курсу"""
    choose_course = State()
    choose_lesson = State()
    choose_name = State()


class AddJoinCodeSG(StatesGroup):
    """Группа состояний aiogram процесса добавления кода подключения к курсу"""
    choose_course = State()
    choose_description = State()


class RemoveCourseSG(StatesGroup):
    """Группа состояний aiogram процесса удаления курса"""
    choose_course = State()
    confirm = State()


class RemoveLessonSG(StatesGroup):
    """Группа состояний aiogram процесса удаления урока"""
    choose_course = State()
    choose_lesson = State()
    confirm = State()


class RemoveActivitySG(StatesGroup):
    """Группа состояний aiogram процесса удаления активности"""
    choose_course = State()
    choose_lesson = State()
    choose_activity = State()
    confirm = State()


async def get_join_code_factory() -> CourseJoinCodeFactory:
    """Фабрика одноразовых кодов подключения к курсу"""
    global join_code_factory
    if join_code_factory is None:
        join_code_factory = CourseJoinCodeFactory(pool=await get_pool())
    return join_code_factory


async def get_teacher_factory() -> TeacherFactory:
    """Фабрика учителей"""
    global teacher_factory
    if teacher_factory is None:
        teacher_factory = TeacherFactory(pool=await get_pool())
    return teacher_factory


async def get_course_factory() -> CourseFactory:
    """Фабрика курсов"""
    global course_factory
    if course_factory is None:
        course_factory = CourseFactory(pool=await get_pool())
    return course_factory


async def get_lesson_factory() -> LessonFactory:
    """Фабрика уроков"""
    global lesson_factory
    if lesson_factory is None:
        lesson_factory = LessonFactory(pool=await get_pool())
    return lesson_factory


async def get_activity_factory() -> ActivityFactory:
    """Фабрика активностей"""
    global activity_factory
    if activity_factory is None:
        activity_factory = ActivityFactory(pool=await get_pool())
    return activity_factory


async def get_activity_record_factory() -> ActivityRecordFactory:
    """Фабрика записей активности"""
    global activity_record_factory
    if activity_record_factory is None:
        activity_record_factory = ActivityRecordFactory(pool=await get_pool())
    return activity_record_factory


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
        text = "Перейди по специальной ссылке или введи /start КОД_АКТИВАЦИИ"

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    button_my_courses = KeyboardButton('Мои курсы')
    keyboard.add(button_my_courses)

    await message.reply(text, reply_markup=keyboard)


@dp.message_handler(text='Мои курсы')
async def msg_my_courses(message: types.Message, state: FSMContext):
    """Обработка сообщения "Мои курсы" для запроса списка курсов и последующей отметки активности"""
    telegram_id = message.from_user.id
    teacher = await (await get_teacher_factory()).load(teacher_id=telegram_id)
    if not await teacher.registered:
        await message.reply("Пeрeйди по спeциальной ссылкe или ввeди /start КОД_АКТИВАЦИИ")
        return

    keyboard = InlineKeyboardMarkup()
    courses = await teacher.courses
    for course in courses:
        course_name = await course.name
        button = InlineKeyboardButton(course_name, callback_data=f'course_{course.id}')
        keyboard.add(button)

    await message.reply("Выберите курс", reply_markup=keyboard)

    await state.set_state(MarkActivitySG.choose_course)


@dp.callback_query_handler(lambda c: re.match(r'^course_\d+$', c.data), state=MarkActivitySG.choose_course)
async def callback_mark_activity_choose_course(callback_query: CallbackQuery, state: FSMContext):
    """Обработчик кнопки выбора курса для отметки активности"""
    course_id = int(callback_query.data.split('_')[1])
    course: Course = await (await get_course_factory()).load(course_id=course_id)

    keyboard = InlineKeyboardMarkup()
    lessons: Tuple[Lesson] = await course.lessons
    for lesson in lessons:
        lesson_date = await lesson.date_from
        lesson_date_str = lesson_date.strftime("%d.%m.%Y")
        lesson_topic = await lesson.topic
        lesson_label = f"{lesson_date_str}: {lesson_topic}"
        button = InlineKeyboardButton(lesson_label, callback_data=f'lesson_{lesson.id}')
        keyboard.add(button)

    if len(lessons) == 0:
        await callback_query.message.reply(text="У курса нет уроков")
        await state.finish()
    else:
        await callback_query.message.reply(text="Выберите урок", reply_markup=keyboard)
        await state.set_state(MarkActivitySG.choose_lesson)

    await callback_query.answer()


@dp.callback_query_handler(lambda c: re.match(r'^lesson_\d+$', c.data), state=MarkActivitySG.choose_lesson)
async def callback_mark_activity_choose_lesson(callback_query: CallbackQuery, state: FSMContext):
    """Обработчик кнопки выбора урока для отметки активности"""
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
        await state.finish()
    else:
        await callback_query.message.reply(text="Выберите активность", reply_markup=keyboard)
        await state.set_state(MarkActivitySG.choose_activity)

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
async def cmd_add_course(message: Message, state: FSMContext):
    """Обработчик команды отмены, работает из любого состояния"""
    await message.answer("Галя, отмена!")
    await state.finish()


@dp.message_handler(Command("add_course"))
async def cmd_add_course(message: Message, state: FSMContext):
    """Обработчик команды добавления курса /add_course"""
    await message.answer(
        "Хорошо, давайте добавим новый курс. Если передумаете, пишите /cancel. Как будет называться новый курс?"
    )
    await state.set_state(AddCourseSG.get_name)


@dp.message_handler(state=AddCourseSG.get_name)
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
async def create_course_no_description(callback_query: CallbackQuery, state: FSMContext):
    """Обработчик нажатия кнопки "Пропустить", ветка, где курс создается без описания процесса создания курса"""
    message = callback_query.message
    async with state.proxy() as data:
        cf = await get_course_factory()
        course = await cf.create(name=data["course_name"], description=None)
        await message.answer(f"Курс {md.hbold(await course.name)} добавлен!", parse_mode=ParseMode.HTML)
    await callback_query.answer()
    await state.finish()


@dp.message_handler(state=AddCourseSG.get_description)
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
    await state.finish()


@dp.message_handler(Command("add_lesson"))
async def cmd_add_lesson(message: Message, state: FSMContext):
    """Команда добавления урока /add_lesson"""
    keyboard = InlineKeyboardMarkup()
    cf = await get_course_factory()
    courses = await cf.get_all()
    for course in courses:
        course_name = await course.name
        button = InlineKeyboardButton(course_name, callback_data=f'course_{course.id}')
        keyboard.add(button)

    await message.reply("Выберите курс, в который хотите добавить урок", reply_markup=keyboard)
    await state.set_state(AddLessonSG.choose_course)


@dp.callback_query_handler(lambda c: re.match(r'^course_\d+$', c.data), state=AddLessonSG.choose_course)
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
async def callback_add_lesson_no_topic(callback_query: CallbackQuery, state: FSMContext):
    """Обработчик кнопки "Не указывать" [тему] для урока в процессе создания урока, предлагаем выбрать период"""
    async with state.proxy() as data:
        data["lesson_topic"] = None

    message = callback_query.message
    await message.answer(admin_client.messages.SET_PERIOD_SUGGESTION, parse_mode=ParseMode.HTML)
    await callback_query.answer()

    await state.set_state(AddLessonSG.choose_period)


@dp.message_handler(state=AddLessonSG.choose_topic)
async def msg_set_lesson_topic(message: Message, state: FSMContext):
    """Обработчик темы прислал урока в процессе создания урока, предлагаем выбрать период"""
    async with state.proxy() as data:
        data["lesson_topic"] = message.text

    await message.answer(admin_client.messages.SET_PERIOD_SUGGESTION, parse_mode=ParseMode.HTML)

    await state.set_state(AddLessonSG.choose_period)


@dp.message_handler(state=AddLessonSG.choose_period)
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

    await state.finish()


@dp.message_handler(Command("add_activity"))
async def cmd_add_activity(message: Message, state: FSMContext):
    """Команда добавления активности /add_activity"""
    keyboard = InlineKeyboardMarkup()
    cf = await get_course_factory()
    courses = await cf.get_all()
    for course in courses:
        course_name = await course.name
        button = InlineKeyboardButton(course_name, callback_data=f'course_{course.id}')
        keyboard.add(button)

    await message.reply("Выберите курс, в который хотите добавить активность", reply_markup=keyboard)
    await state.set_state(AddActivitySG.choose_course)


@dp.callback_query_handler(lambda c: re.match(r'^course_\d+$', c.data), state=AddActivitySG.choose_course)
async def callback_add_course_choosed(callback_query: CallbackQuery, state: FSMContext):
    """Пользователь выбрал курс в процессе добавления активности"""
    course_id = int(callback_query.data.split('_')[1])
    course: Course = await (await get_course_factory()).load(course_id=course_id)

    keyboard = InlineKeyboardMarkup()
    lessons: Tuple[Lesson] = await course.lessons
    for lesson in lessons:
        lesson_date = await lesson.date_from
        lesson_date_str = lesson_date.strftime("%d.%m.%Y")
        lesson_topic = await lesson.topic
        lesson_label = f"{lesson_date_str}: {lesson_topic}"
        button = InlineKeyboardButton(lesson_label, callback_data=f'lesson_{lesson.id}')
        keyboard.add(button)

    await callback_query.message.reply(text="Выберите урок", reply_markup=keyboard)
    await callback_query.answer()

    await state.set_state(AddActivitySG.choose_lesson)


@dp.callback_query_handler(lambda c: re.match(r'^lesson_\d+$', c.data), state=AddActivitySG.choose_lesson)
async def callback_add_activity_lesson_choosed(callback_query: CallbackQuery, state: FSMContext):
    """Обработчик выбора урока в процессе добавления активности"""
    lesson_id = int(callback_query.data.split('_')[1])

    async with state.proxy() as data:
        data["new_activity_lesson_id"] = lesson_id

    await callback_query.message.reply(text="Какое будет название у новой активности?")
    await callback_query.answer()

    await state.set_state(AddActivitySG.choose_name)


@dp.message_handler(state=AddActivitySG.choose_name)
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

    await state.finish()


@dp.message_handler(Command("add_code"))
async def cmd_add_join_code(message: Message, state: FSMContext):
    """Команда добавления кода подключения к курсу /add_code"""
    keyboard = InlineKeyboardMarkup()
    cf = await get_course_factory()
    courses = await cf.get_all()
    for course in courses:
        course_name = await course.name
        button = InlineKeyboardButton(course_name, callback_data=f'course_{course.id}')
        keyboard.add(button)

    await message.reply("Выберите курс для создания кода подключения:", reply_markup=keyboard)
    await state.set_state(AddJoinCodeSG.choose_course)


@dp.callback_query_handler(lambda c: re.match(r'^course_\d+$', c.data), state=AddJoinCodeSG.choose_course)
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
async def callback_add_join_code_no_description(callback_query: CallbackQuery, state: FSMContext):
    """Пользователь решил не указывать тему для урока, предлагаем выбрать период"""
    async with state.proxy() as data:
        data["new_join_code_comment"] = None

    message = callback_query.message

    await create_code(message=message, state=state)

    await callback_query.answer()

    await state.finish()


@dp.message_handler(state=AddJoinCodeSG.choose_description)
async def msg_set_join_code_description(message: Message, state: FSMContext):
    """Пользователь прислал примечание к новому коду"""
    async with state.proxy() as data:
        data["new_join_code_comment"] = message.text

    await create_code(message=message, state=state)

    await state.finish()


@dp.message_handler(Command("remove_course"))
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


@dp.message_handler(Command("remove_lesson"))
async def cmd_remove_lesson(message: Message, state: FSMContext):
    """Команда удаления урока /remove_lesson"""
    keyboard = InlineKeyboardMarkup()
    cf = await get_course_factory()
    courses = await cf.get_all()
    for course in courses:
        course_name = await course.name
        button = InlineKeyboardButton(course_name, callback_data=f'course_{course.id}')
        keyboard.add(button)
    await message.reply("Выберите курс:", reply_markup=keyboard)
    await state.set_state(RemoveLessonSG.choose_course)


@dp.callback_query_handler(lambda c: re.match(r'^course_\d+$', c.data), state=RemoveLessonSG.choose_course)
async def callback_remove_lesson_course_chosen(callback_query: CallbackQuery, state: FSMContext):
    """Пользователь выбрал курс для удаления урока"""
    course_id = int(callback_query.data.split('_')[1])
    async with state.proxy() as data:
        data["remove_lesson_course_id"] = course_id

    keyboard = InlineKeyboardMarkup()
    lf = await get_lesson_factory()
    lessons = await lf.get_all(course_id=course_id)
    for lesson in lessons:
        lesson_name = await lesson.topic
        button = InlineKeyboardButton(text=lesson_name, callback_data=f'lesson_{lesson.id}')
        keyboard.add(button)

    await callback_query.message.reply("Выберите урок для удаления:", reply_markup=keyboard)
    await callback_query.answer()

    await state.set_state(RemoveLessonSG.choose_lesson)


@dp.callback_query_handler(lambda c: re.match(r'^lesson_\d+$', c.data), state=RemoveLessonSG.choose_lesson)
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
async def cmd_remove_activity(message: Message, state: FSMContext):
    """Команда удаления активности /remove_activity"""
    # Выбор курса
    keyboard = InlineKeyboardMarkup()
    cf = await get_course_factory()
    courses = await cf.get_all()
    for course in courses:
        course_name = await course.name
        button = InlineKeyboardButton(course_name, callback_data=f'course_{course.id}')
        keyboard.add(button)
    await message.reply("Выберите курс:", reply_markup=keyboard)
    await state.set_state(RemoveActivitySG.choose_course)


@dp.callback_query_handler(lambda c: re.match(r'^course_\d+$', c.data), state=RemoveActivitySG.choose_course)
async def callback_remove_activity_course_chosen(callback_query: CallbackQuery, state: FSMContext):
    """Пользователь выбрал курс для удаления активности"""
    course_id = int(callback_query.data.split('_')[1])
    async with state.proxy() as data:
        data["remove_activity_course_id"] = course_id

    # Выбор урока
    keyboard = InlineKeyboardMarkup()
    lf = await get_lesson_factory()
    lessons = await lf.get_all(course_id=course_id)
    for lesson in lessons:
        lesson_name = await lesson.topic
        button = InlineKeyboardButton(text=lesson_name, callback_data=f'lesson_{lesson.id}')
        keyboard.add(button)

    await callback_query.message.reply("Выберите урок для удаления:", reply_markup=keyboard)
    await callback_query.answer()

    await state.set_state(RemoveActivitySG.choose_lesson)


@dp.callback_query_handler(lambda c: re.match(r'^lesson_\d+$', c.data), state=RemoveActivitySG.choose_lesson)
async def callback_remove_activity_lesson_chosen(callback_query: CallbackQuery, state: FSMContext):
    """Пользователь выбрал урок для удаления активности"""
    lesson_id = int(callback_query.data.split('_')[1])
    async with state.proxy() as data:
        data["remove_activity_lesson_id"] = lesson_id

    # Выбор активности
    keyboard = InlineKeyboardMarkup()
    af = await get_activity_factory()
    lf = await get_lesson_factory()
    lesson = await lf.load(lesson_id=lesson_id)
    activities = await af.get_all(lesson=lesson)
    for activity in activities:
        activity_name = await activity.name
        button = InlineKeyboardButton(text=activity_name, callback_data=f'activity_{activity.id}')
        keyboard.add(button)

    await callback_query.message.reply("Выберите активность для удаления:", reply_markup=keyboard)
    await callback_query.answer()

    await state.set_state(RemoveActivitySG.choose_activity)


@dp.callback_query_handler(lambda c: re.match(r'^activity_\d+$', c.data), state=RemoveActivitySG.choose_activity)
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


@dp.message_handler(lambda message: message.text.startswith('/'))
async def unknown_command(message: types.Message):
    await message.reply(
        "Что-то пошло не так, я вас не понял. "
        "Пожалуйста, попробуйте еще раз или отмените запрос с помощью /cancel."
    )


@dp.message_handler(content_types=types.ContentType.ANY)
async def unknown_handler(message: types.Message):
    await message.reply(
        "Что-то пошло не так, я вас не понял. "
        "Пожалуйста, введите команду или отмените текущую операцию с помощью /cancel."
    )


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False)
