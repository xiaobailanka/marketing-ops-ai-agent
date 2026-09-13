"""任务活动与审计工作台。"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from src.ui.dataframe import display_dataframe

from src.models.task import TaskStatus
from src.ui.components import empty_state, kpi_grid, page_header, sandbox_notice, section_header
from src.ui.dataframe import safe_display_frame
from src.ui.layout import setup_page
from src.ui.state import get_facade


setup_page("Activity & Audit", ":material/history:")
facade = get_facade()
with st.container(key="page_intro"):
    page_header(
        "Activity & audit",
        "Trace session-scoped cleaning, reporting, synchronization and quality-control executions from summary to row-level evidence.",
        "System",
        "Session repository",
    )
    sandbox_notice("Execution history belongs only to the current browser session")

all_tasks = facade.repository.list_tasks()
status_counts = {status: sum(task.status == status for task in all_tasks) for status in TaskStatus}
section_header("Execution posture", "Current task outcomes recorded by the application task runner.")
kpi_grid(
    [
        {"label": "Total tasks", "value": f"{len(all_tasks):02d}", "badge": "Session", "tone": "neutral"},
        {"label": "Successful", "value": f"{status_counts[TaskStatus.SUCCESS]:02d}", "badge": "SUCCESS", "tone": "success"},
        {"label": "Warnings", "value": f"{status_counts[TaskStatus.WARNING]:02d}", "badge": "WARNING", "tone": "warning"},
        {"label": "Failed", "value": f"{status_counts[TaskStatus.FAILED]:02d}", "badge": "FAILED", "tone": "error" if status_counts[TaskStatus.FAILED] else "success"},
    ]
)

section_header("Task register", "Filter the current session and select an execution for its full evidence trail.")
with st.container(border=True, key="panel_6_Task_History_1"):
    filter_column, scope_column = st.columns([1, 3], vertical_alignment="center")
    failed_only = filter_column.toggle("Failed tasks only", value=False)
    scope_column.caption("Task records include timestamps, row counts, warning/error totals and the service-generated summary.")

tasks = facade.repository.list_tasks(failed_only=failed_only)
if tasks:
    frame = pd.DataFrame([item.model_dump(mode="json") for item in tasks])
    ordered = [
        "started_at", "task_type", "project", "status", "input_rows", "output_rows", "warnings", "errors", "summary", "task_id"
    ]
    display_columns = [column for column in ordered if column in frame.columns]
    display_dataframe(safe_display_frame(frame[display_columns]), width="stretch", hide_index=True)

    labels = [f"{item.task_type.value} · {item.project or 'N/A'} · {item.status.value} · {item.task_id[:8]}" for item in tasks]
    selected = st.selectbox("Task detail", labels)
    task = tasks[labels.index(selected)]
    section_header("Selected execution", "Structured task metadata and any cached operational evidence.", task.task_id[:8])
    kpi_grid(
        [
            {"label": "Status", "value": task.status.value.title(), "badge": "Recorded", "tone": "success" if task.status == TaskStatus.SUCCESS else "warning" if task.status == TaskStatus.WARNING else "error"},
            {"label": "Input rows", "value": f"{task.input_rows:,}", "badge": "Source", "tone": "neutral"},
            {"label": "Output rows", "value": f"{task.output_rows:,}", "badge": "Result", "tone": "success"},
            {"label": "Exceptions", "value": f"{task.warnings + task.errors:,}", "badge": "Review", "tone": "warning" if task.warnings + task.errors else "success"},
        ]
    )
    with st.expander("View full task metadata"):
        st.json(task.model_dump(mode="json"))

    tabs = st.tabs(["Cleaning audit", "QC history"])
    with tabs[0]:
        result = st.session_state.get("cleaning_result")
        if result:
            display_dataframe(pd.DataFrame([entry.model_dump(mode="json") for entry in result.audit_log]), width="stretch", hide_index=True)
        else:
            empty_state("No cleaning audit cached", "Run Data Cleaning in this session to expose row-level corrections here.", "AUDIT")
    with tabs[1]:
        qc = st.session_state.get("qc_result")
        if qc:
            display_dataframe(pd.DataFrame([item.model_dump(mode="json") for item in qc.results]), width="stretch", hide_index=True)
        else:
            empty_state("No QC evidence cached", "Run Google Ads QC in this session to review its field-level findings here.", "QC")
else:
    empty_state(
        "No matching task activity",
        "Run a workflow from Data Cleaning, Daily Report, FIFA Sync or Google Ads QC. Its execution record will appear here automatically.",
        "06",
    )
