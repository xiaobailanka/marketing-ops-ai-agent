"""Marketing Operations Agent Copilot。"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from src.agent.orchestrator import AgentOrchestrator
from src.agent.tools import build_tool_registry
from src.ui.components import empty_state, kpi_grid, notice, page_header, sandbox_notice, section_header
from src.ui.layout import setup_page
from src.ui.state import get_facade


setup_page("Agent Copilot", ":material/smart_toy:")
facade = get_facade()
page_header(
    "Agent Copilot",
    "Route natural-language requests to the same deterministic cleaning, reporting, synchronization and QC services used by the workbenches.",
    "System",
    "Transparent tool routing",
)
sandbox_notice("Session-scoped conversation · Deterministic tools")
notice(
    "The Copilot cannot enable, pause or delete campaigns, or change budget, bid, audience or creative in Google Ads.",
    label="Safety boundary",
    tone="warning",
)

st.session_state.setdefault("chat_history", [])
examples = [
    ("Generate UG daily report", "帮我生成UG昨天的日报"),
    ("Find the best audience", "哪个Audience表现最好？"),
    ("Run FIFA synchronization", "运行FIFA昨天的数据同步"),
    ("Check POVA Google Ads", "重新检查POVA的Google广告 QC"),
    ("Review failed tasks", "最近有哪些失败任务？"),
]
section_header("Common commands", "Start from a safe operational request or enter your own instruction below.")
selected_prompt = None
for start in range(0, len(examples), 3):
    columns = st.columns(3)
    for column, (label, prompt_value) in zip(columns, examples[start : start + 3], strict=False):
        if column.button(label, width="stretch"):
            selected_prompt = prompt_value

section_header("Conversation", "Every response identifies the tool used; calculations remain inside deterministic services.")
if not st.session_state["chat_history"]:
    empty_state(
        "No Copilot activity in this session",
        "Choose a common command or ask for a report, ranked performance answer, synchronization, QC run or task-history review.",
        "AI",
    )

for item in st.session_state["chat_history"]:
    with st.chat_message(item["role"]):
        st.write(item["content"])

prompt = selected_prompt or st.chat_input("Ask the Marketing Operations Copilot...")
if prompt:
    st.session_state["chat_history"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    try:
        orchestrator = AgentOrchestrator(build_tool_registry(facade))
        with st.spinner("Routing the request to an approved operational tool..."):
            response = orchestrator.handle(prompt)
        message = f"{response.message} Tool used: `{response.tool_name}`"
        st.session_state["chat_history"].append({"role": "assistant", "content": message})
        with st.chat_message("assistant"):
            st.write(message)
            if hasattr(response.result, "kpi_cards"):
                cards = response.result.kpi_cards
                preview_items = [
                    {"label": key, "value": f"{value:,.2f}" if isinstance(value, float) else f"{value:,}" if isinstance(value, int) else str(value)}
                    for key, value in list(cards.items())[:4]
                ]
                kpi_grid(preview_items, columns=min(4, len(preview_items)))
            elif hasattr(response.result, "passed"):
                kpi_grid(
                    [
                        {"label": "Passed", "value": response.result.passed, "badge": "PASS", "tone": "success"},
                        {"label": "Warnings", "value": response.result.warnings, "badge": "WARNING", "tone": "warning"},
                        {"label": "Errors", "value": response.result.errors, "badge": "ERROR", "tone": "error"},
                    ],
                    columns=3,
                )
            elif hasattr(response.result, "to_dict"):
                frame = response.result if isinstance(response.result, pd.DataFrame) else pd.DataFrame(response.result)
                st.dataframe(frame, width="stretch", hide_index=True)
    except Exception as exc:
        st.error(f"The Copilot stopped safely. Review the request and try again. Detail: {exc}")
