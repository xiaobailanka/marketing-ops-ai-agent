"""Creative 表现聚合与标记。"""

from __future__ import annotations

import pandas as pd

from src.reporting.kpi import add_derived_metrics, aggregate_totals


def analyze_creatives(
    frame: pd.DataFrame,
    min_impressions: float = 1000,
    min_spend_usd: float = 10,
) -> pd.DataFrame:
    if frame.empty or "Creative Name" not in frame.columns:
        return pd.DataFrame()
    result = add_derived_metrics(aggregate_totals(frame, ["Creative Name"]))
    eligible = (result["Impression"] >= min_impressions) | (result["Spend"] >= min_spend_usd)
    result["Sample Status"] = eligible.map({True: "Sufficient", False: "Insufficient Sample"})
    result["Performance Flag"] = ""
    if eligible.any():
        eligible_rows = result.loc[eligible]
        top_index = eligible_rows["CTR"].fillna(-1).idxmax()
        result.loc[top_index, "Performance Flag"] = "Top Creative"
        average_ctr = eligible_rows["CTR"].dropna().mean()
        average_cpm = eligible_rows["CPM"].dropna().mean()
        if pd.notna(average_ctr):
            low_response = eligible & result["CTR"].lt(average_ctr * 0.8)
            result.loc[low_response, "Performance Flag"] = "Low CTR Creative"
        if pd.notna(average_cpm):
            high_cpm = eligible & result["CPM"].gt(average_cpm * 1.2)
            result.loc[high_cpm, "Performance Flag"] = result.loc[high_cpm, "Performance Flag"].map(
                lambda value: f"{value}; High CPM".strip("; ")
            )
    return result.sort_values("Spend", ascending=False).reset_index(drop=True)

