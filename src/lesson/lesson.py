import datetime
from abc import abstractmethod, ABC

from activity.activity import Activity


class Lesson(ABC):
    """Урок является частью курса, за ним закрепляются активности,
    выполнение которых можно отметить преподавателям"""
    def __init__(self, lesson_id):
        self._id = lesson_id

    @property
    def id(self) -> int:
        """Идентификатор урока"""
        return self._id

    @property
    @abstractmethod
    async def topic(self) -> str:
        """Тема урока"""
        pass

    @topic.setter
    @abstractmethod
    async def topic(self, value: str) -> None:
        """Изменение темы урока"""
        pass

    @property
    @abstractmethod
    async def date(self) -> datetime.datetime:
        """Дата урока"""
        pass

    @date.setter
    @abstractmethod
    async def date(self, new_date) -> None:
        """Изменение даты урока"""
        pass

    @property
    @abstractmethod
    async def activities(self) -> tuple[Activity, ...]:
        """Список активностей урока"""
        pass
