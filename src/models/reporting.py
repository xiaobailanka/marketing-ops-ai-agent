"""日报服务返回模型。"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any

import pandas as pd


@dataclass(slots=True)
class DailyReportResult:
    project_name: str
    report_date: date
    kpi_cards: dict[str, float | None]
    daily_trend: pd.DataFrame
    platform_performance: pd.DataFrame
    audience_performance: pd.DataFrame
    creative_performance: pd.DataFrame
    facts: dict[str, Any]
    anomalies: list[str] = field(default_factory=list)
    diagnosis: dict[str, str] = field(default_factory=dict)

