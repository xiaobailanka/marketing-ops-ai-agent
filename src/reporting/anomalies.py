"""基于结构化事实的异常检测。"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

import pandas as pd

from src.reporting.kpi import calculate_kpis
from src.utils.numbers import safe_divide


def _totals(frame: pd.DataFrame) -> dict[str, float]:
    columns = ["Spend", "Impression", "Link Click", "Engagement", "Video View", "Purchase", "Purchase Value"]
    return {column: float(frame[column].fillna(0).sum()) if column in frame.columns else 0.0 for column in columns}


def diagnose_changes(
    frame: pd.DataFrame,
    report_date: date,
    threshold: float = 0.2,
) -> tuple[dict[str, Any], list[str]]:
    dates = pd.to_datetime(frame["Date"], errors="coerce").dt.date
    yesterday_frame = frame.loc[dates == report_date]
    trailing_start = report_date - timedelta(days=7)
    trailing = frame.loc[(dates >= trailing_start) & (dates < report_date)]
    yesterday_totals = _totals(yesterday_frame)
    trailing_daily = trailing.assign(_date=dates.loc[trailing.index]).groupby("_date").sum(numeric_only=True)
    trailing_average = {
        column: float(trailing_daily[column].mean()) if column in trailing_daily else 0.0
        for column in yesterday_totals
    }
    yesterday_kpis = calculate_kpis(yesterday_totals)
    trailing_kpis = calculate_kpis(trailing_average)
    facts: dict[str, Any] = {**{key.lower().replace(" ", "_"): value for key, value in yesterday_totals.items()}}
    anomalies: list[str] = []
    for metric in ("Spend", "Impression"):
        change = safe_divide(yesterday_totals[metric] - trailing_average[metric], trailing_average[metric])
        facts[f"{metric.lower()}_vs_7d"] = change
        if change is not None and abs(change) >= threshold:
            anomalies.append(f"{metric} vs 7-day average: {change:+.1%}")
    for metric in ("CTR", "CPM", "CPC"):
        current = yesterday_kpis.get(metric)
        baseline = trailing_kpis.get(metric)
        change = safe_divide((current or 0) - (baseline or 0), baseline)
        facts[metric.lower()] = current
        facts[f"{metric.lower()}_vs_7d"] = change
        if change is not None and abs(change) >= threshold:
            anomalies.append(f"{metric} vs 7-day average: {change:+.1%}")
    return facts, anomalies

