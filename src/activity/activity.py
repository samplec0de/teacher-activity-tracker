from abc import abstractmethod, ABC


class Activity(ABC):
    def __init__(self, activity_id: int):
        self._id = activity_id

    def __repr__(self):
        return f'Activity(id={self.id})'

    @property
    def id(self):
        """Идентификатор активности"""
        return self._id

    @property
    @abstractmethod
    async def name(self):
        """Название активности"""
        pass

    @name.setter
    @abstractmethod
    async def name(self, value):
        """Изменение названия активности"""
        pass
