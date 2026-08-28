"""Project Configuration 与连接状态。"""

from __future__ import annotations

import os

import pandas as pd
import streamlit as st

from src.models.project import ProjectConfig
from src.ui.layout import page_header, sandbox_banner, setup_page
from src.ui.state import get_facade
from src.utils.config import load_anomaly_thresholds

setup_page("Settings", "⚙️")
facade = get_facade()
page_header("Settings", "Edit session-scoped project budgets, dates, Sheet IDs and anomaly thresholds.")
sandbox_banner()

st.subheader("Project Configuration")
project_frame = pd.DataFrame([project.model_dump() for project in facade.config.projects])
edited = st.data_editor(
    project_frame,
    width="stretch",
    num_rows="dynamic",
    column_config={
        "total_budget": st.column_config.NumberColumn("Total Budget", min_value=1.0, format="$%.2f"),
        "anomaly_threshold": st.column_config.NumberColumn("Anomaly Threshold", min_value=0.01, max_value=0.99, format="%.2f"),
    },
)
if st.button("Save Project Settings", type="primary"):
    try:
        projects = [ProjectConfig.model_validate(record) for record in edited.to_dict(orient="records")]
        facade.save_projects(projects)
        st.success("Settings saved for this Public Sandbox session.")
    except Exception as exc:
        st.error(f"Settings validation failed: {exc}")

st.subheader("Global Thresholds")
thresholds = load_anomaly_thresholds()
st.json(thresholds)

st.subheader("Connector Status")
connectors = {
    "Google Sheets": bool(os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")),
    "Feishu Bitable": all(os.getenv(name) for name in ("FEISHU_APP_ID", "FEISHU_APP_SECRET", "FEISHU_BITABLE_APP_TOKEN", "FEISHU_TABLE_ID")),
    "Google Ads (Read Only)": bool(os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN")),
    "LLM Service": bool(os.getenv("OPENAI_API_KEY")),
}
status_frame = pd.DataFrame([
    {"Connector": name, "Status": "EXTERNAL CONFIGURED" if configured else "SANDBOX CONNECTOR", "Safe Fallback": True}
    for name, configured in connectors.items()
])
st.dataframe(status_frame, width="stretch", hide_index=True)
st.caption("Secrets are loaded only from environment variables and are never displayed or committed.")
