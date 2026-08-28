"""Agent 白名单工具注册表。"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Callable[..., Any]] = {}

    def register(self, name: str, function: Callable[..., Any]) -> None:
        if any(word in name.casefold() for word in ("enable", "pause", "update_budget", "update_bid", "delete")):
            raise ValueError("Unsafe advertising write tool cannot be registered")
        self._tools[name] = function

    def call(self, name: str, **kwargs: Any) -> Any:
        if name not in self._tools:
            raise KeyError(f"Unknown or blocked tool: {name}")
        return self._tools[name](**kwargs)

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._tools))

