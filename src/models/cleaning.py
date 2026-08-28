"""数据清洗结果与审计模型。"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel

if TYPE_CHECKING:
    import pandas as pd


class CleaningAuditEntry(BaseModel):
    row_number: int
    field: str
    original_value: Any = None
    new_value: Any = None
    rule: str
    timestamp: datetime


class CleaningSummary(BaseModel):
    input_rows: int = 0
    filtered_rows: int = 0
    removed_total_rows: int = 0
    removed_zero_impression_rows: int = 0
    funnel_filled: int = 0
    funnel_corrected: int = 0
    duplicates_found: int = 0
    validation_warnings: int = 0
    final_clean_rows: int = 0


@dataclass(slots=True)
class CleaningResult:
    """DataFrame 与结构化元数据一起返回，避免页面解析日志文本。"""

    before: "pd.DataFrame"
    after: "pd.DataFrame"
    summary: CleaningSummary
    audit_log: list[CleaningAuditEntry] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

