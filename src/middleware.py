from aiogram import Bot, Dispatcher
from aiogram.dispatcher import FSMContext
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


class FSMFinishMiddleware(BaseMiddleware):
    def __init__(self, dispatcher: Dispatcher):
        self.dispatcher = dispatcher
        super().__init__()

    async def trigger(self, action, args):
        if isinstance(args[0], Message) and action == 'process_message' and args[0].text.startswith('/'):
            message: Message = args[0]
            state = FSMContext(
                storage=self.dispatcher.storage, chat=message.chat.id, user=message.from_user.id
            )

            if await state.get_state() is not None:
                await message.answer("Операция отменена")
                await state.finish()

            # Вызываем следующий middleware или обработчик в цепочке
            return await super().trigger(action, args)
