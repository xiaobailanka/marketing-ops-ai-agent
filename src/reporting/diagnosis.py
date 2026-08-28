"""兼容导出：实际实现位于 connectors/llm。"""

from src.connectors.llm.base import LLMService
from src.connectors.llm.demo import DemoLLMService

__all__ = ["DemoLLMService", "LLMService"]

