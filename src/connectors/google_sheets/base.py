"""Google Sheets Connector 接口。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Protocol

import pandas as pd


@dataclass(slots=True)
class SheetWriteResult:
    worksheet: str
    action: str
    rows_written: int
    message: str = ""


class GoogleSheetsConnector(Protocol):
    def write_daily_report(
        self,
        sheet_id: str,
        report_date: date,
        frame: pd.DataFrame,
    ) -> SheetWriteResult: ...

