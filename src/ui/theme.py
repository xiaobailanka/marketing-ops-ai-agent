"""Marketing Operations 的统一视觉主题与 Plotly 样式。"""

from __future__ import annotations

from pathlib import Path

import streamlit as st


COLORS = {
    "accent": "#10B981",
    "nav": "#FFFFFF",
    "nav_active": "#ECFDF5",
    "primary": "#047857",
    "primary_hover": "#065F46",
    "primary_soft": "#ECFDF5",
    "canvas": "#F8FAFC",
    "surface": "#FFFFFF",
    "ink": "#0F172A",
    "muted": "#64748B",
    "border": "#E2E8F0",
    "success": "#047857",
    "success_soft": "#ECFDF5",
    "warning": "#925F16",
    "warning_soft": "#FFF4DE",
    "error": "#B23D48",
    "error_soft": "#FCEDEF",
    "neutral_soft": "#F1F5F9",
}

CHART_COLORS = ["#047857", "#10B981", "#6EE7B7", "#B58B4C", "#64748B", "#B23D48"]

PLOTLY_LAYOUT = {
    "font": {"family": "Segoe UI, sans-serif", "color": COLORS["ink"], "size": 12},
    "paper_bgcolor": COLORS["surface"],
    "plot_bgcolor": COLORS["surface"],
    "hoverlabel": {
        "bgcolor": COLORS["ink"],
        "bordercolor": COLORS["ink"],
        "font": {"color": "#FFFFFF", "family": "Segoe UI, sans-serif"},
    },
    "xaxis": {
        "gridcolor": "#F1F5F9",
        "linecolor": COLORS["border"],
        "zerolinecolor": COLORS["border"],
        "title": {"font": {"color": COLORS["muted"]}},
    },
    "yaxis": {
        "gridcolor": "#F1F5F9",
        "linecolor": COLORS["border"],
        "zerolinecolor": COLORS["border"],
        "title": {"font": {"color": COLORS["muted"]}},
    },
    "legend": {
        "orientation": "h",
        "yanchor": "bottom",
        "y": 1.02,
        "xanchor": "right",
        "x": 1,
        "font": {"size": 11, "color": COLORS["muted"]},
    },
}


# Native widget colors are adapted in .streamlit/config.toml.
_TOKEN_CSS = ":root {" + "".join(
    f"--mops-{name.replace('_', '-')}: {value};" for name, value in COLORS.items()
) + "}"
GLOBAL_CSS = "<style>" + _TOKEN_CSS + Path(__file__).with_name("workspace.css").read_text(encoding="utf-8") + "</style>"


def inject_theme() -> None:
    """Inject shared presentation without modifying application behavior."""
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
