"""Language resolution, including the GRT-005 fallback decision.

The whole behavioural core of the service is the table in data-model.md,
reproduced by `resolve` below. It carries no caller identity by design:
there is nothing here that could differ between two callers asking for
the same language, which is what makes GRT-004 structural rather than a
property somebody has to remember to preserve.
"""

from typing import Dict, NamedTuple, Optional

from src.config import DEFAULT_LANGUAGE


class Greeting(NamedTuple):
    """One response, in the shape contracts/greeting-api.yaml publishes."""

    message: str
    language: str
    requested_language: Optional[str]
    fallback: bool


def resolve(locales: Dict[str, str], requested: Optional[str]) -> Greeting:
    """Pick the greeting for a caller's language preference.

    Three cases, matching the resolution table in data-model.md:

    - no preference supplied -> the default language          (GRT-002)
    - a supported language   -> that language                 (GRT-001)
    - an unsupported language -> the default, flagged         (GRT-005)

    The third case is a *fallback, not a rejection*. The approved spec
    (AMB-003 ruling) requires the end user to still see a greeting while
    the caller can detect and report the gap, so the unsupported path
    returns text plus `fallback=True` rather than an error.

    No distinction is drawn between "a real language we do not carry" and
    "not a language at all": the spec treats both as one deterministic
    outcome, so an unrecognised or malformed identifier takes this same
    path rather than a second failure mode no criterion describes.
    """
    if requested is not None and requested in locales:
        return Greeting(
            message=locales[requested],
            language=requested,
            requested_language=requested,
            fallback=False,
        )

    return Greeting(
        message=locales[DEFAULT_LANGUAGE],
        language=DEFAULT_LANGUAGE,
        requested_language=requested,
        # True only when the caller asked for something we could not
        # serve. Asking for nothing is not a fallback — it is GRT-002.
        fallback=requested is not None,
    )
