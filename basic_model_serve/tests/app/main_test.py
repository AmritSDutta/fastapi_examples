from unittest.mock import patch, AsyncMock, Mock

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


@patch("app.main.predict_async", new_callable=AsyncMock)
def test_predict_endpoint_mocked(mock_predict):
    # Arrange: mock async function to return 0
    mock_predict.return_value = 0
    app.state.model = Mock()

    payload = {"features": [5.1, 3.5, 1.4, 0.2]}
    response = client.post("/predict", json=payload)

    # Assert
    assert response.status_code == 200
    assert response.json() == {"prediction": 0}

    # Verify it was called with expected args
    mock_predict.assert_awaited_once_with(app.state.model, [5.1, 3.5, 1.4, 0.2])
