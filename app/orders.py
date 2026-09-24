"""Order domain models and validation."""
from typing import Dict, List

from pydantic import BaseModel, validator

from app.config import get_settings


class OrderItem(BaseModel):
    sku: str
    quantity: int
    unit_price_cents: int

    @validator("sku")
    def sku_must_be_upper(cls, v: str) -> str:
        if not v or not v.isupper():
            raise ValueError("sku must be non-empty and upper-case")
        return v

    @validator("quantity")
    def quantity_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("quantity must be positive")
        return v


class Order(BaseModel):
    order_id: str
    customer_email: str
    items: List[OrderItem]

    @validator("items")
    def items_within_limit(cls, v: List[OrderItem]) -> List[OrderItem]:
        limit = get_settings().max_order_items
        if len(v) == 0:
            raise ValueError("order must contain at least one item")
        if len(v) > limit:
            raise ValueError(f"order exceeds max of {limit} items")
        return v

    def total_cents(self) -> int:
        return sum(i.quantity * i.unit_price_cents for i in self.items)

    def to_record(self) -> Dict:
        record = self.dict()
        record["total_cents"] = self.total_cents()
        return record


def parse_order(raw_json: str) -> Order:
    return Order.parse_raw(raw_json)
