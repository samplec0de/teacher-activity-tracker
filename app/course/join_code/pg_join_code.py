from typing import Optional

from course.course import Course
from course.join_code.join_code import CourseJoinCode
from course.pg_course import PGCourse
from pg_object import PGObject
from teacher.pg_teacher import PGTeacher


class PGCourseJoinCode(PGObject, CourseJoinCode):

    def __init__(self, pool, code: Optional[str] = None):
        CourseJoinCode.__init__(self, code=code)
        PGObject.__init__(self, object_id=self.code, pool=pool, table='course_join_codes', id_column_name='code_id')

    @property
    async def comment(self) -> str:
        return await self._get_single_attribute('comment')

    @property
    async def course(self) -> Optional[PGCourse]:
        course_id = await self._get_single_attribute('course_id')
        return None if course_id is None else PGCourse(course_id=course_id, pool=self._pool)

    @property
    async def activated_by(self) -> Optional[PGTeacher]:
        teacher_id = await self._get_single_attribute('activated_by_teacher_id')
        return None if teacher_id is None else PGTeacher(teacher_id=teacher_id, pool=self._pool)

    async def activate(self, teacher: PGTeacher) -> bool:
        if await self.activated_by is not None:
            return False
        teacher_id = teacher.id

        async with self._pool.acquire() as conn:
            async with conn.transaction():
                update_query = f'UPDATE course_join_codes SET activated_by_teacher_id=$1 WHERE code_id = $2'
                await conn.execute(update_query, teacher_id, self._id)

                query = f'INSERT INTO teacher_courses (teacher_id, course_id) VALUES ($1, $2);'
                course = await self.course
                course_id = course.id
                teacher_id = teacher.id
                await conn.execute(query, teacher_id, course_id)

        return True

    async def issue(self, course: Course, comment: Optional[str] = None) -> None:
        async with self._pool.acquire() as conn:
            query = f'INSERT INTO course_join_codes (code_id, course_id, comment) VALUES ($1, $2, $3);'
            course_id = course.id
            await conn.execute(query, self.code, course_id, comment)

    async def delete(self) -> None:
        async with self._pool.acquire() as conn:
            query = f'DELETE FROM course_join_codes WHERE code_id=$1;'
            await conn.execute(query, self.code)
