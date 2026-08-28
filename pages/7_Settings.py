"""项目配置、阈值与连接状态。"""

from __future__ import annotations

import os

import pandas as pd
import streamlit as st

from src.models.project import ProjectConfig
from src.ui.components import kpi_grid, page_header, sandbox_notice, section_header
from src.ui.layout import setup_page
from src.ui.state import get_facade
from src.utils.config import load_anomaly_thresholds


setup_page("Settings", ":material/settings:")
facade = get_facade()
page_header(
    "Workspace settings",
    "Manage session-scoped project budgets, reporting dates, destination identifiers, anomaly thresholds and connector readiness.",
    "System",
    "Secrets never rendered",
)
sandbox_notice("Configuration changes apply only to the current browser session")

section_header("Project configuration", "Edit the operating scope used by cleaning, reporting and downstream synchronization.", f"{len(facade.config.projects)} projects")
project_frame = pd.DataFrame([project.model_dump() for project in facade.config.projects])
with st.container(border=True):
    edited = st.data_editor(
        project_frame,
        width="stretch",
        num_rows="dynamic",
        hide_index=True,
        column_config={
            "total_budget": st.column_config.NumberColumn("Total budget", min_value=1.0, format="$%.2f"),
            "anomaly_threshold": st.column_config.NumberColumn("Anomaly threshold", min_value=0.01, max_value=0.99, format="%.2f"),
        },
    )
    save_column, reset_note = st.columns([1, 4], vertical_alignment="center")
    save = save_column.button("Save project settings", type="primary", width="stretch")
    reset_note.caption("Saved values remain isolated to this session and do not modify the repository configuration files.")

if save:
    try:
        projects = [ProjectConfig.model_validate(record) for record in edited.to_dict(orient="records")]
        facade.save_projects(projects)
        st.success("Project settings saved for the current public-sandbox session.")
    except Exception as exc:
        st.error(f"Settings validation failed. Correct the highlighted values and try again. Detail: {exc}")

section_header("Global thresholds", "Deterministic thresholds used to flag delivery and performance anomalies.")
thresholds = load_anomaly_thresholds()
threshold_frame = pd.DataFrame(
    [{"Threshold": str(name).replace("_", " ").title(), "Configured value": value} for name, value in thresholds.items()]
)
with st.container(border=True):
    st.dataframe(threshold_frame, width="stretch", hide_index=True)
    st.caption("Thresholds are loaded from version-controlled configuration and are not calculated or changed by the LLM.")

section_header("Connector readiness", "External credentials are detected from environment variables; unavailable services use explicit sandbox adapters.")
connectors = {
    "Google Sheets": bool(os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")),
    "Feishu Bitable": all(os.getenv(name) for name in ("FEISHU_APP_ID", "FEISHU_APP_SECRET", "FEISHU_BITABLE_APP_TOKEN", "FEISHU_TABLE_ID")),
    "Google Ads (read only)": bool(os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN")),
    "LLM service": bool(os.getenv("OPENAI_API_KEY")),
}
configured_count = sum(connectors.values())
kpi_grid(
    [
        {"label": "Connectors", "value": f"{len(connectors):02d}", "badge": "Registered", "tone": "neutral"},
        {"label": "External configured", "value": f"{configured_count:02d}", "badge": "Environment", "tone": "success" if configured_count else "neutral"},
        {"label": "Sandbox adapters", "value": f"{len(connectors) - configured_count:02d}", "badge": "Safe fallback", "tone": "success"},
        {"label": "Write-sensitive Ads actions", "value": "Disabled", "badge": "Read only", "tone": "success"},
    ]
)
status_frame = pd.DataFrame(
    [
        {
            "Connector": name,
            "Operating mode": "EXTERNAL CONFIGURED" if configured else "SANDBOX CONNECTOR",
            "Safe fallback": True,
            "Credentials displayed": False,
        }
        for name, configured in connectors.items()
    ]
)
st.dataframe(status_frame, width="stretch", hide_index=True)
st.caption("Secrets are loaded only from environment variables and are never displayed, logged or committed.")
