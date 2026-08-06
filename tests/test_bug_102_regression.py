from threading import Barrier, Thread

from shopflow.inventory import InventoryLedger


def test_bug_102_concurrent_reservations_reject_one_order():
    barrier = Barrier(2)
    ledger = InventoryLedger({"sku-1": 1}, before_reservation_write=barrier.wait)
    errors: list[Exception] = []

    def reserve(order_id: str) -> None:
        try:
            ledger.reserve(order_id, "sku-1", 1)
        except Exception as exc:
            errors.append(exc)

    threads = [Thread(target=reserve, args=(f"order-{index}",)) for index in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert ledger.available("sku-1") == 0
    assert len(errors) == 1
