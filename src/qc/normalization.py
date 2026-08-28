"""严格比较前允许的最小 Canonical Normalization。"""

from __future__ import annotations

from datetime import date
from typing import Any

import pandas as pd

from src.qc.naming_parser import normalize_cosmetic_name
from src.utils.numbers import parse_number

NUMERIC_FIELDS = {"total_budget", "bid"}
DATE_FIELDS = {"start_date", "end_date"}
CATEGORY_FIELDS = {
    "country", "channel", "objective", "ad_type", "product", "stage", "bid_strategy",
    "language", "status", "budget_type", "targeting_strategy", "creative_format",
}


def canonicalize(field: str, value: Any) -> Any:
    if value is None or (not isinstance(value, (list, dict)) and pd.isna(value)):
        return None
    if field in NUMERIC_FIELDS:
        return parse_number(value)
    if field in DATE_FIELDS:
        parsed = pd.to_datetime(value, errors="coerce")
        return None if pd.isna(parsed) else parsed.date()
    if field == "campaign_name":
        return normalize_cosmetic_name(str(value))
    if field in CATEGORY_FIELDS:
        return " ".join(str(value).strip().casefold().split())
    if field in {"keywords", "placement"}:
        return tuple(sorted(" ".join(str(item).strip().casefold().split()) for item in value))
    # URL 和所有业务文本只允许 trim，不改变路径、Query 或文字内容。
    return str(value).strip() if isinstance(value, str) else value

