"""Error codes and body shape for the greeting service.

The `code` is the contract; HTTP status is presentation (plan.md decision D2).
Callers branch on the code, so the status mapping can change to match a platform
convention without touching GRT-004 or GRT-008.

UNSUPPORTED_LANGUAGE and MISSING_LANGUAGE must remain distinct values — that
distinction is the whole content of AMB-009, which lets a miswired caller be
told apart from genuine demand for a language the service does not carry.
"""

UNSUPPORTED_LANGUAGE = "UNSUPPORTED_LANGUAGE"
MISSING_LANGUAGE = "MISSING_LANGUAGE"


def error_body(code: str, message: str) -> dict[str, str]:
    """Build an error body.

    Deliberately carries no `greeting` key. GRT-004 requires that no greeting is
    returned for an unsupported language, and absence is what the acceptance
    test asserts — an empty string would not satisfy it.
    """
    return {"code": code, "message": message}
