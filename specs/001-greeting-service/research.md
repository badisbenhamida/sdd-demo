# Phase 0 Research: Global Greeting Service

**Feature**: `specs/001-greeting-service` | **Date**: 2026-08-12
**Status**: 🔶 DRAFT — supports plan.md, pending G2

The stack was given (Python 3.12, FastAPI, pytest, `config/locales.yml`, no database), so
no technology selection was needed. What follows resolves the design questions that the
approved criteria raise but do not answer.

---

## D1 — Preventing FastAPI's 422 from swallowing GRT-008

**Decision**: Declare `language` as an *optional* query parameter and validate its presence
in application code, returning the `MISSING_LANGUAGE` error explicitly.

**Rationale**: GRT-008 requires a `MISSING_LANGUAGE` error that is *distinct from*
`UNSUPPORTED_LANGUAGE`. FastAPI's natural idiom — a required parameter — makes the
framework answer first, with a `422 Unprocessable Entity` whose body is Pydantic's
validation structure. That response contains neither error code, so a service written the
obvious way passes a naive smoke test and still violates GRT-008. Making the parameter
optional moves the decision into code the tests can pin.

**Alternatives considered**:

- *Required parameter + `RequestValidationError` handler*: works, but couples the error
  contract to Pydantic's internal error shape, and the handler fires for any future
  validation failure — a wide blast radius for one narrow rule.
- *Accept the 422*: rejected. It fails GRT-008 as written.

**Risk if ignored**: this is the most likely path to a green-looking implementation that
breaches the spec. `tests/test_errors.py` must assert the code, not just a 4xx status.

---

## D2 — HTTP status codes for the two error paths

**Decision**: `MISSING_LANGUAGE` → `400 Bad Request`; `UNSUPPORTED_LANGUAGE` →
`404 Not Found`. Both bodies carry a machine-readable `code`, and the contract tells
callers to branch on `code`, not on status.

**Rationale**: the request that omits a language is malformed — the caller made a mistake
(400). The request naming a real-but-uncarried language is well-formed and asks for
something the service does not have (404). Keeping `code` authoritative means this mapping
is a presentation detail that can change without touching GRT-004 or GRT-008.

**Alternatives considered**:

- *400 for both*: simpler, but erases at HTTP level exactly the distinction AMB-009 was
  resolved to preserve. Callers reading only the status could not tell an integration bug
  from genuine unsupported-locale demand.
- *422 for unsupported*: closer to "semantically invalid", but collides with FastAPI's own
  422 (see D1) and would make the two indistinguishable in logs.

**Note for G2**: the spec does not mandate any status code. If the platform has a house
standard for error responses, it overrides this decision — the criteria stay satisfied
either way as long as the two codes remain distinct.

---

## D3 — Health semantics under GRT-005

**Decision**: load and validate `config/locales.yml` once at startup; abort startup on
failure. `/health` reports healthy only while a non-empty catalogue is in memory.

**Rationale**: GRT-005 asks whether the service "is able to serve greetings", and the
spec's edge cases require that a service which is running but cannot serve must not report
healthy. Fail-fast handles the ordinary case (a broken file never reaches traffic), while
the catalogue check keeps the unhealthy state reachable and testable rather than
theoretical.

**Alternatives considered**:

- *Start unhealthy and serve 503s*: more machinery — readiness vs liveness, degraded
  states — none of which BR-4 or AMB-005 asked for.
- *Static `{"status": "ok"}`*: cheapest, but reports healthy for a service that cannot
  serve a single greeting. Fails the spec's edge case.

---

## D4 — Guaranteeing identical text across callers (GRT-002)

**Decision**: one immutable in-memory catalogue, loaded once at startup, returned verbatim.
No per-request formatting, no caller-specific branching, no template interpolation.

**Rationale**: GRT-002 is the criterion that carries the BRD's actual business case (§1:
inconsistent tone, duplicated translation cost). It holds trivially if there is exactly one
source and nothing mutates it. Interpolation would reintroduce per-caller variance, and §3
puts personalization out of scope regardless.

**Alternatives considered**:

- *Re-read the YAML per request*: allows text to change under a running service, which
  contradicts AMB-008 and could serve two callers different text within one deployment —
  a direct GRT-002 violation.

---

## D5 — Locale file shape

**Decision**: a flat mapping of language code → greeting text, with the supported set being
exactly the file's keys.

```yaml
en: "Hello"
fr: "Bonjour"
de: "Hallo"
es: "Hola"
ja: "こんにちは"
```

**Rationale**: makes GRT-007 directly testable — assert the loaded key set equals the five
approved languages — and keeps `config/locales.yml` the single source of both the text and
the supported-language list, so the two cannot drift apart.

**Alternatives considered**:

- *Nested metadata per locale* (display name, region, direction): none of it is required by
  any criterion, and unused structure invites scope the business excluded.
- *Supported list hard-coded separately from the text*: two sources that can disagree; a
  language could be advertised with no text behind it.

---

## D6 — Enforcing statelessness (GRT-006)

**Decision**: the request surface accepts a language and nothing else. No user identifier,
header, cookie, or body field is read.

**Rationale**: GRT-006 says the preference comes from the request and is never looked up.
The cleanest enforcement is to give the service nothing to look up *with* — this is also
why the design has no database (AMB-001 resolved to a stateless service). A test asserts
that a user identifier supplied by a caller has no effect on the response.

---

## Open items for the G2 reviewer

None blocking. Three judgement calls are flagged in plan.md ("Design Decisions Requiring
G2 Attention"): D1, D2 and D3. D2 in particular is the one most likely to be overridden by
an existing platform convention.

**Environment skew**: `.venv` is Python 3.13.2; plan and CI target 3.12. No design decision
here depends on the difference, but the reviewer may want the venv rebuilt on 3.12.
