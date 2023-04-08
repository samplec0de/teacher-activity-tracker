import asyncpg

from activity.activity import Activity
from pg_object import PGObject


class PGActivity(PGObject, Activity):
    def __init__(self, activity_id: int, pool: asyncpg.pool.Pool):
        PGObject.__init__(self, object_id=activity_id, pool=pool, table='activities', id_column_name='activity_id')
        Activity.__init__(self, activity_id=activity_id)

    @property
    async def name(self):
        return await self._get_single_attribute('name')

    @name.setter
    async def name(self, value):
        await self._set_single_attribute('name', value)
