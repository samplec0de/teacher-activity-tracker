import os

import asyncpg


pool = None


async def get_pool() -> asyncpg.pool.Pool:
    global pool
    if pool is None:
        pool = await asyncpg.create_pool(
            user=os.environ.get('POSTGRES_USER'),
            password=os.environ.get('POSTGRES_PASSWORD'),
            database=os.environ.get('POSTGRES_DB'),
            host='postgresql',
            port=5432,
            max_size=100
        )
    return pool
