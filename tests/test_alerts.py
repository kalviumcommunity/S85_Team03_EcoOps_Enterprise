from src.analytics.alerts import get_breached_alerts
from src.config.alerts import ALERT_THRESHOLDS


def test_alerts_detect_above_and_below_thresholds():
    metrics = {
        "churn_rate": 8.5,
        "avg_order_value": 25.0,
        "null_percentage": 2.0,
    }

    alerts = get_breached_alerts(metrics, ALERT_THRESHOLDS)

    assert [alert["key"] for alert in alerts] == [
        "churn_rate",
        "avg_order_value",
    ]


def test_alerts_skip_metrics_without_a_value():
    metrics = {
        "churn_rate": None,
        "avg_order_value": 45.0,
        "null_percentage": 0.0,
    }

    assert get_breached_alerts(metrics, ALERT_THRESHOLDS) == []


def test_alerts_are_clear_when_values_are_within_limits():
    metrics = {
        "churn_rate": 3.0,
        "avg_order_value": 45.0,
        "null_percentage": 1.0,
    }

    assert get_breached_alerts(metrics, ALERT_THRESHOLDS) == []
