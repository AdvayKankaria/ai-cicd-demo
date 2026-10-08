from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from services.api.config import settings
from services.api.database import get_db, get_redis

router = APIRouter()


@router.get("/")
@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        from sqlalchemy import text

        db.execute(text("SELECT 1"))
        redis_client = get_redis()
        redis_client.ping()
        status = "healthy"
    except Exception:  # noqa: BLE001
        status = "unhealthy"
    return {"status": status}


@router.get("/ready")
def readiness_check(db: Session = Depends(get_db)):
    # readiness is similar to health check here
    try:
        from sqlalchemy import text

        db.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception:  # noqa: BLE001
        return {"status": "not ready"}


@router.get("/version")
def version():
    return {"version": settings.APP_VERSION, "env": settings.APP_ENV}
