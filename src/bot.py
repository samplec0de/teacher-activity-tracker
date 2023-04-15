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

from activity.activity import Activity
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


class AddCourseSG(StatesGroup):
    get_name = State()
    get_description = State()


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
    course_name: str = await course.name

    keyboard = InlineKeyboardMarkup()
    lessons: Tuple[Lesson] = await course.lessons
    for lesson in lessons:
        lesson_date = await lesson.date
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
                md.code(description),
                sep='\n'
            ),
            parse_mode=ParseMode.HTML
        )
    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False)
