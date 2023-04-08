import asyncpg

from course.course import Course
from pg_object import PGObject


class PGCourse(PGObject, Course):
    def __init__(self, course_id: int, pool: asyncpg.pool.Pool):
        Course.__init__(self, course_id=course_id)
        PGObject.__init__(self, object_id=course_id, pool=pool, table='courses', id_column_name='course_id')

    @property
    async def name(self):
        return await self._get_single_attribute('name')

    @name.setter
    async def name(self, value):
        await self._set_single_attribute('name', value)
