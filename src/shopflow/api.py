"""Small FastAPI surface for the simulated ecommerce service."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .inventory import InsufficientStock, InventoryLedger
from .orders import OrderService


class CreateOrder(BaseModel):
    order_id: str = Field(min_length=3)
    sku: str = Field(min_length=3)
    quantity: int = Field(gt=0)


inventory = InventoryLedger({"sku-phone-01": 20, "sku-headset-02": 50})
orders = OrderService(inventory)
app = FastAPI(title="ShopFlow v2.6 demo")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/orders")
def create_order(payload: CreateOrder) -> dict[str, object]:
    try:
        return vars(orders.create(payload.order_id, payload.sku, payload.quantity))
    except InsufficientStock as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.post("/orders/{order_id}/pay")
def pay_order(order_id: str) -> dict[str, object]:
    try:
        return vars(orders.pay(order_id))
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/orders/{order_id}/cancel")
def cancel_order(order_id: str) -> dict[str, object]:
    try:
        return vars(orders.cancel(order_id))
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/inventory")
def inventory_snapshot() -> dict[str, object]:
    return inventory.snapshot()

