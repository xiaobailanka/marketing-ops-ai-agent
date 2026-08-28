from datetime import date

import pandas as pd

from src.etl.cleaning_engine import CleaningEngine


def _base_rows() -> list[dict]:
    return [
        {
            "Country": " ug ", "Project Name": "CAMON 50 Campaign", "Date": "2026/08/26",
            "Platform": "facebook", "Objective": " reach ", "Marketing Funnel": None,
            "Creative Name": " Hero Video ", "Creative Type": "video", "Spend": "$10.00", "Impression": 1000,
        },
        {
            "Country": "UG", "Project Name": "CAMON 50 Campaign", "Date": date(2026, 8, 26),
            "Platform": "FB", "Objective": "Reach", "Marketing Funnel": "Traffic",
            "Creative Name": "Keep Exact", "Creative Type": "Image", "Spend": 12, "Impression": 800,
        },
        {
            "Country": "UG", "Project Name": "CAMON 50 Campaign", "Date": date(2026, 8, 26),
            "Platform": "FB", "Objective": "Traffic", "Marketing Funnel": "Traffic",
            "Creative Name": "Zero", "Creative Type": "Image", "Spend": 5, "Impression": 0,
        },
        {"Country": "TOTAL", "Project Name": None, "Date": None, "Platform": None, "Objective": None, "Impression": 1800},
    ]


def test_cleaning_rules_and_audit() -> None:
    result = CleaningEngine().clean(pd.DataFrame(_base_rows()))
    assert result.summary.removed_total_rows == 1
    assert result.summary.removed_zero_impression_rows == 1
    assert result.summary.funnel_filled == 1
    assert result.summary.funnel_corrected == 1
    assert len(result.after) == 2
    assert result.after.iloc[0]["Country"] == "UG"
    assert result.after.iloc[0]["Platform"] == "FB"
    assert result.after.iloc[0]["Marketing Funnel"] == "Awareness"
    assert result.after.iloc[0]["Creative Name"] == " Hero Video "
    assert {entry.rule for entry in result.audit_log} >= {
        "funnel_missing_fill", "funnel_wrong_value_correction"
    }


def test_duplicate_is_removed() -> None:
    row = _base_rows()[1]
    result = CleaningEngine().clean(pd.DataFrame([row, dict(row)]))
    assert result.summary.duplicates_found == 1
    assert len(result.after) == 1

