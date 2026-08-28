"""独立日报命令，可供 Windows Task Scheduler、Cron 或 Railway Cron 调用。"""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

import pandas as pd

from src.application.facade import MarketingOpsFacade
from src.ui.dataframe import safe_display_frame
from src.utils.config import PROJECT_ROOT
from src.utils.dates import yesterday


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate one Marketing Ops daily report")
    parser.add_argument("--country", default="UG", choices=["UG", "SN", "PK"])
    parser.add_argument("--date", dest="report_date", default=None, help="YYYY-MM-DD; defaults to yesterday")
    parser.add_argument("--demo", action="store_true", help="Explicitly run with Demo connectors")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report_date = date.fromisoformat(args.report_date) if args.report_date else yesterday()
    facade = MarketingOpsFacade({})
    project = facade.project(args.country)
    report = facade.run_daily_report(project, report_date)
    output_dir = PROJECT_ROOT / "data/outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"daily_report_{args.country}_{report_date.isoformat()}.xlsx"
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        safe_display_frame(report.daily_trend).to_excel(writer, sheet_name="Daily Trend", index=False)
        safe_display_frame(report.platform_performance).to_excel(writer, sheet_name="Platform", index=False)
        safe_display_frame(report.audience_performance).to_excel(writer, sheet_name="Audience", index=False)
        safe_display_frame(report.creative_performance).to_excel(writer, sheet_name="Creative", index=False)
    print(json.dumps({
        "status": "SUCCESS",
        "country": args.country,
        "report_date": report_date.isoformat(),
        "output": str(path),
        "anomalies": report.anomalies,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

