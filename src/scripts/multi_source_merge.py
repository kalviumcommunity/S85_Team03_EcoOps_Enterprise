import pandas as pd
import json
import os

os.makedirs("output", exist_ok=True)

# Load datasets
df_customers = pd.read_csv("data/raw/customers.csv")
df_orders = pd.read_csv("data/raw/orders.csv")

print("BEFORE MERGE")
print("=" * 50)
print(f"Left table (customers): {len(df_customers)}")
print(f"Right table (orders): {len(df_orders)}")

# Task 1 - Explicit left join
df_merged = pd.merge(
    df_customers,
    df_orders,
    on="customer_id",
    how="left"
)

print("\nAFTER LEFT JOIN")
print("=" * 50)
print(f"Merged result: {len(df_merged)}")
print(
    f"Change: "
    f"{len(df_merged) - len(df_customers)}"
)

# Task 2 - Detect unmatched keys

unmatched_customers = df_customers[
    ~df_customers["customer_id"].isin(
        df_orders["customer_id"]
    )
]

unmatched_orders = df_orders[
    ~df_orders["customer_id"].isin(
        df_customers["customer_id"]
    )
]

print("\nUNMATCHED KEYS")
print("=" * 50)
print(
    f"Customers without orders: "
    f"{len(unmatched_customers)}"
)
print(
    f"Orphaned orders: "
    f"{len(unmatched_orders)}"
)

unmatched_customers.to_csv(
    "output/unmatched_customers.csv",
    index=False
)

unmatched_orders.to_csv(
    "output/unmatched_orders.csv",
    index=False
)

# Task 3 - Compare join types

inner = pd.merge(
    df_customers,
    df_orders,
    on="customer_id",
    how="inner"
)

left = pd.merge(
    df_customers,
    df_orders,
    on="customer_id",
    how="left"
)

outer = pd.merge(
    df_customers,
    df_orders,
    on="customer_id",
    how="outer"
)

print("\nJOIN TYPE COMPARISON")
print("=" * 50)
print(f"Inner: {len(inner)}")
print(f"Left: {len(left)}")
print(f"Outer: {len(outer)}")

# Task 4 - Validate duplication

print("\nMERGE VALIDATION")
print("=" * 50)

print("Merged columns:")
print(df_merged.columns.tolist())

key_counts = df_merged["customer_id"].value_counts()

print(
    f"Max orders per customer: "
    f"{key_counts.max()}"
)

# Task 5 - Join report

join_report = {
    "join_type": "left",
    "left_table": "customers",
    "right_table": "orders",
    "join_key": "customer_id",
    "left_rows": len(df_customers),
    "right_rows": len(df_orders),
    "result_rows": len(df_merged),
    "unmatched_left": len(unmatched_customers),
    "unmatched_right": len(unmatched_orders),
    "reasoning": (
        "Left join preserves all customers; "
        "unmatched customers have no orders."
    )
}

print("\nJOIN DECISION REPORT")
print("=" * 50)
print(json.dumps(join_report, indent=2))

with open(
    "output/join_validation_report.json",
    "w"
) as f:
    json.dump(
        join_report,
        f,
        indent=2
    )

# Save merged dataset
df_merged.to_csv(
    "data/processed/merged_customers_orders.csv",
    index=False
)

print("\nMerged dataset saved successfully.")