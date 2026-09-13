"""避免 NaN/Infinity 直接显示。"""

from __future__ import annotations

import math
from io import BytesIO

import pandas as pd
import streamlit as st

from src.ui.theme import COLORS


def display_dataframe(frame: pd.DataFrame, **kwargs):
    """Style read-only views only; original data and export values are untouched."""
    def stripe(row):
        background = COLORS["canvas"] if frame.index.get_loc(row.name) % 2 else COLORS["surface"]
        return [f"background-color: {background}; color: {COLORS['ink']}"] * len(row)

    styled = frame.style.apply(stripe, axis=1) if frame.index.is_unique else frame.style
    columns = {name: str(name).upper() for name in frame.columns}
    columns.update(kwargs.pop("column_config", {}) or {})
    kwargs["column_config"] = columns
    return st.dataframe(styled, **kwargs)


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
