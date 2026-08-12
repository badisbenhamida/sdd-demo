"""Acceptance tests for the Greeting Service.

Each test declares the criterion it covers with an `Implements:` marker.
scripts/spec_drift.py parses these markers and fails CI if any GRT
criterion is uncovered or any marker points at an unknown/retired ID.
"""

import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from greeting_service.app import app, _state  # noqa: E402


def client() -> TestClient:
    return TestClient(app)  # context-less: startup runs on first request


def test_greet_returns_json_shape():
    # Implements: GRT-001
    with TestClient(app) as c:
        body = c.get("/greet").json()
    assert set(body) == {"message", "locale"}
    assert isinstance(body["message"], str) and isinstance(body["locale"], str)


def test_supported_locale_returns_template():
    # Implements: GRT-002
    with TestClient(app) as c:
        resp = c.get("/greet", params={"locale": "fr-FR"})
    assert resp.status_code == 200
    assert resp.json() == {"message": "Bonjour !", "locale": "fr-FR"}


def test_unsupported_locale_rejected_explicitly():
    # Implements: GRT-003
    with TestClient(app) as c:
        resp = c.get("/greet", params={"locale": "xx-XX"})
    assert resp.status_code == 400
    body = resp.json()
    assert body["error"] == "UNSUPPORTED_LOCALE"
    assert "en-US" in body["supported_locales"]


def test_missing_locale_falls_back_to_default():
    # Implements: GRT-004
    with TestClient(app) as c:
        resp = c.get("/greet")
    assert resp.status_code == 200
    assert resp.json()["locale"] == "en-US"


def test_health_reflects_config_load_state():
    # Implements: GRT-005
    _state["loaded"] = False
    with TestClient(app) as c:  # startup not yet run inside client
        # TestClient runs startup on __enter__, so capture pre-state via raw app
        pass
    # Pre-load behavior: simulate unloaded state directly.
    _state["loaded"] = False
    bare = TestClient(app)  # no context manager → no startup event
    assert bare.get("/health").status_code == 503
    # Post-load behavior.
    with TestClient(app) as c:
        resp = c.get("/health")
    assert resp.status_code == 200
    assert resp.json()["locales_loaded"] >= 4


def test_templates_loaded_from_config_not_hardcoded():
    # Implements: GRT-006
    import greeting_service.app as mod

    source = Path(mod.__file__).read_text(encoding="utf-8")
    assert "Bonjour" not in source, "greeting text must live in locales.yml only"
    with TestClient(app) as c:
        assert c.get("/greet", params={"locale": "de-DE"}).json()["message"] == "Hallo!"
