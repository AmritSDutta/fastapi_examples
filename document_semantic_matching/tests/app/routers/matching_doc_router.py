from unittest.mock import AsyncMock, Mock, patch
from fastapi.testclient import TestClient
from app.main import app  # adjust import to match your project
from app.routers.matching_doc_router import get_document_service

client = TestClient(app)


def test_search_endpoint():
    mock_svc = Mock()
    mock_response = [{"name": "lovely_wine", "description": "fruity aromatic wine"}]
    mock_svc.get_matching_docs = AsyncMock(return_value=mock_response)
    app.dependency_overrides[get_document_service] = lambda: mock_svc
    try:
        resp = client.post("/api/docs/search", json={"search_term": " test ", "limit": 3})
        assert resp.status_code == 200
        assert resp.json() == mock_response
        mock_svc.get_matching_docs.assert_awaited_once_with("test", 3)
    finally:
        app.dependency_overrides.clear()


def test_search_endpoint_failure():
    mock_svc = Mock()
    mock_response = [{"name": "lovely_wine", "description": "fruity aromatic wine"}]
    mock_svc.get_matching_docs = AsyncMock(return_value=mock_response)
    app.dependency_overrides[get_document_service] = lambda: mock_svc
    try:
        resp = client.post("/api/docs/search", json={"search_term": " test ", "limit": 10})
        assert resp.status_code == 422

    finally:
        app.dependency_overrides.clear()
