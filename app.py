"""Marketing Ops AI Agent Overview。"""

from __future__ import annotations

import streamlit as st

from src.ui.layout import page_header, sandbox_banner, setup_page
from src.ui.state import get_facade

setup_page("Overview", "📈")
facade = get_facade()
page_header(
    "Advertising Data Automation & QC",
    "Clean data, generate daily insights, synchronize FIFA records, and validate Google Ads builds.",
    "Operations Workspace",
)
sandbox_banner()

action_left, action_middle, action_right = st.columns([1, 1, 3])
with action_left:
    if st.button("▶ Open Workspace", type="primary", width="stretch"):
        st.session_state["workspace_started"] = True
        st.success("Workspace initialized. Start with Data Cleaning.")
with action_middle:
    uploaded = st.file_uploader("Upload Your Data", type=["xlsx", "xls"], label_visibility="collapsed")
    if uploaded:
        st.session_state["overview_upload"] = uploaded.getvalue()
        st.info("File loaded for this session. Open Data Cleaning to process it.")
with action_right:
    if st.button("Reset Workspace", width="content"):
        facade.reset_workspace()
        st.success("Current workspace session was reset.")
        st.rerun()

stats = facade.overview_stats()
columns = st.columns(4)
columns[0].metric("Source Records", f"{stats['source_rows']:,}", "computed from workbook")
columns[1].metric("Projects", stats["projects"], "UG · SN · PK")
columns[2].metric("QC Pass Rate", f"{stats['qc_pass_rate']:.0%}", "field-level checks")
columns[3].metric("Recent Tasks", stats["recent_tasks"], "this session")

st.subheader("Operational Workflow")
flow = st.columns(4)
with flow[0]:
    with st.container(border=True):
        st.markdown("### 1 · Clean")
        st.caption("Inspect dirty rows and audit every correction.")
        st.page_link("pages/1_Data_Cleaning.py", label="Open Data Cleaning →")
with flow[1]:
    with st.container(border=True):
        st.markdown("### 2 · Report")
        st.caption("Review KPIs, pacing, audiences and creatives.")
        st.page_link("pages/2_Daily_Report.py", label="Open Daily Report →")
with flow[2]:
    with st.container(border=True):
        st.markdown("### 3 · Sync")
        st.caption("See deterministic insert, update and skip behavior.")
        st.page_link("pages/3_FIFA_Dashboard_Sync.py", label="Open FIFA Sync →")
with flow[3]:
    with st.container(border=True):
        st.markdown("### 4 · QC")
        st.caption("Confirm mapping and investigate strict QC errors.")
        st.page_link("pages/4_Google_Ads_QC.py", label="Open Google Ads QC →")

st.subheader("Platform Capabilities")
left, right = st.columns(2)
with left:
    st.markdown(
        """
        - Deterministic Python ETL, KPI and Rule Engine
        - Replaceable Sandbox/External API Connectors
        - Session-isolated public operations
        - Idempotent Google Sheets and Feishu workflows
        """
    )
with right:
    st.markdown(
        """
        - Human-confirmed variable Media Plan mapping
        - Read-only Google Ads QC with PASS/WARNING/ERROR
        - LLM explains facts but never calculates metrics
        - No customer credentials or customer data in the repository
        """
    )
