import unittest
from unittest.mock import create_autospec, AsyncMock

from app.schema.employee import Employee
from app.service.EmployeeService import EmployeeService


class TestEmployeeService(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.repo = create_autospec(spec=["get_by_id"])
        self.repo.get_by_id = AsyncMock()
        self.svc = EmployeeService(self.repo)

    async def test_get_employee_found(self):
        self.repo.get_by_id.return_value = {"employee_id": 1, "first_name": "Alice", "salary": 50000.0}
        emp = await self.svc.get_employee(1)
        self.repo.get_by_id.assert_awaited_once_with(1)
        self.assertIsInstance(emp, Employee)
        self.assertEqual(emp.first_name, "Alice")
