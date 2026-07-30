import pandas as pd
import matplotlib.pyplot as plt

# -----------------------------
# Sample Transaction Dataset
# -----------------------------
data = {
    "customer_id": [101, 102, 101, 103, 104, 102, 101, 105],
    "transaction_date": [
        "2025-01-15 14:30:45",
        "2025-01-16 09:15:10",
        "2025-01-17 18:45:20",
        "2025-01-18 11:20:30",
        "2025-01-20 16:10:05",
        "2025-01-21 13:50:15",
        "2025-01-22 20:05:55",
        "2025-01-23 08:40:00"
    ],
    "amount": [120, 250, 180, 300, 150, 275, 220, 190]
}

df = pd.DataFrame(data)

# ------------------------------------
# Task 1 : Parse datetime
# ------------------------------------
df["transaction_date"] = pd.to_datetime(
    df["transaction_date"],
    format="%Y-%m-%d %H:%M:%S"
)

print("Datatype:")
print(df["transaction_date"].dtype)

# ------------------------------------
# Task 2 : Extract Features
# ------------------------------------
df["day_of_week"] = df["transaction_date"].dt.day_name()
df["hour"] = df["transaction_date"].dt.hour

print("\nHourly Distribution")
hourly_volume = df.groupby("hour").size()
print(hourly_volume)

plt.figure(figsize=(8,4))
plt.hist(df["hour"], bins=24)
plt.title("Transaction Hours")
plt.xlabel("Hour")
plt.ylabel("Frequency")
plt.show()

# ------------------------------------
# Task 3 : Week Number & Resampling
# ------------------------------------
df["week_num"] = df["transaction_date"].dt.isocalendar().week

df_ts = df.set_index("transaction_date")

weekly_revenue = df_ts["amount"].resample("W").sum()

print("\nWeekly Revenue")
print(weekly_revenue)

# ------------------------------------
# Task 4 : Days Since Purchase
# ------------------------------------
today = pd.Timestamp.now()

customer_last_purchase = df.groupby("customer_id")["transaction_date"].transform("max")

df["days_since_last_purchase"] = (
    today - customer_last_purchase
).dt.days

print("\nRecency Statistics")
print(df["days_since_last_purchase"].describe())

# ------------------------------------
# Task 5 : Multi-level Aggregation
# ------------------------------------
hourly_daily = df.groupby(["day_of_week", "hour"]).agg({
    "amount": ["sum", "count", "mean"]
})

print("\nHourly-Day Aggregation")
print(hourly_daily)

pivot_table = pd.pivot_table(
    df,
    values="amount",
    index="hour",
    columns="day_of_week",
    aggfunc="sum"
)

print("\nPivot Table")
print(pivot_table)

# ------------------------------------
# Testing
# ------------------------------------
print("\nTesting")

print("Min Date:", df["transaction_date"].min())
print("Max Date:", df["transaction_date"].max())

print(
    "Dataset Days:",
    (df["transaction_date"].max() -
     df["transaction_date"].min()).days
)

print("Hours:", df["hour"].unique())

print("Weeks:", df["week_num"].nunique())

print("Minimum Days Since Purchase:",
      df["days_since_last_purchase"].min())

print("Maximum Days Since Purchase:",
      df["days_since_last_purchase"].max())