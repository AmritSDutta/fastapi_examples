from fastapi import APIRouter, Depends

from app.data.EmployeeRepository import EmployeeRepository
from app.data.CoreDB import CoreDB, get_db
from app.schema.employee import Employee
from app.service.EmployeeService import EmployeeService
import logging

logger = logging.getLogger("employee_web")

router = APIRouter(prefix="/employees", tags=["employees"])


def get_employee_service(db: CoreDB = Depends(get_db)) -> EmployeeService:
    logger.info('inside get_employee_service')
    return EmployeeService(EmployeeRepository(db))


@router.get("/{employee_id}", response_model=Employee, status_code=200)
async def root(emp_id: int, svc: EmployeeService = Depends(get_employee_service)) -> Employee:
    logger.info('inside @router.get("/{employee_id}')
    return await svc.get_employee(emp_id)
