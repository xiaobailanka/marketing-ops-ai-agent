"""GTM Data Cleaning 页面。"""

from __future__ import annotations

from datetime import date
from io import BytesIO

import pandas as pd
import streamlit as st

from src.ui.dataframe import excel_bytes, safe_display_frame
from src.ui.layout import page_header, sandbox_banner, setup_page
from src.ui.state import get_facade

setup_page("Data Cleaning", "🧹")
facade = get_facade()
page_header("Data Cleaning", "Upload raw Excel or process the included GTM workbook through the auditable cleaning engine.")
sandbox_banner()

project_names = [f"{item.country} · {item.project_name}" for item in facade.config.projects]
controls = st.columns([1.3, 1, 1, 1])
with controls[0]:
    selection = st.selectbox("Project", project_names)
with controls[1]:
    report_date = st.date_input("Report Date", value=date(2026, 8, 26))
with controls[2]:
    uploaded = st.file_uploader("Raw Excel", type=["xlsx", "xls"])
with controls[3]:
    st.write("")
    st.write("")
    run = st.button("Run Cleaning", type="primary", width="stretch")

if run:
    project = facade.config.projects[project_names.index(selection)]
    source = BytesIO(uploaded.getvalue()) if uploaded else None
    try:
        with st.spinner("Filtering and cleaning selected platform sheets..."):
            st.session_state["cleaning_result"] = facade.run_cleaning(project, report_date, source)
        st.success("Cleaning completed.")
    except Exception as exc:
        st.error(f"Cleaning failed: {exc}")

result = st.session_state.get("cleaning_result")
if result:
    summary = result.summary
    labels = [
        ("Input Rows", summary.input_rows), ("Filtered Rows", summary.filtered_rows),
        ("Removed Total", summary.removed_total_rows), ("Removed Zero-Impression", summary.removed_zero_impression_rows),
        ("Funnel Filled", summary.funnel_filled), ("Funnel Corrected", summary.funnel_corrected),
        ("Duplicates", summary.duplicates_found), ("Warnings", summary.validation_warnings),
        ("Final Rows", summary.final_clean_rows),
    ]
    for start in range(0, len(labels), 5):
        metric_columns = st.columns(min(5, len(labels) - start))
        for column, (label, value) in zip(metric_columns, labels[start : start + 5], strict=True):
            column.metric(label, value)

    tabs = st.tabs(["Preview Before", "Preview After", "Cleaning Log", "Validation Warnings"])
    with tabs[0]:
        st.dataframe(safe_display_frame(result.before.head(200)), width="stretch", hide_index=True)
    with tabs[1]:
        st.dataframe(safe_display_frame(result.after.head(500)), width="stretch", hide_index=True)
    with tabs[2]:
        audit = pd.DataFrame([item.model_dump(mode="json") for item in result.audit_log])
        st.dataframe(safe_display_frame(audit), width="stretch", hide_index=True)
    with tabs[3]:
        if result.warnings:
            for warning in result.warnings:
                st.warning(warning)
        else:
            st.success("No validation warnings.")
    audit_frame = pd.DataFrame([item.model_dump(mode="json") for item in result.audit_log])
    st.download_button(
        "Download Clean Data",
        excel_bytes({"Clean Data": result.after, "Audit Log": audit_frame}),
        file_name=f"clean_data_{report_date.isoformat()}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
else:
    st.info("Select a project and run cleaning. The included workbook contains missing funnels, incorrect funnels, duplicates, zero-impression rows and mixed numeric types for validation.")
