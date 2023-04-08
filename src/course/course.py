from abc import abstractmethod, ABC
from typing import Tuple

from lesson.lesson import Lesson


class Course(ABC):
    """Курс, на котором преподаватели выставляют свою активность"""
    def __init__(self, course_id: int):
        self._id = course_id

    @property
    def id(self) -> int:
        """Идентификатор курса"""
        return self._id

    @property
    @abstractmethod
    async def lessons(self) -> Tuple[Lesson, ...]:
        """Список уроков курса"""
        pass

    @property
    @abstractmethod
    async def title(self) -> str:
        """Название курса"""
        pass

    @title.setter
    @abstractmethod
    async def title(self, value) -> None:
        """Изменить название курса"""
        pass

    async def generate_join_code(self, ) -> str:
        """Возвращает одноразовый код, который может использоваться для присоединения к курсу"""
        pass
