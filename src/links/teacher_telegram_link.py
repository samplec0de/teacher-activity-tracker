from typing import Optional

from aiogram import Bot

from teacher.teacher import Teacher


class TeacherTelegramLink:
    def __init__(self, bot: Bot):
        self._bot = bot

    async def get_full_name(self, teacher: Teacher) -> str:
        """first_name [+ last_name] (при наличии)"""
        teacher_chat = await self._bot.get_chat(teacher.id)
        name = [teacher_chat.first_name, teacher_chat.last_name]
        return ' '.join(list(filter(lambda obj: obj is not None, name)))

    async def get_username(self, teacher: Teacher) -> Optional[str]:
        """Имя пользователя"""
        teacher_chat = await self._bot.get_chat(teacher.id)
        return teacher_chat.username

