from pathlib import Path

from streamlit.testing.v1 import AppTest


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _button(app: AppTest, label: str):
    return next(button for button in app.button if button.label == label)


def test_data_cleaning_primary_workflow() -> None:
    app = AppTest.from_file(PROJECT_ROOT / "pages/1_Data_Cleaning.py", default_timeout=30).run()
    app = _button(app, "Run cleaning").click().run(timeout=30)
    assert not app.exception
    assert "cleaning_result" in app.session_state


def test_daily_report_primary_workflow() -> None:
    app = AppTest.from_file(PROJECT_ROOT / "pages/2_Daily_Report.py", default_timeout=30).run()
    app = _button(app, "Generate report").click().run(timeout=30)
    assert not app.exception
    assert "daily_report_result" in app.session_state


def test_fifa_preview_and_idempotent_sync_workflow() -> None:
    app = AppTest.from_file(PROJECT_ROOT / "pages/3_FIFA_Dashboard_Sync.py", default_timeout=30).run()
    app = _button(app, "Preview cleaning").click().run(timeout=30)
    assert not app.exception
    assert "fifa_preview" in app.session_state
    app = _button(app, "Run sync").click().run(timeout=30)
    assert not app.exception
    assert "fifa_sync_result" in app.session_state


def test_google_ads_qc_detect_confirm_and_run_workflow() -> None:
    app = AppTest.from_file(PROJECT_ROOT / "pages/4_Google_Ads_QC.py", default_timeout=30).run()
    app = _button(app, "Detect schema").click().run(timeout=30)
    assert not app.exception
    app = _button(app, "Confirm mapping").click().run(timeout=30)
    assert not app.exception
    app = _button(app, "Run quality control").click().run(timeout=30)
    assert not app.exception
    assert app.session_state["qc_result"].errors == 8


def test_agent_copilot_routes_a_report_command() -> None:
    app = AppTest.from_file(PROJECT_ROOT / "pages/5_Agent_Chat.py", default_timeout=30).run()
    app = _button(app, "Generate UG daily report").click().run(timeout=30)
    assert not app.exception
    assert len(app.session_state["chat_history"]) == 2
