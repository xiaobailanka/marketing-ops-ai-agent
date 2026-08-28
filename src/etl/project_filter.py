"""项目与日期过滤；比较时规范化，结果值保持原样。"""

from __future__ import annotations

from datetime import date

import pandas as pd

from src.models.project import ProjectConfig


def filter_project_date(
    frame: pd.DataFrame,
    project: ProjectConfig,
    report_date: date | None = None,
) -> pd.DataFrame:
    if frame.empty:
        return frame.copy()
    required = {"Country", "Project Name"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"项目过滤缺少字段: {', '.join(sorted(missing))}")
    country = frame["Country"].astype(str).str.strip().str.upper()
    project_name = frame["Project Name"].astype(str).str.strip().str.casefold()
    mask = (country == project.country) & (project_name == project.project_name.casefold())
    if report_date is not None:
        if "Date" not in frame.columns:
            raise ValueError("日期过滤缺少 Date 字段")
        dates = pd.to_datetime(frame["Date"], errors="coerce").dt.date
        mask &= dates == report_date
    return frame.loc[mask].copy()

