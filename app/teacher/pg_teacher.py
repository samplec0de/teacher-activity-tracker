from typing import Tuple

import asyncpg

from course.pg_course import PGCourse
from pg_object import PGObject
from teacher.teacher import Teacher


class PGTeacher(PGObject, Teacher):
    def __init__(self, teacher_id: int, pool: asyncpg.pool.Pool):
        PGObject.__init__(self, object_id=teacher_id, pool=pool, table='teachers', id_column_name='teacher_id')
        Teacher.__init__(self, teacher_id=teacher_id)

    @property
    async def registered(self) -> bool:
        return await self._get_single_attribute('teacher_id') is not None

    async def register(self) -> None:
        if await self.registered:
            return

        async with self._pool.acquire() as conn:
            query = f'INSERT INTO teachers (teacher_id) VALUES ($1)'
            await conn.execute(query, self.id)

    @property
    async def courses(self) -> Tuple[PGCourse]:
        async with self._pool.acquire() as conn:
            query = f'SELECT course_id FROM teacher_courses WHERE teacher_id = $1'
            teacher_courses = await conn.fetch(query, self._id)
            return tuple([PGCourse(course_id=row['course_id'], pool=self._pool) for row in teacher_courses])

    @property
    async def comment(self) -> str:
        return await self._get_single_attribute('comment')

    @comment.setter
    async def comment(self, value: str) -> None:
        await self._set_single_attribute('comment', value)

    @property
    async def is_manager(self) -> bool:
        return await self._get_single_attribute('is_manager')

    async def make_manager(self) -> None:
        await self._set_single_attribute('is_manager', True)
