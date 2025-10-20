from app.data.CoreDB import CoreDB
import logging

logger = logging.getLogger(__name__)


class EmployeeRepository:
    def __init__(self, db: CoreDB):
        logger.info('inside def __init__(self, db: CoreDB)')
        self.db = db

    async def get_by_id(self, emp_id: int):
        rows = await self.db.fetch("SELECT * FROM employees WHERE employee_id=$1", emp_id)
        return rows[0] if rows else None
