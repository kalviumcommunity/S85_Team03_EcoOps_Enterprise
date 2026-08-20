def generate_report(df, report_date):
    """Generate structured text report from analysis output."""

    revenue = df["revenue"].sum()
    customers = df["customer_id"].nunique()
    avg_order = df["revenue"].mean()

    lines = []

    lines.append("WEEKLY ANALYTICS REPORT")
    lines.append("Date: " + str(report_date))
    lines.append("")

    # KPI Summary
    lines.append("== KPI SUMMARY ==")
    lines.append("Total Revenue: $" + f"{revenue:,.0f}")
    lines.append("Active Customers: " + f"{customers:,}")
    lines.append("Average Order Value: $" + f"{avg_order:,.0f}")
    lines.append("")

    # Key Finding
    lines.append("== KEY FINDING ==")
    top_segment = df.groupby("segment")["revenue"].sum().idxmax()
    lines.append("Top Performing Segment: " + str(top_segment))
    lines.append("")

    # Recommended Action
    lines.append("== RECOMMENDED ACTION ==")
    lines.append(
        "Review segment performance and allocate resources "
        "to high-growth areas."
    )

    return "\n".join(lines)