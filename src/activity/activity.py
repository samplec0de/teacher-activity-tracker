from abc import abstractmethod, ABC


class Activity(ABC):
    def __init__(self, activity_id: int):
        self._id = activity_id

    def __repr__(self):
        return f'Activity(id={self.id})'

    @property
    def id(self) -> int:
        """Идентификатор активности"""
        return self._id

    @property
    @abstractmethod
    async def name(self) -> str:
        """Название активности"""
        pass

    @name.setter
    @abstractmethod
    async def name(self, value) -> None:
        """Изменение названия активности"""
        pass

    @property
    async def course(self) -> 'Course':
        """Курс активности"""
        return await (await self.lesson).course

    @property
    @abstractmethod
    async def lesson(self) -> 'Lesson':
        """Урок активности"""
        pass

    @property
    async def name_quoted(self) -> str:
        """Имя в кавычках"""
        name = await self.name
        return f'"{name}"'

    async def delete(self) -> None:
        """Удаление активности"""
        await self._delete()
        self._id = None

    @abstractmethod
    async def _delete(self) -> None:
        """Удаление активности"""
        pass
