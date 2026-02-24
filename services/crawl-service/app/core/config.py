from pydantic_settings import BaseSettings
from typing import List
import json


class Settings(BaseSettings):
    # Database
    POSTGRES_URL: str = "postgresql+asyncpg://bookuser:bookpass@localhost:5432/bookapp"
    DEBUG: bool = False

    # Google Gemini LLM
    GOOGLE_API_KEY: str = ""
    GOOGLE_MODEL_NAME: str = "gemini-2.0-flash"

    # Crawling
    CRAWL_DELAY_SECONDS: float = 2.0

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
