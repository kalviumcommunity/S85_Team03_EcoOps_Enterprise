import pandas as pd

from pipeline import aggregate, clean


def test_clean_supports_repository_interaction_schema():
    raw = pd.DataFrame(
        {
            "user_id": ["u1", None, "u2", "u3"],
            "price": [10, 20, -5, "invalid"],
            "category": ["A", "B", "A", "C"],
        }
    )

    cleaned = clean(raw)

    assert len(cleaned) == 1
    assert cleaned.loc[0, "customer_id"] == "u1"
    assert cleaned.loc[0, "amount"] == 10
    assert cleaned.loc[0, "segment"] == "A"
    assert cleaned.loc[0, "order_id"].startswith("generated_")


def test_aggregate_returns_revenue_orders_and_customers():
    cleaned = pd.DataFrame(
        {
            "customer_id": ["u1", "u1", "u2"],
            "amount": [10, 15, 20],
            "segment": ["A", "A", "B"],
            "order_id": ["o1", "o2", "o3"],
        }
    )

    aggregated = aggregate(cleaned).set_index("segment")

    assert aggregated.loc["A", "revenue"] == 25
    assert aggregated.loc["A", "orders"] == 2
    assert aggregated.loc["A", "customers"] == 1
