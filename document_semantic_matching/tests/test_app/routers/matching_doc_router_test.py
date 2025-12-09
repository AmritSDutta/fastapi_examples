from unittest.mock import AsyncMock, Mock, patch
from fastapi.testclient import TestClient
from app.main import app
from app.routers.matching_doc_router import get_document_service
from app.schema.document_record import ClassificationResult, Topic
import app.routers.matching_doc_router as router_module

client = TestClient(app)


# /api/docs/search
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


# /api/docs/search
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


# /api/docs/classify
def test_classify_endpoint_success():
    # mock GenAIService instance
    mock_service = Mock()
    mock_response = ClassificationResult(
        result=[
            Topic(name="low", confidence=0.1),
            Topic(name="high", confidence=0.9),
            Topic(name="mid", confidence=0.5),
        ]
    )

    mock_service.classify = Mock(return_value=mock_response)

    # Patch the module-level service used by the router
    router_module.llm = mock_service

    resp = client.post("/api/docs/classify", json={"passage": "A short passage"})
    assert resp.status_code == 200

    data = resp.json()
    names = [t["name"] for t in data["result"]]
    confidences = [t["confidence"] for t in data["result"]]

    assert names == ["high", "mid", "low"]
    assert confidences == sorted(confidences, reverse=True)
    mock_service.classify.assert_called_once_with("A short passage")


# /api/docs/classify
def test_classify_endpoint_validates_request():
    mock_service = Mock()
    mock_service.classify = Mock(
        return_value=ClassificationResult(
            result=[Topic(name="sports", confidence=0.88)]
        )
    )
    router_module.llm = mock_service

    resp = client.post("/api/docs/classify", json={"passage": "Sports victory story"})
    assert resp.status_code == 200
    body = resp.json()
    assert "result" in body
    assert isinstance(body["result"], list)
    assert len(body["result"]) == 1
    mock_service.classify.assert_called_once_with("Sports victory story")
