"""Minimal catalog read model for the demo API."""

PRODUCTS = {
    "sku-phone-01": {"name": "Nova Phone", "price_cents": 399900},
    "sku-headset-02": {"name": "Pulse Headset", "price_cents": 69900},
}


def get_product(sku: str) -> dict[str, object]:
    try:
        return {"sku": sku, **PRODUCTS[sku]}
    except KeyError as exc:
        raise LookupError(f"product {sku} not found") from exc

