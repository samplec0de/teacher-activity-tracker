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
    async def name(self) -> str:
        """Название курса"""
        pass

    @name.setter
    @abstractmethod
    async def name(self, value) -> None:
        """Изменить название курса"""
        pass

    @property
    async def name_quoted(self) -> str:
        """Название курса в кавычках"""
        return f'"{await self.name}"'

    async def delete(self) -> None:
        """Удалить курс"""
        pass
