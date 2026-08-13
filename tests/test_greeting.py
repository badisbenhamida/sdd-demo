"""Acceptance tests for the greeting interface.

The `# Implements: GRT-###` annotations are the contract between spec and
code (constitution Art. II.1). scripts/spec_drift.py harvests them, and a
criterion with no annotation here fails the required check on main.
"""

import pytest
from fastapi.testclient import TestClient

from src.config import DEFAULT_LANGUAGE
from src.main import LOCALES, app

client = TestClient(app)


def _unsupported_language() -> str:
    """A language identifier the configured table does not carry.

    Derived rather than hardcoded. The supported-language set is
    business-owned configuration (AMB-001 ruling), so a literal like
    "fr" could become supported tomorrow and silently invert the
    assertion instead of failing it.
    """
    candidate = "zz"
    while candidate in LOCALES:
        candidate += "z"
    return candidate


def _a_configured_language() -> str:
    """Any language the table actually carries, preferring a non-default one.

    Also derived rather than hardcoded (AMB-001): a literal "fr" would
    test the configuration rather than the code, and would break the day
    the business changes the launch set.
    """
    non_default = sorted(set(LOCALES) - {DEFAULT_LANGUAGE})
    return non_default[0] if non_default else DEFAULT_LANGUAGE


# Implements: GRT-005
def test_unsupported_language_falls_back_to_default_and_says_so():
    """GRT-005: fall back to the default language, and say that you did.

    Status is 200, not an error. The approved spec rules
    fallback-with-notice (AMB-003): a fallback is a successful request
    that reports a gap, so callers treating non-2xx as an exception
    still render a greeting.
    """
    unsupported = _unsupported_language()

    response = client.get("/greeting", params={"lang": unsupported})

    assert response.status_code == 200
    body = response.json()
    assert body["message"] == LOCALES[DEFAULT_LANGUAGE]
    assert body["language"] == DEFAULT_LANGUAGE
    assert body["requested_language"] == unsupported
    assert body["fallback"] is True
    assert body["message"], "a fallback must still yield a usable greeting"


# Implements: GRT-005
def test_unsupported_language_response_is_identical_on_repeat():
    """GRT-005: the same unsupported request yields the same response.

    The spec's second acceptance scenario for this story. Holds because
    the locale table is immutable for the process lifetime (research R-4).
    """
    unsupported = _unsupported_language()

    bodies = [
        client.get("/greeting", params={"lang": unsupported}).json()
        for _ in range(3)
    ]

    assert bodies[0] == bodies[1] == bodies[2]


# Implements: GRT-002
def test_no_language_preference_returns_the_default_language():
    """GRT-002: no preference supplied -> the configured default, English.

    `fallback` stays False here. Asking for nothing is not a failed
    request: the caller expressed no preference, so serving the default
    is the correct answer rather than a substitution for one.
    """
    response = client.get("/greeting")

    assert response.status_code == 200
    body = response.json()
    assert body["message"] == LOCALES[DEFAULT_LANGUAGE]
    assert body["language"] == DEFAULT_LANGUAGE
    assert body["requested_language"] is None
    assert body["fallback"] is False


# Implements: GRT-004
def test_same_language_yields_identical_text_for_every_caller():
    """GRT-004: one language, one text — regardless of who asks or from where.

    Three independent clients stand in for three regional applications,
    each declaring a different region. The service carries no caller
    identity at all (data-model.md), so there is nothing that *could*
    vary; this asserts that stays true.

    Byte-identity is the measure, per SC-003: zero text variants per
    language across all consumers.
    """
    language = _a_configured_language()
    regions = [None, "emea", "apac"]

    bodies = []
    for region in regions:
        headers = {"X-Region": region} if region else {}
        # A fresh client per caller — not one shared session.
        response = TestClient(app).get(
            "/greeting", params={"lang": language}, headers=headers
        )
        assert response.status_code == 200
        bodies.append(response.json())

    assert len({body["message"] for body in bodies}) == 1
    assert bodies[0] == bodies[1] == bodies[2]


# Implements: GRT-001
@pytest.mark.parametrize("language", sorted(LOCALES))
def test_supported_language_returns_that_language(language):
    """GRT-001: a supported language preference yields that language's text.

    Parameterised over whatever the table currently carries rather than
    a fixed list. Under the AMB-001 ruling the supported set is
    business-owned configuration, so this test grows with the launch set
    instead of needing an edit each time it changes.
    """
    response = client.get("/greeting", params={"lang": language})

    assert response.status_code == 200
    body = response.json()
    assert body["message"] == LOCALES[language]
    assert body["language"] == language
    assert body["requested_language"] == language
    assert body["fallback"] is False


# Implements: GRT-001
def test_the_configured_table_carries_more_than_the_default():
    """GRT-001 is only meaningfully exercised with a real choice of language.

    data-model.md requires the acceptance tests to exercise the default
    plus at least two further languages. Without this, the parameterised
    test above could silently shrink to a single default-language case
    and still pass, covering GRT-001 in name only.
    """
    assert len(LOCALES) >= 3, "config/locales.yml must carry en plus two more"
    assert DEFAULT_LANGUAGE in LOCALES
