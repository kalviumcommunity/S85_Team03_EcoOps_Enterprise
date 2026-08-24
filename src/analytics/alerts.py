"""Alert evaluation for filtered dashboard metrics."""

from collections.abc import Mapping


def get_breached_alerts(
    current_metrics: Mapping[str, float | int | None], thresholds: Mapping
) -> list[dict]:
    """Return configured alerts whose thresholds are breached."""
    breached_alerts = []
    for key, config in thresholds.items():
        value = current_metrics.get(key)
        if value is None:
            continue
        threshold = config["threshold"]
        is_breached = (
            value > threshold
            if config["direction"] == "above"
            else value < threshold
        )
        if is_breached:
            breached_alerts.append(
                {
                    "key": key,
                    "value": value,
                    "config": config,
                }
            )
    return breached_alerts
