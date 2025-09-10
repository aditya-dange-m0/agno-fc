from pydantic import BaseSettings, Field
from typing import List, Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    MONGO_URI: str = Field(..., env="MONGO_URI")
    DATABASE_NAME: str = Field("plm_dev", env="DATABASE_NAME")
    JWT_SECRET_KEY: str = Field(..., env="JWT_SECRET_KEY")
    JWT_REFRESH_SECRET_KEY: str = Field(..., env="JWT_REFRESH_SECRET_KEY")
    JWT_ALGORITHM: str = Field("HS256", env="JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(15, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(30, env="REFRESH_TOKEN_EXPIRE_DAYS")
    BCRYPT_ROUNDS: int = Field(12, env="BCRYPT_ROUNDS")
    REDIS_URL: Optional[str] = Field(None, env="REDIS_URL")
    S3_ENDPOINT: Optional[str] = Field(None, env="S3_ENDPOINT")
    S3_BUCKET: Optional[str] = Field(None, env="S3_BUCKET")
    PORT: int = Field(8000, env="PORT")
    CORS_ORIGINS: Optional[List[str]] = None

    class Config:
        case_sensitive = True

settings = Settings()