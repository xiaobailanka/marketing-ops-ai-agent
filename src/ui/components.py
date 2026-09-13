"""无业务逻辑的 Streamlit 展示组件。"""

from __future__ import annotations

from html import escape
from typing import Any, Iterable, Mapping, Sequence

import streamlit as st


Tone = str


def _safe(value: Any) -> str:
    return escape(str(value))


def page_header(title: str, description: str, eyebrow: str = "Marketing operations", meta: str | None = None) -> None:
    meta_html = f'<div class="mops-page-header__meta">{_safe(meta)}</div>' if meta else ""
    st.markdown(
        f"""<div class="mops-page-header"><div><div class="mops-page-header__eyebrow">{_safe(eyebrow)}</div>
        <h1>{_safe(title)}</h1><p>{_safe(description)}</p></div>{meta_html}</div>""",
        unsafe_allow_html=True,
    )

def notice(message: str, *, label: str = "Public sandbox", meta: str | None = None, tone: Tone = "info") -> None:
    tone_class = "" if tone == "info" else f" mops-notice--{_safe(tone)}"
    meta_html = f'<span class="mops-notice__meta">{_safe(meta)}</span>' if meta else ""
    st.markdown(
        f'<div class="mops-notice{tone_class}"><span><strong>{_safe(label)}</strong> · {_safe(message)}</span>{meta_html}</div>',
        unsafe_allow_html=True,
    )


def sandbox_notice(meta: str | None = None) -> None:
    notice("Anonymized sample data; no customer records. Metrics and workflow findings are calculated at runtime.", meta=meta)


def section_header(title: str, description: str | None = None, meta: str | None = None) -> None:
    description_html = f"<p>{_safe(description)}</p>" if description else ""
    meta_html = f'<div class="mops-section-header__meta">{_safe(meta)}</div>' if meta else ""
    st.markdown(
        f'<div class="mops-section-header"><div><h2>{_safe(title)}</h2>{description_html}</div>{meta_html}</div>',
        unsafe_allow_html=True,
    )


def pill(label: str, tone: Tone = "neutral") -> str:
    return f'<span class="mops-pill mops-pill--{_safe(tone)}">{_safe(label)}</span>'


def kpi_grid(items: Sequence[Mapping[str, Any]], columns: int = 4) -> None:
    cards: list[str] = []
    for item in items:
        tone = str(item.get("tone", "neutral"))
        badge = pill(str(item["badge"]), tone) if item.get("badge") else ""
        meta = f'<div class="mops-kpi__meta">{_safe(item["meta"])}</div>' if item.get("meta") else ""
        cards.append(
            f'<div class="mops-kpi"><div class="mops-kpi__label">{_safe(item["label"])}</div>'
            f'<div class="mops-kpi__row"><div class="mops-kpi__value">{_safe(item["value"])}</div>{badge}</div>{meta}</div>'
        )
    st.markdown(
        f'<div class="mops-kpi-grid" style="--mops-columns:{max(1, columns)}">{"".join(cards)}</div>',
        unsafe_allow_html=True,
    )


def workflow_stepper(steps: Sequence[str], active_index: int) -> None:
    rendered: list[str] = []
    for index, step in enumerate(steps):
        if index < active_index:
            modifier, marker = " mops-step--done", "✓"
        elif index == active_index:
            modifier, marker = " mops-step--active", str(index + 1)
        else:
            modifier, marker = "", str(index + 1)
        rendered.append(
            f'<div class="mops-step{modifier}"><span class="mops-step__number">{marker}</span><span>{_safe(step)}</span></div>'
        )
    st.markdown(
        f'<div class="mops-stepper" style="--mops-steps:{max(1, len(steps))}">{"".join(rendered)}</div>',
        unsafe_allow_html=True,
    )


def empty_state(title: str, description: str, marker: str = "01") -> None:
    st.markdown(
        f'<div class="mops-empty"><div class="mops-empty__icon">{_safe(marker)}</div><h3>{_safe(title)}</h3><p>{_safe(description)}</p></div>',
        unsafe_allow_html=True,
    )


def attention_item(title: str, description: str, tone: Tone = "warning") -> None:
    st.markdown(
        f'<div class="mops-attention"><span class="mops-attention__dot mops-attention__dot--{_safe(tone)}"></span>'
        f'<div><strong>{_safe(title)}</strong><p>{_safe(description)}</p></div></div>',
        unsafe_allow_html=True,
    )


def html_table(headers: Sequence[str], rows: Iterable[Sequence[str]]) -> None:
    head = "".join(f'<th scope="col">{_safe(item)}</th>' for item in headers)
    body = "".join("<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>" for row in rows)
    st.markdown(
        f'<div class="mops-table-wrap"><table class="mops-data-table"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>',
        unsafe_allow_html=True,
    )
