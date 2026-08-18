import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json

# Make sure your dataframe is already loaded as df
# Example:
# df = pd.read_csv("data.csv")


# -------------------------------
# Task 1: Pearson & Spearman
# -------------------------------

pearson_corr = df.corr(numeric_only=True, method='pearson')
spearman_corr = df.corr(numeric_only=True, method='spearman')

comparison = pd.DataFrame({
    'pearson': pearson_corr['churn'],
    'spearman': spearman_corr['churn']
})

print("Pearson vs Spearman Correlation:")
print(comparison)


# -------------------------------
# Task 2: Correlation Heatmap
# -------------------------------

plt.figure(figsize=(12, 10))

sns.heatmap(
    pearson_corr,
    annot=True,
    cmap='coolwarm',
    center=0
)

plt.title('Feature Correlation Matrix')
plt.tight_layout()

plt.savefig('correlation_heatmap.png')
plt.show()


# -------------------------------
# Task 3: Strong Correlations
# -------------------------------

corr_flat = pearson_corr.unstack()

strong = corr_flat[
    (corr_flat.abs() > 0.7) &
    (corr_flat.abs() < 1.0)
].sort_values(ascending=False)

print("\nStrong Correlations:")
print(strong.head(10))


# -------------------------------
# Task 4: Business Interpretation
# -------------------------------

analysis = {
    "support_tickets_vs_churn": {
        "correlation": 0.8,
        "meaning": "Support tickets and churn move strongly together.",
        "possible_causes": [
            "Support tickets may contribute to churn",
            "Unhappy customers may create more support tickets",
            "Customer pain may cause both support tickets and churn"
        ],
        "important_point": "Correlation does not mean causation.",
        "business_action": "Focus on finding and reducing customer pain."
    }
}

print("\nBusiness Interpretation:")
print(json.dumps(analysis, indent=2))


# -------------------------------
# Task 5: Feature Selection
# -------------------------------

features = [
    'engagement',
    'transactions_per_month',
    'support_tickets',
    'churn'
]

# Keep only columns that exist in the dataset
features = [column for column in features if column in df.columns]

df_features = df[features].copy()

print("\nFeature Correlation:")
print(df_features.corr(numeric_only=True))

# Example: remove redundant engagement feature
if 'engagement' in df_features.columns:
    df_features = df_features.drop('engagement', axis=1)

print("\nAfter Feature Selection:")
print(df_features.corr(numeric_only=True))

print("\nAssignment completed successfully!")