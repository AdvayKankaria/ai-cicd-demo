import requests
import time

BASE_URL = "http://localhost:8001"


def test_health():
    resp = requests.get(f"{BASE_URL}/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"


def test_e2e_flow():
    import uuid

    random_email = f"e2e_{uuid.uuid4().hex[:8]}@example.com"
    # Create user
    user_resp = requests.post(
        f"{BASE_URL}/users/", json={"name": "E2E User", "email": random_email}
    )
    assert user_resp.status_code == 200
    user_id = user_resp.json()["id"]

    # Create product
    prod_resp = requests.post(
        f"{BASE_URL}/products/", json={"name": "E2E Product", "price": 49.99}
    )
    assert prod_resp.status_code == 200
    prod_id = prod_resp.json()["id"]

    # Create order
    order_resp = requests.post(
        f"{BASE_URL}/orders/",
        json={"user_id": user_id, "items": [{"product_id": prod_id, "quantity": 2}]},
    )
    assert order_resp.status_code == 200
    order_id = order_resp.json()["id"]

    # Wait for worker to process
    time.sleep(3)

    # Fetch order to verify it was COMPLETED by worker
    check_resp = requests.get(f"{BASE_URL}/orders/{order_id}")
    assert check_resp.status_code == 200
    assert check_resp.json()["status"] == "COMPLETED"


if __name__ == "__main__":
    print("Running E2E tests against running Docker stack...")
    test_health()
    test_e2e_flow()
    print("E2E tests passed successfully!")
