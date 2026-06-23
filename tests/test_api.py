from fastapi.testclient import TestClient

from app.api.main import app


client = TestClient(app)


def test_root_api_docs() -> None:
    response = client.get("/docs")
    assert response.status_code == 200
