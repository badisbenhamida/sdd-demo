"""Acceptance tests for the single greeting interface.

# Implements: GRT-003

GRT-003: "The Greeting Service shall expose one interface through which any
regional application can retrieve a greeting."

"One interface" is the testable part: there must be exactly one greeting route,
not a family of per-application variants, and reaching it must require nothing
application-specific. Authentication and network exposure are deliberately
absent — ruled platform-layer and out of scope at G1 (AMB-003), so a security
scheme appearing here would be scope the business declined.
"""

import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_exactly_one_greeting_route_is_exposed(client):
    """No per-application or per-region variants of the greeting endpoint."""
    paths = client.get("/openapi.json").json()["paths"]
    greeting_paths = [p for p in paths if "greeting" in p]

    assert greeting_paths == ["/greeting"], (
        f"GRT-003 requires one greeting interface; found {greeting_paths}."
    )


def test_any_caller_reaches_it_without_application_specific_setup(client):
    """No credential, header, or registration step stands in front of it."""
    response = client.get("/greeting")

    assert response.status_code == 200


def test_the_greeting_route_accepts_a_plain_get(client):
    """A standard interface: GET with an optional query parameter."""
    operations = client.get("/openapi.json").json()["paths"]["/greeting"]

    assert list(operations) == ["get"]
