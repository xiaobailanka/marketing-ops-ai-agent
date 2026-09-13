"""Marketing Operations 管理驾驶舱。"""

from __future__ import annotations

from html import escape

import streamlit as st

from src.ui.dataframe import display_dataframe

from src.models.task import TaskStatus, TaskType
from src.ui.charts import quality_posture_chart, source_coverage_chart
from src.ui.components import attention_item, html_table, kpi_grid, page_header, pill, sandbox_notice, section_header
from src.ui.layout import setup_page
from src.ui.state import get_facade


setup_page("Overview", ":material/space_dashboard:")
facade = get_facade()
stats = facade.overview_stats()

with st.container(key="page_intro"):
    header, action = st.columns([5, 1.25], vertical_alignment="bottom")
    with header:
        page_header(
            "Operations overview",
            "Delivery readiness, data quality and workflow status across the active marketing workspace.",
            "Monitor",
            "Runtime status · Healthy",
        )
    with action:
        if st.button("Start daily report", type="primary", width="stretch"):
            st.switch_page("pages/2_Daily_Report.py")

    sandbox_notice(meta=f"Data scope · {' · '.join(stats['markets'])}")

kpi_grid(
    [
        {"label": "Source records", "value": f"{stats['source_rows']:,}", "badge": "Ready", "tone": "success", "meta": "FB · TT · GG source workbooks"},
        {"label": "Active markets", "value": f"{stats['projects']:02d}", "badge": "On track", "tone": "success", "meta": " · ".join(stats["markets"])},
        {"label": "QC pass rate", "value": f"{stats['qc_pass_rate']:.1%}", "badge": f"{stats['qc_passed']} passed", "tone": "success", "meta": "Field-level deterministic checks"},
        {"label": "Open exceptions", "value": f"{stats['open_exceptions']:02d}", "badge": "Needs review", "tone": "warning", "meta": f"{stats['qc_errors']} errors · {stats['qc_warnings']} warning"},
    ]
)

quality_column, attention_column = st.columns([1.6, 1])
with quality_column:
    with st.container(border=True, key="panel_0_Overview_1"):
        section_header("Quality posture", "Canonical media plan versus deployed ad objects.", f"{stats['qc_total']:,} checks")
        st.plotly_chart(
            quality_posture_chart(stats["qc_passed"], stats["qc_warnings"], stats["qc_errors"]),
            width="stretch",
            config={"displayModeBar": False},
        )
with attention_column:
    with st.container(border=True, key="panel_0_Overview_2"):
        section_header("Attention queue", "Items that require an operator decision.", f"{stats['open_exceptions']} open")
        if stats["qc_errors"]:
            attention_item(f"{stats['qc_errors']} blocking QC mismatches", "Review naming, targeting and configuration fields before activation.", "error")
        if stats["qc_warnings"]:
            attention_item(f"{stats['qc_warnings']} value requires review", "Confirm the variance against the approved media plan.", "warning")
        if not stats["open_exceptions"]:
            attention_item("No open quality exceptions", "All current checks meet the confirmed rules.", "success")
        if st.button("Open Google Ads QC", width="stretch"):
            st.switch_page("pages/4_Google_Ads_QC.py")

section_header("Source readiness", "Record coverage by input platform before project filtering.", "Current workbook")
source_chart, source_context = st.columns([1.35, 1])
with source_chart:
    with st.container(border=True, key="panel_0_Overview_3"):
        st.plotly_chart(source_coverage_chart(stats["source_counts"]), width="stretch", config={"displayModeBar": False})
with source_context:
    with st.container(border=True, key="panel_0_Overview_4"):
        section_header("Daily operating sequence", "Use the same traceable path for every reporting cycle.")
        attention_item("1 · Prepare source data", "Filter by market, repair funnel values and review the audit log.", "success")
        attention_item("2 · Review performance", "Generate deterministic KPIs, pacing and anomaly diagnosis.", "success")
        attention_item("3 · Assure downstream quality", "Sync FIFA records and resolve Google Ads exceptions.", "warning")

section_header("Operational workflow", "Latest execution state for the current browser session.", f"{stats['recent_tasks']} session tasks")
latest_by_type = {}
for task in stats["latest_tasks"]:
    latest_by_type.setdefault(task.task_type, task)

workflow_definitions = [
    ("Data cleaning", TaskType.DATA_CLEANING, "Growth Ops"),
    ("Daily performance report", TaskType.DAILY_REPORT, "Growth Ops"),
    ("FIFA dashboard sync", TaskType.FIFA_SYNC, "Data Ops"),
    ("Google Ads quality control", TaskType.ADS_QC, "Media QA"),
]
status_tones = {
    TaskStatus.SUCCESS: "success",
    TaskStatus.WARNING: "warning",
    TaskStatus.FAILED: "error",
    TaskStatus.RUNNING: "neutral",
}
rows = []
for name, task_type, owner in workflow_definitions:
    task = latest_by_type.get(task_type)
    if task:
        latest_run = task.started_at.astimezone().strftime("%Y-%m-%d %H:%M")
        status = pill(task.status.value.title(), status_tones[task.status])
        result = escape(task.summary or "Execution recorded")
    else:
        latest_run = "Not run in this session"
        status = pill("Ready", "neutral")
        result = "Available"
    rows.append((escape(name), escape(latest_run), escape(owner), status, result))

html_table(("Workflow", "Latest run", "Owner", "Status", "Result"), rows)
