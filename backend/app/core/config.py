from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    secret_key: str = Field(min_length=32)
    access_token_expire_minutes: int = Field(default=60, gt=0)
    cors_origins: list[str] = ["http://localhost:5173"]
    terms_version: str = "2026-10"


@lru_cache
def get_settings() -> Settings:
    return Settings()
