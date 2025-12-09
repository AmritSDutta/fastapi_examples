from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_status_and_body():
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json() == {"health": "Server in fine health"}
