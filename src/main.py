"""HTTP interface for the Global Greeting Service.

One endpoint serves every regional application (GRT-003). The published
contract is specs/001-greeting-service/contracts/greeting-api.yaml.
"""

from typing import Optional

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse

from src.config import LocaleConfigError, load_locales
from src.greetings import resolve

app = FastAPI(title="Global Greeting Service")

# Loaded once, at import, and never reloaded (design D-5, research R-4).
# Re-reading per request would let two callers straddling a config edit
# receive different text for the same language, so GRT-004 would hold
# only between deployments rather than always.
try:
    LOCALES = load_locales()
    LOCALE_ERROR = None  # type: Optional[str]
except LocaleConfigError as exc:
    # Start unhealthy rather than abort (G2 ruling on research R-6):
    # operations gets a definite answer instead of a crash-looping
    # container with the reason buried in logs.
    LOCALES = {}
    LOCALE_ERROR = str(exc)


@app.get("/greeting")
def get_greeting(lang: Optional[str] = Query(default=None)):
    """Return a greeting for the caller's language preference.

    `lang` is passed explicitly by the caller (AMB-005 ruling, design
    D-1) rather than negotiated from a header, so "what did the caller
    ask for?" has one unambiguous answer to echo back on the GRT-005
    fallback path.

    Unsupported languages return **200**, not an error status — see
    `src.greetings.resolve`.
    """
    if LOCALE_ERROR is not None:
        return JSONResponse(status_code=503, content={"status": "unavailable"})

    greeting = resolve(LOCALES, lang)
    return {
        "message": greeting.message,
        "language": greeting.language,
        "requested_language": greeting.requested_language,
        "fallback": greeting.fallback,
    }


@app.get("/health")
def get_health():
    """Report whether the service is available (GRT-006).

    Availability means the locale table loaded. A process accepting
    connections but holding no table cannot serve any greeting, so
    config-load state is not extra observability here — it *is*
    availability (research R-5).

    Deliberately reports nothing else. The AMB-004 ruling scoped this
    release to an availability indication and deferred metrics,
    per-language demand and structured logging to a separate BRD; a
    request count or locale list here would be scope creep past an
    approved gate.
    """
    if LOCALE_ERROR is not None:
        return JSONResponse(status_code=503, content={"status": "unavailable"})

    return {"status": "ok"}
