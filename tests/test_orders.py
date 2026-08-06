from shopflow.inventory import InventoryLedger
from shopflow.orders import OrderService


def test_paid_order_consumes_physical_stock():
    ledger = InventoryLedger({"sku-1": 2})
    service = OrderService(ledger)
    service.create("order-1", "sku-1", 1)
    service.pay("order-1")
    assert ledger.snapshot()["stock"]["sku-1"] == 1


def test_cancelled_order_releases_reservation():
    ledger = InventoryLedger({"sku-1": 2})
    service = OrderService(ledger)
    service.create("order-1", "sku-1", 2)
    service.cancel("order-1")
    assert ledger.available("sku-1") == 2

