import pandas as pd
import numpy as np
import time

# ---------------------------------------
# Sample Dataset
# ---------------------------------------

np.random.seed(42)

df = pd.DataFrame({
    "customer_id": range(1, 100001),
    "revenue": np.random.randint(100, 10000, 100000)
})

print("Dataset Created Successfully")
print(df.head())

# =======================================
# Task 1: Min-Max Normalization
# =======================================

revenue_array = df["revenue"].values

normalized = (
    revenue_array - revenue_array.min()
) / (
    revenue_array.max() - revenue_array.min()
)

df["revenue_normalized"] = normalized

print("\nMin-Max Normalization Completed")

# =======================================
# Task 2: Z-Score Normalization
# =======================================

z_scores = (
    revenue_array - revenue_array.mean()
) / revenue_array.std()

df["revenue_zscore"] = z_scores

print("Z-Score Normalization Completed")

# =======================================
# Task 3: Loop vs Vectorization
# =======================================

start = time.time()

loop_result = []

minimum = revenue_array.min()
maximum = revenue_array.max()

for value in revenue_array:
    loop_result.append(
        (value - minimum) / (maximum - minimum)
    )

loop_time = time.time() - start

start = time.time()

vectorized_result = (
    revenue_array - minimum
) / (
    maximum - minimum
)

vector_time = time.time() - start

print("\nPerformance Comparison")
print(f"Loop Time        : {loop_time:.6f} seconds")
print(f"Vectorized Time  : {vector_time:.6f} seconds")

if vector_time > 0:
    print(f"Speedup          : {loop_time/vector_time:.2f}x")

# =======================================
# Task 4: Ranking Customers
# =======================================

df["revenue_rank"] = df["revenue"].rank(
    ascending=False,
    method="dense"
)

print("\nCustomer Ranking Completed")

# =======================================
# Task 5: Business Categories
# =======================================

conditions = [
    revenue_array < 3000,
    (revenue_array >= 3000) & (revenue_array < 7000),
    revenue_array >= 7000
]

choices = [
    "Low",
    "Medium",
    "High"
]

df["revenue_category"] = np.select(
    conditions,
    choices,
    default="Unknown"
)

print("Revenue Categories Assigned")

# =======================================
# Summary
# =======================================

print("\nFirst Five Rows")
print(df.head())

print("\nStatistics")
print(df.describe())

print("\nRevenue Category Counts")
print(df["revenue_category"].value_counts())

print("\nTop 10 Customers")
print(
    df.sort_values(
        "revenue",
        ascending=False
    ).head(10)
)

# Save Output

df.to_csv(
    "vectorized_output.csv",
    index=False
)

print("\nOutput saved as vectorized_output.csv")