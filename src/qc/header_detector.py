"""Media Plan 动态表头检测。"""

from __future__ import annotations

from typing import Any

import pandas as pd

HEADER_KEYWORDS = {
    "country", "objective", "ad type", "budget", "start date", "end date",
    "campaign", "creative", "audience", "final url", "cta",
}


def detect_header_row(raw: pd.DataFrame, max_rows: int = 25) -> tuple[int, list[str], int]:
    best_index = -1
    best_headers: list[str] = []
    best_score = 0
    for index in range(min(len(raw), max_rows)):
        headers = [str(value).strip() for value in raw.iloc[index].tolist() if pd.notna(value) and str(value).strip()]
        lowered = [value.casefold() for value in headers]
        score = sum(any(keyword in value for keyword in HEADER_KEYWORDS) for value in lowered)
        if score > best_score:
            best_index, best_headers, best_score = index, headers, score
    if best_index < 0 or best_score < 2:
        raise ValueError("未识别到可靠的 Media Plan 表头")
    return best_index, best_headers, best_score

