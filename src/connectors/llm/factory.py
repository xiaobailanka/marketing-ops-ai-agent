"""按环境变量选择 LLM 实现。"""

from __future__ import annotations

import os

from src.connectors.llm.base import LLMService
from src.connectors.llm.demo import DemoLLMService
from src.connectors.llm.real import RealLLMService


def build_llm_service() -> LLMService:
    return RealLLMService() if os.getenv("OPENAI_API_KEY") else DemoLLMService()

