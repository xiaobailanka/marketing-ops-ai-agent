"""避免 NaN/Infinity 直接显示。"""

from __future__ import annotations

import math
from io import BytesIO

import pandas as pd


def safe_display_frame(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy().astype(object)
    return result.map(
        lambda value: None
        if (isinstance(value, float) and (math.isnan(value) or math.isinf(value)))
        else value
    )


def excel_bytes(sheets: dict[str, pd.DataFrame]) -> bytes:
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        for name, frame in sheets.items():
            safe_display_frame(frame).to_excel(writer, sheet_name=name[:31], index=False)
    return buffer.getvalue()

