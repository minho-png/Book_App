from pydantic import field_validator, AliasChoices, Field
from pydantic_settings import BaseSettings
from typing import List
import json


class Settings(BaseSettings):
    # Database
    POSTGRES_URL: str = Field(
        default="postgresql+asyncpg://bookuser:bookpass@db:5432/bookapp",
        validation_alias=AliasChoices("POSTGRES_URL", "DATABASE_URL")
    )
    DEBUG: bool = False

    @field_validator("POSTGRES_URL", mode="before")
    @classmethod
    def validate_postgres_url(cls, v: str) -> str:
        if v.startswith("postgres://"):
            v = v.replace("postgres://", "postgresql+asyncpg://", 1)
        elif v.startswith("postgresql://"):
            v = v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v

    # Google Gemini LLM
    GOOGLE_API_KEY: str = ""
    GOOGLE_MODEL_NAME: str = "gemini-2.0-flash"

    # Crawling
    CRAWL_DELAY_SECONDS: float = 2.0
    CRAWL_INTERVAL_HOURS: int = 6

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
