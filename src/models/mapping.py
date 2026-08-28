"""Human-in-the-loop Schema Mapping 模型。"""

from __future__ import annotations

from pydantic import BaseModel, Field


class MappingEntry(BaseModel):
    source_column: str
    canonical_field: str
    confidence: float = Field(ge=0, le=1)
    confirmed: bool = False
    source_sheet: str = ""


class MediaPlanInspection(BaseModel):
    detected_sheets: list[str]
    selected_sheet: str
    header_row: int
    mappings: list[MappingEntry]

