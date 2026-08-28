from datetime import date

from src.agent.intent_router import IntentRouter
from src.agent.orchestrator import AgentOrchestrator
from src.agent.tool_registry import ToolRegistry


def test_chinese_intent_routing() -> None:
    router = IntentRouter()
    assert router.route("帮我生成UG昨天的日报").tool_name == "generate_daily_report"
    assert router.route("运行FIFA昨天的数据同步").tool_name == "run_fifa_sync"
    assert router.route("重新检查POVA的Google广告 QC").tool_name == "run_google_ads_qc"
    assert router.route("最近有哪些失败任务").tool_name == "get_failed_tasks"


def test_unsafe_actions_are_blocked() -> None:
    registry = ToolRegistry()
    orchestrator = AgentOrchestrator(registry, date(2026, 8, 26))
    response = orchestrator.handle("请帮我启用这个 Campaign 并修改预算")
    assert response.tool_name == "blocked_action"
    assert "不能" in response.message
