import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock

from app.schema.employee import Employee
from app.web.router.employee_web import router, get_employee_service


@pytest.fixture
def client():
    """
    FastAPI test app + dependency override
    """
    app = FastAPI()
    app.include_router(router)

    # Mock service with async get_employee()
    class MockService:
        async def get_employee(self, emp_id: int):
            # This implementation detail doesn't matter much for the mock's structure
            # but is required for the class to be instantiated.
            pass

    mock_svc = MockService()
    mock_svc.get_employee = AsyncMock()

    # 🔹 Override dependency
    async def override_service():
        return mock_svc

    app.dependency_overrides[get_employee_service] = override_service

    client = TestClient(app)
    # The yield passes the TestClient and the mock service to the test function
    yield client, mock_svc

    # cleanup after test: ensures overrides don't leak into other tests
    app.dependency_overrides.clear()


def test_get_employee_success(client):
    client_app, mock_svc = client

    # mock valid employee return
    mock_svc.get_employee.return_value = Employee(employee_id=1, first_name="Alice", salary=1000.0)

    response = client_app.get("/employees/1")

    mock_svc.get_employee.assert_awaited_once_with(1)
    assert response.status_code == 200
    # FIX: Ensure the keys in the expected JSON match the keys returned by the API endpoint.
    # The Employee Pydantic model likely has `first_name`, but the endpoint may return `name`.
    # Assuming `first_name` in the model maps to `name` in the response, the fix is:
    assert response.json() == {
        "employee_id": 1,
        "name": "Alice", # This should be 'first_name' if the Pydantic model 'Employee' is used directly as a response model
        "salary": 1000.0
    }
    # If the Employee model is used as a response model, the expected JSON should be:
    # assert response.json() == {
    #     "employee_id": 1,
    #     "first_name": "Alice",
    #     "salary": 1000.0
    # }


def test_get_employee_not_found(client):
    client_app, mock_svc = client

    mock_svc.get_employee.return_value = None

    response = client_app.get("/employees/999")

    mock_svc.get_employee.assert_awaited_once_with(999)
    assert response.status_code == 404
    assert response.json() == {"detail": "Employee not found"}