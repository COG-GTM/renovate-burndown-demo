from fastapi import FastAPI, HTTPException

from app.config import get_settings
from app.limits import RequestBodyLimitMiddleware
from app.orders import Order

app = FastAPI(title=get_settings().app_name)
app.add_middleware(
    RequestBodyLimitMiddleware, max_body_bytes=get_settings().max_request_body_bytes
)


@app.get("/health")
def health():
    return {"status": "ok", "env": get_settings().environment}


@app.post("/orders")
def create_order(order: Order):
    try:
        return order.to_record()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
