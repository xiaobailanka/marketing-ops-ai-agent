"""FIFA 专用 Schema 校验与清洗。"""

from __future__ import annotations

import pandas as pd

from src.etl.cleaning_engine import CleaningEngine
from src.fifa.schema import FIFA_TARGET_COLUMNS
from src.models.cleaning import CleaningResult
from src.utils.config import load_cleaning_rules


def clean_fifa_frame(frame: pd.DataFrame) -> CleaningResult:
    rules = load_cleaning_rules()
    rules = dict(rules)
    rules["required_fields"] = ["Country", "Date", "Platform", "Objective", "Impression"]
    allowed = [column for column in frame.columns if not str(column).startswith("未命名")]
    prepared = frame[allowed].copy()
    for column in FIFA_TARGET_COLUMNS:
        if column not in prepared.columns:
            prepared[column] = None
    prepared = prepared[FIFA_TARGET_COLUMNS]
    return CleaningEngine(rules).clean(prepared)

