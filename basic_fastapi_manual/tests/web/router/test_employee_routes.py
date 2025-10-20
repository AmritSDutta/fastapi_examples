import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.schema.employee import Employee
from app.web.router.employee_web import get_employee_service, router


class FakeEmployeeService:
    async def get_employee(self, employee_id: int):
        return Employee(employee_id=employee_id, first_name="Alice", salary=10.0)


@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_employee_service] = lambda: FakeEmployeeService()
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def test_get_employee_ok(client):
    r = client.get("/employees/123")
    print(r.json())
    assert r.status_code == 200
    assert r.json()["employee_id"] == 123


def test_get_employee_404(client, monkeypatch):
    class EmptyService:
        async def get_employee(self, emp_id: int): return None

    client.app.dependency_overrides[get_employee_service] = lambda: EmptyService()
    r = client.get("/employees/999")
    print(r.json())
    assert r.status_code == 404
