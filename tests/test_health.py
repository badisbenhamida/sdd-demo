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
from src.main import UNAVAILABLE, app


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


# Implements: GRT-008
#
# GRT-008: "While the Greeting Service's greeting content is not loaded, the
# health indicator shall report unhealthy."
#
# The point is that the process STAYS UP and says so. Failing fast at import
# would be the usual instinct for a config error, but it would leave nothing
# running to answer /health -- an unreachable port is indistinguishable from a
# network fault, and the criterion would be unobservable (research.md R-2).
# "Running but unable to greet" has to be a reachable state to be a testable
# one, which is why the first test below asserts the service responds at all.


@pytest.fixture
def broken_client(monkeypatch, tmp_path):
    """A service whose configuration could not be loaded."""
    missing = tmp_path / "absent.yml"
    monkeypatch.setattr("src.main.load_catalog", lambda: load_catalog(missing))
    with TestClient(app) as test_client:
        yield test_client


def test_a_running_service_with_unloadable_config_still_answers(broken_client):
    """A crash would make this criterion unobservable, not merely untested."""
    response = broken_client.get("/health")

    assert response.status_code == UNAVAILABLE


def test_it_reports_unhealthy_in_the_body_too(broken_client):
    body = broken_client.get("/health").json()

    assert body["status"] == "unhealthy"
    assert body["locales_loaded"] == 0
    assert body["detail"], "operations needs to know why, not just that"


def test_greetings_are_refused_rather_than_invented(broken_client):
    """With no catalog there is no default to fall back to.

    A greeting served here would mean a hardcoded literal survived in src/,
    breaking config exclusivity (research.md R-4). This is deliberately NOT
    the AMB-001 fallback path: that ruling governs unsupported locales, which
    presumes a catalog to be unsupported against.
    """
    response = broken_client.get("/greeting", params={"locale": "fr-FR"})

    assert response.status_code == UNAVAILABLE
    assert "message" not in response.json()


def test_a_malformed_config_is_unhealthy_not_merely_empty(monkeypatch, tmp_path):
    """Every failure path reaches the same observable state."""
    broken = tmp_path / "locales.yml"
    broken.write_text("default: en-US\nlocales: [not, a, mapping]\n",
                      encoding="utf-8")
    monkeypatch.setattr("src.main.load_catalog", lambda: load_catalog(broken))

    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == UNAVAILABLE
    assert response.json()["status"] == "unhealthy"


def test_process_liveness_alone_is_not_health(broken_client):
    """The AMB-004 ruling: up is not the same as able to greet."""
    assert broken_client.get("/openapi.json").status_code == 200
    assert broken_client.get("/health").status_code == UNAVAILABLE
