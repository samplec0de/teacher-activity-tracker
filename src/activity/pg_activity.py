import asyncpg

from activity.activity import Activity
from pg_object import PGObject


class PGActivity(PGObject, Activity):
    def __init__(self, activity_id: int, pool: asyncpg.pool.Pool):
        PGObject.__init__(self, object_id=activity_id, pool=pool, table='activities', id_column_name='activity_id')
        Activity.__init__(self, activity_id=activity_id)

    @property
    async def name(self) -> str:
        return await self._get_single_attribute('name')

    @name.setter
    async def name(self, value) -> None:
        await self._set_single_attribute('name', value)

    @property
    async def lesson(self) -> 'PGLesson':
        lesson_id = await self._get_single_attribute('lesson_id')
        from lesson.pg_lesson import PGLesson
        return PGLesson(lesson_id=lesson_id, pool=self._pool)
