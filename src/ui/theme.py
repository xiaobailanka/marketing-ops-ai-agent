"""Marketing Operations 的统一视觉主题与 Plotly 样式。"""

from __future__ import annotations

import streamlit as st


COLORS = {
    "nav": "#102E31",
    "nav_active": "#1D4847",
    "primary": "#167A6C",
    "primary_hover": "#12685D",
    "primary_soft": "#EDF7F4",
    "canvas": "#F3F6F5",
    "surface": "#FFFFFF",
    "ink": "#142725",
    "muted": "#6B817D",
    "border": "#DCE5E2",
    "success": "#177259",
    "success_soft": "#E3F4EE",
    "warning": "#9C6219",
    "warning_soft": "#FFF1D6",
    "error": "#AD3E45",
    "error_soft": "#FAE7E8",
    "neutral_soft": "#E8EEEE",
}

CHART_COLORS = ["#167A6C", "#5BAA9D", "#8CC8BE", "#D29A36", "#627C78", "#AD3E45"]

PLOTLY_LAYOUT = {
    "font": {"family": "Inter, Segoe UI, sans-serif", "color": COLORS["ink"], "size": 12},
    "paper_bgcolor": COLORS["surface"],
    "plot_bgcolor": COLORS["surface"],
    "hoverlabel": {
        "bgcolor": COLORS["nav"],
        "bordercolor": COLORS["nav"],
        "font": {"color": "#FFFFFF", "family": "Inter, Segoe UI, sans-serif"},
    },
    "xaxis": {
        "gridcolor": "#EAF0EE",
        "linecolor": COLORS["border"],
        "zerolinecolor": COLORS["border"],
        "title": {"font": {"color": COLORS["muted"]}},
    },
    "yaxis": {
        "gridcolor": "#EAF0EE",
        "linecolor": COLORS["border"],
        "zerolinecolor": COLORS["border"],
        "title": {"font": {"color": COLORS["muted"]}},
    },
    "legend": {
        "orientation": "h",
        "yanchor": "bottom",
        "y": 1.02,
        "xanchor": "right",
        "x": 1,
        "font": {"size": 11, "color": COLORS["muted"]},
    },
}


