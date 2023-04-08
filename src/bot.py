import logging

import asyncpg
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters import CommandStart
from aiogram.utils import executor

from course.join_code.join_code import CourseJoinCode
from course.join_code.join_code_factory import CourseJoinCodeFactory
from database import create_pool
from teacher.teacher_factory import TeacherFactory

logging.basicConfig(level=logging.INFO)

bot = Bot(token='5952854813:AAFemh5A5MbK_EBZB8p7BBjDnYvWpjav-Eo')
dp = Dispatcher(bot)

asyncpg_pool: asyncpg.pool.Pool = create_pool()

join_code_factory = CourseJoinCodeFactory(pool=asyncpg_pool)
teacher_factory = TeacherFactory(pool=asyncpg_pool)


@dp.message_handler(CommandStart())
async def start_command(message: types.Message):
    username = message.from_user.first_name
    # Получаем аргументы команды
    parameter_value = message.get_args()
    # Если есть аргументы, отправляем сообщение с ними
    if parameter_value:
        join_code: CourseJoinCode = await join_code_factory.load(code=parameter_value)
        if join_code.course is None:
            await message.reply(f'Кода "{parameter_value}" не существует')
        elif join_code.activated_by is not None:
            await message.reply(f'Код "{parameter_value}" уже активирован')
        else:
            await message.reply(f'Подключаю по коду "{parameter_value}"...')
            course = await join_code.course
            course_title = await course.title
            await message.reply(f'Курс: "{course_title}"')
            telegram_id = message.from_user.id
            teacher = await teacher_factory.load(teacher_id=telegram_id)
            await join_code.activate(teacher=teacher)
            await message.reply(f'Подключение к курсу "{course_title}" успешно!')
    # Если аргументов нет, отправляем обычное сообщение
    else:
        await message.reply("Привет, {username}! Перейди по специальной ссылке для подключения к курсу.")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False)
