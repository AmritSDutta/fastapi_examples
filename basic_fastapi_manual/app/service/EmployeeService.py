import logging

from app.data import EmployeeRepository
from app.schema.employee import Employee
logger = logging.getLogger("EmployeeService")


class EmployeeService:
    def __init__(self, repo: EmployeeRepository):
        logger.info('inside def __init__(self, repo: EmployeeRepository):')
        self.repo = repo

    async def get_employee(self, emp_id: int) -> Employee | None:
        r = await self.repo.get_by_id(emp_id)
        logger.info('inside get_employee')
        return Employee(**dict(r)) if r else None
