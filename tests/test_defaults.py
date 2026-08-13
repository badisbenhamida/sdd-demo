"""Acceptance tests for the no-preference default.

# Implements: GRT-002

GRT-002: "When a calling application requests a greeting without naming a
language preference, the Greeting Service shall return a greeting in the
configured default language."

The sharp edge here is that this is NOT a fallback. The caller expressed no
preference, so nothing was substituted against their wishes -- flagging it
would make the indicator useless for the log-the-gap purpose the G1 ruling on
AMB-001 gave it. A future change that folds "no locale" into the fallback path
would still serve the right text and is caught only by the fallback assertion.
"""

import pytest
import yaml
from fastapi.testclient import TestClient

from src.config import CONFIG_PATH, LocaleCatalog
from src.greetings import resolve
from src.main import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def raw():
    return yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))


def test_no_locale_returns_the_configured_default(client, raw):
    response = client.get("/greeting")

    assert response.status_code == 200
    body = response.json()
    assert body["locale"] == raw["default"]
    assert body["message"] == raw["locales"][raw["default"]]


def test_no_locale_is_not_reported_as_a_fallback(client, raw):
    body = client.get("/greeting").json()

    assert body["fallback"] is False, (
        "no preference was expressed, so nothing was substituted against the "
        "caller's wishes; reporting a fallback would make the flag useless "
        "for detecting genuine gaps (G1 ruling on AMB-001)."
    )
    assert body["requested_locale"] == raw["default"]


def test_an_empty_locale_is_a_request_not_an_omission(client, raw):
    """An explicit empty value is an unsupported identifier, so it falls back.

    Distinct from omitting the parameter: the caller did send something, and
    membership of the configured set is the contract (G1 ruling on AMB-006).
    """
    body = client.get("/greeting", params={"locale": ""}).json()

    assert body["message"] == raw["locales"][raw["default"]]
    assert body["fallback"] is True
    assert body["requested_locale"] == ""


def test_the_default_follows_configuration_not_code():
    """Change the configured default and the no-preference answer changes."""
    catalog = LocaleCatalog(
        default="ja-jp",
        greetings={"en-us": "Hello!", "ja-jp": "Konnichiwa!"},
        display_names={"en-us": "en-US", "ja-jp": "ja-JP"},
        loaded=True,
    )

    result = resolve(catalog, None)

    assert result.message == "Konnichiwa!"
    assert result.locale == "ja-JP"
    assert result.fallback is False
