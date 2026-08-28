"""显式分组的 Streamlit 页面导航。"""

from __future__ import annotations

from typing import Any

import streamlit as st


def build_navigation() -> Any:
    return st.navigation(
        {
            "Monitor": [st.Page("pages/0_Overview.py", title="Overview", icon=":material/space_dashboard:", default=True)],
            "Operate": [
                st.Page("pages/1_Data_Cleaning.py", title="Data Cleaning", icon=":material/cleaning_services:"),
                st.Page("pages/2_Daily_Report.py", title="Daily Report", icon=":material/query_stats:"),
            ],
            "Assurance": [
                st.Page("pages/3_FIFA_Dashboard_Sync.py", title="FIFA Sync", icon=":material/sync_alt:"),
                st.Page("pages/4_Google_Ads_QC.py", title="Google Ads QC", icon=":material/fact_check:"),
            ],
            "System": [
                st.Page("pages/5_Agent_Chat.py", title="Agent Copilot", icon=":material/smart_toy:"),
                st.Page("pages/6_Task_History.py", title="Activity & Audit", icon=":material/history:"),
                st.Page("pages/7_Settings.py", title="Settings", icon=":material/settings:"),
            ],
        },
        position="sidebar",
        expanded=True,
    )


def render_sidebar_context(configured_integrations: int) -> None:
    st.sidebar.markdown(
        f"""<div class="mops-sidebar-context"><div class="mops-sidebar-context__status">PUBLIC SANDBOX · HEALTHY</div>
        <div class="mops-sidebar-context__copy">Anonymized operational sample data.<br>
        External integrations configured: {configured_integrations}/4</div></div>""",
        unsafe_allow_html=True,
    )
