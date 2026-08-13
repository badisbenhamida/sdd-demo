"""Acceptance tests for the service's interface surface and health.

The `# Implements: GRT-###` annotations are the contract between spec and
code (constitution Art. II.1), harvested by scripts/spec_drift.py.
"""

from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def _served_paths() -> set:
    """Every path this application actually serves."""
    return {route.path for route in app.routes if hasattr(route, "path")}


# Implements: GRT-003
def test_a_single_greeting_interface_serves_every_regional_application():
    """GRT-003: one interface, usable by every regional application.

    This is a negative claim — that no second, per-region greeting
    interface exists — so it asserts the served route set rather than a
    response. Exactly one greeting path, and it takes the region-neutral
    form: no /greeting/emea, no /emea/greeting.

    A test can only hold the route set as it stands today. Nothing here
    stops a second interface being added tomorrow; that is a reviewer's
    job, and plan.md says so rather than implying this test covers it.
    """
    greeting_paths = {path for path in _served_paths() if "greeting" in path}

    assert greeting_paths == {"/greeting"}

    # The same single path answers callers that declare different
    # regions — the interface does not vary by who is calling.
    for region in ("emea", "apac", "amer"):
        response = client.get("/greeting", headers={"X-Region": region})
        assert response.status_code == 200
