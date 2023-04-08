import logging

from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters import CommandStart
from aiogram.utils import executor

from database import create_pool

logging.basicConfig(level=logging.INFO)

bot = Bot(token='5952854813:AAFemh5A5MbK_EBZB8p7BBjDnYvWpjav-Eo')
dp = Dispatcher(bot)

asyncpg_pool = create_pool()



@dp.message_handler(CommandStart())
async def start_command(message: types.Message):
    username = message.from_user.first_name
    # Получаем аргументы команды
    parameter_value = message.get_args()
    # Если есть аргументы, отправляем сообщение с ними
    if parameter_value:

        await message.reply(f"Привет, {username}! Активирую код {parameter_value}.")
    # Если аргументов нет, отправляем обычное сообщение
    else:
        await message.reply("Привет, {username}! Перейди по специальной ссылке для подключения к курсу.")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False)
