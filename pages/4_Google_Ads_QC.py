"""Google Ads 只读质量控制工作台。"""

from __future__ import annotations

from io import BytesIO

import pandas as pd
import streamlit as st

from src.ui.dataframe import display_dataframe

from src.ui.components import empty_state, kpi_grid, page_header, sandbox_notice, section_header, workflow_stepper
from src.ui.dataframe import excel_bytes, safe_display_frame
from src.ui.layout import setup_page
from src.ui.state import get_facade


setup_page("Google Ads QC", ":material/fact_check:")
facade = get_facade()
with st.container(key="page_intro"):
    page_header(
        "Google Ads quality control",
        "Confirm a variable media-plan schema, then compare deployed GDN, VRC and VVC objects through strict read-only rules.",
        "Assurance",
        "Google Ads connector · Read only",
    )
    sandbox_notice("Media-plan sample and sandbox ad objects · No campaign mutation")

    inspection = st.session_state.get("qc_inspection")
    mapping_confirmed = bool(st.session_state.get("mapping_confirmed"))
    qc = st.session_state.get("qc_result")
    active_step = 2 if mapping_confirmed else 1 if inspection else 0
    workflow_stepper(("Detect source", "Confirm mapping", "Review findings"), active_step)

section_header("Media-plan source", "Use the included plan or upload an Excel workbook with a compatible campaign schema.")
with st.container(border=True, key="panel_4_Google_Ads_QC_1"):
    source_column, upload_column, action_column = st.columns([1.15, 1.6, .9], vertical_alignment="bottom")
    with source_column:
        source_mode = st.radio("Source", ["Included media plan", "Upload media plan"], horizontal=False)
    with upload_column:
        uploaded = st.file_uploader("Media plan workbook", type=["xlsx", "xls"], disabled=source_mode == "Included media plan")
    with action_column:
        detect = st.button("Detect schema", type="primary" if not inspection else "secondary", width="stretch")

if detect:
    try:
        source_bytes = (
            facade.paths["media_plan"].read_bytes()
            if source_mode == "Included media plan"
            else uploaded.getvalue() if uploaded else None
        )
        if not source_bytes:
            raise ValueError("Upload a media-plan workbook first.")
        with st.spinner("Detecting sheets, header row and canonical field mappings..."):
            detected = facade.inspect_media_plan(BytesIO(source_bytes))
            st.session_state["qc_source_bytes"] = source_bytes
            st.session_state["qc_source_mode"] = source_mode
            st.session_state["qc_inspection"] = detected
            st.session_state["mapping_confirmed"] = False
            st.session_state.pop("qc_result", None)
        st.success(f"Detected sheet '{detected.selected_sheet}' with header row {detected.header_row}.")
        st.rerun()
    except Exception as exc:
        st.error(f"Schema detection failed. Confirm the workbook contains a campaign table. Detail: {exc}")

inspection = st.session_state.get("qc_inspection")
if inspection:
    section_header("Schema mapping", "Review every source-to-canonical field decision before enabling QC.", f"Sheet · {inspection.selected_sheet}")
    mapping_frame = pd.DataFrame([item.model_dump() for item in inspection.mappings])
    with st.container(border=True, key="panel_4_Google_Ads_QC_2"):
        st.caption(f"Detected sheets: {', '.join(inspection.detected_sheets)} · Header row: {inspection.header_row}")
        display_dataframe(
            mapping_frame[["source_column", "canonical_field", "confidence"]],
            width="stretch",
            hide_index=True,
            column_config={"confidence": st.column_config.ProgressColumn("Confidence", min_value=0.0, max_value=1.0, format="%.0%%")},
        )
        low_confidence = mapping_frame["confidence"].lt(0.85).sum() if not mapping_frame.empty else 0
        if low_confidence:
            st.warning(f"{low_confidence} low-confidence mapping(s) require operator review before confirmation.")
        elif not mapping_confirmed:
            st.success("All detected mappings meet the confidence threshold.")
        confirm_column, _ = st.columns([1, 4])
        if confirm_column.button("Confirm mapping", type="primary" if not mapping_confirmed else "secondary", disabled=mapping_confirmed, width="stretch"):
            inspection.mappings = [item.model_copy(update={"confirmed": True}) for item in inspection.mappings]
            st.session_state["qc_inspection"] = inspection
            st.session_state["mapping_confirmed"] = True
            st.success("Mapping confirmed. Read-only quality control is enabled.")
            st.rerun()

