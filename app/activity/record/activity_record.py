from abc import abstractmethod

from activity.activity import Activity
from teacher.teacher import Teacher


class ActivityRecord:
    """Запись об активности"""
    def __init__(self, activity_record_id: int):
        """Загрузка записи активности"""
        self._id = activity_record_id

    @property
    def id(self) -> int:
        """Идентификатор записи активности"""
        return self._id

    @property
    @abstractmethod
    async def hours(self) -> float:
        """Количество часов"""
        pass

    @hours.setter
    @abstractmethod
    async def hours(self, value) -> None:
        """Изменение количества часов по активности"""
        pass

    @property
    @abstractmethod
    async def activity(self) -> Activity:
        """Активность, к которой принадлежит запись"""
        pass

    @property
    @abstractmethod
    async def teacher(self) -> Teacher:
        """Учитель, который заявил активность"""
        pass
