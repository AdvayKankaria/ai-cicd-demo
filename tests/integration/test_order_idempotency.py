import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from services.api.database import Base, get_db, get_redis
from services.api.main import app

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

is_duplicate_scenario = os.getenv("FAILURE_SCENARIO") == "duplicate_order_failure"
is_ai_fix_branch = os.getenv("GITHUB_HEAD_REF", "").startswith("ai-fix/")
is_ai_run = os.getenv("GITHUB_REF_NAME", "").startswith("ai-fix/")
should_run = is_duplicate_scenario or is_ai_fix_branch or is_ai_run


@pytest.mark.skipif(
    not should_run,
    reason="Only run this defect reproduction when duplicate_order_failure is selected or on ai-fix branches",
)
def test_duplicate_order_idempotency_violation():
    """
    Simulates a client sending two exact requests with the same Idempotency-Key.
    The application SHOULD return the same order.
    Currently, the application contains a bug and will create TWO separate orders.
    """
    # Ensure a valid user and product exist
    users_resp = client.post(
        "/users/", json={"name": "Alice", "email": "alice_idem@example.com"}
    )
    user_id = users_resp.json()["id"]

    prod_resp = client.post("/products/", json={"name": "TestProduct", "price": 10.00})
    prod_id = prod_resp.json()["id"]

    idempotency_key = "idem-test-12345"

    # First request
    payload = {"user_id": user_id, "items": [{"product_id": prod_id, "quantity": 1}]}

    response1 = client.post(
        "/orders/", json=payload, headers={"Idempotency-Key": idempotency_key}
    )
    assert response1.status_code == 200
    order1 = response1.json()

    # Second request (duplicate)
    response2 = client.post(
        "/orders/", json=payload, headers={"Idempotency-Key": idempotency_key}
    )
    assert response2.status_code == 200
    order2 = response2.json()

    try:
        # The expected behavior is that the same order is returned
        assert (
            order1["id"] == order2["id"]
        ), f"Expected same order ID {order1['id']} but got {order2['id']} for same Idempotency-Key"
    except AssertionError as e:
        # Emit the exact diagnostic metadata expected by the AI Engine
        print("\n::error::Idempotency violation detected: duplicate orders created.")
        print("FAILURE_STAGE=APPLICATION_TESTS")
        print("FAILURE_CLASS=APPLICATION_BUG")
        print("FAILURE_REASON=IDEMPOTENCY_VIOLATION")
        raise e
