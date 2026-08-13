"""Acceptance tests for configuration as the single source of truth.

# Implements: GRT-010

GRT-010: "The Greeting Service shall determine its supported language set and
its default language from configuration, so that adding or changing a language
requires no change to any calling application."

The second test below is the one that matters most. "Loads from configuration"
is easy to satisfy while also carrying a hardcoded safety-net greeting, and
that literal would pass every other test in this suite while breaking the
exclusivity constraint (research.md R-4) and masking the unhealthy state
GRT-008 exists to expose. So it is asserted directly rather than trusted.
"""

from pathlib import Path

import yaml

from src.config import CONFIG_PATH, load_catalog

SRC = Path(__file__).resolve().parents[1] / "src"


def configured() -> dict:
    return yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))


def test_supported_set_and_default_come_from_the_config_file():
    catalog = load_catalog()
    raw = configured()

    assert catalog.loaded
    assert set(catalog.greetings) == {name.lower() for name in raw["locales"]}
    assert catalog.default == raw["default"].lower()
    for name, text in raw["locales"].items():
        assert catalog.greetings[name.lower()] == text


def test_no_greeting_text_is_hardcoded_anywhere_in_src():
    """Every greeting must come from the file, with no literal fallback."""
    sources = {path: path.read_text(encoding="utf-8") for path in SRC.glob("*.py")}

    for text in configured()["locales"].values():
        for path, body in sources.items():
            assert text not in body, (
                f"greeting {text!r} is hardcoded in src/{path.name}. Greeting "
                f"text must come only from {CONFIG_PATH.name} (GRT-010)."
            )


def test_adding_a_locale_needs_no_code_change(tmp_path):
    """A locale absent from src/ entirely becomes supported by config alone."""
    config = tmp_path / "locales.yml"
    config.write_text(
        yaml.safe_dump({"default": "en-US", "locales": {
            "en-US": "Hello!", "is-IS": "Halló!"}}),
        encoding="utf-8",
    )

    catalog = load_catalog(config)

    assert catalog.loaded
    assert catalog.greetings["is-is"] == "Halló!"
    assert catalog.display_names["is-is"] == "is-IS"


def test_a_default_outside_the_configured_set_fails_to_load(tmp_path):
    """Half-working is worse than unhealthy: both fallback paths would break."""
    config = tmp_path / "locales.yml"
    config.write_text(
        yaml.safe_dump({"default": "zz-ZZ", "locales": {"en-US": "Hello!"}}),
        encoding="utf-8",
    )

    catalog = load_catalog(config)

    assert not catalog.loaded
    assert "zz-ZZ" in catalog.error


def test_a_configured_locale_with_no_text_is_not_supported(tmp_path):
    """The spec's 'configured but no greeting behind it' edge case."""
    config = tmp_path / "locales.yml"
    config.write_text(
        yaml.safe_dump({"default": "en-US", "locales": {
            "en-US": "Hello!", "fr-FR": ""}}),
        encoding="utf-8",
    )

    catalog = load_catalog(config)

    assert catalog.loaded
    assert "fr-fr" not in catalog.greetings
