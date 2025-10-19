# tests/test_main.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_read_root_status_and_body():
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json() == {"message": "Hello FastAPI"}
