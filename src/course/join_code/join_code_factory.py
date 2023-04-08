import asyncpg

from course.join_code.join_code import CourseJoinCode
from course.join_code.pg_join_code import PGCourseJoinCode


class CourseJoinCodeFactory:
    """Интерфейс для загрузки кодов подключения"""

    def __init__(self, pool: asyncpg.pool.Pool):
        self._pool = pool

    async def load(self, code: str) -> CourseJoinCode:
        """Получение кода"""
        return PGCourseJoinCode(code=code, pool=self._pool)
