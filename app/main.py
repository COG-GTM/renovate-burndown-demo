from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from app.config import get_settings
from app.orders import Order

app = FastAPI(title=get_settings().app_name)

CONSOLE_HTML = Path(__file__).parent / "static" / "index.html"


@app.get("/", response_class=HTMLResponse)
def console():
    return CONSOLE_HTML.read_text()


@app.get("/health")
def health():
    return {"status": "ok", "env": get_settings().environment}


@app.post("/orders")
def create_order(order: Order):
    try:
        return order.to_record()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
