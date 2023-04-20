from typing import List

import openpyxl as openpyxl

from course.course import Course
from links.teacher_activity_link import TeacherActivityLink
from links.teacher_telegram_link import TeacherTelegramLink
from teacher.teacher import Teacher


class ReportGenerator:
    def __init__(self, teacher_tg_link: TeacherTelegramLink, teacher_activity_link: TeacherActivityLink):
        self._teacher_tg_link = teacher_tg_link
        self._teacher_activity_link = teacher_activity_link

    async def generate_report(self, courses: List[Course], teachers: List[Teacher], file_name: str):
        # Создание новой книги
        workbook = openpyxl.Workbook()

        for course in courses:
            # Создание нового листа с именем курса
            sheet = workbook.active if workbook.active.title == "Sheet" else workbook.create_sheet()
            sheet.title = await course.name

            # Заполнение первой строки именами преподавателей
            for idx, teacher in enumerate(teachers):
                sheet.cell(row=1, column=idx + 3).value = await self._teacher_tg_link.get_full_name(teacher)

            lessons = await course.lessons
            for l_idx, lesson in enumerate(lessons):
                # Заполнение списка уроков курса в первом столбце
                sheet.cell(row=l_idx + 2, column=1).value = await lesson.topic

                activities = await lesson.activities
                for a_idx, activity in enumerate(activities):
                    # Заполнение списка активностей во втором столбце
                    sheet.cell(row=l_idx + 2, column=2).value = await activity.name

                    # Заполнение ячеек пересечения активности и учителя количеством часов
                    for idx, teacher in enumerate(teachers):
                        hours = await self._teacher_activity_link.get_hours_for_activity_and_teacher(activity, teacher)
                        if hours:
                            sheet.cell(row=l_idx + 2, column=idx + 3).value = hours

        # Сохранение файла
        workbook.save(file_name)


if __name__ == '__main__':
    import asyncio

    from links.teacher_activity_link import TeacherActivityLink, PGTeacherActivityLink
    from database import get_pool

    import bot

    async def main():
        generator = ReportGenerator(
            teacher_tg_link=TeacherTelegramLink(bot=bot.bot), teacher_activity_link=PGTeacherActivityLink(await get_pool())
        )
        cf = await bot.get_course_factory()
        tf = await bot.get_teacher_factory()
        await generator.generate_report(
            courses=[await cf.load(1), await cf.load(16), await cf.load(17), await cf.load(18)],
            teachers=[await tf.load(131898478)],
            file_name='report.xlsx'
        )

    asyncio.run(main())
