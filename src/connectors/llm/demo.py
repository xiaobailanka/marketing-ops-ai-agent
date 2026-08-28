"""无需 API Key 的确定性摘要。"""

from __future__ import annotations

from typing import Any


class DemoLLMService:
    def diagnose(self, facts: dict[str, Any], anomalies: list[str]) -> dict[str, str]:
        spend_change = facts.get("spend_vs_7d")
        overall = "昨日表现总体稳定。"
        if spend_change is not None and abs(spend_change) >= 0.2:
            overall = f"昨日消耗较近 7 日均值变化 {spend_change:+.1%}，需要关注节奏。"
        key_changes = "；".join(anomalies) if anomalies else "主要 KPI 未发现超过阈值的变化。"
        risk = "未发现显著风险。" if not anomalies else "存在超过配置阈值的指标变化，应检查投放设置与素材状态。"
        return {
            "Overall Performance": overall,
            "Key Changes": key_changes,
            "Audience Insights": str(facts.get("top_audience", "请查看 Audience Performance 排名。")),
            "Creative Insights": str(facts.get("top_creative", "请查看 Creative Performance 排名。")),
            "Risks": risk,
            "Recommended Actions": "复核异常平台、Audience 与 Creative，并结合业务背景判断。请与优化师沟通确认后执行。",
        }

