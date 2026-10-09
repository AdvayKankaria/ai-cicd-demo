from fastapi.testclient import TestClient
from services.shipping.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "shipping-service",
        "version": "1.0.0",
    }


def test_ready():
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "service": "shipping-service",
        "version": "1.0.0",
    }
