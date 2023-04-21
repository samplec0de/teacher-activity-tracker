from typing import List

import asyncpg

from activity.activity import Activity
from activity.pg_activity import PGActivity
from lesson.lesson import Lesson


class ActivityFactory:
    """Интерфейс для создания и загрузки активности"""

    def __init__(self, pool: asyncpg.pool.Pool):
        self._pool = pool

    async def create(self, name: str, lesson_id: int) -> Activity:
        """Создает активность, привязанную к уроку"""
        async with self._pool.acquire() as conn:
            query = f'INSERT INTO activities (name, lesson_id) VALUES ($1, $2) RETURNING activity_id;'
            activity_id = await conn.fetchval(query, name, lesson_id)
            return PGActivity(activity_id=activity_id, pool=self._pool)

    async def load(self, activity_id: int) -> Activity:
        """Получение объекта урока по id"""
        return PGActivity(activity_id=activity_id, pool=self._pool)

    async def get_all(self, lesson: Lesson) -> List[Activity]:
        """Получение всех активностей урока"""
        async with self._pool.acquire() as conn:
            query = f'SELECT activity_id FROM activities WHERE lesson_id = $1;'
            activity_ids = await conn.fetch(query, lesson.id)
            return [await self.load(row['activity_id']) for row in activity_ids]
