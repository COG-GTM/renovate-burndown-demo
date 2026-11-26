from app import config
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


def test_get_settings_reused_until_env_changes(monkeypatch):
    built = []

    class CountingSettings(Settings):
        def __init__(self, **kw):
            built.append(1)
            super().__init__(**kw)

    monkeypatch.setattr(config, "Settings", CountingSettings)
    monkeypatch.setattr(config, "_cache", {})
    first = get_settings()
    again = get_settings()
    assert again == first and again is not first
    again.max_order_items = 99
    assert get_settings().max_order_items == first.max_order_items
    assert len(built) == 1
    monkeypatch.setenv("ORDERS_MAX_ORDER_ITEMS", "7")
    changed = get_settings()
    assert changed != first
    assert changed.max_order_items == 7
    assert len(built) == 2
