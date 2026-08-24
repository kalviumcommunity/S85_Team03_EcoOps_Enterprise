import pandas as pd
import pytest

from src.analytics.dashboard_metrics import (
    aggregate_values,
    build_quality_summary,
    calculate_kpis,
    find_column,
)


@pytest.fixture
def sample_data():
    return pd.DataFrame(
        {
            "customer_id": ["c1", "c2", "c1"],
            "segment": ["Enterprise", "SMB", "Enterprise"],
            "revenue": [100, 50, 150],
        }
    )


def test_find_column_is_case_insensitive(sample_data):
    assert find_column(sample_data, ("REVENUE",)) == "revenue"
    assert find_column(sample_data, ("missing",)) is None


def test_calculate_kpis_uses_filtered_rows(sample_data):
    kpis = calculate_kpis(sample_data, "revenue")

    assert kpis["total_value"] == 300
    assert kpis["average_value"] == 100
    assert kpis["records"] == 3
    assert kpis["customers"] == 2
    assert kpis["quality"] == 100


def test_aggregate_values_supports_average_and_count(sample_data):
    assert aggregate_values(sample_data, "segment", "revenue", "Average").to_dict() == {
        "Enterprise": 125.0,
        "SMB": 50.0,
    }
    assert aggregate_values(sample_data, "segment", "revenue", "Count").to_dict() == {
        "Enterprise": 2,
        "SMB": 1,
    }


def test_quality_summary_reports_missing_values(sample_data):
    sample_data.loc[0, "revenue"] = None
    summary = build_quality_summary(sample_data).set_index("Column")

    assert summary.loc["revenue", "Missing Values"] == 1
    assert summary.loc["revenue", "Completeness %"] == 66.7


def test_empty_kpis_are_safe():
    kpis = calculate_kpis(pd.DataFrame(), "revenue")

    assert kpis == {
        "total_value": None,
        "average_value": None,
        "records": 0,
        "customers": 0,
        "quality": 100.0,
    }
