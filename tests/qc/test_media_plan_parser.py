from pathlib import Path

import pytest

from src.demo.generator import seed_all
from src.qc.media_plan_parser import MediaPlanParser


def test_dynamic_header_and_confirmation_gate(tmp_path: Path) -> None:
    path = seed_all(tmp_path)["media_plan"]
    parser = MediaPlanParser()
    inspection = parser.inspect(path)
    assert inspection.selected_sheet == "Media Plan"
    assert inspection.header_row == 4
    assert any(item.canonical_field == "total_budget" for item in inspection.mappings)
    with pytest.raises(PermissionError):
        parser.parse(path, inspection.mappings, False, inspection.selected_sheet, inspection.header_row)
    confirmed = [item.model_copy(update={"confirmed": True}) for item in inspection.mappings]
    frame = parser.parse(path, confirmed, True, inspection.selected_sheet, inspection.header_row)
    assert "total_budget" in frame.columns

