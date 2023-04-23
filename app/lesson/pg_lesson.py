import datetime

import asyncpg

from activity.activity import Activity
from activity.pg_activity import PGActivity
from lesson.lesson import Lesson
from pg_object import PGObject


class PGLesson(PGObject, Lesson):
    def __init__(self, lesson_id: int, pool: asyncpg.pool.Pool):
        PGObject.__init__(self, object_id=lesson_id, pool=pool, table='lessons', id_column_name='lesson_id')
        Lesson.__init__(self, lesson_id=lesson_id)

    @property
    async def date_from(self) -> datetime.datetime:
        return await self._get_single_attribute('date_from')

    async def set_date_from(self, value) -> None:
        await self._set_single_attribute('date_from', value)

    @property
    async def date_to(self) -> datetime.datetime:
        return await self._get_single_attribute('date_to')

    async def set_date_to(self, value) -> None:
        await self._set_single_attribute('date_to', value)

    @property
    async def topic(self) -> str:
        return await self._get_single_attribute('topic')

    async def set_topic(self, value: str) -> None:
        await self._set_single_attribute('topic', value)

    @property
    async def activities(self) -> tuple[Activity, ...]:
        async with self._pool.acquire() as conn:
            query = f'SELECT activity_id FROM activities WHERE lesson_id = $1'
            result = await conn.fetch(query, self._id)
            return tuple([PGActivity(record['activity_id'], pool=self._pool) for record in result])

    @property
    async def course(self) -> 'PGCourse':
        course_id = await self._get_single_attribute('course_id')
        from course.pg_course import PGCourse
        return PGCourse(course_id=course_id, pool=self._pool)

    async def delete(self) -> None:
        async with self._pool.acquire() as conn:
            queries = [
                f'DELETE FROM activity_records WHERE activity_id IN '
                f'(SELECT activity_id FROM activities WHERE lesson_id=$1);',
                f'DELETE FROM activities WHERE lesson_id=$1;',
                f'DELETE FROM lessons WHERE lesson_id=$1;',
            ]
            for query in queries:
                await conn.execute(query, self._id)
