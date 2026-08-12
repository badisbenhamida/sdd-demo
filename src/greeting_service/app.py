"""Greeting Service — reference implementation.

Spec: specs/001-greeting-service/spec.md
Every behavior below traces to a GRT criterion; see inline references.
"""

from pathlib import Path

import yaml
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse

CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "locales.yml"

app = FastAPI(title="Greeting Service")

# Module-level state so /health can distinguish "not loaded" (GRT-005).
_state: dict = {"loaded": False, "default": None, "greetings": {}}


@app.on_event("startup")
def load_locales() -> None:
    # GRT-006: templates come exclusively from config/locales.yml.
    raw = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    _state["default"] = raw["default_locale"]
    _state["greetings"] = raw["greetings"]
    _state["loaded"] = True


@app.get("/greet")
def greet(locale: str | None = Query(default=None)):
    # GRT-004: no locale → default locale, HTTP 200.
    effective = locale or _state["default"]

    if effective not in _state["greetings"]:
        # GRT-003: unsupported locale → 400 + machine-readable code.
        return JSONResponse(
            status_code=400,
            content={
                "error": "UNSUPPORTED_LOCALE",
                "supported_locales": sorted(_state["greetings"]),
            },
        )

    # GRT-001 / GRT-002: JSON shape {message, locale}, HTTP 200.
    return {"message": _state["greetings"][effective], "locale": effective}


@app.get("/health")
def health():
    # GRT-005: 503 while config not loaded, 200 + counts afterwards.
    if not _state["loaded"]:
        return JSONResponse(status_code=503, content={"status": "loading"})
    return {"status": "ok", "locales_loaded": len(_state["greetings"])}
