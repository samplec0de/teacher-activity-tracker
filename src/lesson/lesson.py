import datetime
from abc import abstractmethod, ABC
from typing import Optional

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
    async def topic(self) -> Optional[str]:
        """Тема урока"""
        pass

    @topic.setter
    @abstractmethod
    async def topic(self, value: str) -> None:
        """Изменение темы урока"""
        pass

    @property
    async def topic_quoted(self) -> Optional[str]:
        """Тема в кавычках"""
        topic = await self.topic
        if topic is None:
            return None
        return f'"{topic}"'

    @property
    @abstractmethod
    async def date_from(self) -> datetime.datetime:
        """Дата начала сбора активности по уроку"""
        pass

    @date_from.setter
    @abstractmethod
    async def date_from(self, new_date) -> None:
        """Изменение даты начала сбора активности по уроку"""
        pass

    @property
    @abstractmethod
    async def date_to(self) -> datetime.datetime:
        """Дедлайн сбора активности по уроку"""
        pass

    @date_to.setter
    @abstractmethod
    async def date_to(self, new_date) -> None:
        """Изменение дедлайна сбора активности по уроку"""
        pass

    @property
    @abstractmethod
    async def activities(self) -> tuple[Activity, ...]:
        """Список активностей урока"""
        pass

    @property
    @abstractmethod
    async def course(self) -> 'Course':
        """Курс, к которому относится урок"""
        pass

