import pytest
from pydantic import ValidationError

from app.config import Settings, get_settings


def test_defaults():
    s = Settings()
    assert s.app_name == "orders-api"
    assert s.max_order_items == 50
    assert s.debug is False


def test_env_prefix(monkeypatch):
    monkeypatch.setenv("ORDERS_ENVIRONMENT", "prod")
    monkeypatch.setenv("ORDERS_MAX_ORDER_ITEMS", "3")
    monkeypatch.setenv("orders_debug", "true")
    s = get_settings()
    assert s.environment == "prod"
    assert s.max_order_items == 3
    assert s.debug is True


def test_case_insensitive_env(monkeypatch):
    monkeypatch.setenv("orders_app_name", "lowercase-api")
    assert Settings().app_name == "lowercase-api"


def test_limits_are_bounded(monkeypatch):
    assert Settings().max_request_body_bytes == 100_000
    monkeypatch.setenv("ORDERS_MAX_ORDER_ITEMS", "100000")
    with pytest.raises(ValidationError):
        Settings()
