"""统一 SaaS 风格、Public Sandbox Banner 与页面标题。"""

from __future__ import annotations

import os

import streamlit as st


def setup_page(title: str, icon: str = "📊") -> None:
    st.set_page_config(page_title=f"{title} | Marketing Ops AI Agent", page_icon=icon, layout="wide")
    st.markdown(
        """
        <style>
          .stApp { background: #f6f8fb; }
          [data-testid="stSidebar"] { background: #13213c; }
          [data-testid="stSidebar"] * { color: #eef4ff; }
          .block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 1440px; }
          .sandbox-banner { background:#e8f7ef; border-left:5px solid #1f9d68; border-radius:8px;
                         padding:12px 16px; margin: 10px 0 20px; color:#154c38; }
          .eyebrow { color:#2563eb; text-transform:uppercase; letter-spacing:.08em;
                     font-size:.75rem; font-weight:700; }
          .subtle { color:#64748b; }
          div[data-testid="stMetric"] { background:white; border:1px solid #e2e8f0;
                     border-radius:12px; padding:14px 16px; box-shadow:0 3px 14px rgba(15,23,42,.04); }
          div[data-testid="stVerticalBlockBorderWrapper"] { background:white; border-radius:12px; }
          .status-pass { color:#067647; font-weight:700; }
          .status-warning { color:#b54708; font-weight:700; }
          .status-error { color:#b42318; font-weight:700; }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.sidebar.markdown("## Marketing Ops")
    st.sidebar.caption("AI Agent Platform")
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Environment:** PUBLIC SANDBOX")
    st.sidebar.caption("External services use isolated sandbox adapters unless credentials are configured.")
    credential_count = sum(
        bool(os.getenv(name))
        for name in ("OPENAI_API_KEY", "GOOGLE_SERVICE_ACCOUNT_JSON", "FEISHU_APP_ID", "GOOGLE_ADS_DEVELOPER_TOKEN")
    )
    st.sidebar.caption(f"Configured external integrations: {credential_count}/4")


def page_header(title: str, description: str, eyebrow: str = "Marketing Operations") -> None:
    st.markdown(f'<div class="eyebrow">{eyebrow}</div>', unsafe_allow_html=True)
    st.title(title)
    st.markdown(f'<div class="subtle">{description}</div>', unsafe_allow_html=True)


def sandbox_banner() -> None:
    st.markdown(
        """
        <div class="sandbox-banner"><strong>PUBLIC SANDBOX</strong> — This workspace uses anonymized sample data
        and contains no customer records. Metrics, synchronization results and QC findings are calculated at runtime.</div>
        """,
        unsafe_allow_html=True,
    )
