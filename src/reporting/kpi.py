"""广告 KPI 的唯一确定性计算实现。"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pandas as pd

from src.utils.numbers import safe_divide

METRIC_COLUMNS = [
    "Spend", "Impression", "Reach", "Engagement", "Video View", "Follower",
    "Link Click", "Add to Cart", "Purchase", "Purchase Value", "All Clicks",
]


def calculate_kpis(totals: Mapping[str, Any]) -> dict[str, float | None]:
    spend = float(totals.get("Spend", 0) or 0)
    impression = float(totals.get("Impression", 0) or 0)
    engagement = float(totals.get("Engagement", 0) or 0)
    video_view = float(totals.get("Video View", 0) or 0)
    link_click = float(totals.get("Link Click", 0) or 0)
    purchase = float(totals.get("Purchase", 0) or 0)
    purchase_value = float(totals.get("Purchase Value", 0) or 0)
    return {
        "CPM": (value * 1000) if (value := safe_divide(spend, impression)) is not None else None,
        "CTR": safe_divide(link_click, impression),
        "CPC": safe_divide(spend, link_click),
        "CPE": safe_divide(spend, engagement),
        "ER": safe_divide(engagement, impression),
        "CPV": safe_divide(spend, video_view),
        "VTR": safe_divide(video_view, impression),
        "CVR": safe_divide(purchase, link_click),
        "CPA": safe_divide(spend, purchase),
        "ROAS": safe_divide(purchase_value, spend),
    }


def aggregate_totals(frame: pd.DataFrame, group_by: list[str] | None = None) -> pd.DataFrame:
    numeric = [column for column in METRIC_COLUMNS if column in frame.columns]
    if group_by:
        return frame.groupby(group_by, dropna=False)[numeric].sum().reset_index()
    return pd.DataFrame([{column: float(frame[column].fillna(0).sum()) for column in numeric}])


def add_derived_metrics(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    metric_rows = [calculate_kpis(row) for row in result.to_dict(orient="records")]
    metrics = pd.DataFrame(metric_rows, index=result.index)
    return pd.concat([result, metrics], axis=1)

