"""Acceptance tests for the greeting service's error paths.

Implements: GRT-004
"""

import pytest
from fastapi.testclient import TestClient

from src.greeting_service.app import app
from src.greeting_service.errors import UNSUPPORTED_LANGUAGE


@pytest.fixture(name="client")
def _client() -> TestClient:
    return TestClient(app)


# Implements: GRT-004
def test_unsupported_language_returns_unsupported_language_error(client):
    """GRT-004 — an unsupported language is rejected, not substituted."""
    response = client.get("/greeting", params={"language": "xx"})

    assert response.status_code == 404
    assert response.json()["code"] == UNSUPPORTED_LANGUAGE


# Implements: GRT-004
def test_unsupported_language_returns_no_greeting(client):
    """GRT-004 — "shall not return a greeting". Absence, not an empty string.

    AMB-002 was resolved against a fallback: the caller decides what to show,
    so no user is ever silently served a language they did not ask for.
    """
    response = client.get("/greeting", params={"language": "xx"})
    body = response.json()

    assert "greeting" not in body


# Implements: GRT-004
def test_unsupported_language_leaks_no_fallback_text(client):
    """GRT-004 — no supported greeting may appear anywhere in the response.

    Guards the failure mode AMB-002 rejected: a fallback smuggled into the
    error body would satisfy the two assertions above and still breach the
    criterion.
    """
    supported = client.get("/greeting", params={"language": "en"}).json()["greeting"]
    response = client.get("/greeting", params={"language": "xx"})

    assert supported not in response.text
