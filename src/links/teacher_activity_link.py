import asyncpg

from activity.activity import Activity
from activity.record.pg_activity_record_factory import ActivityRecordFactory
from database import get_pool
from teacher.teacher import Teacher


class TeacherActivityLink:

    async def get_hours_for_activity_and_teacher(self, activity: Activity, teacher: Teacher) -> float:
        """Подсчет суммы часов по активности для учителя"""
        pass


class PGTeacherActivityLink(TeacherActivityLink):

    def __init__(self, pool: asyncpg.Pool):
        self._pool = pool

    async def get_hours_for_activity_and_teacher(self, activity: Activity, teacher: Teacher) -> float:
        hours = 0
        async with self._pool.acquire() as conn:
            query = "SELECT record_id FROM activity_records WHERE teacher_id=$1 AND activity_id=$2"
            records = await conn.fetch(query, teacher.id, activity.id)

        activity_record_factory = ActivityRecordFactory(pool=await get_pool())

        for record in records:
            activity_record = await activity_record_factory.load(record['record_id'])
            hours += (await activity_record.hours) or 0
        return hours
