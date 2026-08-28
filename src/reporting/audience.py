"""Audience 表现聚合与小样本保护。"""

from __future__ import annotations

import pandas as pd

from src.reporting.kpi import add_derived_metrics, aggregate_totals


def analyze_audiences(
    frame: pd.DataFrame,
    min_impressions: float = 1000,
    min_spend_usd: float = 10,
) -> pd.DataFrame:
    if frame.empty or "Audience Name" not in frame.columns:
        return pd.DataFrame()
    groups = [column for column in ["Country", "Project Name", "Audience Name"] if column in frame.columns]
    result = add_derived_metrics(aggregate_totals(frame, groups))
    eligible = (result["Impression"] >= min_impressions) | (result["Spend"] >= min_spend_usd)
    result["Sample Status"] = eligible.map({True: "Sufficient", False: "Insufficient Sample"})
    result["Performance Flag"] = ""
    if eligible.any():
        eligible_rows = result.loc[eligible]
        top_index = eligible_rows["CTR"].fillna(-1).idxmax()
        bottom_index = eligible_rows["CTR"].fillna(float("inf")).idxmin()
        result.loc[top_index, "Performance Flag"] = "Top Audience / High CTR"
        if bottom_index != top_index:
            result.loc[bottom_index, "Performance Flag"] = "Bottom Audience"
        project_cpm = eligible_rows["CPM"].dropna().mean()
        if pd.notna(project_cpm):
            high_cpm = eligible & result["CPM"].gt(project_cpm * 1.2)
            result.loc[high_cpm, "Performance Flag"] = result.loc[high_cpm, "Performance Flag"].map(
                lambda value: f"{value}; High CPM".strip("; ")
            )
    return result.sort_values(["Sample Status", "Spend"], ascending=[False, False]).reset_index(drop=True)

