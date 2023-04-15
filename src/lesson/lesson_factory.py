import datetime
from typing import Optional

import asyncpg

from lesson.lesson import Lesson
from lesson.pg_lesson import PGLesson


class LessonFactory:
    """Интерфейс для создания и загрузки уроков"""

    def __init__(self, pool: asyncpg.pool.Pool):
        self._pool = pool

    async def load(self, lesson_id: int) -> Lesson:
        """Получение объекта урока по id"""
        return PGLesson(lesson_id=lesson_id, pool=self._pool)

    async def create(
            self, course_id: int, topic: Optional[str], date_from: datetime.datetime, date_to: datetime.datetime
    ) -> Lesson:
        """Создает новый урок"""
        async with self._pool.acquire() as conn:
            query = f'INSERT INTO lessons (course_id, topic, date_from, date_to) ' \
                    f'VALUES ($1, $2, $3, $4) RETURNING lesson_id;'
            lesson_id = await conn.fetchval(query, course_id, topic, date_from, date_to)
            return PGLesson(lesson_id=lesson_id, pool=self._pool)