mapping_confirmed = bool(st.session_state.get("mapping_confirmed"))
if mapping_confirmed:
    section_header("Run quality control", "Load the sandbox Google Ads objects and evaluate every configured rule.")
    run_column, context_column = st.columns([1, 4], vertical_alignment="center")
    run_qc = run_column.button("Run quality control", type="primary", width="stretch")
    context_column.caption("The connector lists campaign objects only. Enable, pause, budget, bid, audience and creative changes are not exposed.")
    if run_qc:
        try:
            confirmed_inspection = st.session_state["qc_inspection"]
            if st.session_state.get("qc_source_mode") == "Included media plan":
                plans = None
            else:
                parsed = facade.parse_media_plan(BytesIO(st.session_state["qc_source_bytes"]), confirmed_inspection, True)
                plans = parsed.astype(object).where(pd.notnull(parsed), None).to_dict(orient="records")
            with st.spinner("Comparing canonical plan values with deployed ad objects..."):
                st.session_state["qc_result"] = facade.run_ads_qc(plans)
            st.success("Read-only Google Ads quality control completed.")
        except Exception as exc:
            st.error(f"Quality control failed. Review the confirmed mapping and source values. Detail: {exc}")

qc = st.session_state.get("qc_result")
if qc:
    section_header("Quality summary", "Field-level rule outcomes for the current run.")
    kpi_grid(
        [
            {"label": "Objects checked", "value": f"{qc.objects_checked:,}", "badge": "Scope", "tone": "neutral"},
            {"label": "Passed", "value": f"{qc.passed:,}", "badge": "PASS", "tone": "success"},
            {"label": "Warnings", "value": f"{qc.warnings:,}", "badge": "WARNING", "tone": "warning"},
            {"label": "Errors", "value": f"{qc.errors:,}", "badge": "ERROR", "tone": "error"},
        ]
    )

    result_frame = pd.DataFrame([item.model_dump(mode="json") for item in qc.results])
    result_frame.columns = [column.replace("_", " ").title() for column in result_frame.columns]
    section_header("Findings", "Filter by severity and object level, then inspect the canonical comparison behind any exception.", f"{len(result_frame):,} findings")
    with st.container(border=True, key="panel_4_Google_Ads_QC_3"):
        filter_left, filter_mid, filter_right = st.columns([1, 1, 1.5])
        levels = filter_left.multiselect("Severity", ["PASS", "WARNING", "ERROR"], default=["WARNING", "ERROR"])
        object_level = filter_mid.multiselect("Object level", sorted(result_frame["Object Level"].unique()))
        search = filter_right.text_input("Search object, field or explanation")

    filtered = result_frame[result_frame["Level"].isin(levels)] if levels else result_frame
    if object_level:
        filtered = filtered[filtered["Object Level"].isin(object_level)]
    if search:
        mask = filtered.astype(str).apply(lambda column: column.str.contains(search, case=False, na=False)).any(axis=1)
        filtered = filtered[mask]
    display_dataframe(safe_display_frame(filtered), width="stretch", hide_index=True)

    detail_rows = filtered[filtered["Level"].isin(["WARNING", "ERROR"])]
    if not detail_rows.empty:
        section_header("Exception detail", "Trace the expected value, actual value, rule and recommended operator action.")
        labels = [f"{row['Level']} · {row['Object Name']} · {row['Field']}" for _, row in detail_rows.iterrows()]
        selected = st.selectbox("Finding", labels)
        row = detail_rows.iloc[labels.index(selected)]
        plan_column, ads_column = st.columns(2)
        with plan_column:
            with st.container(border=True, key="panel_4_Google_Ads_QC_4"):
                st.markdown("#### Confirmed media plan")
                st.caption("Source value")
                st.code(str(row["Plan Value"]), language=None)
                st.caption("Canonical value")
                st.code(str(row["Canonical Plan Value"]), language=None)
                st.caption(f"Rule · {row['Rule']}")
        with ads_column:
            with st.container(border=True, key="panel_4_Google_Ads_QC_5"):
                st.markdown("#### Google Ads object")
                st.caption("Source value")
                st.code(str(row["Ads Value"]), language=None)
                st.caption("Canonical value")
                st.code(str(row["Canonical Ads Value"]), language=None)
                st.warning(f"{row['Explanation']} Recommended action: {row['Suggested Action']}")

    export_column, _ = st.columns([1, 4])
    export_column.download_button(
        "Export QC workbook",
        excel_bytes({"QC Results": result_frame}),
        file_name="google_ads_qc_report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        width="stretch",
    )
elif not inspection:
    empty_state(
        "Start with media-plan detection",
        "Detect the source schema and explicitly confirm the mapping before quality control can access the read-only ad-object connector.",
        "04",
    )
elif not mapping_confirmed:
    empty_state("Mapping confirmation required", "Review the detected source fields above. Quality control remains disabled until an operator confirms the mapping.", "02")
