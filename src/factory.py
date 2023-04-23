from activity.activity_factory import ActivityFactory
from activity.record.pg_activity_record_factory import ActivityRecordFactory
from course.course_factory import CourseFactory
from course.join_code.join_code_factory import CourseJoinCodeFactory
from database import get_pool
from lesson.lesson_factory import LessonFactory
from links.course_teacher_link import CourseTeacherLinkFactory
from links.teacher_activity_link import PGTeacherActivityLink, TeacherActivityLink, TeacherActivityLinkFactory
from report.excel.excel_report_persistence_factory import ExcelReportPersistenceFactory
from teacher.teacher_factory import TeacherFactory

join_code_factory = None
teacher_factory = None
course_factory = None
lesson_factory = None
activity_factory = None
activity_record_factory = None
teacher_activity_link_factory = None
course_teacher_link_factory = None
excel_report_persistence_factory = None


async def get_join_code_factory() -> CourseJoinCodeFactory:
    """Фабрика одноразовых кодов подключения к курсу"""
    global join_code_factory
    if join_code_factory is None:
        join_code_factory = CourseJoinCodeFactory(pool=await get_pool())
    return join_code_factory


async def get_teacher_factory() -> TeacherFactory:
    """Фабрика учителей"""
    global teacher_factory
    if teacher_factory is None:
        teacher_factory = TeacherFactory(pool=await get_pool())
    return teacher_factory


async def get_course_factory() -> CourseFactory:
    """Фабрика курсов"""
    global course_factory
    if course_factory is None:
        course_factory = CourseFactory(pool=await get_pool())
    return course_factory


async def get_lesson_factory() -> LessonFactory:
    """Фабрика уроков"""
    global lesson_factory
    if lesson_factory is None:
        lesson_factory = LessonFactory(pool=await get_pool())
    return lesson_factory


async def get_activity_factory() -> ActivityFactory:
    """Фабрика активностей"""
    global activity_factory
    if activity_factory is None:
        activity_factory = ActivityFactory(pool=await get_pool())
    return activity_factory


async def get_activity_record_factory() -> ActivityRecordFactory:
    """Фабрика записей активности"""
    global activity_record_factory
    if activity_record_factory is None:
        activity_record_factory = ActivityRecordFactory(pool=await get_pool())
    return activity_record_factory


async def get_teacher_activity_link_factory() -> TeacherActivityLinkFactory:
    """Связь между учителями и активностями"""
    global teacher_activity_link_factory
    if teacher_activity_link_factory is None:
        teacher_activity_link_factory = TeacherActivityLinkFactory(pool=await get_pool())
    return teacher_activity_link_factory


async def get_course_teacher_link_factory() -> CourseTeacherLinkFactory:
    """Связь между курсами и учителями"""
    global course_teacher_link_factory
    if course_teacher_link_factory is None:
        course_teacher_link_factory = CourseTeacherLinkFactory(pool=await get_pool())
    return course_teacher_link_factory


async def get_excel_report_persistence_factory() -> ExcelReportPersistenceFactory:
    """Фабрика отчетов Excel"""
    global excel_report_persistence_factory
    if excel_report_persistence_factory is None:
        excel_report_persistence_factory = ExcelReportPersistenceFactory(pool=await get_pool())
    return excel_report_persistence_factory
