"""日报 Plotly 图表。"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def cumulative_spend_chart(frame: pd.DataFrame) -> go.Figure:
    figure = go.Figure()
    figure.add_trace(go.Scatter(x=frame["Date"], y=frame["Cumulative Spend"], name="Cumulative Spend", line={"color": "#2563eb", "width": 3}))
    figure.add_trace(go.Scatter(x=frame["Date"], y=frame["Total Budget"], name="Total Budget", line={"color": "#ef4444", "dash": "dash"}))
    figure.update_layout(template="plotly_white", height=360, margin={"l": 10, "r": 10, "t": 40, "b": 10}, legend_orientation="h")
    return figure


def impression_chart(frame: pd.DataFrame) -> go.Figure:
    figure = px.line(frame.tail(14), x="Date", y="Impression", markers=True, color_discrete_sequence=["#0f766e"])
    figure.update_layout(template="plotly_white", height=330, margin={"l": 10, "r": 10, "t": 40, "b": 10})
    return figure


def platform_chart(frame: pd.DataFrame) -> go.Figure:
    figure = px.bar(frame, x="Platform", y=["Spend", "Impression"], barmode="group", color_discrete_sequence=["#2563eb", "#7c3aed"])
    figure.update_layout(template="plotly_white", height=350, margin={"l": 10, "r": 10, "t": 40, "b": 10})
    return figure
