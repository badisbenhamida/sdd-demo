"""Acceptance tests for the service's public interface.

Implements: GRT-003
"""

import pytest
from fastapi.testclient import TestClient

from src.greeting_service.app import app
from src.greeting_service.locales import load_catalogue

# FastAPI mounts these itself; they are not part of the service's contract.
FRAMEWORK_ROUTES = {"/openapi.json", "/docs", "/docs/oauth2-redirect", "/redoc"}

DOCUMENTED_ROUTES = {"/greeting", "/health"}


@pytest.fixture(name="client")
def _client() -> TestClient:
    return TestClient(app)


def _service_routes() -> set[str]:
    return {
        route.path
        for route in app.routes
        if getattr(route, "path", None) and route.path not in FRAMEWORK_ROUTES
    }


# Implements: GRT-003
def test_service_exposes_only_the_documented_routes():
    """GRT-003 — one interface, not a per-application collection.

    BRD §1 blames duplicated, divergent greeting implementations. A private
    variant added for one regional app would recreate exactly that, so the
    assertion is set equality: an undocumented route is a breach even if it
    works.
    """
    assert _service_routes() == DOCUMENTED_ROUTES


# Implements: GRT-003
def test_one_greeting_endpoint_serves_every_caller(client):
    """The same path and shape regardless of who is calling.

    Callers are not identified at all (AMB-004), so there is nothing the
    service could use to vary its interface by application even in principle.
    """
    callers = [
        {"User-Agent": "regional-app-emea"},
        {"User-Agent": "regional-app-apac"},
        {"User-Agent": "regional-app-amer"},
    ]

    responses = [
        client.get("/greeting", params={"language": "es"}, headers=headers)
        for headers in callers
    ]

    assert {r.status_code for r in responses} == {200}
    assert len({r.text for r in responses}) == 1


# Implements: GRT-003
def test_every_supported_language_is_reachable_through_the_same_endpoint(client):
    """No language requires a caller to use a different path."""
    for language in load_catalogue():
        response = client.get("/greeting", params={"language": language})

        assert response.status_code == 200
        assert response.request.url.path == "/greeting"
