from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from services.api.main import app
from services.api.database import Base, get_db, get_redis

from sqlalchemy.pool import StaticPool

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


def override_get_redis():
    class MockRedis:
        def get(self, key):
            return None

        def set(self, key, val, ex=None):
            pass

        def delete(self, key):
            pass

        def lpush(self, key, val):
            pass

        def ping(self):
            return True

    return MockRedis()


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_redis] = override_get_redis

client = TestClient(app)


def test_create_user():
    response = client.post(
        "/users/", json={"name": "Alice", "email": "alice@example.com"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["email"] == "alice@example.com"
    assert "id" in data


def test_create_product():
    response = client.post("/products/", json={"name": "Widget", "price": 19.99})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["name"] == "Widget"
    assert data["price"] == 19.99


def test_create_order():
    # User and Product might already exist from previous tests, but just in case:
    client.post("/users/", json={"name": "Bob", "email": "bob@example.com"})
    client.post("/products/", json={"name": "Gadget", "price": 29.99})

    # We just want any valid user and product
    users_resp = client.post(
        "/users/", json={"name": "Test", "email": "test@example.com"}
    )
    user_id = users_resp.json()["id"]

    prod_resp = client.post("/products/", json={"name": "TestProd", "price": 10.00})
    prod_id = prod_resp.json()["id"]

    response = client.post(
        "/orders/",
        json={"user_id": user_id, "items": [{"product_id": prod_id, "quantity": 2}]},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["total_amount"] == 20.0
