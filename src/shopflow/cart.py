"""Shopping-cart validation path used by PERF-104."""

from .catalog import get_product
from .inventory import InventoryLedger


def validate_cart(items: list[dict[str, object]], inventory: InventoryLedger) -> list[dict[str, object]]:
    """Validate items one by one.

    The production adapter performs one inventory call per item. PERF-104
    proposes a batch query; this baseline behavior is kept for a real PR diff.
    """

    availability = inventory.available_many([str(item["sku"]) for item in items])
    result = []
    for item in items:
        sku = str(item["sku"])
        quantity = int(item["quantity"])
        product = get_product(sku)
        result.append(
            {
                **product,
                "quantity": quantity,
                "available": availability[sku] >= quantity,
            }
        )
    return result
