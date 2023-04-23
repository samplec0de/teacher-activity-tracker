import datetime
import io
from typing import Optional

from asyncpg import Pool
from openpyxl.reader.excel import load_workbook
from openpyxl.workbook import Workbook

from pg_object import PGObject
from report.excel.excel_report_persistence import ExcelReportPersistence


class PGExcelReportPersistence(ExcelReportPersistence, PGObject):
    """Класс для работы с отчетами в Excel в БД PostgreSQL"""

    def __init__(self, pool: Pool, report_id: Optional[int] = None, workbook: Optional[Workbook] = None):
        ExcelReportPersistence.__init__(self, report_id)
        PGObject.__init__(self, object_id=report_id, pool=pool, id_column_name='report_id', table='excel_reports')
        self._workbook = workbook
        if report_id is None and workbook is None:
            raise ValueError('report_id or workbook must be specified')

    @property
    async def created_at(self) -> datetime.datetime:
        """Дата создания отчета"""
        return await self._get_single_attribute('created_at')

    async def get_workbook(self) -> Workbook:
        """Получить отчет"""
        async with self._pool.acquire() as conn:
            file_data = await conn.fetchval('SELECT file_data FROM excel_reports WHERE report_id = $1', self._id)

            if not file_data:
                raise ValueError(f"Отчет с ID {self._id} не найден")

            bytes_stream = io.BytesIO(file_data)
            workbook = load_workbook(bytes_stream)

            return workbook

    async def save_report(self) -> None:
        """Сохранить отчет"""
        async with self._pool.acquire() as conn:
            bytes_stream = io.BytesIO()
            self._workbook.save(bytes_stream)
            bytes_stream.seek(0)
            file_data = bytes_stream.read()

            self._id = await conn.fetchval(
                'INSERT INTO excel_reports (file_data) VALUES ($1) RETURNING report_id', file_data
            )
