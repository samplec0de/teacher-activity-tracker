import asyncpg

from activity.activity import Activity
from activity.pg_activity import PGActivity
from activity.record.activity_record import ActivityRecord
from pg_object import PGObject
from teacher.pg_teacher import PGTeacher
from teacher.teacher import Teacher


class PGActivityRecord(PGObject, ActivityRecord):
    def __init__(self, activity_record_id: int, pool: asyncpg.Pool):
        """Загрузка записи активности"""
        PGObject.__init__(
            self, object_id=activity_record_id, pool=pool, table='activity_records', id_column_name='activity_id'
        )
        ActivityRecord.__init__(self, activity_record_id=activity_record_id)

    @property
    async def hours(self) -> float:
        """Количество часов"""
        return await self._get_single_attribute('hours')

    @hours.setter
    async def hours(self, value) -> None:
        """Изменение количества часов по активности"""
        await self._set_single_attribute('hours', value)

    @property
    async def activity(self) -> Activity:
        """Активность, к которой принадлежит запись"""
        activity_id = await self._get_single_attribute('activity_id')
        return PGActivity(activity_id=activity_id, pool=self._pool)

    @property
    async def teacher(self) -> Teacher:
        """Учитель, который заявил активность"""
        teacher_id = await self._get_single_attribute('teacher_id')
        return PGTeacher(teacher_id=teacher_id, pool=self._pool)
