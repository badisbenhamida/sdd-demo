"""Acceptance tests for the greeting interface.

The `# Implements: GRT-###` annotations are the contract between spec and
code (constitution Art. II.1). scripts/spec_drift.py harvests them, and a
criterion with no annotation here fails the required check on main.
"""

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
