from typing import Optional

import asyncpg

from course.course import Course
from course.pg_course import PGCourse


class CourseFactory:
    """Интерфейс для создания и загрузки курса"""

    def __init__(self, pool: asyncpg.pool.Pool):
        self._pool = pool

    async def create(self, name: str, description: Optional[str]) -> Course:
        """Создает новый курс"""
        async with self._pool.acquire() as conn:
            query = f'INSERT INTO courses (name, description) VALUES ($1, $2) RETURNING course_id;'
            course_id = await conn.fetchval(query, name, description)
            return PGCourse(course_id=course_id, pool=self._pool)

    async def load(self, course_id: int) -> Course:
        """Получение курса по id"""
        return PGCourse(course_id=course_id, pool=self._pool)
