from datetime import date

import pandas as pd

from src.demo.generator import generate_fifa_frame, generate_gtm_frames, generate_qc_records


def test_gtm_sample_is_reproducible_and_material() -> None:
    first = generate_gtm_frames()
    second = generate_gtm_frames()
    assert first.keys() == second.keys()
    pd.testing.assert_frame_equal(first["FB"], second["FB"])
    combined = pd.concat([first["FB"], first["TT"], first["GG"]], ignore_index=True)
    assert combined["Date"].astype(str).nunique() >= 30
    assert set(combined["Country"].astype(str).str.strip().str.upper()) >= {"UG", "SN", "PK"}
    assert combined["Audience Name"].nunique() >= 4
    assert combined["Creative Name"].nunique() >= 5


def test_fifa_sample_contains_expected_validation_cases() -> None:
    frame = generate_fifa_frame(date(2026, 8, 26))
    assert "未命名" in frame.columns
    assert frame["Marketing Funnel"].isna().any()
    assert (pd.to_numeric(frame["Impression"]) == 0).any()
    assert frame.duplicated().any()
    assert frame["Spend"].map(lambda value: isinstance(value, str)).any()


def test_qc_sample_contains_required_differences() -> None:
    plans, ads = generate_qc_records()
    assert len(plans) == len(ads) == 9
    assert plans[0]["total_budget"] != ads[0]["total_budget"]
    assert plans[4]["final_url"] != ads[4]["final_url"]
    assert ads[8]["status"] == "ENABLED"

