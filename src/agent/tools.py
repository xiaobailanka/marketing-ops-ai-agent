"""把 Facade 暴露为 Agent 白名单工具。"""

from __future__ import annotations

from datetime import date

from src.agent.tool_registry import ToolRegistry
from src.application.facade import MarketingOpsFacade


def build_tool_registry(facade: MarketingOpsFacade) -> ToolRegistry:
    registry = ToolRegistry()
    registry.register("run_data_cleaning", lambda country="UG": facade.run_cleaning(facade.project(country)))
    registry.register(
        "generate_daily_report",
        lambda country="UG", report_date=date(2026, 8, 26): facade.run_daily_report(facade.project(country), report_date),
    )
    registry.register(
        "analyze_audience",
        lambda country="UG", report_date=date(2026, 8, 26): facade.run_daily_report(
            facade.project(country), report_date
        ).audience_performance,
    )
    registry.register(
        "analyze_creative",
        lambda country="UG", report_date=date(2026, 8, 26): facade.run_daily_report(
            facade.project(country), report_date
        ).creative_performance,
    )
    registry.register("run_fifa_sync", lambda report_date=date(2026, 8, 26), **_: facade.run_fifa_sync(report_date))
    registry.register("run_google_ads_qc", lambda **_: facade.run_ads_qc())
    registry.register(
        "explain_qc_error",
        lambda **_: "ERROR 表示 Canonical Value 不一致；请查看字段来源、规则和修复建议。",
    )
    registry.register("get_failed_tasks", lambda **_: facade.repository.list_tasks(failed_only=True))
    return registry

