from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize(
    "page_path",
    [
        "app.py",
        "pages/0_Overview.py",
        "pages/1_Data_Cleaning.py",
        "pages/2_Daily_Report.py",
        "pages/3_FIFA_Dashboard_Sync.py",
        "pages/4_Google_Ads_QC.py",
        "pages/5_Agent_Chat.py",
        "pages/6_Task_History.py",
        "pages/7_Settings.py",
    ],
)
def test_streamlit_page_loads_without_exception(page_path: str) -> None:
    app = AppTest.from_file(PROJECT_ROOT / page_path, default_timeout=30).run()
    assert not app.exception


def test_overview_exposes_operational_status_and_primary_action() -> None:
    app = AppTest.from_file(PROJECT_ROOT / "pages/0_Overview.py", default_timeout=30).run()
    rendered_markdown = "\n".join(item.value for item in app.markdown)
    assert "Operations overview" in rendered_markdown
    assert "Open exceptions" in rendered_markdown
    assert any(button.label == "Start daily report" for button in app.button)


def test_navigation_entrypoint_uses_grouped_workspace_pages() -> None:
    source = (PROJECT_ROOT / "src/ui/navigation.py").read_text(encoding="utf-8")
    for group in ("Monitor", "Operate", "Assurance", "System"):
        assert f'"{group}"' in source
    for page_title in ("Overview", "Data Cleaning", "Daily Report", "FIFA Sync", "Google Ads QC", "Agent Copilot", "Activity & Audit", "Settings"):
        assert f'title="{page_title}"' in source
