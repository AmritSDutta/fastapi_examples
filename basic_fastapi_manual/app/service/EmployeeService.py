import logging

from app.data import EmployeeRepository
from app.schema.employee import Employee

logger = logging.getLogger(__name__)


class EmployeeService:
    def __init__(self, repo: EmployeeRepository):
        logger.info('inside def __init__(self, repo: EmployeeRepository):')
        self.repo = repo

    async def get_employee(self, employee_id: int) -> Employee | None:
        r = await self.repo.get_by_id(employee_id)
        logger.info('inside get_employee')
        return Employee(**dict(r)) if r else None
