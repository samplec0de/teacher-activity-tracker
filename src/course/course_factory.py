from typing import Optional, List

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

    async def get_all(self) -> List[Course]:
        """Получение всех курсов"""
        async with self._pool.acquire() as conn:
            query = f'SELECT course_id FROM courses;'
            course_ids = await conn.fetch(query)
            courses = []
            for row in course_ids:
                courses.append(PGCourse(course_id=row['course_id'], pool=self._pool))
            return courses
