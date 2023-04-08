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
