import asyncio
import logging

import asyncpg
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

from course.join_code.join_code import CourseJoinCode
from course.join_code.join_code_factory import CourseJoinCodeFactory
from database import get_pool
from teacher.teacher_factory import TeacherFactory

logging.basicConfig(level=logging.INFO)

bot = Bot(token='5952854813:AAFemh5A5MbK_EBZB8p7BBjDnYvWpjav-Eo')
dp = Dispatcher(bot)


join_code_factory = None
teacher_factory = None


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
    if not teacher.registered:
        await message.reply("Пeрeйди по спeциальной ссылкe или ввeди /start КОД_АКТИВАЦИИ")
        return

    keyboard = InlineKeyboardMarkup()
    courses = await teacher.courses
    for course in courses:
        course_name = await course.name
        button = InlineKeyboardButton(course_name, callback_data=f'course_{course.id}')
        keyboard.add(button)

    await message.reply("Выберите курс", reply_markup=keyboard)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False)
