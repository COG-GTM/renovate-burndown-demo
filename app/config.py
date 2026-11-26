"""Service configuration loaded from environment variables."""
import os
from typing import Dict, Tuple

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


_cache: Dict[Tuple[Tuple[str, str], ...], Settings] = {}


def _orders_env() -> Tuple[Tuple[str, str], ...]:
    prefix = Settings.__config__.env_prefix.lower()
    return tuple((k, os.environ[k]) for k in os.environ if k[: len(prefix)].lower() == prefix)


def get_settings() -> Settings:
    # Settings() re-parses the whole environment (~200 us); reuse it until an ORDERS_* variable changes.
    env = _orders_env()
    settings = _cache.get(env)
    if settings is None:
        settings = Settings()
        if _orders_env() == env:
            if len(_cache) >= 32:
                _cache.clear()
            _cache[env] = settings
    return settings.copy()
