"""Acceptance tests for the operations health indicator.

# Implements: GRT-007

GRT-007: "The Greeting Service shall expose a health indicator that operations
can query to determine whether the service is able to serve greetings."

The HTTP status carries the same signal as the body, deliberately: a monitor
that does not parse JSON must still read the answer correctly. Metrics, log
aggregation, and alerting are absent because they were ruled out of scope at
G1 (AMB-004) -- deferred, not forgotten.
"""

import pytest
from fastapi.testclient import TestClient

from src.config import load_catalog
from src.main import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_health_is_queryable_without_making_a_greeting_request(client):
    """Operations must not have to infer health from a greeting response."""
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_health_reports_how_many_locales_are_loaded(client):
    """A green check that is also informative."""
    body = client.get("/health").json()

    assert body["locales_loaded"] == len(load_catalog().greetings)


def test_a_healthy_service_reports_no_failure_detail(client):
    body = client.get("/health").json()

    assert body.get("detail") is None
