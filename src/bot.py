import asyncio

from activity.activity_factory import ActivityFactory
from database import create_pool
from lesson.pg_lesson import PGLesson


async def main():
    pool = await create_pool()
    pg_lesson = PGLesson(2, pool)
    topic = await pg_lesson.topic
    print(topic)
    activity_factory = ActivityFactory(pool)
    # new_activity = await activity_factory.create(name='Test activity', lesson_id=pg_lesson.id)
    # print(new_activity.id)
    activities = await pg_lesson.activities
    print(activities)


if __name__ == '__main__':
    asyncio.run(main())
