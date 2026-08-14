import pandas as pd


def calculate_mau(df, days=30):
    """Count unique customers active in the last N days."""
    df = df.copy()
    df["transaction_date"] = pd.to_datetime(df["transaction_date"])

    cutoff = pd.Timestamp.now() - pd.Timedelta(days=days)

    return df[df["transaction_date"] >= cutoff]["customer_id"].nunique()


def calculate_revenue_per_customer(df):
    """Calculate average revenue per unique customer."""
    customers = df["customer_id"].nunique()

    if customers == 0:
        return 0

    return df["amount"].sum() / customers


def calculate_churn_rate(df, period_days=30):
    """Calculate customers active before but not active recently."""
    df = df.copy()
    df["transaction_date"] = pd.to_datetime(df["transaction_date"])

    today = pd.Timestamp.now()

    period_1_end = today - pd.Timedelta(days=period_days)
    period_1_start = period_1_end - pd.Timedelta(days=period_days)

    period_2_start = today - pd.Timedelta(days=period_days)

    active_p1 = set(
        df[
            (df["transaction_date"] >= period_1_start)
            & (df["transaction_date"] < period_1_end)
        ]["customer_id"]
    )

    active_p2 = set(
        df[df["transaction_date"] >= period_2_start]["customer_id"]
    )

    if len(active_p1) == 0:
        return 0

    churned = active_p1 - active_p2

    return len(churned) / len(active_p1)


def calculate_total_revenue(df):
    """Calculate total revenue."""
    return df["amount"].sum()


def calculate_average_transaction_value(df):
    """Calculate average transaction value."""
    if len(df) == 0:
        return 0

    return df["amount"].mean()


# Example usage
if __name__ == "__main__":
    df = pd.read_csv("data.csv")

    mau = calculate_mau(df)
    revenue_per_customer = calculate_revenue_per_customer(df)
    churn_rate = calculate_churn_rate(df)
    total_revenue = calculate_total_revenue(df)
    avg_transaction = calculate_average_transaction_value(df)

    print(f"MAU: {mau}")
    print(f"Revenue per Customer: ${revenue_per_customer:.2f}")
    print(f"Churn Rate: {churn_rate:.1%}")
    print(f"Total Revenue: ${total_revenue:,.2f}")
    print(f"Average Transaction: ${avg_transaction:,.2f}")