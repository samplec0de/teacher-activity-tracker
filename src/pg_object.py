from typing import Any

import asyncpg


class PGObject:
    def __init__(self, object_id: int | str, pool: asyncpg.pool.Pool, table: str, id_column_name: str = 'id'):
        self._pool = pool
        self._table = table
        self._id = object_id
        self._id_column_name = id_column_name

    async def _get_single_attribute(self, attribute_name: str) -> Any:
        """Возвращает значение 1 атрибута из БД"""
        async with self._pool.acquire() as conn:
            query = f'SELECT {attribute_name} FROM {self._table} WHERE {self._id_column_name} = $1'
            return await conn.fetchval(query, self._id)

    async def _set_single_attribute(self, attribute_name: str, value):
        """Устанавливает значение 1 атрибута в БД"""
        async with self._pool.acquire() as conn:
            update_query = f'UPDATE {self._table} SET {attribute_name}=$1 WHERE {self._id_column_name} = $2'
            result = await conn.execute(update_query, value, self._id)
            return result
