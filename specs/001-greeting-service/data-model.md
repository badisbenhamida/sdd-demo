# Phase 1 Data Model: Global Greeting Service

**Feature**: `specs/001-greeting-service` | **Date**: 2026-08-12
**Status**: 🔶 DRAFT — supports plan.md, pending G2

**No persistence.** There is no database, no schema, and no migration. The "model" is one
immutable in-memory structure built at startup from `config/locales.yml` (AMB-008), plus
the response shapes callers observe.

---

## Locale catalogue

The single source of greeting text and of the supported-language set (research D4, D5).

| Field | Type | Rules |
|-------|------|-------|
| language code | string, map key | Non-empty. The full key set **is** the supported-language set — nothing else declares it. |
| greeting text | string, map value | Non-empty. Returned verbatim; no interpolation, no per-caller variation (GRT-002). |

**Source**: `config/locales.yml`, read exactly once at startup. Never re-read while
running (research D4).

**Validation at load** — failure aborts startup (research D3):

- File exists and parses as YAML.
- Result is a mapping of string → string.
- No key has empty text.
- Key set equals exactly `{en, fr, de, es, ja}` (GRT-007).

**Lifecycle**: built at startup → immutable → discarded at shutdown. Changing greeting text
requires a release (AMB-008).

**Criteria**: GRT-002, GRT-007.

---

## Greeting response

What a caller receives on success.

| Field | Type | Notes |
|-------|------|-------|
| `language` | string | The language actually served. Always equals the requested language — there is no fallback (AMB-002), so this can never differ from what was asked for. |
| `greeting` | string | Text from the catalogue, verbatim. |

**Criteria**: GRT-001, GRT-002, GRT-006.

---

## Error response

One shape for both error paths. `code` is the contract; HTTP status is presentation
(research D2).

| Field | Type | Notes |
|-------|------|-------|
| `code` | string | `UNSUPPORTED_LANGUAGE` or `MISSING_LANGUAGE`. These two values **must remain distinct** — that distinction is the whole content of AMB-009. |
| `message` | string | Human-readable. Not part of the contract; callers must not parse it. |

Both error responses omit `greeting` entirely. GRT-004 and GRT-008 each require that no
greeting is returned, so absence is asserted in tests, not merely an empty string.

**Criteria**: GRT-004, GRT-008.

---

## Health response

| Field | Type | Notes |
|-------|------|-------|
| `status` | string | Healthy only while a non-empty catalogue is loaded (research D3). |

**Criteria**: GRT-005.

---

## Entities deliberately absent

Each of these would be natural in a greeting service and is excluded by an approved
decision. Their absence is a design requirement, not an oversight:

| Absent entity | Excluded by |
|---------------|-------------|
| User / user identifier | AMB-001, GRT-006 — the service never identifies a user |
| Calling-application identity | AMB-004 — no per-application authorisation |
| Default / fallback language | AMB-002 — errors replaced fallback, so no default exists |
| Request or usage record | AMB-005 — no metrics beyond the health indicator |
| Translation or content record | BRD §3, AMB-008 — no content management |
