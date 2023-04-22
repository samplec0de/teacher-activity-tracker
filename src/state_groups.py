from aiogram.dispatcher.filters.state import StatesGroup, State


class MarkActivitySG(StatesGroup):
    """Группа состояний aiogram процесса отметки активности"""
    choose_course = State()
    choose_lesson = State()
    choose_activity = State()
    choose_comment = State()
    choose_hours = State()


class AddCourseSG(StatesGroup):
    """Группа состояний aiogram процесса добавления курса"""
    get_name = State()
    get_description = State()


class AddLessonSG(StatesGroup):
    """Группа состояний aiogram процесса добавления урока в курс"""
    choose_course = State()
    choose_topic = State()
    choose_period = State()


class AddActivitySG(StatesGroup):
    """Группа состояний aiogram процесса добавления активности в урок по курсу"""
    choose_course = State()
    choose_lesson = State()
    choose_name = State()


class AddJoinCodeSG(StatesGroup):
    """Группа состояний aiogram процесса добавления кода подключения к курсу"""
    choose_course = State()
    choose_description = State()


class RemoveCourseSG(StatesGroup):
    """Группа состояний aiogram процесса удаления курса"""
    choose_course = State()
    confirm = State()


class RemoveLessonSG(StatesGroup):
    """Группа состояний aiogram процесса удаления урока"""
    choose_course = State()
    choose_lesson = State()
    confirm = State()


class RemoveActivitySG(StatesGroup):
    """Группа состояний aiogram процесса удаления активности"""
    choose_course = State()
    choose_lesson = State()
    choose_activity = State()
    confirm = State()
