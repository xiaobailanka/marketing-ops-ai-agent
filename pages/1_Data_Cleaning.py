"""GTM 数据清洗工作台。"""

from __future__ import annotations

from datetime import date
from io import BytesIO

import pandas as pd
import streamlit as st

from src.ui.components import empty_state, kpi_grid, page_header, sandbox_notice, section_header, workflow_stepper
from src.ui.dataframe import excel_bytes, safe_display_frame
from src.ui.layout import setup_page
from src.ui.state import get_facade


setup_page("Data Cleaning", ":material/cleaning_services:")
facade = get_facade()
page_header(
    "Data cleaning",
    "Filter a market workbook, normalize funnel fields and preserve a row-level audit trail for every correction.",
    "Operate",
    "Deterministic ETL · Audited",
)
sandbox_notice("GTM workbook · Session isolated")

workflow_stepper(("Select scope", "Run cleaning", "Review output"), 2 if st.session_state.get("cleaning_result") else 0)
section_header("Source and scope", "Choose the operating market and report date. Uploading a workbook overrides the included sample source.")

project_names = [f"{item.country} · {item.project_name}" for item in facade.config.projects]
with st.container(border=True):
    controls = st.columns([1.25, 1, 1.35, .9], vertical_alignment="bottom")
    with controls[0]:
        selection = st.selectbox("Project", project_names)
    with controls[1]:
        report_date = st.date_input("Report date", value=date(2026, 8, 26))
    with controls[2]:
        uploaded = st.file_uploader("Source workbook", type=["xlsx", "xls"])
    with controls[3]:
        run = st.button("Run cleaning", type="primary", width="stretch")

if run:
    project = facade.config.projects[project_names.index(selection)]
    source = BytesIO(uploaded.getvalue()) if uploaded else None
    try:
        with st.spinner("Filtering platform sheets and applying cleaning rules..."):
            st.session_state["cleaning_result"] = facade.run_cleaning(project, report_date, source)
        st.success("Cleaning completed. Review the correction summary and audit log below.")
    except Exception as exc:
        st.error(f"Cleaning failed. Check the workbook schema and try again. Detail: {exc}")

result = st.session_state.get("cleaning_result")
if result:
    summary = result.summary
    section_header("Processing summary", "Counts reflect the selected project after deterministic filtering and validation.")
    kpi_grid(
        [
            {"label": "Input rows", "value": f"{summary.input_rows:,}", "badge": "Source", "tone": "neutral"},
            {"label": "Filtered rows", "value": f"{summary.filtered_rows:,}", "badge": "Scoped", "tone": "success"},
            {"label": "Removed rows", "value": f"{summary.removed_total_rows:,}", "badge": "Rule based", "tone": "neutral"},
            {"label": "Funnel repaired", "value": f"{summary.funnel_filled + summary.funnel_corrected:,}", "badge": "Audited", "tone": "success"},
            {"label": "Final clean rows", "value": f"{summary.final_clean_rows:,}", "badge": "Ready", "tone": "success"},
        ],
        columns=5,
    )
    kpi_grid(
        [
            {"label": "Zero-impression removed", "value": f"{summary.removed_zero_impression_rows:,}", "meta": "Excluded before reporting"},
            {"label": "Duplicates found", "value": f"{summary.duplicates_found:,}", "badge": "Review", "tone": "warning" if summary.duplicates_found else "success"},
            {"label": "Validation warnings", "value": f"{summary.validation_warnings:,}", "badge": "Review" if summary.validation_warnings else "Clear", "tone": "warning" if summary.validation_warnings else "success"},
            {"label": "Corrections logged", "value": f"{len(result.audit_log):,}", "meta": "Row-level traceability"},
        ],
        columns=4,
    )

    section_header("Data review", "Compare source and cleaned output, then inspect the exact rule applied to each changed row.")
    tabs = st.tabs(["Source preview", "Clean output", "Audit log", "Validation"])
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
            st.success("No validation warnings were produced for this run.")

    audit_frame = pd.DataFrame([item.model_dump(mode="json") for item in result.audit_log])
    download, _ = st.columns([1, 4])
    with download:
        st.download_button(
            "Download clean workbook",
            excel_bytes({"Clean Data": result.after, "Audit Log": audit_frame}),
            file_name=f"clean_data_{report_date.isoformat()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            width="stretch",
        )
else:
    empty_state(
        "Ready to prepare source data",
        "Choose a project and run cleaning. The included workbook contains controlled missing funnels, duplicates, zero-impression rows and mixed numeric types for validating the rules.",
        "01",
    )
