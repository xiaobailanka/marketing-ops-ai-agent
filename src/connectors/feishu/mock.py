"""Session scoped Feishu Upsert 模拟器。"""

from __future__ import annotations

from typing import Any

from src.connectors.feishu.base import UpsertResult


class MockFeishuConnector:
    def __init__(self, state: dict[str, dict[str, Any]] | None = None) -> None:
        self.state = state if state is not None else {}

    def upsert(self, records: list[dict[str, Any]]) -> UpsertResult:
        result = UpsertResult()
        for record in records:
            key = str(record["_business_key"])
            clean_record = {field: value for field, value in record.items() if field != "_business_key"}
            existing = self.state.get(key)
            if existing is None:
                self.state[key] = clean_record
                result.inserted += 1
                result.changes.append({"action": "INSERT", "key": key})
            elif existing == clean_record:
                result.skipped += 1
            else:
                self.state[key] = clean_record
                result.updated += 1
                result.changes.append({"action": "UPDATE", "key": key})
        return result

