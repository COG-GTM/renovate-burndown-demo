"""Service configuration loaded from environment variables."""
import os
from functools import lru_cache
from typing import Tuple

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    app_name: str = "orders-api"
    environment: str = "dev"
    database_url: str = "postgresql://localhost:5432/orders"
    aws_region: str = "us-east-1"
    max_order_items: int = Field(default=50, ge=1)
    debug: bool = False

    class Config:
        env_prefix = "ORDERS_"
        case_sensitive = False


@lru_cache(maxsize=32)
def _settings_for(env: Tuple[Tuple[str, str], ...]) -> Settings:
    return Settings()


def get_settings() -> Settings:
    # Settings() re-parses the whole environment (~200 us); reuse it until an ORDERS_* variable changes.
    prefix = Settings.__config__.env_prefix.lower()
    env = tuple((k, os.environ[k]) for k in os.environ if k[: len(prefix)].lower() == prefix)
    return _settings_for(env)
