"""Streamlit Session 与业务 Facade。"""

from __future__ import annotations

import streamlit as st

from src.application.facade import MarketingOpsFacade


def get_facade() -> MarketingOpsFacade:
    return MarketingOpsFacade(st.session_state)

