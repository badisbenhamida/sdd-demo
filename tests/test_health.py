"""Acceptance tests for the health indicator.

Implements: GRT-005
"""

import pytest
from fastapi.testclient import TestClient

from src.greeting_service import app as app_module
from src.greeting_service.app import app


@pytest.fixture(name="client")
def _client() -> TestClient:
    return TestClient(app)


# Implements: GRT-005
def test_health_reports_healthy_when_the_catalogue_is_loaded(client):
    """GRT-005 — operations can confirm the service can serve greetings."""
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


# Implements: GRT-005
def test_health_does_not_report_healthy_when_the_catalogue_is_empty(
    client, monkeypatch
):
    """GRT-005 — running is not the same as able to serve.

    The spec's edge case: a service that is up but cannot produce a greeting
    must not report healthy. A static {"status": "ok"} would satisfy the test
    above and fail this one.
    """
    monkeypatch.setattr(app_module, "CATALOGUE", {})

    response = client.get("/health")

    assert response.json()["status"] != "healthy"
    assert response.status_code != 200


# Implements: GRT-005
def test_health_needs_no_greeting_request(client):
    """Operations must not have to ask for a greeting on a real user's behalf."""
    response = client.get("/health")

    assert "greeting" not in response.json()
