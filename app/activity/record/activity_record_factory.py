from typing import Optional

import asyncpg

from activity.record.activity_record import ActivityRecord
from activity.record.pg_activity_record import PGActivityRecord


class ActivityRecordFactory:
    """Интерфейс для создания и загрузки записей (отметок) активности"""

    def __init__(self, pool: asyncpg.pool.Pool):
        self._pool = pool

    async def create(self, teacher_id: int, activity_id: int, hours: float, comment: Optional[str]) -> ActivityRecord:
        """Создает запись об активности"""
        async with self._pool.acquire() as conn:
            query = f'INSERT INTO activity_records (teacher_id, activity_id, hours, comment) ' \
                    f'VALUES ($1, $2, $3, $4) RETURNING record_id;'
            activity_record_id = await conn.fetchval(query, teacher_id, activity_id, hours, comment)
            return PGActivityRecord(activity_record_id=activity_record_id, pool=self._pool)

    async def load(self, activity_record_id: int) -> ActivityRecord:
        """Получение объекта записи об активности по id"""
        return PGActivityRecord(activity_record_id=activity_record_id, pool=self._pool)
