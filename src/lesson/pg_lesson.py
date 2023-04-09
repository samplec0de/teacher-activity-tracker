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
    async def date(self) -> datetime.datetime:
        return await self._get_single_attribute('date')

    @date.setter
    async def date(self, value) -> None:
        await self._set_single_attribute('date', value)

    @property
    async def topic(self) -> str:
        return await self._get_single_attribute('topic')

    @topic.setter
    async def topic(self, value: str) -> None:
        await self._set_single_attribute('topic', value)

    @property
    async def activities(self) -> tuple[Activity, ...]:
        async with self._pool.acquire() as conn:
            query = f'SELECT activity_id FROM activities WHERE lesson_id = $1'
            result = await conn.fetch(query, self._id)
            return tuple([PGActivity(record['activity_id'], pool=self._pool) for record in result])
