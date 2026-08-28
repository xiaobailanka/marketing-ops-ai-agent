"""透明的中文关键词意图路由。"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Intent:
    tool_name: str
    country: str | None = None


class IntentRouter:
    BLOCKED_WORDS = {"启用", "暂停广告", "修改预算", "改预算", "修改bid", "改bid", "删除campaign"}

    def route(self, message: str) -> Intent:
        lowered = message.casefold()
        if any(word in lowered for word in self.BLOCKED_WORDS):
            return Intent("blocked_action")
        country = next((code for code in ("UG", "SN", "PK") if code.casefold() in lowered), None)
        if "fifa" in lowered and any(word in lowered for word in ("同步", "运行", "sync")):
            return Intent("run_fifa_sync", country)
        if "qc" in lowered or "重新检查" in lowered:
            return Intent("run_google_ads_qc", country)
        if "失败任务" in lowered or ("任务" in lowered and "失败" in lowered):
            return Intent("get_failed_tasks", country)
        if "日报" in lowered or "报告" in lowered:
            return Intent("generate_daily_report", country or "UG")
        if "素材" in lowered or "creative" in lowered:
            return Intent("analyze_creative", country or "UG")
        if "audience" in lowered or "受众" in lowered:
            return Intent("analyze_audience", country or "UG")
        if "清洗" in lowered:
            return Intent("run_data_cleaning", country or "UG")
        if "为什么" in lowered and "error" in lowered:
            return Intent("explain_qc_error", country)
        return Intent("help", country)

