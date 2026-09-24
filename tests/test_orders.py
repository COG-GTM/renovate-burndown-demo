import json

import pytest

from app.orders import Order, OrderItem, parse_order

VALID = {
    "order_id": "o-1",
    "customer_email": "a@example.com",
    "items": [
        {"sku": "WIDGET", "quantity": 2, "unit_price_cents": 500},
        {"sku": "GADGET", "quantity": 1, "unit_price_cents": 1250},
    ],
}


def test_total_and_record():
    order = Order(**VALID)
    assert order.total_cents() == 2250
    record = order.to_record()
    assert record["total_cents"] == 2250
    assert record["items"][0]["sku"] == "WIDGET"
    assert isinstance(record["items"][0], dict)


def test_parse_raw_json():
    order = parse_order(json.dumps(VALID))
    assert order.order_id == "o-1"
    assert len(order.items) == 2


def test_sku_validator():
    with pytest.raises(ValueError):
        OrderItem(sku="widget", quantity=1, unit_price_cents=1)


def test_quantity_validator():
    with pytest.raises(ValueError):
        OrderItem(sku="WIDGET", quantity=0, unit_price_cents=1)


def test_empty_items_rejected():
    with pytest.raises(ValueError):
        Order(order_id="o-2", customer_email="b@example.com", items=[])


def test_items_limit_from_settings(monkeypatch):
    monkeypatch.setenv("ORDERS_MAX_ORDER_ITEMS", "1")
    with pytest.raises(ValueError):
        Order(**VALID)


def test_fastapi_health():
    from fastapi.testclient import TestClient

    from app.main import app

    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
    r = client.post("/orders", json=VALID)
    assert r.status_code == 200
    assert r.json()["total_cents"] == 2250
