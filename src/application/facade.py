"""Streamlit、CLI 与 Agent 共用的业务 Facade。"""

from __future__ import annotations

import json
from collections.abc import MutableMapping
from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd

from src.application.task_runner import TaskRunner
from src.connectors.feishu.mock import MockFeishuConnector
from src.connectors.google_ads.mock import MockGoogleAdsConnector
from src.connectors.google_sheets.mock import MockGoogleSheetsConnector
from src.connectors.llm.factory import build_llm_service
from src.demo.generator import seed_all
from src.etl.cleaning_engine import CleaningEngine
from src.etl.workbook_inspector import load_gtm_project_data
from src.fifa.sync_service import FIFASyncResult, FIFASyncService
from src.fifa.file_scanner import find_target_file, scan_fifa_files
from src.qc.media_plan_parser import MediaPlanParser
from src.models.cleaning import CleaningResult
from src.models.project import AppConfig, ProjectConfig
from src.models.task import TaskType
from src.qc.service import GoogleAdsQCService, QCRunSummary
from src.reporting.daily_report import DailyReportService
from src.storage.session_repository import SessionRepository
from src.utils.config import PROJECT_ROOT, load_app_config


class MarketingOpsFacade:
    def __init__(self, state: MutableMapping[str, Any]) -> None:
        self.state = state
        base_config = load_app_config()
        saved_projects = state.get("project_configs")
        self.config = AppConfig(
            mode=base_config.mode,
            timezone=base_config.timezone,
            projects=saved_projects or base_config.projects,
        )
        self.repository = SessionRepository(state)
        self.runner = TaskRunner(self.repository, "demo")
        self.cleaner = CleaningEngine()
        self.report_service = DailyReportService(build_llm_service())
        self.state.setdefault("mock_google_sheets", {})
        self.state.setdefault("mock_feishu", {})
        self.state.setdefault("workspace_initialized", False)
        self.paths = self._ensure_workspace()

    def _ensure_workspace(self) -> dict[str, Path]:
        expected = PROJECT_ROOT / "data/sample/gtm/TECNO_GTM_sample.xlsx"
        paths = seed_all() if not expected.exists() else {
            "gtm": expected,
            "fifa_latest": PROJECT_ROOT / "data/sample/fifa_shared_drive/FIFA_2026-08-26.xlsx",
            "media_plan": PROJECT_ROOT / "data/sample/media_plan/Sample_Google_Media_Plan.xlsx",
            "google_ads": PROJECT_ROOT / "data/sample/google_ads/google_ads_sample.json",
            "media_plan_json": PROJECT_ROOT / "data/sample/media_plan/media_plan_canonical.json",
        }
        self.state["workspace_initialized"] = True
        return paths

    def project(self, country_or_name: str) -> ProjectConfig:
        value = country_or_name.strip().casefold()
        for project in self.config.projects:
            if value in {project.country.casefold(), project.project_name.casefold()}:
                return project
        raise ValueError(f"Unknown project: {country_or_name}")

    def run_cleaning(
        self,
        project: ProjectConfig,
        report_date: date | None = None,
        source: str | Path | Any | None = None,
    ) -> CleaningResult:
        source = source or self.paths["gtm"]

        def operation() -> CleaningResult:
            selected = load_gtm_project_data(source, project, report_date)
            return self.cleaner.clean(selected)

        return self.runner.run(
            TaskType.DATA_CLEANING,
            project.project_name,
            operation,
            summarize=lambda result: (
                result.summary.final_clean_rows,
                result.summary.validation_warnings,
                0,
                f"Cleaned {result.summary.final_clean_rows} rows",
            ),
        )

    def run_daily_report(self, project: ProjectConfig, report_date: date):
        def operation():
            selected = load_gtm_project_data(self.paths["gtm"], project, None)
            clean = self.cleaner.clean(selected)
            report = self.report_service.generate(clean.after, project, report_date)
            self.state.setdefault("daily_reports", {})[f"{project.country}:{report_date}"] = report
            return report

        return self.runner.run(
            TaskType.DAILY_REPORT,
            project.project_name,
            operation,
            summarize=lambda report: (
                len(report.daily_trend), len(report.anomalies), 0,
                f"Generated report for {report.report_date}",
            ),
        )

    def write_report_sheet(self, project: ProjectConfig, report) -> Any:
        connector = MockGoogleSheetsConnector(self.state["mock_google_sheets"])
        return connector.write_daily_report(
            project.google_sheet_id or project.country,
            report.report_date,
            report.daily_trend,
        )

    def run_fifa_sync(self, target_date: date) -> FIFASyncResult:
        connector = MockFeishuConnector(self.state["mock_feishu"])
        service = FIFASyncService(connector)
        directory = PROJECT_ROOT / "data/sample/fifa_shared_drive"
        return self.runner.run(
            TaskType.FIFA_SYNC,
            "FIFA",
            lambda: service.run(directory, target_date),
            summarize=lambda result: (
                result.cleaning.summary.final_clean_rows,
                result.cleaning.summary.validation_warnings,
                result.upsert.errors,
                f"Inserted {result.upsert.inserted}, updated {result.upsert.updated}, skipped {result.upsert.skipped}",
            ),
        )

    def scan_fifa_files(self) -> dict[date, Path]:
        return scan_fifa_files(PROJECT_ROOT / "data/sample/fifa_shared_drive")

    def preview_fifa(self, target_date: date) -> tuple[Path, CleaningResult]:
        source = find_target_file(PROJECT_ROOT / "data/sample/fifa_shared_drive", target_date)
        connector = MockFeishuConnector(self.state["mock_feishu"])
        return source, FIFASyncService(connector).preview(source)

    def inspect_media_plan(self, source: Any):
        return MediaPlanParser().inspect(source)

    def parse_media_plan(self, source: Any, inspection, confirmed: bool) -> pd.DataFrame:
        return MediaPlanParser().parse(
            source,
            inspection.mappings,
            confirmed,
            inspection.selected_sheet,
            inspection.header_row,
        )

    def run_ads_qc(self, plans: list[dict[str, Any]] | None = None) -> QCRunSummary:
        def operation() -> QCRunSummary:
            selected_plans = plans or json.loads(Path(self.paths["media_plan_json"]).read_text(encoding="utf-8"))
            ads = MockGoogleAdsConnector(self.paths["google_ads"]).list_qc_objects()
            return GoogleAdsQCService().run(selected_plans, ads)

        return self.runner.run(
            TaskType.ADS_QC,
            "Google Ads",
            operation,
            summarize=lambda result: (
                result.objects_checked,
                result.warnings,
                result.errors,
                f"PASS {result.passed}, WARNING {result.warnings}, ERROR {result.errors}",
            ),
        )

    def overview_stats(self) -> dict[str, Any]:
        excel = pd.ExcelFile(self.paths["gtm"])
        source_rows = sum(len(pd.read_excel(excel, sheet_name=sheet)) for sheet in ("FB", "TT", "GG"))
        plans = json.loads(Path(self.paths["media_plan_json"]).read_text(encoding="utf-8"))
        ads = MockGoogleAdsConnector(self.paths["google_ads"]).list_qc_objects()
        qc = GoogleAdsQCService().run(plans, ads)
        total_checks = qc.passed + qc.warnings + qc.errors
        return {
            "source_rows": source_rows,
            "projects": len(self.config.projects),
            "qc_pass_rate": qc.passed / total_checks if total_checks else 0,
            "recent_tasks": len(self.repository.list_tasks()),
        }

    def save_projects(self, projects: list[ProjectConfig]) -> None:
        self.state["project_configs"] = projects
        self.config = self.config.model_copy(update={"projects": projects})

    def reset_workspace(self) -> None:
        for key in (
            "task_records", "mock_google_sheets", "mock_feishu", "daily_reports",
            "cleaning_result", "qc_result", "mapping_confirmed", "chat_history", "project_configs",
        ):
            self.state.pop(key, None)
        self.repository = SessionRepository(self.state)
        self.runner = TaskRunner(self.repository, "demo")
