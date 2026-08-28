"""按名称与内容结构识别 Media Plan 主 Sheet。"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.qc.header_detector import detect_header_row


def detect_media_plan_sheet(source: str | Path) -> tuple[str, int, list[str]]:
    excel = pd.ExcelFile(source)
    candidates: list[tuple[int, int, str, list[str]]] = []
    for order, sheet_name in enumerate(excel.sheet_names):
        raw = pd.read_excel(excel, sheet_name=sheet_name, header=None, nrows=25)
        try:
            header_index, headers, score = detect_header_row(raw)
        except ValueError:
            continue
        name_bonus = 4 if "media plan" in sheet_name.casefold() else 0
        candidates.append((score + name_bonus, -order, sheet_name, headers + [str(header_index)]))
    if not candidates:
        raise ValueError("没有检测到 Media Plan 数据 Sheet")
    _, _, selected, payload = max(candidates)
    header_index = int(payload[-1])
    return selected, header_index, payload[:-1]

