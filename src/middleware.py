from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import ChatActions, Message


class TypingMiddleware(BaseMiddleware):
    async def trigger(self, action, args):
        if isinstance(args[0], Message) and action == 'process_message':
            message = args[0]
            chat_id = message.chat.id
            bot = message.bot
            # Устанавливаем статус "печатает..."
            await bot.send_chat_action(chat_id, ChatActions.TYPING)

            # Вызываем следующий middleware или обработчик в цепочке
            return await super().trigger(action, args)
