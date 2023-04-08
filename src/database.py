import asyncpg


async def create_pool() -> asyncpg.pool.Pool:
    pool = await asyncpg.create_pool(
        user='postgres', password='coursework', database='motivation', host='localhost', port=5435
    )
    return pool
