"""Inventory reservation domain used by the delivery-risk demo."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from threading import RLock
from typing import Callable


class InsufficientStock(ValueError):
    """Raised when an order cannot reserve the requested quantity."""


@dataclass
class Reservation:
    order_id: str
    sku: str
    quantity: int
    expires_at: datetime
    status: str = "active"


class InventoryLedger:
    """In-memory stock ledger.

    The initial availability check and reservation write are intentionally not
    atomic. BUG-102 tracks this known race and the demo PR contains a failed
    first remediation attempt.
    """

    def __init__(
        self,
        stock: dict[str, int],
        before_reservation_write: Callable[[], None] | None = None,
    ) -> None:
        self._stock = dict(stock)
        self._reservations: dict[str, Reservation] = {}
        self._lock = RLock()
        self._before_reservation_write = before_reservation_write

    def available(self, sku: str) -> int:
        reserved = sum(
            item.quantity
            for item in self._reservations.values()
            if item.sku == sku and item.status == "active"
        )
        return self._stock.get(sku, 0) - reserved

    def reserve(
        self,
        order_id: str,
        sku: str,
        quantity: int,
        ttl: timedelta = timedelta(minutes=15),
    ) -> Reservation:
        if quantity <= 0:
            raise ValueError("quantity must be positive")
        if order_id in self._reservations:
            return self._reservations[order_id]

        # BUG-102: another request can reserve the same stock after this read.
        remaining = self.available(sku)
        if remaining < quantity:
            raise InsufficientStock(f"{sku} has {remaining}, requested {quantity}")
        if self._before_reservation_write:
            self._before_reservation_write()

        reservation = Reservation(
            order_id=order_id,
            sku=sku,
            quantity=quantity,
            expires_at=datetime.now(UTC) + ttl,
        )
        self._reservations[order_id] = reservation
        return reservation

    def confirm(self, order_id: str) -> Reservation:
        with self._lock:
            reservation = self._require(order_id)
            if reservation.status == "confirmed":
                return reservation
            if reservation.status != "active":
                raise ValueError(f"cannot confirm {reservation.status} reservation")
            self._stock[reservation.sku] -= reservation.quantity
            reservation.status = "confirmed"
            return reservation

    def release(self, order_id: str) -> Reservation:
        """Release an active reservation without changing physical stock.

        BUG-103 was caused by subtracting stock during release. This idempotent
        implementation is the merged fix represented in the scenario.
        """

        with self._lock:
            reservation = self._require(order_id)
            if reservation.status == "released":
                return reservation
            if reservation.status != "active":
                raise ValueError(f"cannot release {reservation.status} reservation")
            reservation.status = "released"
            return reservation

    def expire(self, now: datetime | None = None) -> list[str]:
        current = now or datetime.now(UTC)
        expired: list[str] = []
        for reservation in self._reservations.values():
            if reservation.status == "active" and reservation.expires_at <= current:
                reservation.status = "released"
                expired.append(reservation.order_id)
        return expired

    def snapshot(self) -> dict[str, object]:
        return {
            "stock": dict(self._stock),
            "available": {sku: self.available(sku) for sku in self._stock},
            "reservations": [vars(item).copy() for item in self._reservations.values()],
        }

    def _require(self, order_id: str) -> Reservation:
        try:
            return self._reservations[order_id]
        except KeyError as exc:
            raise LookupError(f"reservation for {order_id} not found") from exc
