# Phase 1 — Data Model: Global Greeting Service

**Feature**: `specs/001-greeting-service` | **Date**: 2026-08-12 | **Plan**: [plan.md](./plan.md)

**Status**: Draft — supports a plan PENDING G2.

There is no database (see [research.md](./research.md) R-6). "Data model" here means the shape of the one configuration file, the in-memory structures derived from it, and the load-state machine that drives health.

---

## Entities

### LocaleCatalog

The whole of the service's data, built once at startup from `config/locales.yml`.

| Field | Type | Description |
|---|---|---|
| `default` | locale identifier | The locale served when the caller names none (GRT-002) and when a requested locale is unsupported (GRT-005). |
| `greetings` | map: normalised locale → greeting text | The supported set. Membership *is* support: a locale is supported iff it has an entry here (GRT-010). |
| `display_names` | map: normalised locale → configured spelling | Preserves the author's casing (`fr-FR`) so responses echo canonical form rather than the caller's input (R-3). |
| `loaded` | boolean | Whether the catalog was built successfully. Drives health (GRT-008). |
| `error` | text or absent | Why loading failed, for the health body and logs. Never surfaced to greeting callers. |

**Invariants**:
- `greetings` keys are lowercase; nothing else in the service lowercases a key (R-3).
- `loaded` is true only if the file parsed **and** `default` is present in `greetings`. A default pointing at a missing locale is a failed load, not a half-working catalog — otherwise GRT-002 and GRT-005 would both fall through to nothing at request time.
- An entry whose greeting text is empty or absent is not a supported locale. This is the spec's "a language configured but with no greeting text behind it" edge case: it is excluded from `greetings` at load, so requests for it fall back (GRT-005).
- The catalog is immutable after startup. No request path mutates it.

### GreetingResponse

What a caller receives from `GET /greeting`. Field names are the G2 decision AMB-005 delegated to this plan.

| Field | Type | Description | Criterion |
|---|---|---|---|
| `message` | string | The greeting text, verbatim from configuration. | GRT-001 |
| `locale` | string | The locale actually served, in configured spelling. | GRT-006 |
| `requested_locale` | string | What the caller asked for; equals `locale` on a hit. When the caller named none, this is the default — the request is treated as a request for the default, not as a fallback. | GRT-002, GRT-006 |
| `fallback` | boolean | True when the requested locale was unsupported and the default was substituted. | GRT-005, GRT-006 |

All four fields are always present. `fallback` is never absent-and-therefore-falsy.

### HealthResponse

What operations receives from `GET /health`.

| Field | Type | Description | Criterion |
|---|---|---|---|
| `status` | `"healthy"` \| `"unhealthy"` | Load state, not process liveness. | GRT-007, GRT-008 |
| `locales_loaded` | integer | Size of the supported set; makes a green check informative. | GRT-007 |
| `detail` | string or absent | Present only when unhealthy: why the catalog failed to load. | GRT-008 |

HTTP status carries the same signal for monitors that do not parse bodies: **200** healthy, **503** unhealthy (R-5).

---

## Configuration Contract — `config/locales.yml`

This file does not exist yet; creating it is an implementation task. It is the sole source of greeting text, the supported set, and the default (GRT-010), and it is an operations-facing interface: adding a language must require no code change (SC-005).

```yaml
# config/locales.yml
default: en-US

locales:
  en-US: "Hello!"
  fr-FR: "Bonjour !"
  de-DE: "Hallo!"
  ja-JP: "こんにちは!"
```

**Schema**:

| Key | Required | Type | Rule |
|---|---|---|---|
| `default` | yes | string | Must be a key of `locales` (after case folding), else the load fails. |
| `locales` | yes | map of string → string | At least one entry. Keys are locale identifiers in language-region form; values are non-empty greeting text. |

**Launch contents** are fixed by the G1 ruling on AMB-002: `en-US` (default), `fr-FR`, `de-DE`, `ja-JP`. The greeting text above is illustrative — the actual strings come from the business, since translation authoring is out of scope per BRD §3.

**Validation rules at load**:

1. File missing or unreadable → not loaded, `error` set.
2. File not valid YAML, or not a mapping at the top level → not loaded.
3. `locales` missing, empty, or not a mapping → not loaded.
4. Entries with empty or non-string text → dropped from the supported set; if that empties `locales`, not loaded.
5. `default` missing, or absent from the surviving `locales` → not loaded.
6. Otherwise → loaded; keys folded to lowercase, display spellings retained.

Every failure path above is the same observable outcome: `loaded = false` → `/health` returns 503 (GRT-008). Greeting requests in that state cannot be served from configuration and must not be served from a literal (R-4).

---

## Lookup Rules

Resolution order for `GET /greeting`, given the catalog and an optional requested locale:

1. **No locale supplied** → serve `default`. `fallback = false`, `requested_locale = default`. *(GRT-002)*
2. **Locale supplied, folds to a key in `greetings`** → serve it. `fallback = false`. *(GRT-001, GRT-009)*
3. **Locale supplied, not in `greetings`** → serve `default`. `fallback = true`, `requested_locale` = what the caller sent, unmodified. *(GRT-005, GRT-006)*

Case (1) is deliberately not a fallback. The caller expressed no preference, so nothing was substituted against their wishes — reporting `fallback: true` there would make the flag useless for the log-the-gap purpose the AMB-001 ruling gave it.

Resolution depends only on the requested locale and the catalog — never on caller identity, headers, or request order. That is what makes GRT-004 (identical text to every caller) true by construction rather than by test alone, and it is why AMB-007's ruling (no inference from end-user context) is satisfied structurally.

---

## State Transitions

The service has exactly one state variable — catalog load state — with no runtime transition:

```text
                startup: read config/locales.yml
                          │
              ┌───────────┴───────────┐
        validation passes       validation fails
              │                       │
              ▼                       ▼
   ┌──────────────────┐    ┌────────────────────┐
   │ LOADED           │    │ NOT LOADED         │
   │ /health   → 200  │    │ /health   → 503    │
   │ /greeting → 200  │    │ /greeting → 503    │
   └──────────────────┘    └────────────────────┘
```

No transition edge exists between the two states: the catalog is read once and never reloaded (R-2), so a service that starts unhealthy stays unhealthy until restarted. That is intentional — reload-on-change is unrequested scope — but it is the design's sharpest limitation and worth an explicit G2 nod, since it means a config fix requires a redeploy.

`GET /greeting` in the NOT LOADED state returns 503 rather than a greeting. This is not a fallback: the AMB-001 ruling governs *unsupported locales*, which presumes a catalog to be unsupported against. With no catalog there is no default to fall back to, and inventing one would violate the exclusivity constraint (R-4).
