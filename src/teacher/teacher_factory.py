import asyncpg

from teacher.pg_teacher import PGTeacher
from teacher.teacher import Teacher


class TeacherFactory:
    """Интерфейс для создания и загрузки объекта преподавателя"""

    def __init__(self, pool: asyncpg.pool.Pool):
        self._pool = pool

    async def load(self, teacher_id: int) -> Teacher:
        """Получение объекта урока по id"""
        return PGTeacher(teacher_id=teacher_id, pool=self._pool)
