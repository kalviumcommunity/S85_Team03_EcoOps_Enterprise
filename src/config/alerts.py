"""Business alert thresholds used by the operational dashboard."""

ALERT_THRESHOLDS = {
    "churn_rate": {
        "metric": "Churn Rate",
        "threshold": 7.0,
        "direction": "above",
        "severity": "critical",
        "message": "Churn exceeds the safe limit. Investigate retention.",
    },
    "avg_order_value": {
        "metric": "Avg Order Value",
        "threshold": 30.0,
        "direction": "below",
        "severity": "warning",
        "message": "Average value is below target. Check pricing and product mix.",
    },
    "null_percentage": {
        "metric": "Data Quality",
        "threshold": 5.0,
        "direction": "above",
        "severity": "warning",
        "message": "Null percentage is too high. Check the data pipeline.",
    },
}
