from typing import Tuple

import asyncpg

from course.course import Course
from lesson.lesson import Lesson
from lesson.pg_lesson import PGLesson
from pg_object import PGObject


class PGCourse(PGObject, Course):
    def __init__(self, course_id: int, pool: asyncpg.pool.Pool):
        Course.__init__(self, course_id=course_id)
        PGObject.__init__(self, object_id=course_id, pool=pool, table='courses', id_column_name='course_id')

    @property
    async def name(self):
        return await self._get_single_attribute('name')

    @name.setter
    async def name(self, value):
        await self._set_single_attribute('name', value)

    @property
    async def lessons(self) -> Tuple[Lesson, ...]:
        """Список уроков курса"""
        async with self._pool.acquire() as conn:
            lessons_query = "SELECT lesson_id FROM lessons WHERE course_id=$1"
            lessons_qr = await conn.fetch(lessons_query, self.id)
            return tuple([PGLesson(row['lesson_id'], pool=self._pool) for row in lessons_qr])
