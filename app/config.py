"""Service configuration loaded from environment variables."""
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "orders-api"
    environment: str = "dev"
    database_url: str = "postgresql://localhost:5432/orders"
    aws_region: str = "us-east-1"
    max_order_items: int = Field(default=50, ge=1)
    debug: bool = False

    model_config = SettingsConfigDict(env_prefix="ORDERS_", case_sensitive=False)


def get_settings() -> Settings:
    return Settings()
