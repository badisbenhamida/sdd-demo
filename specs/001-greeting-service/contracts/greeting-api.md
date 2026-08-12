# Interface Contract: Global Greeting Service

**Feature**: `specs/001-greeting-service` | **Date**: 2026-08-12
**Status**: 🔶 DRAFT — supports plan.md, pending G2

The single interface required by GRT-003. Two endpoints, both read-only, no authentication
(AMB-004).

> **Callers must branch on `code`, not on HTTP status.** Status mapping is presentation
> (research D2) and may be revised to match platform conventions; the `code` values are
> the contract and are fixed by GRT-004 and GRT-008.

---

## `GET /greeting`

Returns a greeting in the requested language.

**Query parameters**

| Name | Required | Notes |
|------|----------|-------|
| `language` | Yes, semantically | Declared *optional* at framework level so the service — not FastAPI — produces the missing-language error (research D1). Absence is a `MISSING_LANGUAGE` error, never a framework 422. |

No other input is read. User identifiers, headers or body fields supplied by a caller have
no effect on the response (GRT-006).

### 200 — success

```json
{ "language": "fr", "greeting": "Bonjour" }
```

`language` always equals the requested language: there is no fallback (AMB-002), so a
caller can trust an exact match without inspecting anything else.

*Criteria: GRT-001, GRT-002, GRT-006.*

### 404 — unsupported language

```json
{ "code": "UNSUPPORTED_LANGUAGE", "message": "Language 'xx' is not supported" }
```

No `greeting` field is present. The business chose this over a fallback so that no user is
ever silently shown a language they did not ask for — every calling application must
handle this response.

*Criterion: GRT-004.*

### 400 — no language supplied

```json
{ "code": "MISSING_LANGUAGE", "message": "Query parameter 'language' is required" }
```

No `greeting` field is present. Deliberately distinct from `UNSUPPORTED_LANGUAGE` so a
miswired caller is distinguishable from genuine demand for an uncarried language (AMB-009).

*Criterion: GRT-008.*

---

## `GET /health`

Reports whether the service can serve greetings.

### 200 — healthy

```json
{ "status": "healthy" }
```

Healthy is reported only while a non-empty locale catalogue is loaded. A service that is
running but cannot serve greetings must not report healthy (research D3).

*Criterion: GRT-005.*

---

## Supported languages

Exactly `en`, `fr`, `de`, `es`, `ja` (GRT-007). The set is the key set of
`config/locales.yml` — there is no second place where it is declared, so the advertised
languages and the available text cannot drift apart (research D5).

Adding a language is a code release, not a runtime operation (AMB-008), and expanding the
set beyond these five is a change to GRT-007 and therefore a spec change under CLAUDE.md.

---

## Not in this contract

| Absent | Excluded by |
|--------|-------------|
| Authentication / caller identity | AMB-004 |
| Fallback or default-language behaviour | AMB-002 |
| Metrics, usage, or logging endpoints | AMB-005 (GRT-009 reserved, unused) |
| Any write operation | Whole feature is read-only |
| Latency or availability guarantees | AMB-006 |
