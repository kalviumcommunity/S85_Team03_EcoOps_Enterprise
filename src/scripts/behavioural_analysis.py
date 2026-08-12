import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# Load dataset
df = pd.read_csv("data/raw/data.csv")


# ============================================================
# TASK 1 - DEFINE SEGMENTS AND COMPUTE METRICS
# ============================================================

segment_metrics = df.groupby('customer_type').agg({
    'lifetime_value': 'mean',
    'churn': 'mean',
    'support_tickets': 'mean',
    'retention_days': 'mean',
    'customer_id': 'count'
})

segment_metrics.columns = [
    'avg_ltv',
    'churn_rate',
    'avg_tickets',
    'avg_retention',
    'count'
]

print("\nSEGMENT METRICS")
print("=" * 60)
print(segment_metrics)


# ============================================================
# TASK 2 - SUMMARY STATISTICS AND RANKING
# ============================================================

segment_summary = segment_metrics.copy()

segment_summary['ltv_rank'] = (
    segment_summary['avg_ltv']
    .rank(ascending=False)
)

segment_summary['churn_rank'] = (
    segment_summary['churn_rate']
    .rank(ascending=True)
)

print("\nSEGMENT SUMMARY")
print("=" * 60)
print(
    segment_summary[
        [
            'avg_ltv',
            'ltv_rank',
            'churn_rate',
            'churn_rank',
            'avg_tickets',
            'avg_retention',
            'count'
        ]
    ]
)


# ============================================================
# TASK 3 - VISUAL COMPARISON
# ============================================================

heatmap_data = segment_metrics[
    ['avg_ltv', 'churn_rate', 'avg_tickets']
]

plt.figure(figsize=(10, 6))

sns.heatmap(
    heatmap_data,
    annot=True,
    cmap='RdYlGn',
    cbar_kws={'label': 'Value'}
)

plt.title('Segment Comparison Heatmap')
plt.xlabel('Metrics')
plt.ylabel('Customer Type')
plt.tight_layout()

plt.savefig('output/segment_heatmap.png')

plt.show()


# ============================================================
# TASK 4 - TOP AND BOTTOM PERFORMER ANALYSIS
# ============================================================

top_segment = segment_metrics['avg_ltv'].idxmax()
top_value = segment_metrics.loc[top_segment, 'avg_ltv']

high_churn = segment_metrics['churn_rate'].idxmax()
high_churn_value = segment_metrics.loc[high_churn, 'churn_rate']

best_retention = segment_metrics['avg_retention'].idxmax()

print("\nSEGMENT INSIGHTS")
print("=" * 60)

print(
    f"HIGHEST VALUE: {top_segment} = "
    f"${top_value:,.0f}"
)

print(
    f"HIGHEST CHURN: {high_churn} = "
    f"{high_churn_value:.1%}"
)

print(
    f"BEST RETENTION: {best_retention}"
)


# ============================================================
# TASK 5 - BUSINESS-FACING INSIGHTS
# ============================================================

print("\nBUSINESS-FACING INSIGHTS")
print("=" * 60)

for segment in segment_metrics.index:

    ltv = segment_metrics.loc[segment, 'avg_ltv']
    churn = segment_metrics.loc[segment, 'churn_rate']
    tickets = segment_metrics.loc[segment, 'avg_tickets']
    retention = segment_metrics.loc[segment, 'avg_retention']
    count = segment_metrics.loc[segment, 'count']

    print(f"\n{segment}")
    print(f"Customers: {count}")
    print(f"Average LTV: ${ltv:,.0f}")
    print(f"Churn Rate: {churn:.1%}")
    print(f"Average Support Tickets: {tickets:.1f}")
    print(f"Average Retention: {retention:.1f} days")

    if churn >= 0.10:
        print(
            "Action: High churn detected. "
            "Improve onboarding and retention strategies."
        )
    elif ltv == top_value:
        print(
            "Action: High-value segment. "
            "Maintain premium support and retention focus."
        )
    else:
        print(
            "Action: Monitor performance and improve "
            "customer education and self-service."
        )


# ============================================================
# SAVE SUMMARY
# ============================================================

segment_summary.to_csv(
    'output/segment_summary.csv'
)

print("\nAnalysis completed successfully.")
print("Heatmap saved to output/segment_heatmap.png")
print("Summary saved to output/segment_summary.csv")