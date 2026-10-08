from fastapi.testclient import TestClient

from services.api.main import app

client = TestClient(app)


def test_health_check(mocker):
    # Mock DB and Redis for simple unit test
    mocker.patch("services.api.routes.health.get_db")
    mocker.patch("services.api.routes.health.get_redis")
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] in ["healthy", "unhealthy"]


def test_version():
    response = client.get("/version")
    assert response.status_code == 200
    assert "version" in response.json()
