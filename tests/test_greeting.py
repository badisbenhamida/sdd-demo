"""Acceptance tests for greeting retrieval in the requested language.

# Implements: GRT-001

GRT-001: "When a calling application requests a greeting for a supported
language, the Greeting Service shall return a greeting in that language."

Expected text is read from config/locales.yml rather than written literally
here. A test carrying its own copy of the greeting would still pass if the
service stopped reading the file and served a hardcoded string, which is the
exact regression GRT-010 forbids.
"""

import pytest
import yaml
from fastapi.testclient import TestClient

from src.config import CONFIG_PATH
from src.main import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def configured():
    return yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))["locales"]


def test_each_supported_locale_returns_its_own_language(client, configured):
    for locale, expected in configured.items():
        response = client.get("/greeting", params={"locale": locale})

        assert response.status_code == 200
        body = response.json()
        assert body["message"] == expected, f"{locale} served the wrong language"
        assert body["locale"] == locale
        assert body["fallback"] is False


def test_a_supported_locale_is_never_reported_as_a_fallback(client, configured):
    """Guards the boundary between GRT-001 and GRT-005."""
    for locale in configured:
        body = client.get("/greeting", params={"locale": locale}).json()

        assert body["fallback"] is False
        assert body["requested_locale"] == locale


# Implements: GRT-004
#
# GRT-004: "When two calling applications request a greeting for the same
# language, the Greeting Service shall return identical greeting text to both."
#
# Resolution is a pure function of the locale and the loaded catalog, so this
# holds by construction. These tests exist to catch a future change that makes
# it stop holding -- caller-specific text, or per-request variation.


def test_two_calling_applications_receive_identical_text(client, configured):
    """Different callers, distinguished as far as the interface allows."""
    for locale in configured:
        app_a = client.get(
            "/greeting",
            params={"locale": locale},
            headers={"User-Agent": "regional-app-emea/1.0"},
        )
        app_b = client.get(
            "/greeting",
            params={"locale": locale},
            headers={"User-Agent": "regional-app-apac/2.3"},
        )

        assert app_a.json() == app_b.json(), (
            f"{locale} served different payloads to different callers"
        )


def test_repeated_requests_do_not_drift(client):
    """No per-request variation: not time-of-day, not rotation, not order."""
    responses = [client.get("/greeting", params={"locale": "fr-FR"}).json()
                 for _ in range(5)]

    assert all(response == responses[0] for response in responses)


# Implements: GRT-009
#
# GRT-009: "When a calling application requests a greeting using a supported
# language identifier that differs only in letter case, the Greeting Service
# shall treat it as that supported language."
#
# Ruled at G1 on AMB-006. The response echoes the CONFIGURED spelling, not the
# caller's -- a caller asking for FR-fr gets locale "fr-FR" back, which is more
# useful than a mirror of their own typo.


@pytest.mark.parametrize("variant", ["fr-FR", "fr-fr", "FR-FR", "FR-fr", "Fr-Fr"])
def test_case_variants_resolve_to_the_same_locale(client, configured, variant):
    body = client.get("/greeting", params={"locale": variant}).json()

    assert body["message"] == configured["fr-FR"]
    assert body["fallback"] is False, (
        f"{variant!r} differs from a supported locale only in case, so it must "
        f"never fall back (GRT-009)."
    )


@pytest.mark.parametrize("variant", ["fr-fr", "FR-FR", "FR-fr"])
def test_the_response_echoes_the_configured_spelling(client, variant):
    body = client.get("/greeting", params={"locale": variant}).json()

    assert body["locale"] == "fr-FR"
    assert body["requested_locale"] == variant
