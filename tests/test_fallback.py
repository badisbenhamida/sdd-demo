"""Acceptance tests for unsupported-language handling.

# Implements: GRT-005

GRT-005: "If a calling application requests a greeting for a language the
Greeting Service does not support, then the Greeting Service shall return a
greeting in the configured default language rather than an error, and shall
not fail unhandled."

Note for readers expecting a rejection: there is none, deliberately. The
Ambiguity Log item AMB-001 asked the business whether an unsupported language
should be an error or a default-language fallback, and Gate G1 (PO: Marco,
2026-08-12) ruled for the fallback: "An unsupported language is a successful
response carrying a default-language greeting plus an explicit fallback
indicator, not an error." So a 4xx here would be spec drift, and the first
test below asserts against exactly that regression.

The fallback INDICATOR is GRT-006 and is not claimed by this module — it has
its own task (T3.2) and stays uncovered until then.
"""

import pytest
from fastapi.testclient import TestClient

from src.config import LocaleCatalog, load_catalog
from src.greetings import resolve
from src.main import app

UNSUPPORTED = "pt-BR"


@pytest.fixture
def client():
    # Context manager form: it runs the lifespan handler, which is what loads
    # the catalog. A bare TestClient(app) would leave app.state.catalog unset.
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def catalog():
    return load_catalog()


def test_unsupported_locale_is_not_an_error(client):
    """A 4xx/5xx here would be the AMB-001 ruling being reversed in code."""
    response = client.get("/greeting", params={"locale": UNSUPPORTED})

    assert response.status_code == 200, (
        f"GRT-005 requires a greeting 'rather than an error'; got "
        f"{response.status_code}. Per the G1 ruling on AMB-001, no calling "
        f"application should need error handling to display a greeting."
    )


def test_unsupported_locale_returns_the_configured_default_greeting(client, catalog):
    """The substituted text must be the default locale's, from configuration."""
    response = client.get("/greeting", params={"locale": UNSUPPORTED})
    body = response.json()

    expected = catalog.greetings[catalog.default]
    assert body["message"] == expected
    assert body["locale"] == catalog.display_names[catalog.default]


def test_unsupported_locale_does_not_fail_unhandled(client):
    """'Shall not fail unhandled' — a served greeting, not an empty body."""
    response = client.get("/greeting", params={"locale": UNSUPPORTED})
    body = response.json()

    assert body["message"], "a greeting must actually be served"
    assert isinstance(body["message"], str)


def test_fallback_resolution_needs_no_filesystem():
    """The rule itself is pure, so it is provable without config on disk.

    This is why lookup lives in greetings.py and I/O in config.py.
    """
    synthetic = LocaleCatalog(
        default="en-us",
        greetings={"en-us": "Hello!", "fr-fr": "Bonjour !"},
        display_names={"en-us": "en-US", "fr-fr": "fr-FR"},
        loaded=True,
    )

    result = resolve(synthetic, "pt-BR")

    assert result.message == "Hello!"
    assert result.locale == "en-US"


def test_every_unsupported_shape_falls_back_rather_than_raising():
    """Anything outside the configured set is unsupported, not an error.

    Per the G1 ruling on AMB-006, membership of the configured set is the
    contract — a bare language code with no region is simply not a member.
    """
    synthetic = LocaleCatalog(
        default="en-us",
        greetings={"en-us": "Hello!"},
        display_names={"en-us": "en-US"},
        loaded=True,
    )

    for requested in ("pt-BR", "fr", "zz-ZZ", "not-a-locale", ""):
        result = resolve(synthetic, requested)
        assert result.message == "Hello!", f"{requested!r} should fall back"
