from datetime import date

import pandas as pd

from src.connectors.google_sheets.mock import MockGoogleSheetsConnector


def test_mock_sheet_create_then_replace() -> None:
    connector = MockGoogleSheetsConnector({})
    frame = pd.DataFrame({"Spend": [10]})
    first = connector.write_daily_report("demo", date(2026, 8, 26), frame)
    second = connector.write_daily_report("demo", date(2026, 8, 26), frame)
    assert first.action == "CREATED"
    assert second.action == "REPLACED"

