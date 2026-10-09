import os
import pytest
from fastapi.testclient import TestClient

from services.api.main import app

client = TestClient(app)

@pytest.mark.skipif(
    os.getenv("FAILURE_SCENARIO") != "duplicate_order_failure",
    reason="Only run this defect reproduction when duplicate_order_failure is selected"
)
def test_duplicate_order_idempotency_violation():
    """
    Simulates a client sending two exact requests with the same Idempotency-Key.
    The application SHOULD return the same order.
    Currently, the application contains a bug and will create TWO separate orders.
    """
    idempotency_key = "idem-test-12345"
    
    # First request
    payload = {
        "user_id": 1,
        "items": [{"product_id": 1, "quantity": 1}]
    }
    
    response1 = client.post(
        "/orders/", 
        json=payload,
        headers={"Idempotency-Key": idempotency_key}
    )
    assert response1.status_code == 200
    order1 = response1.json()
    
    # Second request (duplicate)
    response2 = client.post(
        "/orders/", 
        json=payload,
        headers={"Idempotency-Key": idempotency_key}
    )
    assert response2.status_code == 200
    order2 = response2.json()
    
    try:
        # The expected behavior is that the same order is returned
        assert order1["id"] == order2["id"], f"Expected same order ID {order1['id']} but got {order2['id']} for same Idempotency-Key"
    except AssertionError as e:
        # Emit the exact diagnostic metadata expected by the AI Engine
        print("\n::error::Idempotency violation detected: duplicate orders created.")
        print("FAILURE_STAGE=APPLICATION_TESTS")
        print("FAILURE_CLASS=APPLICATION_BUG")
        print("FAILURE_REASON=IDEMPOTENCY_VIOLATION")
        raise e
