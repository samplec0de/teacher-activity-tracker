from abc import abstractmethod
from typing import List

import asyncpg

from course.course import Course
from teacher.pg_teacher import PGTeacher
from teacher.teacher import Teacher


class CourseTeacherLink:
    def __init__(self):
        pass

    @abstractmethod
    async def get_teachers_for_course(self, course: Course) -> List[Teacher]:
        """Получение всех преподавателей для курса"""
        pass


class PGCourseTeacherLink(CourseTeacherLink):
    def __init__(self, pool: asyncpg.pool.Pool):
        super().__init__()
        self._pool = pool

    async def get_teachers_for_course(self, course: Course) -> List[Teacher]:
        """Получение всех преподавателей для курса"""
        async with self._pool.acquire() as conn:
            query = "SELECT teacher_id FROM teacher_courses WHERE course_id=$1"
            teachers_qr = await conn.fetch(query, course.id)
        return [PGTeacher(teacher_id=row['teacher_id'], pool=self._pool) for row in teachers_qr]


class CourseTeacherLinkFactory:
    def __init__(self, pool: asyncpg.pool.Pool):
        self._pool = pool

    async def create(self) -> CourseTeacherLink:
        return PGCourseTeacherLink(pool=self._pool)
