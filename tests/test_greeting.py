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
