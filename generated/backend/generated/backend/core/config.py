from pydantic import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    MONGO_URI: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "plm"
    REDIS_URL: str = "redis://localhost:6379/0"
    JWT_SECRET: str = "CHANGE_ME"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_SECONDS: int = 60 * 60 * 24 * 30
    AWS_S3_BUCKET: str = "plm-bucket"
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: str = "minioadmin"
    AWS_SECRET_ACCESS_KEY: str = "minioadmin"
    AWS_ENDPOINT_URL: Optional[str] = None
    OPENSEARCH_URL: Optional[str] = None
    PORT: int = 8000
    CORS_ORIGINS: List[str] = []

    # Auth hardening
    AUTH_MAX_FAILED_ATTEMPTS: int = 5
    AUTH_LOCKOUT_MINUTES: int = 15

    class Config:
        env_file = ".env"

settings = Settings()