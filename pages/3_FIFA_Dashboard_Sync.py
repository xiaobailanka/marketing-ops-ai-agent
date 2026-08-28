"""FIFA Dashboard Sync。"""

from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st

from src.ui.dataframe import safe_display_frame
from src.ui.layout import page_header, sandbox_banner, setup_page
from src.ui.state import get_facade

setup_page("FIFA Dashboard Sync", "🔄")
facade = get_facade()
page_header("FIFA Dashboard Sync", "Scan the shared workspace, clean the target file and perform deterministic Bitable upsert.")
sandbox_banner()

target_date = st.date_input("Target Date", value=date(2026, 8, 26))
buttons = st.columns(4)
if buttons[0].button("Scan Shared Drive", width="stretch"):
    st.session_state["fifa_files"] = facade.scan_fifa_files()
if buttons[1].button("Preview Cleaning", width="stretch"):
    try:
        source, cleaning = facade.preview_fifa(target_date)
        st.session_state["fifa_preview"] = (source, cleaning)
    except Exception as exc:
        st.error(f"Preview failed: {exc}")
if buttons[2].button("Run Sync", type="primary", width="stretch"):
    try:
        st.session_state["fifa_sync_result"] = facade.run_fifa_sync(target_date)
        st.success("FIFA sync completed.")
    except Exception as exc:
        st.error(f"Sync failed: {exc}")
show_changes = buttons[3].toggle("View Changes", value=True)

files = st.session_state.get("fifa_files") or facade.scan_fifa_files()
latest = max(files) if files else None
meta = st.columns(3)
meta[0].metric("Latest File Detected", files[latest].name if latest else "N/A")
meta[1].metric("Target Date", target_date.isoformat())
meta[2].metric("Files Available", len(files))

preview = st.session_state.get("fifa_preview")
if preview:
    source, cleaning = preview
    st.caption(f"Preview source: {source.name}")
    summary = cleaning.summary
    metrics = st.columns(5)
    metrics[0].metric("Input Rows", summary.input_rows)
    metrics[1].metric("Rows Removed", summary.input_rows - summary.final_clean_rows)
    metrics[2].metric("Rows Corrected", summary.funnel_filled + summary.funnel_corrected)
    metrics[3].metric("Duplicates", summary.duplicates_found)
    metrics[4].metric("Final Rows", summary.final_clean_rows)
    st.dataframe(safe_display_frame(cleaning.after.head(100)), width="stretch", hide_index=True)

sync = st.session_state.get("fifa_sync_result")
if sync:
    result = sync.upsert
    metrics = st.columns(5)
    metrics[0].metric("Rows Inserted", result.inserted)
    metrics[1].metric("Rows Updated", result.updated)
    metrics[2].metric("Rows Skipped", result.skipped)
    metrics[3].metric("Errors", result.errors)
    metrics[4].metric("Sync Status", "SUCCESS" if result.errors == 0 else "WARNING")
    if show_changes:
        st.subheader("Changes")
        st.dataframe(pd.DataFrame(result.changes), width="stretch", hide_index=True)
    st.caption("Run Sync again with the same file to verify idempotency. The current visitor's Sandbox Bitable is isolated in Session State.")
