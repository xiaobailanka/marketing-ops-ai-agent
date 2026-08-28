"""Daily Report Dashboard。"""

from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st

from src.ui.charts import cumulative_spend_chart, impression_chart, platform_chart
from src.ui.dataframe import excel_bytes, safe_display_frame
from src.ui.layout import page_header, sandbox_banner, setup_page
from src.ui.state import get_facade

setup_page("Daily Report", "📊")
facade = get_facade()
page_header("Daily Report", "Python-computed KPIs, budget pacing, audience/creative performance and fact-grounded diagnosis.")
sandbox_banner()

project_names = [f"{item.country} · {item.project_name}" for item in facade.config.projects]
control_left, control_mid, control_right = st.columns([1.5, 1, 1])
selection = control_left.selectbox("Project", project_names)
report_date = control_mid.date_input("Report Date", value=date(2026, 8, 26))
run = control_right.button("Generate Daily Report", type="primary", width="stretch")

if run:
    project = facade.config.projects[project_names.index(selection)]
    try:
        with st.spinner("Calculating report facts..."):
            st.session_state["daily_report_result"] = facade.run_daily_report(project, report_date)
            st.session_state["daily_report_project"] = project
        st.success("Daily report generated from cleaned workspace data.")
    except Exception as exc:
        st.error(f"Report failed: {exc}")

report = st.session_state.get("daily_report_result")
project = st.session_state.get("daily_report_project")
if report:
    cards = report.kpi_cards
    card_columns = st.columns(6)
    card_columns[0].metric("Yesterday Spend", f"${cards['Yesterday Spend']:,.2f}")
    card_columns[1].metric("Cumulative Spend", f"${cards['Cumulative Spend']:,.2f}")
    card_columns[2].metric("Total Budget", f"${cards['Total Budget']:,.0f}")
    card_columns[3].metric("Budget Utilization", f"{(cards['Budget Utilization'] or 0):.1%}")
    card_columns[4].metric("Time Progress", f"{(cards['Time Progress'] or 0):.1%}")
    card_columns[5].metric("Yesterday Impression", f"{cards['Yesterday Impression']:,.0f}")

    left_chart, right_chart = st.columns([1.3, 1])
    with left_chart:
        st.subheader("Cumulative Spend")
        st.plotly_chart(cumulative_spend_chart(report.daily_trend), width="stretch")
    with right_chart:
        st.subheader("Daily Impression Trend")
        st.plotly_chart(impression_chart(report.daily_trend), width="stretch")

    st.subheader("Platform Performance")
    platform_left, platform_right = st.columns([1, 1])
    platform_left.plotly_chart(platform_chart(report.platform_performance), width="stretch")
    platform_right.dataframe(safe_display_frame(report.platform_performance), width="stretch", hide_index=True)

    tabs = st.tabs(["Audience Performance", "Creative Performance", "AI Diagnosis", "All KPI"])
    with tabs[0]:
        st.dataframe(safe_display_frame(report.audience_performance), width="stretch", hide_index=True)
    with tabs[1]:
        st.dataframe(safe_display_frame(report.creative_performance), width="stretch", hide_index=True)
    with tabs[2]:
        for heading, text in report.diagnosis.items():
            st.markdown(f"#### {heading}")
            st.write(text)
        if report.anomalies:
            st.markdown("#### Detected Threshold Events")
            for item in report.anomalies:
                st.warning(item)
    with tabs[3]:
        kpis = pd.DataFrame([cards])
        st.dataframe(safe_display_frame(kpis), width="stretch", hide_index=True)

    action_columns = st.columns([1, 1, 3])
    if action_columns[0].button("Sync Report Worksheet", width="stretch"):
        write = facade.write_report_sheet(project, report)
        st.success(f"{write.worksheet}: {write.action}, {write.rows_written} rows")
    action_columns[1].download_button(
        "Download Report",
        excel_bytes({
            "Daily Trend": report.daily_trend,
            "Platform": report.platform_performance,
            "Audience": report.audience_performance,
            "Creative": report.creative_performance,
        }),
        file_name=f"daily_report_{project.country}_{report.report_date}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        width="stretch",
    )
else:
    st.info("Generate a report to calculate KPIs and pacing. No metric is calculated by the LLM or hard-coded in this page.")
