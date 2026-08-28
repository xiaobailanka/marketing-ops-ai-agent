"""LLM Service 接口。"""

from __future__ import annotations

from typing import Any, Protocol


class LLMService(Protocol):
    def diagnose(self, facts: dict[str, Any], anomalies: list[str]) -> dict[str, str]: ...

