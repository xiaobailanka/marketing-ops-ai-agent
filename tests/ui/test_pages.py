from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize(
    "page_path",
    [
        "app.py",
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
