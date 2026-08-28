"""Feishu Bitable Connector 接口。"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(slots=True)
class UpsertResult:
    inserted: int = 0
    updated: int = 0
    skipped: int = 0
    errors: int = 0
    changes: list[dict[str, Any]] = field(default_factory=list)


class FeishuBitableConnector(Protocol):
    def upsert(self, records: list[dict[str, Any]]) -> UpsertResult: ...

