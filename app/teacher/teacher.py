from abc import ABC, abstractmethod
from typing import Tuple

from course.course import Course


class Teacher(ABC):
    """Учитель, преподаватель. Выставляет себе часы по активностям для оплаты"""

    def __init__(self, teacher_id: int):
        self._id = teacher_id

    @property
    def id(self) -> int:
        """Идентификатор учителя"""
        return self._id

    @property
    @abstractmethod
    async def registered(self) -> bool:
        """Проверяет зарегистрирован ли преподаватель"""
        pass

    @abstractmethod
    async def register(self) -> None:
        """Регистрирует аккаунт"""
        pass

    @property
    @abstractmethod
    async def courses(self) -> Tuple[Course]:
        """Кортеж курсов, которые ведет преподаватель"""
        pass

    @property
    @abstractmethod
    async def comment(self) -> str:
        """Заметка, комментарий, которую оставили про учителя"""
        pass

    @comment.setter
    @abstractmethod
    async def comment(self, value: str) -> None:
        """Заметка, комментарий, которую оставили про учителя"""
        pass

    @property
    @abstractmethod
    async def is_manager(self) -> bool:
        """Является ли учитель менеджером"""
        pass

    @abstractmethod
    async def make_manager(self) -> None:
        """Делает учителя менеджером"""
        pass
