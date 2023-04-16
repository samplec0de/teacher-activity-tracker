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
    CallbackQuery, Message, ParseMode
from aiogram.utils import executor

import admin_client
from activity.activity import Activity
from activity.activity_factory import ActivityFactory
from course.course import Course
from course.course_factory import CourseFactory
from course.join_code.join_code import CourseJoinCode
from course.join_code.join_code_factory import CourseJoinCodeFactory
from database import get_pool
from lesson.lesson import Lesson
from lesson.lesson_factory import LessonFactory
from teacher.teacher_factory import TeacherFactory

logging.basicConfig(level=logging.INFO)

bot = Bot(token='5952854813:AAFemh5A5MbK_EBZB8p7BBjDnYvWpjav-Eo')
dp = Dispatcher(bot, storage=MemoryStorage())


join_code_factory = None
teacher_factory = None
course_factory = None
lesson_factory = None
activity_factory = None


class AddCourseSG(StatesGroup):
    get_name = State()
    get_description = State()


class AddLessonSG(StatesGroup):
    choose_course = State()
    choose_topic = State()
    choose_period = State()


class AddActivitySG(StatesGroup):
    choose_course = State()
    choose_lesson = State()
    choose_name = State()


async def get_join_code_factory():
    global join_code_factory
    if join_code_factory is None:
        join_code_factory = CourseJoinCodeFactory(pool=await get_pool())
    return join_code_factory


async def get_teacher_factory():
    global teacher_factory
    if teacher_factory is None:
        teacher_factory = TeacherFactory(pool=await get_pool())
    return teacher_factory


async def get_course_factory():
    global course_factory
    if course_factory is None:
        course_factory = CourseFactory(pool=await get_pool())
    return course_factory


async def get_lesson_factory():
    global lesson_factory
    if lesson_factory is None:
        lesson_factory = LessonFactory(pool=await get_pool())
    return lesson_factory


async def get_activity_factory():
    global activity_factory
    if activity_factory is None:
        activity_factory = ActivityFactory(pool=await get_pool())
    return activity_factory


@dp.message_handler(CommandStart())
async def start_command(message: types.Message):
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
async def process_my_courses_message(message: types.Message):
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


@dp.callback_query_handler(lambda c: re.match(r'^course_\d+$', c.data))
async def process_course_callback(callback_query: CallbackQuery):
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


@dp.callback_query_handler(lambda c: re.match(r'^lesson_\d+$', c.data))
async def process_lesson_callback(callback_query: CallbackQuery):
    lesson_id = int(callback_query.data.split('_')[1])
    lesson: Lesson = await (await get_lesson_factory()).load(lesson_id=lesson_id)

    keyboard = InlineKeyboardMarkup()
    activities: Tuple[Activity] = await lesson.activities
    for activity in activities:
        activity_topic = await activity.name
        button = InlineKeyboardButton(activity_topic, callback_data=f'activity_{lesson.id}')
        keyboard.add(button)

    await callback_query.message.reply(text="Выберите активность", reply_markup=keyboard)
    await callback_query.answer()


@dp.message_handler(Command("cancel"), state='*')
async def cmd_add_course(message: Message, state: FSMContext):
    await message.answer("Галя, отмена!")
    await state.finish()


@dp.message_handler(Command("add_course"))
async def cmd_add_course(message: Message, state: FSMContext):
    await message.answer(
        "Хорошо, давайте добавим новый курс. Если передумаете, пишите /cancel. Как будет называться новый курс?"
    )
    await state.set_state(AddCourseSG.get_name)


@dp.message_handler(state=AddCourseSG.get_name)
async def msg_set_course_name(message: Message, state: FSMContext):
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
    message = callback_query.message
    async with state.proxy() as data:
        cf = await get_course_factory()
        course = await cf.create(name=data["course_name"], description=None)
        await message.answer(f"Курс {md.hbold(await course.name)} добавлен!", parse_mode=ParseMode.HTML)
    await callback_query.answer()
    await state.finish()


@dp.message_handler(state=AddCourseSG.get_description)
async def msg_set_course_desc(message: Message, state: FSMContext):
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
    """Команда добавления курса"""
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
    """Пользователь выбрал курс, предложить указать тему"""
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
    """Пользователь решил не указывать тему для урока, предлагаем выбрать период"""
    async with state.proxy() as data:
        data["lesson_topic"] = None

    message = callback_query.message
    await message.answer(admin_client.messages.SET_PERIOD_SUGGESTION, parse_mode=ParseMode.HTML)
    await callback_query.answer()

    await state.set_state(AddLessonSG.choose_period)


@dp.message_handler(state=AddLessonSG.choose_topic)
async def msg_set_lesson_topic(message: Message, state: FSMContext):
    """Пользователь прислал тему урока, предлагаем выбрать период"""
    async with state.proxy() as data:
        data["lesson_topic"] = message.text

    await message.answer(admin_client.messages.SET_PERIOD_SUGGESTION, parse_mode=ParseMode.HTML)

    await state.set_state(AddLessonSG.choose_period)


@dp.message_handler(state=AddLessonSG.choose_period)
async def msg_set_lesson_period(message: Message, state: FSMContext):
    """Пользователь прислал период сбора активности по курсу"""
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
    """Команда добавления активности"""
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
async def callback_add_course_lesson_choosed(callback_query: CallbackQuery, state: FSMContext):
    lesson_id = int(callback_query.data.split('_')[1])

    async with state.proxy() as data:
        data["new_activity_lesson_id"] = lesson_id

    await callback_query.message.reply(text="Какое будет название у новой активности?")
    await callback_query.answer()

    await state.set_state(AddActivitySG.choose_name)


@dp.message_handler(state=AddActivitySG.choose_name)
async def msg_set_activity_name(message: Message, state: FSMContext):
    """Пользователь прислал имя новой активности"""
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


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False)
