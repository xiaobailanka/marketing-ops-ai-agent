"""营销日报分析工作台。"""

from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st

from src.ui.charts import cumulative_spend_chart, impression_chart, platform_chart
from src.ui.components import empty_state, kpi_grid, page_header, sandbox_notice, section_header
from src.ui.dataframe import excel_bytes, safe_display_frame
from src.ui.layout import setup_page
from src.ui.state import get_facade


setup_page("Daily Report", ":material/query_stats:")
facade = get_facade()
page_header(
    "Daily performance report",
    "Review Python-computed KPIs, budget pacing, audience and creative performance, and fact-grounded diagnosis.",
    "Operate",
    "Metrics computed in Python",
)
sandbox_notice("Daily GTM performance · LLM never calculates metrics")

section_header("Reporting scope", "Select a market and reporting date. Generation always starts from the auditable cleaning engine.")
project_names = [f"{item.country} · {item.project_name}" for item in facade.config.projects]
with st.container(border=True):
    control_left, control_mid, control_right = st.columns([1.5, 1, .95], vertical_alignment="bottom")
    selection = control_left.selectbox("Project", project_names)
    report_date = control_mid.date_input("Report date", value=date(2026, 8, 26))
    run = control_right.button("Generate report", type="primary", width="stretch")

if run:
    project = facade.config.projects[project_names.index(selection)]
    try:
        with st.spinner("Cleaning the selected data and calculating report facts..."):
            st.session_state["daily_report_result"] = facade.run_daily_report(project, report_date)
            st.session_state["daily_report_project"] = project
        st.success("Daily report generated from the cleaned workspace data.")
    except Exception as exc:
        st.error(f"Report generation failed. Confirm the project date range and source data. Detail: {exc}")

report = st.session_state.get("daily_report_result")
project = st.session_state.get("daily_report_project")
if report:
    cards = report.kpi_cards
    section_header("Executive KPI", "Current delivery and pacing for the selected reporting date.", str(report.report_date))
    kpi_grid(
        [
            {"label": "Yesterday spend", "value": f"${cards['Yesterday Spend']:,.2f}", "badge": "Daily", "tone": "neutral"},
            {"label": "Cumulative spend", "value": f"${cards['Cumulative Spend']:,.2f}", "badge": "Actual", "tone": "success"},
            {"label": "Total budget", "value": f"${cards['Total Budget']:,.0f}", "badge": "Plan", "tone": "neutral"},
            {"label": "Budget utilization", "value": f"{(cards['Budget Utilization'] or 0):.1%}", "badge": "Pacing", "tone": "success"},
            {"label": "Time progress", "value": f"{(cards['Time Progress'] or 0):.1%}", "badge": "Calendar", "tone": "neutral"},
            {"label": "Yesterday impressions", "value": f"{cards['Yesterday Impression']:,.0f}", "badge": "Reach", "tone": "success"},
        ],
        columns=6,
    )

    section_header("Delivery trend", "Spend pacing and recent impression movement.", "Runtime calculation")
    left_chart, right_chart = st.columns([1.35, 1])
    with left_chart:
        with st.container(border=True):
            section_header("Cumulative spend", "Actual delivery against the approved total budget.")
            st.plotly_chart(cumulative_spend_chart(report.daily_trend), width="stretch", config={"displayModeBar": False})
    with right_chart:
        with st.container(border=True):
            section_header("Impression trend", "Most recent 14-day delivery volume.")
            st.plotly_chart(impression_chart(report.daily_trend), width="stretch", config={"displayModeBar": False})

    section_header("Platform performance", "Compare channel delivery and inspect the underlying calculated fields.")
    platform_left, platform_right = st.columns([1, 1])
    with platform_left:
        with st.container(border=True):
            st.plotly_chart(platform_chart(report.platform_performance), width="stretch", config={"displayModeBar": False})
    with platform_right:
        st.dataframe(safe_display_frame(report.platform_performance), width="stretch", hide_index=True)

    section_header("Performance detail", "Ranked breakdowns, deterministic anomaly events and fact-grounded narrative.")
    tabs = st.tabs(["Audience", "Creative", "Diagnosis", "All KPI"])
    with tabs[0]:
        st.dataframe(safe_display_frame(report.audience_performance), width="stretch", hide_index=True)
    with tabs[1]:
        st.dataframe(safe_display_frame(report.creative_performance), width="stretch", hide_index=True)
    with tabs[2]:
        for heading, text in report.diagnosis.items():
            st.markdown(f"#### {heading}")
            st.write(text)
        if report.anomalies:
            st.markdown("#### Detected threshold events")
            for item in report.anomalies:
                st.warning(item)
        else:
            st.success("No threshold events were detected for this report.")
    with tabs[3]:
        st.dataframe(safe_display_frame(pd.DataFrame([cards])), width="stretch", hide_index=True)

    action_columns = st.columns([1.1, 1.1, 3])
    if action_columns[0].button("Sync report worksheet", width="stretch"):
        write = facade.write_report_sheet(project, report)
        st.success(f"{write.worksheet}: {write.action}, {write.rows_written} rows written.")
    action_columns[1].download_button(
        "Download report",
        excel_bytes(
            {
                "Daily Trend": report.daily_trend,
                "Platform": report.platform_performance,
                "Audience": report.audience_performance,
                "Creative": report.creative_performance,
            }
        ),
        file_name=f"daily_report_{project.country}_{report.report_date}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        width="stretch",
    )
else:
    empty_state(
        "No report generated for this session",
        "Select a project and date, then generate the report. KPIs and pacing are computed by deterministic Python services before any narrative is produced.",
        "02",
    )
