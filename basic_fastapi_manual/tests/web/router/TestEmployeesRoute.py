import unittest
from unittest.mock import AsyncMock, Mock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.schema.employee import Employee
from app.web.router.employee_web import router


class TestEmployeesRoute(unittest.TestCase):
    def setUp(self):
        self.app = FastAPI()
        self.app.include_router(router)

        # Mock service with async get_employee
        self.mock_svc = Mock(spec=["get_employee"])
        self.mock_svc.get_employee = AsyncMock()

        async def override_get_employee_service():
            return self.mock_svc

        # ✅ Correct override
        # self.app.dependency_overrides[get_employee_service] = override_get_employee_service
        self.client = TestClient(self.app)

    def tearDown(self):
        pass

    def test_200(self):
        self.mock_svc.get_employee.return_value = Employee(employee_id=1, first_name="Alice", salary=10.0)
        res = self.client.get("/employees/1")
        self.mock_svc.get_employee.assert_awaited_once_with(1)
        assert res.status_code == 200 and res.json()["name"] == "Alice"

    def test_404(self):
        self.mock_svc.get_employee.return_value = None
        res = self.client.get("/employees/999")
        self.mock_svc.get_employee.assert_awaited_once_with(999)
        assert res.status_code == 404


if __name__ == "__main__":
    unittest.main()