from src.ui.components import pill
from src.ui.theme import COLORS, GLOBAL_CSS


def test_semantic_status_colors_are_distinct() -> None:
    assert len({COLORS["success"], COLORS["warning"], COLORS["error"]}) == 3
    assert COLORS["primary"] != COLORS["error"]


def test_global_css_contains_responsive_and_navigation_rules() -> None:
    assert "@media (max-width: 720px)" in GLOBAL_CSS
    assert 'data-testid="stSidebarNav"' in GLOBAL_CSS
    assert "mops-kpi-grid" in GLOBAL_CSS


def test_status_pill_escapes_untrusted_text() -> None:
    rendered = pill('<script>alert("x")</script>', "error")
    assert "<script>" not in rendered
    assert "&lt;script&gt;" in rendered
