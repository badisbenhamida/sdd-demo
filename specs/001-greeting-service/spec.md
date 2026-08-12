# Specification: Greeting Service

**Spec ID:** 001
**Derived from:** BRD-2026-014 (Global Greeting Service)
**Status:** Approved (Gate G1 passed — PO: Marco, 2026-07-30)
**Notation:** EARS (Easy Approach to Requirements Syntax)

---

## 1. Acceptance Criteria

Each criterion has a stable ID. Tests declare coverage with
`Implements: GRT-###`. The `spec-drift` gate enforces the chain.

| ID | Type | Criterion | Traces to BRD |
|----|------|-----------|---------------|
| GRT-001 | Ubiquitous | The service shall expose `GET /greet` returning JSON with fields `message` (string) and `locale` (string). | BR-1, BR-2 |
| GRT-002 | Event-driven | WHEN a request supplies a supported `locale` query parameter, the service shall return HTTP 200 with the greeting template for that locale. | BR-1 |
| GRT-003 | Event-driven | WHEN a request supplies an unsupported `locale`, the service shall return HTTP 400 with JSON error code `UNSUPPORTED_LOCALE` and the list of supported locales. | BR-3 |
| GRT-004 | Unwanted behavior | IF no `locale` parameter is provided, THEN the service shall respond using the default locale `en-US` with HTTP 200. | BR-1 |
| GRT-005 | State-driven | WHILE locale configuration is not loaded, `GET /health` shall return HTTP 503; once loaded, it shall return HTTP 200 with body `{"status": "ok", "locales_loaded": <count>}`. | BR-4 |
| GRT-006 | Ubiquitous | The service shall load greeting templates exclusively from `config/locales.yml` at startup; templates shall not be hard-coded. | BR-2 |

## 2. Ambiguity Log

> Agent-drafted during BRD→spec transformation; every item resolved by
> a human before Gate G1. This is the artifact that makes the
> transformation step visibly valuable.

| # | BRD gap | Resolution | Resolved by |
|---|---------|-----------|-------------|
| A1 | BR-1 does not define behavior when no language preference is sent. | Fall back to `en-US` (→ GRT-004). | Marco (PO) |
| A2 | BR-3 "handle" is undefined — silent fallback or explicit error? | Explicit 400 with machine-readable code, so callers can react (→ GRT-003). | Marco (PO) |
| A3 | BR-4 does not define "monitorable." | Healthcheck endpoint with load-state semantics (→ GRT-005). | Ops liaison |
| A4 | BRD silent on transport/format. | JSON over HTTP, per constitution defaults (→ GRT-001). | Tech lead (Dana) |

## 3. Retired Criteria

*(none — section exists so retirement is additive, per constitution Art. I.2)*

