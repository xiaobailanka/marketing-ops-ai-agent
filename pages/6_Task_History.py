"""Task History 页面。"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from src.ui.dataframe import safe_display_frame
from src.ui.layout import page_header, sandbox_banner, setup_page
from src.ui.state import get_facade

setup_page("Task History", "🕘")
facade = get_facade()
page_header("Task History", "Session-scoped execution history for cleaning, reporting, FIFA sync and Ads QC.")
sandbox_banner()

failed_only = st.toggle("Failed tasks only", value=False)
tasks = facade.repository.list_tasks(failed_only=failed_only)
if tasks:
    frame = pd.DataFrame([item.model_dump(mode="json") for item in tasks])
    st.dataframe(safe_display_frame(frame), width="stretch", hide_index=True)
    labels = [f"{item.task_type.value} · {item.project or 'N/A'} · {item.status.value} · {item.task_id[:8]}" for item in tasks]
    selected = st.selectbox("Task Detail", labels)
    task = tasks[labels.index(selected)]
    st.json(task.model_dump(mode="json"))
    tabs = st.tabs(["Cleaning Audit", "QC History"])
    with tabs[0]:
        result = st.session_state.get("cleaning_result")
        if result:
            st.dataframe(pd.DataFrame([entry.model_dump(mode="json") for entry in result.audit_log]), width="stretch")
        else:
            st.caption("No cleaning audit is cached in this session.")
    with tabs[1]:
        qc = st.session_state.get("qc_result")
        if qc:
            st.dataframe(pd.DataFrame([item.model_dump(mode="json") for item in qc.results]), width="stretch")
        else:
            st.caption("No QC run is cached in this session.")
else:
    st.info("No tasks in this session yet. Run a workflow from another page.")
