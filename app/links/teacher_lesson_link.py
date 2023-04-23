from abc import abstractmethod

from lesson import Lesson
from teacher import Teacher, PGTeacher


class TeacherLessonLink:
    @abstractmethod
    async def get_teachers_by_lesson(self, lesson: Lesson) -> list[Teacher]:
        """Получение всех преподавателей, которые ведут урок"""
        pass


class PGTeacherLessonLink(TeacherLessonLink):
    def __init__(self, pool):
        self._pool = pool

    async def get_teachers_by_lesson(self, lesson: Lesson) -> list[Teacher]:
        async with self._pool.acquire() as conn:
            query = f'SELECT teacher_id FROM teacher_courses WHERE course_id=$1;'
            teacher_ids = await conn.fetch(query, (await lesson.course).id)
        return [PGTeacher(teacher_id=row['teacher_id'], pool=self._pool) for row in teacher_ids]


class TeacherLessonLinkFactory:
    def __init__(self, pool):
        self._pool = pool

    async def create(self) -> TeacherLessonLink:
        return PGTeacherLessonLink(pool=self._pool)
