
import pandas as pd
import matplotlib.pyplot as plt
import os

# --------------------------------------------------
# Load data
# --------------------------------------------------

# Change this filename if your dataset has another name
df = pd.read_csv("data.csv")

# Convert date column to datetime
df["date"] = pd.to_datetime(df["date"])

# Sort by date
df = df.sort_values("date").reset_index(drop=True)

# Create output folder
os.makedirs("output", exist_ok=True)


# --------------------------------------------------
# Task 1: Resample Data
# --------------------------------------------------

df_ts = df.set_index("date")

# Weekly
weekly_revenue = df_ts["revenue"].resample("W").sum()
weekly_count = df_ts["orders"].resample("W").count()
weekly_avg = df_ts["revenue"].resample("W").mean()

# Monthly
monthly_revenue = df_ts["revenue"].resample("ME").sum()
monthly_count = df_ts["orders"].resample("ME").count()
monthly_avg = df_ts["revenue"].resample("ME").mean()

print("\n--- Weekly Revenue ---")
print(weekly_revenue)

print("\n--- Monthly Revenue ---")
print(monthly_revenue)

print("\nHighest revenue week:")
print(weekly_revenue.idxmax(), weekly_revenue.max())

print("\nHighest revenue month:")
print(monthly_revenue.idxmax(), monthly_revenue.max())


# --------------------------------------------------
# Task 2: Rolling Averages
# --------------------------------------------------

df["revenue_ma7"] = df["revenue"].rolling(window=7).mean()
df["revenue_ma30"] = df["revenue"].rolling(window=30).mean()

plt.figure(figsize=(12, 6))

plt.plot(
    df["date"],
    df["revenue"],
    label="Raw Revenue",
    alpha=0.3
)

plt.plot(
    df["date"],
    df["revenue_ma7"],
    label="7-Day Moving Average"
)

plt.plot(
    df["date"],
    df["revenue_ma30"],
    label="30-Day Moving Average"
)

plt.xlabel("Date")
plt.ylabel("Revenue")
plt.title("Revenue: Raw vs Rolling Averages")
plt.legend()
plt.tight_layout()

plt.savefig("output/rolling_avg.png")
plt.close()


# --------------------------------------------------
# Task 3: Month-over-Month Change
# --------------------------------------------------

mom_change = monthly_revenue.pct_change() * 100

print("\n--- Month-over-Month Change ---")
print(mom_change)

growth_months = mom_change[mom_change > 0]
decline_months = mom_change[mom_change < 0]

print("\nMonths with positive growth:")
print(growth_months)

print("\nMonths with decline:")
print(decline_months)


# --------------------------------------------------
# Task 4: Cumulative Revenue
# --------------------------------------------------

df["cumulative_revenue"] = df["revenue"].cumsum()

plt.figure(figsize=(12, 6))

plt.plot(
    df["date"],
    df["cumulative_revenue"]
)

plt.xlabel("Date")
plt.ylabel("Cumulative Revenue")
plt.title("Cumulative Revenue Over Time")
plt.tight_layout()

plt.savefig("output/cumulative.png")
plt.close()

print(
    f"\nTotal accumulated revenue: "
    f"${df['cumulative_revenue'].iloc[-1]:,.0f}"
)


# --------------------------------------------------
# Task 5: Trend Analysis
# --------------------------------------------------

recent_ma30 = df["revenue_ma30"].dropna().tail(30)

if len(recent_ma30) >= 2:

    first_value = recent_ma30.iloc[0]
    last_value = recent_ma30.iloc[-1]

    trend_magnitude = (
        (last_value - first_value) / first_value
    ) * 100

    if trend_magnitude > 1:
        trend_direction = "UP"
        business_action = (
            "Revenue is growing. Maintain the current strategy "
            "and investigate opportunities to accelerate growth."
        )

    elif trend_magnitude < -1:
        trend_direction = "DOWN"
        business_action = (
            "Revenue is declining. Investigate the causes and "
            "take corrective action."
        )

    else:
        trend_direction = "FLAT"
        business_action = (
            "Revenue is relatively stable. Continue monitoring "
            "and look for opportunities for improvement."
        )

else:
    trend_direction = "INSUFFICIENT DATA"
    trend_magnitude = 0
    business_action = "Not enough data for trend analysis."


latest_mom = mom_change.dropna().iloc[-1] if len(mom_change.dropna()) > 0 else 0

analysis = f"""
TIME-SERIES TREND ANALYSIS

Trend Direction: {trend_direction}

30-Day Rolling Average Change: {trend_magnitude:.2f}%

Latest Month-over-Month Change: {latest_mom:.2f}%

Revenue Volatility:
${df['revenue'].std():,.2f}

Total Accumulated Revenue:
${df['cumulative_revenue'].iloc[-1]:,.2f}

Business Implication:
{business_action}

Rolling averages help remove daily noise and show the underlying
business trend. Month-over-month percentage change shows whether
revenue is increasing or decreasing between periods.
"""

print("\n" + analysis)

with open("output/trend_analysis.txt", "w") as file:
    file.write(analysis)

print("\nAssignment completed successfully!")