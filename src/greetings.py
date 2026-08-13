"""Locale resolution — a pure function of the catalog and the request.

No I/O, no clock, no caller identity. Kept separate from config.py so the
fallback rule can be proved without a filesystem, and so that identical text
for every caller (GRT-004) holds by construction rather than by convention.
"""

from __future__ import annotations

from dataclasses import dataclass

from src.config import LocaleCatalog


@dataclass(frozen=True)
class Resolution:
    """What was served, and whether it is what was asked for."""

    message: str
    locale: str
    requested_locale: str
    fallback: bool


def resolve(catalog: LocaleCatalog, requested: str | None) -> Resolution:
    """Resolve a greeting for `requested`, substituting the default if needed.

    Three cases, per specs/001-greeting-service/data-model.md:

    1. No locale asked for      -> default served, fallback False.
    2. Asked-for locale known   -> that locale served, fallback False.
    3. Asked-for locale unknown -> default served, fallback True.  (GRT-005)

    Case 1 is deliberately NOT a fallback. The caller expressed no preference,
    so nothing was substituted against their wishes, and flagging it would make
    the indicator useless for the log-the-gap purpose the G1 ruling gave it.
    """
    default_text = catalog.greetings[catalog.default]
    default_display = catalog.default_display

    if requested is None:
        return Resolution(default_text, default_display, default_display, False)

    key = requested.lower()
    if key in catalog.greetings:
        return Resolution(catalog.greetings[key], catalog.display_names[key],
                          requested, False)

    # GRT-005: an unsupported language is a successful response carrying the
    # default-language greeting, not an error. Ruled at G1 on AMB-001 — the
    # rejecting alternative was considered and refused, so returning an error
    # here would be spec drift rather than a stricter reading.
    return Resolution(default_text, default_display, requested, True)
