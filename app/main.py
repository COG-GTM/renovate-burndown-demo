from fastapi import FastAPI, HTTPException

from app.config import get_settings
from app.orders import Order

app = FastAPI(title=get_settings().app_name)


@app.get("/health")
def health():
    return {"status": "ok", "env": get_settings().environment}


@app.post("/orders")
def create_order(order: Order):
    try:
        return order.to_record()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
