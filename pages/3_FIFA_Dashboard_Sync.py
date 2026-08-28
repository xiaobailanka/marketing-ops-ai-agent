"""FIFA Dashboard 幂等同步工作台。"""

from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st

from src.ui.components import empty_state, kpi_grid, page_header, sandbox_notice, section_header, workflow_stepper
from src.ui.dataframe import safe_display_frame
from src.ui.layout import setup_page
from src.ui.state import get_facade


setup_page("FIFA Dashboard Sync", ":material/sync_alt:")
facade = get_facade()
page_header(
    "FIFA dashboard sync",
    "Scan the shared workspace, validate the target file and perform deterministic idempotent Bitable upsert.",
    "Assurance",
    "Sandbox Bitable · Session isolated",
)
sandbox_notice("Shared-drive sample files · Deterministic business key")

sync = st.session_state.get("fifa_sync_result")
preview = st.session_state.get("fifa_preview")
active_step = 2 if sync else 1 if preview else 0
workflow_stepper(("Select source", "Preview cleaning", "Review sync"), active_step)

section_header("Sync controls", "Select the target date, inspect the latest available file and run the upsert only when the source is ready.")
with st.container(border=True):
    target_column, scan_column, preview_column, sync_column = st.columns([1.1, .9, .9, .9], vertical_alignment="bottom")
    with target_column:
        target_date = st.date_input("Target date", value=date(2026, 8, 26))
    with scan_column:
        scan = st.button("Scan workspace", width="stretch")
    with preview_column:
        run_preview = st.button("Preview cleaning", width="stretch")
    with sync_column:
        run_sync = st.button("Run sync", type="primary", width="stretch")

if scan:
    st.session_state["fifa_files"] = facade.scan_fifa_files()
    st.success("Workspace scan completed.")

if run_preview:
    try:
        with st.spinner("Loading the target file and evaluating cleaning rules..."):
            source, cleaning = facade.preview_fifa(target_date)
            st.session_state["fifa_preview"] = (source, cleaning)
        st.success("Preview is ready. Review row counts before synchronization.")
    except Exception as exc:
        st.error(f"Preview failed. Confirm that a file exists for the selected date. Detail: {exc}")

if run_sync:
    try:
        with st.spinner("Cleaning the target file and applying idempotent upsert..."):
            st.session_state["fifa_sync_result"] = facade.run_fifa_sync(target_date)
        st.success("FIFA synchronization completed. The result is recorded in this session's task history.")
    except Exception as exc:
        st.error(f"Synchronization failed. Review the target date and source file. Detail: {exc}")

files = st.session_state.get("fifa_files") or facade.scan_fifa_files()
latest = max(files) if files else None
latest_name = files[latest].name if latest else "Not available"
date_ready = target_date in files
section_header("Source readiness", "Current shared-workspace inventory and selected-date availability.")
kpi_grid(
    [
        {"label": "Latest file", "value": latest.isoformat() if latest else "N/A", "badge": "Detected" if latest else "Missing", "tone": "success" if latest else "error", "meta": latest_name},
        {"label": "Target date", "value": target_date.isoformat(), "badge": "Ready" if date_ready else "Unavailable", "tone": "success" if date_ready else "warning", "meta": "Exact-date selection"},
        {"label": "Files available", "value": f"{len(files):02d}", "badge": "Workspace", "tone": "neutral", "meta": "Date-keyed source files"},
        {"label": "Connector mode", "value": "Sandbox", "badge": "Isolated", "tone": "success", "meta": "No external record mutation"},
    ]
)

preview = st.session_state.get("fifa_preview")
if preview:
    source, cleaning = preview
    summary = cleaning.summary
    section_header("Cleaning preview", "Rows and corrections that will be supplied to the upsert service.", source.name)
    kpi_grid(
        [
            {"label": "Input rows", "value": f"{summary.input_rows:,}", "badge": "Source", "tone": "neutral"},
            {"label": "Rows removed", "value": f"{summary.input_rows - summary.final_clean_rows:,}", "badge": "Rules", "tone": "neutral"},
            {"label": "Rows corrected", "value": f"{summary.funnel_filled + summary.funnel_corrected:,}", "badge": "Audited", "tone": "success"},
            {"label": "Duplicates", "value": f"{summary.duplicates_found:,}", "badge": "Review" if summary.duplicates_found else "Clear", "tone": "warning" if summary.duplicates_found else "success"},
            {"label": "Final rows", "value": f"{summary.final_clean_rows:,}", "badge": "Ready", "tone": "success"},
        ],
        columns=5,
    )
    st.dataframe(safe_display_frame(cleaning.after.head(100)), width="stretch", hide_index=True)

sync = st.session_state.get("fifa_sync_result")
if sync:
    result = sync.upsert
    section_header("Synchronization result", "Inserted, updated and skipped records are determined by the stable business key.")
    kpi_grid(
        [
            {"label": "Rows inserted", "value": f"{result.inserted:,}", "badge": "New", "tone": "success"},
            {"label": "Rows updated", "value": f"{result.updated:,}", "badge": "Changed", "tone": "warning" if result.updated else "neutral"},
            {"label": "Rows skipped", "value": f"{result.skipped:,}", "badge": "Idempotent", "tone": "success"},
            {"label": "Errors", "value": f"{result.errors:,}", "badge": "Clear" if result.errors == 0 else "Blocked", "tone": "success" if result.errors == 0 else "error"},
            {"label": "Sync status", "value": "Healthy" if result.errors == 0 else "Review", "badge": "Complete", "tone": "success" if result.errors == 0 else "warning"},
        ],
        columns=5,
    )
    with st.expander("View change audit", expanded=True):
        if result.changes:
            st.dataframe(pd.DataFrame(result.changes), width="stretch", hide_index=True)
        else:
            empty_state("No record changes", "Every business key and canonical value already matched the current sandbox table.", "OK")
    st.caption("Run synchronization again with the same file to verify idempotency. The visitor's sandbox table remains isolated in Session State.")
elif not preview:
    empty_state(
        "Ready to validate the next shared-drive file",
        "Preview the selected date before synchronization. This confirms cleaning output without writing any sandbox records.",
        "03",
    )
