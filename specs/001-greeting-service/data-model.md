# Phase 1 — Data Model: Global Greeting Service

**Feature**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)
**Date**: 2026-08-12

There is no database (plan constraint). "Data model" here means the
in-memory locale table loaded at startup, the shape of the config file it
comes from, and the response payload. Entities are taken from the spec's
Key Entities section; nothing is added that the spec does not name.

---

## Entity: Locale entry

The unit the service stores. One per supported language.

| Field | Type | Required | Notes |
|---|---|---|---|
| `language` | string | yes | Language identifier, the map key. Values are business-owned configuration (AMB-001); the service does not restrict the set |
| `message` | string | yes | The greeting text for that language. The only content the service serves |

**Source**: `config/locales.yml`, exclusively. No locale entry originates
in code — see research R-6.

**Cardinality**: One or more. A table with zero entries is a
misconfiguration, not an empty valid state.

**Mutability**: Immutable for the process lifetime. Loaded once at
startup (research R-4); a config change ships as a restart.

**Validation rules**:

| Rule | Consequence if violated | Serves |
|---|---|---|
| The file exists and parses as YAML | Locale table unavailable → service reports unhealthy | GRT-006 |
| The table contains at least one entry | Locale table unavailable → service reports unhealthy | GRT-006 |
| The table contains the default language `en` | Locale table unavailable → GRT-002 cannot be satisfied, so the service is not serviceable | GRT-002, GRT-006 |
| Each entry's message is a non-empty string | That entry is invalid; treat the config as invalid rather than serving an empty greeting | GRT-001 |

The last rule is deliberately strict. Serving an empty string would
satisfy "returned a greeting" mechanically while showing the end user
nothing — a silent failure of the kind GRT-005's fallback exists to
prevent.

---

## Config file shape: `config/locales.yml`

**Does not exist yet.** Created during implementation by the task that
first needs it (plan constraint). Shape:

```yaml
# Greeting text per language. Business-owned configuration (AMB-001).
# This file is the only source of greeting text — see research R-6.
locales:
  en: "Hello"
  fr: "Bonjour"
  de: "Hallo"
```

Notes:

- `en` is required, because AMB-002 ruled English the default. The
  identifier `en` is a constant in code; the text is not, which is what
  keeps "exclusively from config" true (design D-6).
- The languages beyond `en` shown above are illustrative. The real launch
  set is a business deliverable under the AMB-001 ruling and is not fixed
  by this document. Acceptance tests must exercise the default plus at
  least two further languages, whatever they turn out to be, and must not
  hardcode a specific non-default language — a test that asserts `fr`
  exists would fail the moment the business changes the set, and would be
  testing the config rather than the code.

---

## Entity: Language preference

The caller-supplied indication of which language is wanted.

| Aspect | Value |
|---|---|
| Carried as | Query parameter `lang` on `GET /greeting` (design D-1) |
| Required | No. Absent means "no preference" and triggers the GRT-002 default |
| Permitted values | Not restricted by the service. Any value is accepted; one that is not in the locale table is unsupported and takes the GRT-005 fallback path |

**Why unvalidated**: The spec draws no distinction between "a real
language we do not carry" and "not a language at all". The Edge Cases
section makes this explicit — an unrecognised or malformed identifier is
covered by GRT-005, which treats "cannot be served in the requested
language" as one deterministic outcome. Adding a format check would
create a second failure mode no criterion describes.

---

## Entity: Greeting response

What a caller receives. Same schema on every path, including fallback
(research R-2). Formal definition: [contracts/greeting-api.yaml](./contracts/greeting-api.yaml).

| Field | Type | Nullable | Meaning |
|---|---|---|---|
| `message` | string | no | The greeting text to display |
| `language` | string | no | The language the text is actually in |
| `requested_language` | string | yes | What the caller asked for; null when no preference was supplied |
| `fallback` | boolean | no | True when the requested language was unavailable and the default was used |

### Resolution logic

The whole behavioural core, stated once:

| Caller supplied | In locale table | `message` | `language` | `requested_language` | `fallback` | Criterion |
|---|---|---|---|---|---|---|
| nothing | — | default text | `en` | null | false | GRT-002 |
| a language | yes | that language's text | as requested | as requested | false | GRT-001 |
| a language | no | default text | `en` | as requested | true | GRT-005 |

Two properties follow from this table and are asserted directly by tests:

- **Determinism** — the same input yields the same row every time, since
  the locale table cannot change while the process runs (GRT-005's
  repeatability scenario).
- **Caller-independence** — no row depends on who is calling or from
  where. There is no caller identity in the model at all, which is what
  makes GRT-004 true by construction rather than by assertion.

---

## Entity: Health indication

| Field | Type | Meaning |
|---|---|---|
| `status` | string | `ok` when the locale table loaded; `unavailable` when it did not |

Returned with HTTP 200 when available and 503 when not (design D-7).

Nothing further is reported: no counters, no uptime, no locale list. The
AMB-004 ruling scoped this release to an availability indication and
deferred metrics and structured logging to a separate BRD. See research
R-5 for what was deliberately left out.

---

## What is not modelled

Recorded so a reviewer can see these were considered and excluded on
authority, not overlooked:

| Not modelled | Why |
|---|---|
| User, name, time of day | Personalization is out of scope, BRD §3 |
| Caller identity, API key, tenant | No per-caller authentication this release, AMB-006 ruling. There is no caller entity |
| Translation workflow, draft/published state, authorship | Content management is out of scope, BRD §3. The service reads a file it does not manage |
| Region | GRT-004 requires text to be identical *regardless of* region, so region is deliberately absent from the model |
| Request counts, per-language demand | Deferred to a separate BRD, AMB-004 ruling |
