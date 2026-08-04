import pandas as pd
import numpy as np

# ============================================
# Feature Engineering & Derived Business Columns
# ============================================

# Sample transaction/customer data
data = {
    "customer_id": range(1, 21),

    "total_transactions": [
        5, 12, 25, 3, 18,
        40, 8, 15, 30, 2,
        22, 10, 35, 6, 14,
        28, 4, 20, 45, 9
    ],

    "days_as_customer": [
        150, 240, 365, 90, 300,
        600, 180, 270, 450, 60,
        330, 210, 500, 120, 250,
        400, 100, 320, 550, 200
    ],

    "total_spent": [
        500, 1500, 3500, 250, 2200,
        6000, 800, 1800, 4500, 150,
        3000, 1200, 5500, 600, 2000,
        4000, 300, 2700, 7000, 1000
    ],

    "days_since_last_purchase": [
        10, 20, 5, 90, 15,
        3, 45, 12, 7, 120,
        25, 30, 8, 60, 18,
        4, 100, 14, 2, 35
    ],

    "purchase_count": [
        5, 12, 25, 3, 18,
        40, 8, 15, 30, 2,
        22, 10, 35, 6, 14,
        28, 4, 20, 45, 9
    ]
}

df = pd.DataFrame(data)

print("Original Data")
print(df.head())

# ============================================
# TASK 1: Compute Ratio Features
# ============================================

# Transactions per month
df["transactions_per_month"] = (
    df["total_transactions"] /
    (df["days_as_customer"] / 30)
)

# Average spend per transaction
df["avg_spend_per_transaction"] = (
    df["total_spent"] /
    df["total_transactions"]
)

# Lifetime value per month
df["lifetime_value_per_month"] = (
    df["total_spent"] /
    (df["days_as_customer"] / 30)
)

print("\n================================")
print("TASK 1: Ratio Features")
print("================================")

print(
    df[
        [
            "transactions_per_month",
            "avg_spend_per_transaction",
            "lifetime_value_per_month"
        ]
    ].describe()
)

# ============================================
# TASK 2: Equal-Width Binning
# ============================================

df["engagement_tier"] = pd.cut(
    df["transactions_per_month"],
    bins=[0, 2, 10, float("inf")],
    labels=["low", "medium", "high"]
)

print("\n================================")
print("TASK 2: Engagement Tier")
print("================================")

print(df["engagement_tier"].value_counts())

# ============================================
# TASK 3: Quantile Binning
# ============================================

df["spend_quartile"] = pd.qcut(
    df["total_spent"],
    q=4,
    labels=["Q1", "Q2", "Q3", "Q4"]
)

print("\n================================")
print("TASK 3: Spend Quartile")
print("================================")

print(df["spend_quartile"].value_counts())

# ============================================
# TASK 4: Composite RFM Score
# ============================================

# Recency:
# Lower days since purchase = better.
df["recency_score"] = pd.qcut(
    df["days_since_last_purchase"],
    q=5,
    labels=[5, 4, 3, 2, 1]
)

# Frequency:
# Higher purchase count = better.
df["frequency_score"] = pd.qcut(
    df["purchase_count"],
    q=5,
    labels=[1, 2, 3, 4, 5]
)

# Monetary:
# Higher spending = better.
df["monetary_score"] = pd.qcut(
    df["total_spent"],
    q=5,
    labels=[1, 2, 3, 4, 5]
)

# Convert scores to integers and combine
df["rfm_score"] = (
    df["recency_score"].astype(int)
    + df["frequency_score"].astype(int)
    + df["monetary_score"].astype(int)
)

print("\n================================")
print("TASK 4: RFM Score")
print("================================")

print(
    df[
        [
            "customer_id",
            "recency_score",
            "frequency_score",
            "monetary_score",
            "rfm_score"
        ]
    ]
)

# ============================================
# TASK 5: Feature Validation
# ============================================

print("\n================================")
print("TASK 5: Feature Validation")
print("================================")

print(
    "Engagement tier distribution:"
)
print(df["engagement_tier"].value_counts())

print(
    f"\nRFM score range: "
    f"{df['rfm_score'].min()}-"
    f"{df['rfm_score'].max()}"
)

print("\nMissing values:")

print(
    df[
        [
            "engagement_tier",
            "spend_quartile",
            "rfm_score"
        ]
    ].isna().sum()
)

# ============================================
# Final Feature Summary
# ============================================

print("\n================================")
print("FINAL DATASET")
print("================================")

print(df.head(10))

# Save final engineered dataset
df.to_csv(
    "feature_engineered_customers.csv",
    index=False
)

print(
    "\nFeature engineered dataset saved as "
    "feature_engineered_customers.csv"
)