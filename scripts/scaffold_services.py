import os

SERVICES = [
    "catalog",
    "cart",
    "checkout",
    "order",
    "pricing",
    "inventory",
    "payment",
    "fulfillment",
    "shipping",
    "notification",
    "search",
    "customer",
    "identity",
    "returns",
    "reviews",
    "recommendation",
]

BASE_DIR = "/Users/advaykankaria/Documents/ai cicd demo"
SERVICES_DIR = os.path.join(BASE_DIR, "services")
TESTS_DIR = os.path.join(BASE_DIR, "tests", "unit", "services")
DOCKER_DIR = os.path.join(BASE_DIR, "docker")

os.makedirs(TESTS_DIR, exist_ok=True)

MAIN_PY_TEMPLATE = """from fastapi import FastAPI, APIRouter
from pydantic import BaseModel

app = FastAPI(title="{Title} Service", version="1.0.0")
router = APIRouter()

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str

@app.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(status="ok", service="{name}-service", version="1.0.0")

@app.get("/ready", response_model=HealthResponse)
def ready():
    return HealthResponse(status="ready", service="{name}-service", version="1.0.0")

app.include_router(router)
"""

TEST_PY_TEMPLATE = """from fastapi.testclient import TestClient
from services.{name}.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {{"status": "ok", "service": "{name}-service", "version": "1.0.0"}}

def test_ready():
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json() == {{"status": "ready", "service": "{name}-service", "version": "1.0.0"}}
"""

DOCKERFILE_TEMPLATE = """FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY services/{name}/ /app/services/{name}/
CMD ["uvicorn", "services.{name}.main:app", "--host", "0.0.0.0", "--port", "8000"]
"""

REQUIREMENTS = "fastapi==0.104.1\nuvicorn==0.24.0\npydantic==2.5.2\n"

for name in SERVICES:
    service_dir = os.path.join(SERVICES_DIR, name)
    os.makedirs(service_dir, exist_ok=True)

    # main.py
    with open(os.path.join(service_dir, "main.py"), "w") as f:
        f.write(MAIN_PY_TEMPLATE.format(Title=name.capitalize(), name=name))

    # __init__.py
    with open(os.path.join(service_dir, "__init__.py"), "w") as f:
        f.write("")

    # test
    with open(os.path.join(TESTS_DIR, f"test_{name}.py"), "w") as f:
        f.write(TEST_PY_TEMPLATE.format(name=name))

    # dockerfile
    with open(os.path.join(DOCKER_DIR, f"{name}.Dockerfile"), "w") as f:
        f.write(DOCKERFILE_TEMPLATE.format(name=name))

print("Scaffolding complete.")
