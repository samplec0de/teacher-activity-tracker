import random
import string
from abc import abstractmethod, ABC
from typing import Optional

from course.course import Course
from teacher.teacher import Teacher


class CourseJoinCode(ABC):
    """Код, который может использовать Teacher для подключения к курсу"""
    def __init__(self, code: Optional[str] = None):
        self._code = code or self._generate_str()

    @property
    def code(self) -> str:
        """Значение кода, ввод которого позволит подключиться к курсу"""
        return self._code

    @property
    @abstractmethod
    async def comment(self) -> str:
        """Комментарий, оставленный к коду при создании"""
        pass

    @property
    async def comment_quoted(self) -> str:
        """Комментарий, оставленный к коду при создании. В кавычках"""
        comment = await self.comment
        if comment is None:
            return None
        return f'"{comment}"'

    @property
    async def is_issued(self) -> bool:
        """True, если код уже был создан"""
        return await self.course is not None

    @property
    @abstractmethod
    async def course(self) -> Optional[Course]:
        """Курс, к которому можно присоединиться по данному коду"""
        pass

    @abstractmethod
    async def activate(self, teacher: Teacher) -> Course:
        """Активирует код, подключая преподавателя к курсу"""
        pass

    @property
    @abstractmethod
    async def activated_by(self) -> Optional[Teacher]:
        """Учитель, который активировал код. Может быть None, если код не активирован."""
        pass

    async def issue(self, course: Course, comment: Optional[str] = None) -> None:
        """Создает новый код для подключения к курсу"""
        pass

    @staticmethod
    def _generate_str(length: int = 12) -> str:
        """Генерирует случайную строку с будущим кодом активации"""
        all_chars = string.ascii_letters + string.digits
        code = ''.join(random.choices(all_chars, k=length))
        return code

    async def delete(self) -> None:
        """Удаляет код"""
        pass
