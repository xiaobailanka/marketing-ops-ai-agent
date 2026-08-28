"""可变 Media Plan 解析。"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.models.mapping import MappingEntry, MediaPlanInspection
from src.qc.schema_mapper import map_headers
from src.qc.sheet_detector import detect_media_plan_sheet


class MediaPlanParser:
    def inspect(self, source: str | Path) -> MediaPlanInspection:
        excel = pd.ExcelFile(source)
        selected, header_index, headers = detect_media_plan_sheet(source)
        return MediaPlanInspection(
            detected_sheets=excel.sheet_names,
            selected_sheet=selected,
            header_row=header_index + 1,
            mappings=map_headers(headers, selected),
        )

    def parse(
        self,
        source: str | Path,
        mappings: list[MappingEntry],
        confirmed: bool,
        sheet_name: str,
        header_row: int,
    ) -> pd.DataFrame:
        if not confirmed:
            raise PermissionError("Schema Mapping 必须人工确认后才能运行 QC")
        frame = pd.read_excel(source, sheet_name=sheet_name, header=header_row - 1)
        rename = {item.source_column: item.canonical_field for item in mappings if item.confirmed}
        if not rename:
            raise ValueError("没有已确认的 Schema Mapping")
        return frame.rename(columns=rename)[list(dict.fromkeys(rename.values()))].dropna(how="all")

