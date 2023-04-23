import datetime
from abc import abstractmethod

from openpyxl.workbook import Workbook


class ExcelReportPersistence:
    """Абстрактный класс для работы с отчетами в Excel"""
    def __init__(self, report_id: int):
        self._id = report_id

    @property
    def id(self) -> int:
        return self._id

    @property
    @abstractmethod
    async def created_at(self) -> datetime.datetime:
        """Дата создания отчета"""
        pass

    @abstractmethod
    async def get_workbook(self) -> Workbook:
        """Получить отчет"""
        pass

    @abstractmethod
    async def save_report(self) -> None:
        """Сохранить отчет"""
        pass
