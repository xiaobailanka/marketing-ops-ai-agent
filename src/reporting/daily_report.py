"""独立于 Streamlit 的日报应用服务。"""

from __future__ import annotations

from datetime import date

import pandas as pd

from src.models.project import ProjectConfig
from src.models.reporting import DailyReportResult
from src.reporting.anomalies import diagnose_changes
from src.reporting.audience import analyze_audiences
from src.reporting.creative import analyze_creatives
from src.reporting.diagnosis import DemoLLMService, LLMService
from src.reporting.kpi import add_derived_metrics, aggregate_totals, calculate_kpis
from src.utils.config import load_anomaly_thresholds
from src.utils.numbers import safe_divide


class DailyReportService:
    def __init__(self, llm_service: LLMService | None = None) -> None:
        self.llm_service = llm_service or DemoLLMService()
        self.thresholds = load_anomaly_thresholds()

    def generate(
        self,
        frame: pd.DataFrame,
        project: ProjectConfig,
        report_date: date,
    ) -> DailyReportResult:
        if frame.empty:
            raise ValueError("没有可用于日报的数据")
        dates = pd.to_datetime(frame["Date"], errors="coerce").dt.date
        project_mask = (
            frame["Country"].astype(str).str.strip().str.upper().eq(project.country)
            & frame["Project Name"].astype(str).str.strip().str.casefold().eq(project.project_name.casefold())
            & dates.le(report_date)
        )
        project_frame = frame.loc[project_mask].copy()
        if project_frame.empty:
            raise ValueError("所选项目和日期没有可用数据")
        project_dates = pd.to_datetime(project_frame["Date"], errors="coerce").dt.date
        yesterday_frame = project_frame.loc[project_dates == report_date]
        if yesterday_frame.empty:
            raise ValueError("所选 Report Date 没有数据")

        yesterday_totals = aggregate_totals(yesterday_frame).iloc[0].to_dict()
        yesterday_kpis = calculate_kpis(yesterday_totals)
        cumulative_spend = float(project_frame["Spend"].fillna(0).sum())
        elapsed_days = max(0, (report_date - project.campaign_start_date).days + 1)
        duration_days = (project.campaign_end_date - project.campaign_start_date).days + 1
        time_progress = min(1.0, safe_divide(elapsed_days, duration_days) or 0.0)
        kpi_cards = {
            "Yesterday Spend": float(yesterday_totals.get("Spend", 0)),
            "Cumulative Spend": cumulative_spend,
            "Total Budget": project.total_budget,
            "Budget Utilization": safe_divide(cumulative_spend, project.total_budget),
            "Time Progress": time_progress,
            "Yesterday Impression": float(yesterday_totals.get("Impression", 0)),
            **yesterday_kpis,
        }

        daily = add_derived_metrics(aggregate_totals(project_frame.assign(Date=project_dates), ["Date"]))
        daily = daily.sort_values("Date").reset_index(drop=True)
        daily["Cumulative Spend"] = daily["Spend"].cumsum()
        daily["Total Budget"] = project.total_budget
        platform = add_derived_metrics(aggregate_totals(yesterday_frame, ["Platform"]))
        audience = analyze_audiences(
            project_frame,
            self.thresholds["min_impressions"],
            self.thresholds["min_spend_usd"],
        )
        creative = analyze_creatives(
            project_frame,
            self.thresholds["min_impressions"],
            self.thresholds["min_spend_usd"],
        )
        facts, anomalies = diagnose_changes(
            project_frame,
            report_date,
            float(self.thresholds["relative_change"]),
        )
        pacing_gap = (kpi_cards["Budget Utilization"] or 0) - time_progress
        facts["budget_pacing_gap"] = pacing_gap
        if abs(pacing_gap) >= float(self.thresholds["budget_pacing_percentage_points"]):
            anomalies.append(f"Budget Progress vs Time Progress: {pacing_gap:+.1%}")
        if not audience.empty:
            facts["top_audience"] = audience.iloc[0]["Audience Name"]
        if not creative.empty:
            facts["top_creative"] = creative.iloc[0]["Creative Name"]
        diagnosis = self.llm_service.diagnose(facts, anomalies)
        return DailyReportResult(
            project_name=project.project_name,
            report_date=report_date,
            kpi_cards=kpi_cards,
            daily_trend=daily,
            platform_performance=platform,
            audience_performance=audience,
            creative_performance=creative,
            facts=facts,
            anomalies=anomalies,
            diagnosis=diagnosis,
        )

