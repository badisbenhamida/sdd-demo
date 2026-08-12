"""Acceptance tests for the greeting service's error paths.

Implements: GRT-004, GRT-008
"""

import pytest
from fastapi.testclient import TestClient

from src.greeting_service.app import app
from src.greeting_service.errors import MISSING_LANGUAGE, UNSUPPORTED_LANGUAGE


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


# Implements: GRT-008
def test_missing_language_returns_missing_language_error(client):
    """GRT-008 — no language supplied is its own failure, not an unsupported one."""
    response = client.get("/greeting")

    assert response.status_code == 400
    assert response.json()["code"] == MISSING_LANGUAGE


# Implements: GRT-008
def test_missing_language_is_not_a_framework_validation_error(client):
    """GRT-008 — the service answers, not FastAPI.

    This is decision D1 in plan.md. Declaring `language` as a required query
    parameter is the natural way to write this endpoint, and it makes FastAPI
    return its own 422 with a Pydantic body carrying no error code. That
    implementation looks correct and breaches GRT-008. This test is what
    catches it.
    """
    response = client.get("/greeting")

    assert response.status_code != 422
    assert "code" in response.json()


# Implements: GRT-008
def test_missing_language_returns_no_greeting(client):
    response = client.get("/greeting")

    assert "greeting" not in response.json()


# Implements: GRT-004, GRT-008
def test_the_two_error_codes_are_distinct(client):
    """The whole content of AMB-009.

    A miswired caller that forgot the parameter must be distinguishable from
    genuine demand for a language the service does not carry — otherwise an
    integration bug and a coverage gap look identical in the logs.
    """
    missing = client.get("/greeting").json()["code"]
    unsupported = client.get("/greeting", params={"language": "xx"}).json()["code"]

    assert missing != unsupported
    assert {missing, unsupported} == {MISSING_LANGUAGE, UNSUPPORTED_LANGUAGE}


# Implements: GRT-004, GRT-008
def test_error_paths_are_distinguishable_by_status_too(client):
    """Status codes differ as well, per plan.md decision D2.

    Callers are told to branch on `code`, so this is a weaker guarantee than
    the one above — but a caller reading only the status must not be misled.
    """
    missing = client.get("/greeting")
    unsupported = client.get("/greeting", params={"language": "xx"})

    assert missing.status_code != unsupported.status_code
