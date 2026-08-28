import pytest

from src.reporting.kpi import calculate_kpis


def test_kpi_formulas() -> None:
    metrics = calculate_kpis({
        "Spend": 100, "Impression": 10000, "Engagement": 500, "Video View": 2000,
        "Link Click": 200, "Purchase": 10, "Purchase Value": 500,
    })
    assert metrics["CPM"] == pytest.approx(10)
    assert metrics["CTR"] == pytest.approx(0.02)
    assert metrics["CPC"] == pytest.approx(0.5)
    assert metrics["CPE"] == pytest.approx(0.2)
    assert metrics["CPV"] == pytest.approx(0.05)
    assert metrics["CPA"] == pytest.approx(10)
    assert metrics["ROAS"] == pytest.approx(5)


def test_zero_denominators_are_none() -> None:
    metrics = calculate_kpis({"Spend": 10, "Impression": 0, "Link Click": 0})
    assert metrics["CPM"] is None
    assert metrics["CTR"] is None
    assert metrics["CPC"] is None

