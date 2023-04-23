import asyncpg


pool = None


async def get_pool() -> asyncpg.pool.Pool:
    global pool
    if pool is None:
        pool = await asyncpg.create_pool(
            user='postgres',
            password='coursework',
            database='motivation',
            host='localhost',
            port=5435,
            max_size=100
        )
    return pool
