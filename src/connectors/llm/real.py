"""基于 OpenAI Responses API 的可选真实摘要服务。"""

from __future__ import annotations

import json
import os
from typing import Any

from openai import OpenAI

from src.connectors.llm.demo import DemoLLMService

SECTIONS = [
    "Overall Performance", "Key Changes", "Audience Insights",
    "Creative Insights", "Risks", "Recommended Actions",
]


class RealLLMService:
    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        key = api_key or os.getenv("OPENAI_API_KEY", "")
        if not key:
            raise RuntimeError("Real LLM credentials are not configured.")
        self.client = OpenAI(api_key=key)
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
        self.fallback = DemoLLMService()

    def diagnose(self, facts: dict[str, Any], anomalies: list[str]) -> dict[str, str]:
        payload = {"facts": facts, "anomalies": anomalies, "required_sections": SECTIONS}
        try:
            response = self.client.responses.create(
                model=self.model,
                instructions=(
                    "You are a marketing performance analyst. Use only supplied facts. "
                    "Never recalculate metrics. Return a JSON object with exactly the requested sections. "
                    "Recommended Actions must end with: 请与优化师沟通确认后执行。"
                ),
                input=json.dumps(payload, ensure_ascii=False, default=str),
            )
            parsed = json.loads(response.output_text)
            if set(parsed) != set(SECTIONS):
                raise ValueError("LLM response sections are incomplete")
            if not str(parsed["Recommended Actions"]).endswith("请与优化师沟通确认后执行。"):
                parsed["Recommended Actions"] = f"{parsed['Recommended Actions']} 请与优化师沟通确认后执行。"
            return {key: str(parsed[key]) for key in SECTIONS}
        except Exception:
            # Public Demo 必须在限流、网络或格式异常时继续运行。
            return self.fallback.diagnose(facts, anomalies)

