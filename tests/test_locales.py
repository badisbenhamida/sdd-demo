"""Acceptance tests for the locale catalogue.

Implements: GRT-007
"""

import pytest

from src.greeting_service.locales import (
    CONFIG_PATH,
    LocaleConfigError,
    load_catalogue,
)

APPROVED_LANGUAGES = {"en", "fr", "de", "es", "ja"}


# Implements: GRT-007
def test_catalogue_supports_exactly_the_approved_languages():
    """GRT-007 — en, fr, de, es, ja. No more, no fewer.

    Asserts set equality rather than membership: a sixth language shipping
    unnoticed is as much a breach of GRT-007 as a missing one, and would
    change what the service advertises without a spec change.
    """
    assert set(load_catalogue()) == APPROVED_LANGUAGES


# Implements: GRT-007
def test_every_approved_language_has_non_empty_text():
    catalogue = load_catalogue()

    for language in APPROVED_LANGUAGES:
        assert catalogue[language].strip()


# Implements: GRT-007
def test_catalogue_is_loaded_from_the_config_file():
    """The supported set comes from config/locales.yml, not from code.

    Guards the drift AMB-008 and decision D5 were meant to prevent: a second
    place declaring which languages exist could disagree with the text.
    """
    assert CONFIG_PATH.name == "locales.yml"
    assert CONFIG_PATH.parent.name == "config"


# Implements: GRT-007
@pytest.mark.parametrize(
    ("content", "reason"),
    [
        ("", "empty file"),
        ("[]", "not a mapping"),
        ("en: ''", "empty greeting text"),
        ("en: '   '", "whitespace-only greeting text"),
        ("en: 42", "non-string greeting text"),
        ("{unclosed", "invalid YAML"),
    ],
)
# Implements: GRT-007
def test_unusable_catalogue_is_rejected(tmp_path, content, reason):
    """An unusable catalogue must fail loudly, never load a partial one.

    Startup aborts on any of these (plan.md decision D3) so a service that
    cannot serve greetings never reaches traffic.
    """
    bad = tmp_path / "locales.yml"
    bad.write_text(content, encoding="utf-8")

    with pytest.raises(LocaleConfigError):
        load_catalogue(bad)


# Implements: GRT-007
def test_missing_catalogue_file_is_rejected(tmp_path):
    with pytest.raises(LocaleConfigError):
        load_catalogue(tmp_path / "does-not-exist.yml")
