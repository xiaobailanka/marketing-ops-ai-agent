"""Session scoped Google Sheets 模拟器。"""

from __future__ import annotations

from datetime import date
from typing import Any

import pandas as pd

from src.connectors.google_sheets.base import SheetWriteResult


class MockGoogleSheetsConnector:
    def __init__(self, state: dict[str, Any] | None = None) -> None:
        self.state = state if state is not None else {}

    def write_daily_report(self, sheet_id: str, report_date: date, frame: pd.DataFrame) -> SheetWriteResult:
        worksheet = report_date.isoformat()
        book_key = sheet_id or "demo-sheet"
        book = self.state.setdefault(book_key, {})
        action = "REPLACED" if worksheet in book else "CREATED"
        book[worksheet] = frame.copy()
        return SheetWriteResult(worksheet, action, len(frame), f"Demo worksheet {action.lower()}")

