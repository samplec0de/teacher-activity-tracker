from typing import List

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

    async def get_all(self) -> List[Teacher]:
        """Получение всех преподавателей"""
        teachers_qr = await self._pool.fetch("SELECT teacher_id FROM teachers")
        return [PGTeacher(teacher_id=row['teacher_id'], pool=self._pool) for row in teachers_qr]
