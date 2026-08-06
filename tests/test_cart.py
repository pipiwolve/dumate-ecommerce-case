from shopflow.cart import validate_cart
from shopflow.inventory import InventoryLedger


def test_cart_batch_validation_handles_duplicate_skus():
    ledger = InventoryLedger({"sku-phone-01": 2})
    items = [
        {"sku": "sku-phone-01", "quantity": 1},
        {"sku": "sku-phone-01", "quantity": 3},
    ]
    result = validate_cart(items, ledger)
    assert [item["available"] for item in result] == [True, False]
