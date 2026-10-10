import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CSS = (PROJECT_ROOT / "static" / "style.css").read_text(
    encoding="utf-8"
)
HTML = (PROJECT_ROOT / "templates" / "index.html").read_text(
    encoding="utf-8"
)


def _relative_luminance(hex_color):
    channels = [
        int(hex_color[index:index + 2], 16) / 255
        for index in (1, 3, 5)
    ]

    linear = [
        channel / 12.92
        if channel <= 0.04045
        else ((channel + 0.055) / 1.055) ** 2.4
        for channel in channels
    ]

    return (
        0.2126 * linear[0]
        + 0.7152 * linear[1]
        + 0.0722 * linear[2]
    )


def _contrast_ratio(first, second):
    lighter, darker = sorted(
        (
            _relative_luminance(first),
            _relative_luminance(second)
        ),
        reverse=True
    )

    return (lighter + 0.05) / (darker + 0.05)


def test_ink_and_marigold_tokens_are_present():
    required_tokens = {
        "--bg: #F7F5F0;",
        "--surface: #FFFFFF;",
        "--primary: #1F2A44;",
        "--accent: #E8A33D;",
        "--urgent: #C2410C;",
        "--on-track: #2F7D5B;",
        "--bg: #14161B;",
        "--surface: #1C1F27;",
        "--primary: #8FA3D1;",
        "--accent: #F0B455;"
    }

    css_lines = {
        line.strip()
        for line in CSS.splitlines()
    }

    assert required_tokens.issubset(css_lines)


def test_old_teal_palette_is_removed():
    old_teal_values = {
        "#68bdb5",
        "#8bd0c9",
        "#17312f",
        "#197e77",
        "#106a64",
        "#d9ece9"
    }

    assert not any(
        color in CSS.lower()
        for color in old_teal_values
    )


def test_color_literals_only_appear_in_theme_tokens():
    css_after_theme_tokens = CSS.split("* { box-sizing", 1)[1]

    assert not re.search(
        r"#[0-9a-fA-F]{3,8}(?![0-9a-zA-Z_-])|rgba?\(",
        css_after_theme_tokens
    )


def test_theme_uses_dark_attribute_and_removes_it_for_light():
    first_tag = HTML.splitlines()[1]

    assert first_tag == '<html lang="en">'
    assert 'setAttribute(\n                "data-theme",\n                "dark"' in HTML
    assert 'removeAttribute(\n                "data-theme"' in HTML


def test_status_badges_use_matching_palette_tokens():
    assert "background: var(--urgent-soft);" in CSS
    assert "border-color: var(--urgent);" in CSS
    assert "background: var(--soon-soft);" in CSS
    assert "border-color: var(--soon);" in CSS
    assert "background: var(--on-track-soft);" in CSS
    assert "border-color: var(--on-track);" in CSS
    assert "color: var(--text);" in CSS


def test_selected_controls_and_primary_buttons_use_palette_roles():
    assert "border-color: var(--accent);" in CSS
    assert "background: var(--accent-soft);" in CSS
    assert "color: var(--accent-text);" in CSS
    assert "background: var(--primary);" in CSS
    assert "color: var(--on-primary);" in CSS
    assert "box-shadow: var(--focus-ring);" in CSS


def test_placeholder_uses_dedicated_lighter_token():
    assert "input::placeholder" in CSS
    assert "color: var(--text-placeholder);" in CSS


def test_primary_text_pairs_meet_normal_text_contrast():
    pairs = [
        ("#1C1C1E", "#F7F5F0"),
        ("#5B6070", "#F7F5F0"),
        ("#FFFFFF", "#1F2A44"),
        ("#7A4E0E", "#FBEBD0"),
        ("#1C1C1E", "#FBE4D8"),
        ("#1C1C1E", "#FAEED6"),
        ("#1C1C1E", "#DDF0E6"),
        ("#ECEAE4", "#14161B"),
        ("#A4A9B6", "#14161B"),
        ("#14161B", "#8FA3D1"),
        ("#F4C677", "#3A2C14"),
        ("#ECEAE4", "#3B2016"),
        ("#ECEAE4", "#362A14"),
        ("#ECEAE4", "#16301F")
    ]

    assert all(
        _contrast_ratio(foreground, background) >= 4.5
        for foreground, background in pairs
    )
