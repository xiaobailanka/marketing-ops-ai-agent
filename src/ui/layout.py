"""Streamlit 页面配置与共享应用外壳。"""

from __future__ import annotations

import os
from pathlib import Path

import streamlit as st

from src.ui.components import page_header, sandbox_notice
from src.ui.navigation import render_sidebar_context
from src.ui.theme import inject_theme


def configured_integration_count() -> int:
    return sum(
        bool(os.getenv(name))
        for name in ("OPENAI_API_KEY", "GOOGLE_SERVICE_ACCOUNT_JSON", "FEISHU_APP_ID", "GOOGLE_ADS_DEVELOPER_TOKEN")
    )


def configure_app() -> None:
    """配置多页入口；必须在 ``st.navigation`` 之前调用。"""

    st.set_page_config(
        page_title="Marketing Operations Workspace",
        page_icon=":material/monitoring:",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.session_state["_mops_entrypoint_configured"] = True
    inject_theme()
    st.logo(Path(__file__).resolve().parents[2] / "assets/marketing_ops_logo.svg", size="large")


def finish_app_shell() -> None:
    """在导航菜单之后渲染侧栏环境上下文。"""

    render_sidebar_context(configured_integration_count())


def setup_page(title: str, icon: str = ":material/monitoring:") -> None:
    """让页面既可经统一入口运行，也可被 AppTest 单独加载。"""

    if not st.session_state.get("_mops_entrypoint_configured"):
        st.set_page_config(
            page_title=f"{title} | Marketing Operations",
            page_icon=icon,
            layout="wide",
            initial_sidebar_state="expanded",
        )
        inject_theme()
        st.logo(Path(__file__).resolve().parents[2] / "assets/marketing_ops_logo.svg", size="large")
        render_sidebar_context(configured_integration_count())


def sandbox_banner(meta: str | None = None) -> None:
    """向后兼容旧页面名称；新页面统一使用紧凑 notice。"""

    sandbox_notice(meta)


__all__ = ["configure_app", "finish_app_shell", "page_header", "sandbox_banner", "setup_page"]
