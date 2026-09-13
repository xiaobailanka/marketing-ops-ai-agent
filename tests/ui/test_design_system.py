from src.ui.components import pill
from src.ui.theme import COLORS, GLOBAL_CSS


def test_native_theme_adapter_matches_shared_tokens() -> None:
    import tomllib
    from pathlib import Path

    root = Path(__file__).resolve().parents[2]
    with (root / ".streamlit/config.toml").open("rb") as source:
        theme = tomllib.load(source)["theme"]
    for native, shared in (("primaryColor", "primary"), ("backgroundColor", "canvas"),
                           ("secondaryBackgroundColor", "surface"), ("textColor", "ink")):
        assert theme[native] == COLORS[shared]


def test_text_and_semantic_statuses_meet_normal_text_contrast() -> None:
    def luminance(color):
        channels = [int(color[i:i+2], 16) / 255 for i in (1, 3, 5)]
        linear = [x / 12.92 if x <= .04045 else ((x + .055) / 1.055) ** 2.4 for x in channels]
        return sum(x * weight for x, weight in zip(linear, (.2126, .7152, .0722)))

    pairs = [("ink", "surface"), ("muted", "canvas"), ("surface", "primary"),
             ("success", "success_soft"), ("warning", "warning_soft"), ("error", "error_soft")]
    for foreground, background in pairs:
        light, dark = sorted((luminance(COLORS[foreground]), luminance(COLORS[background])), reverse=True)
        assert (light + .05) / (dark + .05) >= 4.5, (foreground, background)


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


def test_interface_v2_targets_current_framework_controls() -> None:
    assert '[role="tablist"]' in GLOBAL_CSS
    assert '[role="tab"][aria-selected="true"]' in GLOBAL_CSS
    assert 'input[role="combobox"]' in GLOBAL_CSS
    assert COLORS["nav"] == "#FFFFFF"
