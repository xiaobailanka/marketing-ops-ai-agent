from datetime import date

import pandas as pd

from src.demo.generator import generate_gtm_frames
from src.etl.cleaning_engine import CleaningEngine
from src.reporting.daily_report import DailyReportService
from src.utils.config import load_app_config


def test_daily_report_is_computed_from_clean_data() -> None:
    frames = generate_gtm_frames()
    combined = pd.concat([frames["FB"], frames["TT"], frames["GG"]], ignore_index=True)
    clean = CleaningEngine().clean(combined).after
    project = load_app_config().projects[0]
    report = DailyReportService().generate(clean, project, date(2026, 8, 26))
    assert report.kpi_cards["Yesterday Spend"] > 0
    assert report.kpi_cards["Cumulative Spend"] >= report.kpi_cards["Yesterday Spend"]
    assert report.kpi_cards["Total Budget"] == project.total_budget
    assert not report.platform_performance.empty
    assert set(report.diagnosis) == {
        "Overall Performance", "Key Changes", "Audience Insights",
        "Creative Insights", "Risks", "Recommended Actions",
    }
    assert report.diagnosis["Recommended Actions"].endswith("请与优化师沟通确认后执行。")
