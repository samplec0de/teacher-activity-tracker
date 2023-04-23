from asyncpg import Pool
from openpyxl.workbook import Workbook

from report.excel.excel_report_persistence import ExcelReportPersistence
from report.excel.pg_excel_report_persistence import PGExcelReportPersistence


class ExcelReportPersistenceFactory:
    """Фабрика отчетов Excel"""

    def __init__(self, pool: Pool):
        self._pool = pool

    async def create(self, workbook: Workbook) -> ExcelReportPersistence:
        persist_report = PGExcelReportPersistence(workbook=workbook, pool=self._pool)
        await persist_report.save_report()
        return persist_report

    async def load(self, report_id: int) -> ExcelReportPersistence:
        return PGExcelReportPersistence(report_id=report_id, pool=self._pool)
