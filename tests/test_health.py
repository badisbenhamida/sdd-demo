"""Acceptance tests for the service's interface surface and health.

The `# Implements: GRT-###` annotations are the contract between spec and
code (constitution Art. II.1), harvested by scripts/spec_drift.py.
"""

import importlib

from fastapi.testclient import TestClient

import src.config
import src.main
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


# Implements: GRT-006
def test_health_reports_available_when_the_locale_table_loaded():
    """GRT-006: operations can determine the service is available.

    Queryable directly, with no assistance from the owning team (SC-002).

    The payload carries `status` and nothing else. The AMB-004 ruling
    scoped this release to an availability indication and deferred
    metrics, per-language demand and structured logging to a separate
    BRD, so this asserts the *absence* of extra fields too — scope creep
    past an approved gate should fail a test, not pass unnoticed.
    """
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# Implements: GRT-006
def test_health_reports_unavailable_when_the_locale_table_did_not_load(
    tmp_path, monkeypatch
):
    """GRT-006: the failure case, which is the one operations cares about.

    A process accepting connections but holding no locale table cannot
    serve any greeting, so reporting it healthy would mislead exactly
    when the answer matters (research R-5).

    Exercises real startup against a missing config file rather than
    poking the module's state, because the G2 ruling on R-6 is
    specifically about what startup does: begin unhealthy and report it,
    rather than abort.
    """
    monkeypatch.setattr(src.config, "CONFIG_PATH", tmp_path / "absent.yml")
    reloaded = importlib.reload(src.main)
    try:
        response = TestClient(reloaded.app).get("/health")

        assert response.status_code == 503
        assert response.json() == {"status": "unavailable"}
    finally:
        # Restore the good module state for any later test.
        monkeypatch.undo()
        importlib.reload(src.main)
