"""
Dataset schema definitions.

Defines the expected columns for each raw dataset.
"""

EXPECTED_SCHEMAS = {
    "interactions": [
        "user_id",
        "product_id",
        "seller_id",
        "category",
        "price",
        "action",
        "rating",
        "timestamp",
    ],
    "products": [
        "product_id",
        "seller",
        "category",
        "price",
        "final_quality",
        "rating_count",
    ],
    "sellers": [
        "seller_id",
        "quality",
    ],
    "users": [
        "user_id",
        "loyalty",
        "price_sensitivity",
    ],
}