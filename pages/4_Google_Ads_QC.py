"""Google Ads QC Workflow。"""

from __future__ import annotations

from io import BytesIO

import pandas as pd
import streamlit as st

from src.ui.dataframe import excel_bytes, safe_display_frame
from src.ui.layout import page_header, sandbox_banner, setup_page
from src.ui.state import get_facade

setup_page("Google Ads QC", "✅")
facade = get_facade()
page_header("Google Ads QC", "Human-confirmed Media Plan mapping and strict read-only validation for GDN, VRC and VVC.")
sandbox_banner()

source_mode = st.radio("Media Plan Source", ["Sample Media Plan", "Upload Media Plan"], horizontal=True)
uploaded = st.file_uploader("Upload Media Plan", type=["xlsx", "xls"], disabled=source_mode == "Sample Media Plan")
detect = st.button("1 · Detect Sheets & Schema", type="primary")
if detect:
    try:
        source_bytes = (
            facade.paths["media_plan"].read_bytes()
            if source_mode == "Sample Media Plan"
            else uploaded.getvalue() if uploaded else None
        )
        if not source_bytes:
            raise ValueError("Please upload a Media Plan first.")
        inspection = facade.inspect_media_plan(BytesIO(source_bytes))
        st.session_state["qc_source_bytes"] = source_bytes
        st.session_state["qc_inspection"] = inspection
        st.session_state["mapping_confirmed"] = False
        st.success(f"Detected {inspection.selected_sheet}, header row {inspection.header_row}.")
    except Exception as exc:
        st.error(f"Detection failed: {exc}")

inspection = st.session_state.get("qc_inspection")
if inspection:
    st.markdown("### 2 · Review Schema Mapping")
    st.caption(f"Detected sheets: {', '.join(inspection.detected_sheets)}")
    mapping_frame = pd.DataFrame([item.model_dump() for item in inspection.mappings])
    st.dataframe(mapping_frame[["source_column", "canonical_field", "confidence"]], width="stretch", hide_index=True)
    low_confidence = mapping_frame["confidence"].lt(0.85).sum() if not mapping_frame.empty else 0
    if low_confidence:
        st.warning(f"{low_confidence} low-confidence mappings require special attention.")
    if st.button("Confirm Mapping"):
        inspection.mappings = [item.model_copy(update={"confirmed": True}) for item in inspection.mappings]
        st.session_state["qc_inspection"] = inspection
        st.session_state["mapping_confirmed"] = True
        st.success("Mapping confirmed. QC is now enabled.")

st.markdown("### 3 · Load Google Ads Data & Run QC")
mapping_confirmed = bool(st.session_state.get("mapping_confirmed"))
if st.button("Run QC", type="primary", disabled=not mapping_confirmed):
    try:
        inspection = st.session_state["qc_inspection"]
        parsed = facade.parse_media_plan(
            BytesIO(st.session_state["qc_source_bytes"]),
            inspection,
            True,
        )
        plans = parsed.astype(object).where(pd.notnull(parsed), None).to_dict(orient="records")
        st.session_state["qc_result"] = facade.run_ads_qc(plans)
        st.success("Read-only Google Ads QC completed.")
    except Exception as exc:
        st.error(f"QC failed: {exc}")

qc = st.session_state.get("qc_result")
if qc:
    summary = st.columns(4)
    summary[0].metric("Objects Checked", qc.objects_checked)
    summary[1].metric("PASS", qc.passed)
    summary[2].metric("WARNING", qc.warnings)
    summary[3].metric("ERROR", qc.errors)
    result_frame = pd.DataFrame([item.model_dump(mode="json") for item in qc.results])
    result_frame.columns = [column.replace("_", " ").title() for column in result_frame.columns]
    filter_left, filter_mid, filter_right = st.columns([1, 1, 2])
    levels = filter_left.multiselect("Level", ["PASS", "WARNING", "ERROR"], default=["WARNING", "ERROR"])
    object_level = filter_mid.multiselect("Object Level", sorted(result_frame["Object Level"].unique()))
    search = filter_right.text_input("Search object or field")
    filtered = result_frame[result_frame["Level"].isin(levels)] if levels else result_frame
    if object_level:
        filtered = filtered[filtered["Object Level"].isin(object_level)]
    if search:
        mask = filtered.astype(str).apply(lambda column: column.str.contains(search, case=False, na=False)).any(axis=1)
        filtered = filtered[mask]
    st.dataframe(safe_display_frame(filtered), width="stretch", hide_index=True)

    detail_rows = filtered[filtered["Level"].isin(["WARNING", "ERROR"])]
    if not detail_rows.empty:
        st.markdown("### Error Detail")
        labels = [f"{row['Level']} · {row['Object Name']} · {row['Field']}" for _, row in detail_rows.iterrows()]
        selected = st.selectbox("Select result", labels)
        row = detail_rows.iloc[labels.index(selected)]
        detail_columns = st.columns(2)
        detail_columns[0].json({
            "Media Plan Source": row["Plan Value"],
            "Canonical Plan Value": row["Canonical Plan Value"],
            "Rule": row["Rule"],
        })
        detail_columns[1].json({
            "Google Ads Source": row["Ads Value"],
            "Canonical Ads Value": row["Canonical Ads Value"],
            "Reason": row["Explanation"],
            "Suggested Fix": row["Suggested Action"],
        })
    st.download_button(
        "Export QC Excel",
        excel_bytes({"QC Results": result_frame}),
        file_name="google_ads_qc_report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
else:
    st.info("Detect the Media Plan and explicitly confirm the mapping before running QC. Google Ads access remains read-only for both Sandbox and External connectors.")
