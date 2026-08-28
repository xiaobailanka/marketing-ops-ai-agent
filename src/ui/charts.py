"""日报 Plotly 图表。"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.ui.theme import CHART_COLORS, COLORS, PLOTLY_LAYOUT


def _style(figure: go.Figure, height: int) -> go.Figure:
    figure.update_layout(
        **PLOTLY_LAYOUT,
        height=height,
        margin={"l": 12, "r": 12, "t": 28, "b": 12},
    )
    figure.update_xaxes(showline=False)
    figure.update_yaxes(showline=False)
    return figure


def cumulative_spend_chart(frame: pd.DataFrame) -> go.Figure:
    figure = go.Figure()
    figure.add_trace(
        go.Scatter(
            x=frame["Date"], y=frame["Cumulative Spend"], name="Cumulative spend",
            line={"color": COLORS["primary"], "width": 3}, fill="tozeroy", fillcolor="rgba(22,122,108,.08)",
        )
    )
    figure.add_trace(
        go.Scatter(
            x=frame["Date"], y=frame["Total Budget"], name="Total budget",
            line={"color": "#D29A36", "dash": "dash", "width": 2},
        )
    )
    return _style(figure, 340)


def impression_chart(frame: pd.DataFrame) -> go.Figure:
    figure = px.line(frame.tail(14), x="Date", y="Impression", markers=True, color_discrete_sequence=[COLORS["primary"]])
    figure.update_traces(line={"width": 2.5}, marker={"size": 6})
    return _style(figure, 330)


def platform_chart(frame: pd.DataFrame) -> go.Figure:
    figure = px.bar(
        frame, x="Platform", y=["Spend", "Impression"], barmode="group",
        color_discrete_sequence=[COLORS["primary"], "#8CC8BE"],
    )
    figure.update_traces(marker_line_width=0)
    return _style(figure, 340)


def quality_posture_chart(passed: int, warnings: int, errors: int) -> go.Figure:
    figure = go.Figure()
    values = (("Passed", passed, COLORS["success"]), ("Warnings", warnings, "#D29A36"), ("Errors", errors, COLORS["error"]))
    for label, value, color in values:
        figure.add_trace(
            go.Bar(
                y=["Field-level checks"], x=[value], name=label, orientation="h",
                marker={"color": color}, text=[f"{value:,}" if value else ""], textposition="inside",
            )
        )
    figure.update_layout(barmode="stack", xaxis_title="Checks", yaxis_title=None)
    return _style(figure, 235)


def source_coverage_chart(source_counts: dict[str, int]) -> go.Figure:
    frame = pd.DataFrame({"Source": list(source_counts), "Records": list(source_counts.values())})
    figure = px.bar(frame, x="Source", y="Records", color="Source", color_discrete_sequence=CHART_COLORS[: len(frame)])
    figure.update_traces(marker_line_width=0, texttemplate="%{y:,}", textposition="outside")
    figure.update_layout(showlegend=False)
    return _style(figure, 245)
