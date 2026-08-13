"""Global Greeting Service — HTTP surface.

Contract: specs/001-greeting-service/contracts/greeting-api.yaml

The catalog is loaded once at startup and never reloaded. A failed load does
not stop the service: it starts and reports that it cannot greet, so that
"running but unable to serve" is an observable state rather than an
unreachable port (research.md R-2).
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from src.config import LocaleCatalog, load_catalog
from src.greetings import resolve

UNAVAILABLE = 503


def _unavailable(catalog: LocaleCatalog) -> JSONResponse:
    """The one shape both endpoints use to say 'running, cannot greet'."""
    return JSONResponse(
        status_code=UNAVAILABLE,
        content={
            "status": "unhealthy",
            "locales_loaded": 0,
            "detail": catalog.error,
        },
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.catalog = load_catalog()
    yield


app = FastAPI(
    title="Global Greeting Service",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/greeting")
def get_greeting(locale: str | None = None):
    """Return a greeting for `locale`, or the default when it is unknown.

    An unsupported locale is answered with HTTP 200 and the default-language
    greeting, flagged via `fallback` (GRT-005). It is not an error: the Gate G1
    ruling on AMB-001 rejected the erroring alternative so that no calling
    application needs error handling in order to display a greeting.
    """
    catalog = app.state.catalog

    if not catalog.loaded:
        # Not a fallback: with no catalog there is no default to substitute,
        # and inventing one would break config exclusivity (research.md R-4).
        return _unavailable(catalog)

    result = resolve(catalog, locale)
    return {
        "message": result.message,
        "locale": result.locale,
        "requested_locale": result.requested_locale,
        "fallback": result.fallback,
    }


@app.get("/health")
def get_health():
    """Report whether the service can actually serve greetings.

    Reflects catalog load state, not process liveness: a running process that
    could not read its configuration is unhealthy (GRT-008). The HTTP status
    carries the same signal as the body so a monitor that does not parse JSON
    still reads it correctly.
    """
    catalog = app.state.catalog

    if not catalog.loaded:
        return _unavailable(catalog)

    return {"status": "healthy", "locales_loaded": len(catalog.greetings)}
