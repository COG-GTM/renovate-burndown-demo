import json

import pytest
from pydantic import ValidationError

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


def test_items_limit_checked_before_items_are_parsed(monkeypatch):
    monkeypatch.setenv("ORDERS_MAX_ORDER_ITEMS", "2")
    calls = []
    original = OrderItem.__fields__["sku"].validators[0]

    def counting(*args, **kwargs):
        calls.append(1)
        return original(*args, **kwargs)

    monkeypatch.setattr(OrderItem.__fields__["sku"], "validators", [counting])
    items = [{"sku": "WIDGET", "quantity": 1, "unit_price_cents": 1}] * 10_000
    with pytest.raises(ValidationError) as exc:
        Order(order_id="o-3", customer_email="c@example.com", items=items)
    errors = exc.value.errors()
    assert len(errors) == 1
    assert "exceeds max of 2 items" in errors[0]["msg"]
    assert calls == []


def test_items_must_be_a_list():
    with pytest.raises(ValidationError):
        Order(order_id="o-4", customer_email="d@example.com", items="WIDGET")


def _client():
    from fastapi.testclient import TestClient

    from app.main import app

    return TestClient(app)


def test_orders_rejects_oversized_item_array_with_422():
    order = dict(VALID, items=[VALID["items"][0]] * 51)
    r = _client().post("/orders", json=order)
    assert r.status_code == 422
    assert "exceeds max of 50 items" in r.text


def test_orders_rejects_body_over_size_limit():
    order = dict(VALID, items=[VALID["items"][0]] * 5_000)
    r = _client().post("/orders", json=order)
    assert r.status_code == 413
    assert r.json() == {"detail": "request body too large"}


def test_orders_rejects_streamed_body_over_size_limit():
    payload = json.dumps(dict(VALID, items=[VALID["items"][0]] * 5_000)).encode()

    def chunks():
        for i in range(0, len(payload), 4096):
            yield payload[i : i + 4096]

    r = _client().post(
        "/orders", content=chunks(), headers={"content-type": "application/json"}
    )
    assert r.status_code == 413
