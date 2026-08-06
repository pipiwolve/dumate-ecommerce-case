from datetime import UTC, datetime, timedelta
from threading import Barrier, Thread

import pytest

from shopflow.inventory import InsufficientStock, InventoryLedger


def test_reservation_reduces_available_stock():
    ledger = InventoryLedger({"sku-1": 3})
    ledger.reserve("order-1", "sku-1", 2)
    assert ledger.available("sku-1") == 1


def test_rejects_reservation_above_available_stock():
    ledger = InventoryLedger({"sku-1": 1})
    with pytest.raises(InsufficientStock):
        ledger.reserve("order-1", "sku-1", 2)


def test_release_is_idempotent_and_restores_availability():
    ledger = InventoryLedger({"sku-1": 2})
    ledger.reserve("order-1", "sku-1", 2)
    ledger.release("order-1")
    ledger.release("order-1")
    assert ledger.available("sku-1") == 2


def test_expired_reservation_is_released():
    ledger = InventoryLedger({"sku-1": 2})
    ledger.reserve("order-1", "sku-1", 1, ttl=timedelta(seconds=1))
    expired = ledger.expire(datetime.now(UTC) + timedelta(seconds=2))
    assert expired == ["order-1"]
    assert ledger.available("sku-1") == 2


def test_concurrent_reservations_never_oversell():
    barrier = Barrier(2)
    ledger = InventoryLedger({"sku-1": 1}, before_reservation_write=barrier.wait)
    errors: list[Exception] = []

    def reserve(order_id: str) -> None:
        try:
            ledger.reserve(order_id, "sku-1", 1)
        except Exception as exc:  # pragma: no cover - expected after the fix
            errors.append(exc)

    threads = [Thread(target=reserve, args=(f"order-{index}",)) for index in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert ledger.available("sku-1") == 0
    assert len(errors) == 1
