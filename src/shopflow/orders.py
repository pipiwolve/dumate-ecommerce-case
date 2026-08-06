"""Order workflow built on the inventory reservation module."""

from __future__ import annotations

from dataclasses import dataclass

from .inventory import InventoryLedger


@dataclass
class Order:
    order_id: str
    sku: str
    quantity: int
    status: str = "pending_payment"


class OrderService:
    def __init__(self, inventory: InventoryLedger) -> None:
        self.inventory = inventory
        self.orders: dict[str, Order] = {}

    def create(self, order_id: str, sku: str, quantity: int) -> Order:
        if order_id in self.orders:
            return self.orders[order_id]
        self.inventory.reserve(order_id, sku, quantity)
        order = Order(order_id=order_id, sku=sku, quantity=quantity)
        self.orders[order_id] = order
        return order

    def pay(self, order_id: str) -> Order:
        order = self._require(order_id)
        if order.status == "paid":
            return order
        self.inventory.confirm(order_id)
        order.status = "paid"
        return order

    def cancel(self, order_id: str) -> Order:
        order = self._require(order_id)
        if order.status == "cancelled":
            return order
        self.inventory.release(order_id)
        order.status = "cancelled"
        return order

    def _require(self, order_id: str) -> Order:
        try:
            return self.orders[order_id]
        except KeyError as exc:
            raise LookupError(f"order {order_id} not found") from exc

