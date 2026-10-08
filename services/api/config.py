from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_ENV: str = "local"
    APP_VERSION: str = "1.0.0"
    DATABASE_URL: str
    REDIS_URL: str
    SIMULATE_FAILURE: bool = False
    FAILURE_SCENARIO: str = "none"

    class Config:
        env_file = ".env"


settings = Settings()
