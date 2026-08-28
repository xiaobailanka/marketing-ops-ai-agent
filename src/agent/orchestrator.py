"""轻量 Agent Orchestrator。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

from src.agent.intent_router import IntentRouter
from src.agent.tool_registry import ToolRegistry


@dataclass(slots=True)
class AgentResponse:
    message: str
    tool_name: str
    result: Any = None


class AgentOrchestrator:
    def __init__(self, registry: ToolRegistry, demo_report_date: date = date(2026, 8, 26)) -> None:
        self.registry = registry
        self.router = IntentRouter()
        self.demo_report_date = demo_report_date

    def handle(self, message: str) -> AgentResponse:
        intent = self.router.route(message)
        if intent.tool_name == "blocked_action":
            return AgentResponse(
                "为保证安全，本 Agent 不能启用、暂停或修改 Google Ads。请与优化师沟通确认后执行。",
                intent.tool_name,
            )
        if intent.tool_name == "help":
            return AgentResponse(
                "我可以运行数据清洗、生成日报、分析 Audience/Creative、同步 FIFA、运行 Google Ads QC 和查询失败任务。",
                "help",
            )
        kwargs: dict[str, Any] = {}
        if intent.country:
            kwargs["country"] = intent.country
        if intent.tool_name in {"generate_daily_report", "run_fifa_sync", "analyze_creative", "analyze_audience"}:
            kwargs["report_date"] = self.demo_report_date
        result = self.registry.call(intent.tool_name, **kwargs)
        return AgentResponse(f"已执行 {intent.tool_name}。", intent.tool_name, result)

