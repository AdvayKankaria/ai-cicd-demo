from fastapi import FastAPI, APIRouter
from pydantic import BaseModel

app = FastAPI(title="Search Service", version="1.0.0")
router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


@app.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(status="ok", service="search-service", version="1.0.0")


@app.get("/ready", response_model=HealthResponse)
def ready():
    return HealthResponse(status="ready", service="search-service", version="1.0.0")


app.include_router(router)
