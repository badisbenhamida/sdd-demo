"""FastAPI application for the Global Greeting Service.

Spec: specs/001-greeting-service/spec.md (approved, G1)
Contract: specs/001-greeting-service/contracts/greeting-api.md
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from .errors import MISSING_LANGUAGE, UNSUPPORTED_LANGUAGE, error_body
from .locales import load_catalogue

app = FastAPI(title="Global Greeting Service")

# Loaded once at import. A failure here aborts startup rather than letting a
# service with no greetings accept traffic (plan.md decision D3).
CATALOGUE = load_catalogue()


@app.get("/health")
def get_health():
    """Report whether the service can actually serve greetings.

    Implements: GRT-005 — "running" and "able to serve" are different states.
    Startup already aborts on an unusable catalogue (decision D3), so this
    re-asserts the same invariant at request time and keeps the unhealthy
    state reachable rather than theoretical.

    503 is not fixed by the spec, which defines only the healthy response; it
    is the same kind of presentation choice as decision D2.
    """
    if not CATALOGUE:
        return JSONResponse(status_code=503, content={"status": "unhealthy"})

    return {"status": "healthy"}


@app.get("/greeting")
def get_greeting(language: str | None = None):
    """Return a greeting in the requested language.

    `language` is declared optional so that this function — not FastAPI —
    decides what a missing language means (plan.md decision D1). Declaring it
    required would make the framework answer first with a 422 carrying no error
    code, which would breach GRT-008 while looking correct.
    """
    if language is None:
        return JSONResponse(
            status_code=400,
            content=error_body(
                MISSING_LANGUAGE, "Query parameter 'language' is required"
            ),
        )

    # Implements: GRT-004 — reject, never substitute. AMB-002 was resolved
    # against a fallback so no user is silently served a language they did not
    # ask for; the caller decides what to display.
    if language not in CATALOGUE:
        return JSONResponse(
            status_code=404,
            content=error_body(
                UNSUPPORTED_LANGUAGE, f"Language '{language}' is not supported"
            ),
        )

    return {"language": language, "greeting": CATALOGUE[language]}
