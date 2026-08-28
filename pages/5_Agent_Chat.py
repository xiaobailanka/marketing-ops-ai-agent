"""Agent Chat 页面。"""

from __future__ import annotations

import streamlit as st

from src.agent.orchestrator import AgentOrchestrator
from src.agent.tools import build_tool_registry
from src.ui.layout import page_header, sandbox_banner, setup_page
from src.ui.state import get_facade

setup_page("Agent Chat", "💬")
facade = get_facade()
page_header("Agent Chat", "A transparent intent router calling the same deterministic services as every dashboard button.")
sandbox_banner()

st.session_state.setdefault("chat_history", [])
examples = [
    "帮我生成UG昨天的日报",
    "哪个Audience表现最好？",
    "运行FIFA昨天的数据同步",
    "重新检查POVA的Google广告 QC",
    "最近有哪些失败任务？",
]
st.caption("Try an example")
example_columns = st.columns(len(examples))
selected_prompt = None
for column, example in zip(example_columns, examples, strict=True):
    if column.button(example, width="stretch"):
        selected_prompt = example

for item in st.session_state["chat_history"]:
    with st.chat_message(item["role"]):
        st.write(item["content"])

prompt = selected_prompt or st.chat_input("Ask the Marketing Ops Agent...")
if prompt:
    st.session_state["chat_history"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    try:
        orchestrator = AgentOrchestrator(build_tool_registry(facade))
        with st.spinner("Routing request to a safe tool..."):
            response = orchestrator.handle(prompt)
        message = f"{response.message} Tool: `{response.tool_name}`"
        st.session_state["chat_history"].append({"role": "assistant", "content": message})
        with st.chat_message("assistant"):
            st.write(message)
            if hasattr(response.result, "kpi_cards"):
                st.json(response.result.kpi_cards)
            elif hasattr(response.result, "passed"):
                st.json({"PASS": response.result.passed, "WARNING": response.result.warnings, "ERROR": response.result.errors})
            elif hasattr(response.result, "to_dict"):
                st.dataframe(response.result, width="stretch")
    except Exception as exc:
        st.error(f"Agent task failed safely: {exc}")

st.warning("Safety boundary: the Agent cannot enable, pause, delete, change budget/bid, audience or creative in Google Ads.")