GLOBAL_CSS = f"""
<style>
  :root {{
    --mops-nav: {COLORS['nav']}; --mops-nav-active: {COLORS['nav_active']};
    --mops-primary: {COLORS['primary']}; --mops-primary-hover: {COLORS['primary_hover']};
    --mops-primary-soft: {COLORS['primary_soft']}; --mops-canvas: {COLORS['canvas']};
    --mops-surface: {COLORS['surface']}; --mops-ink: {COLORS['ink']}; --mops-muted: {COLORS['muted']};
    --mops-border: {COLORS['border']}; --mops-success: {COLORS['success']};
    --mops-success-soft: {COLORS['success_soft']}; --mops-warning: {COLORS['warning']};
    --mops-warning-soft: {COLORS['warning_soft']}; --mops-error: {COLORS['error']};
    --mops-error-soft: {COLORS['error_soft']};
  }}
  html, body, [class*="css"] {{ font-family: Inter, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif; }}
  .stApp {{ background: var(--mops-canvas); color: var(--mops-ink); }}
  [data-testid="stHeader"] {{ background: rgba(243, 246, 245, .92); }}
  [data-testid="stToolbar"] {{ right: 1rem; }}
  .block-container {{ max-width: 1480px; padding: 1.35rem 2.2rem 3.5rem; }}

  [data-testid="stSidebar"] {{ background: var(--mops-nav); border-right: 0; }}
  [data-testid="stSidebar"] > div:first-child {{ padding-top: .65rem; }}
  [data-testid="stSidebar"] * {{ color: #B8CAC7; }}
  [data-testid="stSidebar"] hr {{ border-color: rgba(255, 255, 255, .10); }}
  [data-testid="stSidebarNav"] {{ padding-top: .15rem; }}
  [data-testid="stSidebarNav"] span {{ font-size: .83rem; font-weight: 560; }}
  [data-testid="stSidebarNav"] [data-testid="stSidebarNavItems"] > div > span {{
    color: #688B86; font-size: .67rem; font-weight: 760; letter-spacing: .11em;
    text-transform: uppercase; margin-top: .85rem;
  }}
  [data-testid="stSidebarNav"] a {{ border-radius: 7px; margin: 2px 7px; min-height: 2.35rem; }}
  [data-testid="stSidebarNav"] a:hover {{ background: rgba(255, 255, 255, .06); }}
  [data-testid="stSidebarNav"] a[aria-current="page"] {{ background: var(--mops-nav-active); box-shadow: inset 3px 0 #64D2BD; }}
  [data-testid="stSidebarNav"] a[aria-current="page"] span {{ color: #FFFFFF; font-weight: 680; }}
  [data-testid="stSidebarNav"] svg {{ fill: #7FA39D; }}
  [data-testid="stSidebarNav"] a[aria-current="page"] svg {{ fill: #8BE0D0; }}

  .mops-sidebar-context {{ margin: .85rem .72rem .2rem; padding: .82rem .85rem; border: 1px solid rgba(255,255,255,.10);
    border-radius: 9px; background: rgba(255,255,255,.035); }}
  .mops-sidebar-context__status {{ color: #8FE1D1; font-size: .67rem; font-weight: 760; letter-spacing: .07em; }}
  .mops-sidebar-context__copy {{ color: #7E9E99; font-size: .69rem; line-height: 1.55; margin-top: .4rem; }}

  h1, h2, h3 {{ color: var(--mops-ink); letter-spacing: -.025em; }}
  h1 {{ font-size: clamp(1.65rem, 2vw, 2rem) !important; font-weight: 720 !important; line-height: 1.16 !important; }}
  h2 {{ font-size: 1.28rem !important; font-weight: 700 !important; }}
  h3 {{ font-size: 1.03rem !important; font-weight: 680 !important; }}
  p, li, label {{ color: var(--mops-ink); }}

  .mops-page-header {{ display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem; padding: .1rem 0 .75rem; }}
  .mops-page-header__eyebrow {{ color: var(--mops-primary); font-size: .67rem; font-weight: 780;
    letter-spacing: .11em; text-transform: uppercase; margin-bottom: .45rem; }}
  .mops-page-header h1 {{ margin: 0; }}
  .mops-page-header p {{ color: var(--mops-muted); max-width: 780px; font-size: .89rem; line-height: 1.55; margin: .48rem 0 0; }}
  .mops-page-header__meta {{ white-space: nowrap; color: var(--mops-muted); font-size: .72rem; padding-top: 1.55rem; }}

  .mops-notice {{ display: flex; justify-content: space-between; gap: 1rem; align-items: center; padding: .72rem .9rem;
    border: 1px solid #CFE2DC; background: var(--mops-primary-soft); border-radius: 9px; color: #35655D;
    font-size: .78rem; line-height: 1.45; margin: .3rem 0 1rem; }}
  .mops-notice strong {{ color: #145F53; }}
  .mops-notice--warning {{ border-color: #E9D3A8; background: var(--mops-warning-soft); color: #80531C; }}
  .mops-notice--error {{ border-color: #EDC9CC; background: var(--mops-error-soft); color: #923941; }}
  .mops-notice__meta {{ white-space: nowrap; font-weight: 680; }}

  .mops-section-header {{ display: flex; align-items: end; justify-content: space-between; gap: 1rem; margin: 1.3rem 0 .65rem; }}
  .mops-section-header h2 {{ margin: 0; }}
  .mops-section-header p {{ color: var(--mops-muted); font-size: .78rem; margin: .24rem 0 0; }}
  .mops-section-header__meta {{ color: var(--mops-muted); font-size: .72rem; }}

  .mops-kpi-grid {{ display: grid; grid-template-columns: repeat(var(--mops-columns, 4), minmax(0, 1fr)); gap: .72rem; margin: .25rem 0 .85rem; }}
  .mops-kpi {{ min-width: 0; background: var(--mops-surface); border: 1px solid var(--mops-border); border-radius: 10px;
    padding: .88rem 1rem; box-shadow: 0 2px 8px rgba(16,46,49,.035); }}
  .mops-kpi__label {{ color: var(--mops-muted); font-size: .73rem; font-weight: 650; }}
  .mops-kpi__row {{ display: flex; justify-content: space-between; align-items: end; gap: .5rem; margin-top: .55rem; }}
  .mops-kpi__value {{ color: var(--mops-ink); font-size: 1.55rem; font-weight: 720; line-height: 1; letter-spacing: -.04em; }}
  .mops-kpi__meta {{ color: var(--mops-muted); font-size: .68rem; margin-top: .52rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
  .mops-pill {{ display: inline-flex; align-items: center; width: fit-content; border-radius: 999px; padding: .22rem .48rem;
    font-size: .65rem; font-weight: 720; line-height: 1; }}
  .mops-pill--success {{ color: var(--mops-success); background: var(--mops-success-soft); }}
  .mops-pill--warning {{ color: var(--mops-warning); background: var(--mops-warning-soft); }}
  .mops-pill--error {{ color: var(--mops-error); background: var(--mops-error-soft); }}
  .mops-pill--neutral {{ color: #526B67; background: #E8EEEE; }}

  .mops-stepper {{ display: grid; grid-template-columns: repeat(var(--mops-steps, 3), minmax(0,1fr)); background: #FFFFFF;
    border: 1px solid var(--mops-border); border-radius: 10px; padding: .72rem .9rem; margin: .25rem 0 .8rem; }}
  .mops-step {{ position: relative; display: flex; align-items: center; gap: .52rem; color: var(--mops-muted); font-size: .73rem; }}
  .mops-step:not(:last-child)::after {{ content: ""; position: absolute; height: 1px; background: var(--mops-border); left: 57%; right: 8%; top: .72rem; }}
  .mops-step__number {{ z-index: 1; width: 1.48rem; height: 1.48rem; display: grid; place-items: center; border-radius: 50%;
    border: 1px solid #CAD8D4; background: #FFFFFF; font-size: .64rem; font-weight: 780; }}
  .mops-step--done {{ color: var(--mops-success); font-weight: 680; }}
  .mops-step--done .mops-step__number {{ background: var(--mops-success-soft); border-color: #A8D9CC; }}
  .mops-step--active {{ color: var(--mops-ink); font-weight: 720; }}
  .mops-step--active .mops-step__number {{ color: #FFFFFF; background: var(--mops-primary); border-color: var(--mops-primary); }}

  .mops-empty {{ text-align: center; padding: 2rem 1.25rem; border: 1px dashed #C8D6D2; border-radius: 10px; background: rgba(255,255,255,.58); }}
  .mops-empty__icon {{ color: var(--mops-primary); font-size: 1.35rem; font-weight: 780; }}
  .mops-empty h3 {{ margin: .5rem 0 .25rem; }}
  .mops-empty p {{ color: var(--mops-muted); font-size: .8rem; max-width: 620px; margin: 0 auto; line-height: 1.55; }}

  .mops-attention {{ display: flex; gap: .7rem; padding: .7rem 0; border-bottom: 1px solid #EDF2F0; }}
  .mops-attention:last-child {{ border-bottom: 0; }}
  .mops-attention__dot {{ width: .5rem; height: .5rem; border-radius: 50%; margin-top: .28rem; flex: 0 0 auto; }}
  .mops-attention__dot--error {{ background: #C85258; box-shadow: 0 0 0 3px #FBE9EA; }}
  .mops-attention__dot--warning {{ background: #D89A28; box-shadow: 0 0 0 3px #FFF3DC; }}
  .mops-attention__dot--success {{ background: #258B72; box-shadow: 0 0 0 3px #E3F4EE; }}
  .mops-attention strong {{ display: block; font-size: .79rem; }}
  .mops-attention p {{ color: var(--mops-muted); font-size: .7rem; line-height: 1.45; margin: .2rem 0 0; }}

  div[data-testid="stVerticalBlockBorderWrapper"] {{ background: var(--mops-surface); border-color: var(--mops-border);
    border-radius: 10px; box-shadow: 0 2px 8px rgba(16,46,49,.03); }}
  div[data-testid="stMetric"] {{ background: var(--mops-surface); border: 1px solid var(--mops-border); border-radius: 10px;
    padding: .78rem .9rem; box-shadow: 0 2px 8px rgba(16,46,49,.03); }}
  [data-testid="stMetricLabel"] {{ color: var(--mops-muted); font-weight: 620; }}
  [data-testid="stMetricValue"] {{ color: var(--mops-ink); font-weight: 720; letter-spacing: -.03em; }}

  .stButton > button, .stDownloadButton > button, [data-testid="stFormSubmitButton"] > button {{
    min-height: 2.45rem; border-radius: 7px; border-color: #C9D7D3; font-weight: 660; box-shadow: none;
  }}
  .stButton > button:hover, .stDownloadButton > button:hover {{ border-color: var(--mops-primary); color: var(--mops-primary); }}
  .stButton > button[kind="primary"], [data-testid="stBaseButton-primary"] {{ background: var(--mops-primary); border-color: var(--mops-primary); color: #FFFFFF; }}
  .stButton > button[kind="primary"]:hover, [data-testid="stBaseButton-primary"]:hover {{
    background: var(--mops-primary-hover); border-color: var(--mops-primary-hover); color: #FFFFFF;
  }}
  [data-baseweb="select"] > div, [data-baseweb="base-input"], [data-testid="stDateInput"] > div > div,
  [data-testid="stFileUploaderDropzone"] {{ border-color: #CAD8D4; border-radius: 7px; background: #FFFFFF; }}
  [data-testid="stFileUploaderDropzone"] {{ padding: .65rem; }}
  [data-testid="stFileUploaderDropzoneInstructions"] span {{ font-size: .76rem; }}

  [data-testid="stAlert"] {{ border-radius: 9px; border-width: 1px; }}
  [data-testid="stDataFrame"] {{ border: 1px solid var(--mops-border); border-radius: 9px; overflow: hidden; background: #FFFFFF; }}
  [data-baseweb="tab-list"] {{ gap: .3rem; border-bottom: 1px solid var(--mops-border); }}
  [data-baseweb="tab"] {{ border-radius: 7px 7px 0 0; padding-left: .85rem; padding-right: .85rem; }}
  [data-baseweb="tab"][aria-selected="true"] {{ background: var(--mops-primary-soft); color: var(--mops-primary); }}
  [data-testid="stChatMessage"] {{ background: #FFFFFF; border: 1px solid var(--mops-border); border-radius: 10px; padding: .3rem .6rem; }}

  .mops-data-table {{ width: 100%; border-collapse: collapse; font-size: .75rem; }}
  .mops-data-table th {{ text-align: left; padding: .65rem .72rem; color: var(--mops-muted); background: #F7F9F8;
    border-bottom: 1px solid var(--mops-border); font-size: .65rem; letter-spacing: .055em; text-transform: uppercase; }}
  .mops-data-table td {{ padding: .7rem .72rem; border-bottom: 1px solid #EDF2F0; vertical-align: middle; }}
  .mops-data-table tr:last-child td {{ border-bottom: 0; }}
  .mops-table-wrap {{ border: 1px solid var(--mops-border); border-radius: 9px; overflow-x: auto; background: #FFFFFF; }}

  @media (max-width: 1100px) {{
    .block-container {{ padding-left: 1.25rem; padding-right: 1.25rem; }}
    .mops-kpi-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
  }}
  @media (max-width: 720px) {{
    .block-container {{ padding-left: .85rem; padding-right: .85rem; }}
    .mops-page-header, .mops-notice, .mops-section-header {{ display: block; }}
    .mops-page-header__meta, .mops-notice__meta, .mops-section-header__meta {{ padding-top: .5rem; white-space: normal; }}
    .mops-kpi-grid {{ grid-template-columns: 1fr; }}
    .mops-stepper {{ grid-template-columns: 1fr; gap: .5rem; }}
    .mops-step::after {{ display: none; }}
  }}
</style>
"""


def inject_theme() -> None:
    """把统一主题注入当前 Streamlit 页面。"""

    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
