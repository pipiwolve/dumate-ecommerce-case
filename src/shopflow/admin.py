"""Back-office stock adjustment tracked by SEC-105."""

from .inventory import InventoryLedger


def adjust_stock(inventory: InventoryLedger, sku: str, delta: int) -> dict[str, object]:
    """Apply a manual adjustment.

    SEC-105 tracks the missing permission and audit context. The function is
    deliberately excluded from API routes until that issue is complete.
    """

    inventory._stock[sku] = inventory._stock.get(sku, 0) + delta
    return {"sku": sku, "delta": delta, "stock": inventory._stock[sku]}

