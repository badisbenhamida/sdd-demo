"""Acceptance tests for greeting retrieval.

Implements: GRT-001, GRT-002, GRT-006
"""

import pytest
from fastapi.testclient import TestClient

from src.greeting_service.app import app
from src.greeting_service.locales import load_catalogue

SUPPORTED = sorted(load_catalogue())


@pytest.fixture(name="client")
def _client() -> TestClient:
    return TestClient(app)


# Implements: GRT-001
@pytest.mark.parametrize("language", SUPPORTED)
def test_supported_language_returns_a_greeting_in_that_language(client, language):
    """GRT-001 — the greeting comes back in the language that was asked for."""
    response = client.get("/greeting", params={"language": language})

    assert response.status_code == 200
    body = response.json()
    assert body["language"] == language
    assert body["greeting"] == load_catalogue()[language]


# Implements: GRT-001
@pytest.mark.parametrize("language", SUPPORTED)
def test_each_language_returns_its_own_distinct_text(client, language):
    """A catalogue that returned one language's text for another would still
    satisfy a naive "returns 200 with a greeting" check."""
    others = {lang for lang in SUPPORTED if lang != language}
    greeting = client.get("/greeting", params={"language": language}).json()["greeting"]

    assert greeting not in {load_catalogue()[lang] for lang in others}


# Implements: GRT-002
@pytest.mark.parametrize("language", SUPPORTED)
def test_independent_callers_receive_identical_text(language):
    """GRT-002 — the business case from BRD §1: one wording, not per-app drift.

    Two separate clients stand in for two regional applications.
    """
    first = TestClient(app).get("/greeting", params={"language": language})
    second = TestClient(app).get("/greeting", params={"language": language})

    assert first.json()["greeting"] == second.json()["greeting"]


# Implements: GRT-002
def test_repeated_requests_are_stable(client):
    """Text must not vary between calls — no rotation, no per-request assembly."""
    responses = {
        client.get("/greeting", params={"language": "fr"}).json()["greeting"]
        for _ in range(5)
    }

    assert len(responses) == 1


# Implements: GRT-006
def test_caller_supplied_user_identifier_does_not_affect_the_response(client):
    """GRT-006 — the language comes from the request, never from a user record.

    AMB-001 was resolved to a stateless service: it holds no user state and
    performs no lookup, so a user identifier must be inert.
    """
    plain = client.get("/greeting", params={"language": "fr"})
    with_user = client.get("/greeting", params={"language": "fr", "user_id": "8842"})

    assert plain.json() == with_user.json()


# Implements: GRT-006
def test_language_is_taken_from_the_request_not_a_profile(client):
    """Two callers claiming different identities get whatever they ask for."""
    first = client.get("/greeting", params={"language": "de", "user_id": "1"})
    second = client.get("/greeting", params={"language": "ja", "user_id": "1"})

    assert first.json()["language"] == "de"
    assert second.json()["language"] == "ja"
