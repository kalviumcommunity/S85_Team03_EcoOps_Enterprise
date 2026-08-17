import os
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats


# -----------------------------
# Load dataset
# -----------------------------

# Change this path if your dataset has a different name/location
df = pd.read_csv("data/dataset.csv")

print("Dataset loaded successfully!")
print(f"Rows: {len(df)}")
print(f"Columns: {len(df.columns)}")


# -----------------------------
# Check revenue column
# -----------------------------

if "revenue" not in df.columns:
    raise ValueError("The dataset must contain a 'revenue' column.")

df["revenue"] = pd.to_numeric(df["revenue"], errors="coerce")
revenue = df["revenue"].dropna()

if revenue.empty:
    raise ValueError("No valid revenue values found.")


# -----------------------------
# Create output folder
# -----------------------------

os.makedirs("output", exist_ok=True)


# -----------------------------
# Task 1: Distribution Plots
# -----------------------------

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Histogram
axes[0].hist(revenue, bins=50, edgecolor="black")
axes[0].set_title("Revenue Distribution (Histogram)")
axes[0].set_xlabel("Revenue")
axes[0].set_ylabel("Count")

# KDE
revenue.plot(kind="density", ax=axes[1])
axes[1].set_title("Revenue Distribution (KDE)")
axes[1].set_xlabel("Revenue")
axes[1].set_ylabel("Density")

plt.tight_layout()
plt.savefig("output/revenue_distribution.png", dpi=150)
plt.close()

print("\nDistribution plot saved.")


# -----------------------------
# Task 2: Skewness & Kurtosis
# -----------------------------

skewness = stats.skew(revenue)
kurtosis = stats.kurtosis(revenue)

print("\n--- Skewness and Kurtosis ---")
print(f"Skewness: {skewness:.2f}")
print(f"Kurtosis: {kurtosis:.2f}")

if abs(skewness) > 1:
    print("Highly skewed - use median instead of mean.")
elif abs(skewness) > 0.5:
    print("Moderately skewed.")
else:
    print("Approximately symmetric.")

if kurtosis > 3:
    print("Heavy tails - possible extreme outliers.")
else:
    print("No strong evidence of heavy tails.")


# -----------------------------
# Task 3: Abnormal Patterns
# -----------------------------

print("\n--- Revenue Statistics ---")
print(revenue.describe())

percentiles = revenue.quantile(
    [0.25, 0.50, 0.75, 0.90, 0.95, 0.99]
)

print("\n--- Revenue Percentiles ---")
print(percentiles)


# -----------------------------
# Task 4: Compare Segments
# -----------------------------

q75 = revenue.quantile(0.75)
q25 = revenue.quantile(0.25)

high_value = revenue[revenue > q75]
low_value = revenue[revenue < q25]

print("\n--- Segment Comparison ---")
print(
    f"High-value customers: "
    f"mean={high_value.mean():.0f}, "
    f"median={high_value.median():.0f}"
)

print(
    f"Low-value customers: "
    f"mean={low_value.mean():.0f}, "
    f"median={low_value.median():.0f}"
)

# Segment visualization
plt.figure(figsize=(10, 6))

plt.hist(
    high_value,
    bins=30,
    alpha=0.7,
    label="High-Value"
)

plt.hist(
    low_value,
    bins=30,
    alpha=0.7,
    label="Low-Value"
)

plt.xlabel("Revenue")
plt.ylabel("Count")
plt.title("Revenue: High vs Low Value Customers")
plt.legend()

plt.tight_layout()
plt.savefig("output/high_vs_low_revenue.png", dpi=150)
plt.close()

print("Segment comparison plot saved.")


# -----------------------------
# Task 5: Business Interpretation
# -----------------------------

mean_revenue = revenue.mean()
median_revenue = revenue.median()
max_revenue = revenue.max()
top_1_percent = revenue.quantile(0.99)

if skewness > 1:
    distribution_message = (
        "Revenue is highly right-skewed. "
        "Most customers have lower revenue while a few customers "
        "generate very high revenue."
    )
    business_action = (
        "Use the median for typical customer revenue and "
        "segment customers into small and enterprise groups."
    )
else:
    distribution_message = "Revenue distribution is not highly right-skewed."
    business_action = "A more uniform customer strategy may be suitable."


interpretation = f"""
REVENUE DISTRIBUTION ANALYSIS
=============================

Skewness: {skewness:.2f}
Kurtosis: {kurtosis:.2f}

Mean Revenue: ${mean_revenue:.2f}
Median Revenue: ${median_revenue:.2f}
Maximum Revenue: ${max_revenue:.2f}
Top 1% Revenue Threshold: ${top_1_percent:.2f}

Interpretation:
{distribution_message}

Business Action:
{business_action}
"""

print("\n" + interpretation)


# -----------------------------
# Save analysis report
# -----------------------------

with open("output/distribution_analysis.txt", "w") as file:
    file.write(interpretation)

print("Analysis report saved.")
print("\nAnalysis completed successfully!")