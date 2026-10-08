import os
import sys
import time

import httpx

API_URL = os.getenv("API_URL", "http://localhost:8001")
MAX_ATTEMPTS = 12
ATTEMPT_DELAY = 5


def check_health():
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            r = httpx.get(f"{API_URL}/health")
            if r.status_code == 200 and r.json().get("status") == "healthy":
                print("Health check passed.")
                return 0
        except Exception:  # noqa: BLE001
            pass
        print(f"Attempt {attempt} failed. Retrying in {ATTEMPT_DELAY}s...")
        time.sleep(ATTEMPT_DELAY)
    print("Health check failed.")
    return 1


if __name__ == "__main__":
    sys.exit(check_health())
