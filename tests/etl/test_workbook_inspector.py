from src.etl.workbook_inspector import select_platform_sheets


def test_first_google_sheet_is_selected() -> None:
    selected = select_platform_sheets(["README", "FB", "TT Daily", "GG Source A", "GG Source B"])
    assert selected == {"FB": "FB", "TT": "TT Daily", "GG": "GG Source A"}

