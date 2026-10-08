from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from services.api.config import settings
import redis

# SQLAlchemy setup
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Redis setup
def get_redis():
    return redis.from_url(settings.REDIS_URL, decode_responses=True)
