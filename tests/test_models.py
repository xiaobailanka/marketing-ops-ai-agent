from datetime import date

import pytest
from pydantic import ValidationError

from src.models.project import ProjectConfig
from src.utils.numbers import parse_number, safe_divide


def test_project_rejects_reversed_dates() -> None:
    with pytest.raises(ValidationError):
        ProjectConfig(
            country="ug",
            project_name="Demo",
            campaign_start_date=date(2026, 8, 20),
            campaign_end_date=date(2026, 8, 19),
            total_budget=100,
        )


def test_safe_number_helpers() -> None:
    assert safe_divide(10, 0) is None
    assert safe_divide(10, 2) == 5
    assert parse_number("$5,000.00") == 5000
    assert parse_number("12%") == 0.12
    assert parse_number("not-a-number") is None

