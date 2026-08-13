# Implementation Plan: Global Greeting Service

**Feature Directory**: `specs/001-greeting-service` | **Date**: 2026-08-12 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/001-greeting-service/spec.md` (Approved at G1, 2026-08-12, PO: Marco)

**Status**: **Draft — PENDING G2** (plan approval). Per constitution Art. III.2, a human (tech lead) approves this plan before implementation begins. Per Art. IV.2, this artifact is a draft until then.

---

## Summary

Serve a per-language greeting to regional applications over a small HTTP API, with all greeting text and the supported-language set loaded from a single YAML configuration file. An unsupported language never errors: the service substitutes the default language and marks the response so callers can detect it. A health endpoint reports whether that configuration actually loaded, so "process up" and "able to greet" are distinguishable.

Ten criteria (GRT-001…GRT-010) are satisfied by three small modules: a config loader, a lookup with fallback, and a FastAPI surface exposing two endpoints. No database — the service holds no state beyond what it read from configuration at startup.

---

## Technical Context

**Language/Version**: Python 3.12 *(matches `.github/workflows/spec-drift.yml`, which pins `python-version: "3.12"`)*

**Primary Dependencies**: FastAPI (HTTP surface), PyYAML (configuration), uvicorn (server) — all already pinned in `requirements.txt`; no new dependency is introduced by this plan.

**Storage**: None. No database (explicit input constraint). The only persistent artifact is `config/locales.yml`, read at startup.

**Testing**: pytest 8.4.2, with `httpx` via FastAPI's `TestClient` for endpoint tests. `pytest.ini` already sets `pythonpath = .` and `testpaths = tests`, so tests import the app as `from src.main import app`.

**Target Platform**: Linux server (containerised or bare uvicorn); no platform-specific behaviour.

**Project Type**: Single-project web service.

**Performance Goals**: None contractual — AMB-008 was ruled at G1 to set no availability or latency target for this release. Calling applications own their own timeouts.

**Constraints**:
- Locale templates load **exclusively** from `config/locales.yml` (explicit input constraint). No hardcoded greeting text anywhere in `src/`, including no built-in default greeting.
- `config/locales.yml` **does not exist yet** — it is created during implementation, and its creation is a task, not a prerequisite.
- No database, no cache, no external service call.

**Scale/Scope**: 2 endpoints, 4 launch locales (en-US, fr-FR, de-DE, ja-JP), ~150 lines of source. First-party internal callers only.

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

| Article | Requirement | Status (pre-Phase 0) | Status (post-Phase 1) |
|---|---|---|---|
| I.1 | Spec derived from approved BRD, lives under `specs/` | PASS — `specs/001-greeting-service/spec.md` from BRD-2026-014 | PASS |
| I.2 | Stable `GRT-###` IDs, never reused | PASS — GRT-001…GRT-010 fixed at G1 | PASS — plan adds no criteria and renumbers none |
| I.3 | Issues derived from spec, never the reverse | PASS — no issues created yet; `gh_sync.py` will derive them from `tasks.md` | PASS |
| II.1 | Every criterion covered by a test declaring `Implements: GRT-###` | PENDING — no tests yet (0/10 covered) | PASS by design — every criterion is assigned a test module below |
| II.2 | `spec-drift` required check fails on uncovered criteria | PASS — gate is live and correctly red at 0/10 | PASS |
| II.3 | Commits reference criterion IDs | PASS — enforced per task at implementation | PASS |
| III.1 | G1 spec approval, Ambiguity Log resolved | PASS — approved 2026-08-12, PO: Marco, 8/8 resolved | PASS |
| III.2 | G2 plan approval by tech lead | **PENDING — this document** | **PENDING — this document** |
| III.3 | Human review under branch protection; agents never merge | PASS — no merge attempted | PASS |
| IV.1 | Agents cite criterion IDs | PASS — every design decision below carries its IDs | PASS |
| IV.2 | Agent artifacts labelled draft until approved | PASS — status line above | PASS |
| IV.3 | Agents do not modify constitution, approved spec, issues, or workflows | PASS — this plan modifies none of them | PASS — no change proposed to `spec.md`, `scripts/`, or `.github/workflows/` |

**Verdict**: no violations. The only open item is G2 itself, which is this document's purpose. **Complexity Tracking is therefore empty and omitted** — nothing here requires justification against a simpler alternative.

One deliberate note on II.1: the plan does not mark it PASS on the promise of future work. It is PASS *by design* — the criterion-to-test map below assigns all ten criteria to a named test module, so no criterion can reach implementation without an owner. The gate itself stays red until those tests exist, which is correct.

---

## Project Structure

### Documentation (this feature)

```text
specs/001-greeting-service/
├── spec.md              # Approved at G1
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── greeting-api.yaml   # Phase 1 output — OpenAPI 3.1
├── checklists/
│   └── requirements.md
└── tasks.md             # Phase 2 — created by /speckit.tasks, NOT by this command
```

### Source Code (repository root)

```text
config/
└── locales.yml          # Created at implementation time. Sole source of
                         # greeting text, supported set, and default locale.

src/
├── __init__.py
├── config.py            # Load + validate locales.yml; normalise keys
├── greetings.py         # Lookup with fallback; no I/O
└── main.py              # FastAPI app: GET /greeting, GET /health

tests/
├── test_greeting.py     # GRT-001, GRT-004, GRT-009
├── test_defaults.py     # GRT-002
├── test_fallback.py     # GRT-005, GRT-006
├── test_config.py       # GRT-010
├── test_api.py          # GRT-003
└── test_health.py       # GRT-007, GRT-008
```

**Structure Decision**: single-project layout, driven by an existing constraint rather than preference — `pytest.ini` documents that tests import the service as `from src.main import app`, so the app must live at `src/main.py`. `src/` and `tests/` already exist and are empty. The split between `config.py` (all file I/O) and `greetings.py` (pure lookup) exists so that fallback and case-matching logic — GRT-005, GRT-006, GRT-009 — can be tested without touching the filesystem, while `config.py` carries the exclusivity constraint in one auditable place.

---

## Design Decisions by Criterion

Every criterion is mapped to the component that satisfies it and the test module that proves it. No criterion is unassigned; no component exists without a criterion.

| Criterion | Design decision | Component | Test module |
|---|---|---|---|
| GRT-001 | `GET /greeting?locale=<id>` returns the configured text for a supported locale | `main.py`, `greetings.py` | `test_greeting.py` |
| GRT-002 | Omitted `locale` resolves to the config's `default` key | `greetings.py` | `test_defaults.py` |
| GRT-003 | One HTTP endpoint, no per-application variation or client-specific route | `main.py` | `test_api.py` |
| GRT-004 | Lookup is a pure function of locale — no caller identity is read, so identical input yields identical text by construction | `greetings.py` | `test_greeting.py` |
| GRT-005 | Unknown locale returns HTTP 200 with the default-language greeting, never 4xx | `greetings.py`, `main.py` | `test_fallback.py` |
| GRT-006 | Response carries `fallback: true` and `requested_locale`, so substitution is detectable without reading `message` | `main.py` | `test_fallback.py` |
| GRT-007 | `GET /health` reports service readiness | `main.py` | `test_health.py` |
| GRT-008 | Health is derived from config load state: 200 when locales loaded, 503 when not | `config.py`, `main.py` | `test_health.py` |
| GRT-009 | Locale keys normalised to lowercase at load and lookup, so case never causes a fallback | `config.py`, `greetings.py` | `test_greeting.py` |
| GRT-010 | Supported set and default both read from `config/locales.yml`; no greeting literal in `src/` | `config.py` | `test_config.py` |

**The load-time normalisation choice (GRT-009) is worth flagging for G2.** Keys are lowercased once when the file is read, not on every request. That makes case-insensitivity a property of the loaded data rather than of each call site, so a future endpoint cannot accidentally reintroduce case sensitivity. The cost is that `config/locales.yml` can be authored in natural `fr-FR` casing while lookups compare lowercased — the response echoes the **configured** spelling, not the caller's, so `locale` in the payload is always canonical.

---

## Response Shape — the G2 decision the spec delegated

AMB-005 was resolved at G1 as: JSON payload carrying the greeting text, the language served, and the fallback indicator, with **exact field naming explicitly delegated to G2**. This plan is that decision point. Proposed:

```json
{ "message": "Bonjour !", "locale": "fr-FR", "requested_locale": "fr-FR", "fallback": false }
```

- `message` — the greeting text (GRT-001).
- `locale` — the language actually served, in its configured spelling (GRT-006).
- `requested_locale` — what the caller asked for; echoes `locale` on a hit, differs on a fallback. Present so a caller can log the gap, which the AMB-001 ruling explicitly wanted.
- `fallback` — boolean; the machine-readable substitution flag (GRT-006). A boolean rather than inferring from `locale != requested_locale`, so callers need no comparison logic.

All four fields are always present, including when `locale` was omitted from the request. A stable key set is easier for callers to consume than a conditional one, and it means `fallback` is never absent-and-therefore-falsy.

**This is the one place G2 approval carries a decision the spec did not already make.** If the tech lead prefers a narrower payload — `message` + `locale` only, with fallback inferred — say so at G2; GRT-006 would then need re-reading, since inference by comparison is arguably still "machine-readable".

---

## Phase 0 — Research

**Output**: [research.md](./research.md) — resolves the technical unknowns this plan opened (YAML load strategy, health semantics under FastAPI, fallback status code, config-exclusivity enforcement). No `NEEDS CLARIFICATION` markers remain in Technical Context.

## Phase 1 — Design & Contracts

**Outputs**:
- [data-model.md](./data-model.md) — entities, the `config/locales.yml` schema, validation rules, load-state transitions.
- [contracts/greeting-api.yaml](./contracts/greeting-api.yaml) — OpenAPI 3.1 for both endpoints.
- [quickstart.md](./quickstart.md) — runnable validation: start the service, exercise each criterion, run the three gates.

## Phase 2 — Tasks

**Not produced by this command.** `/speckit.tasks` generates `tasks.md` in the house format (`- [ ] T<s>.<n> <title> (GRT-###) [P1..P4]`) parsed by `scripts/gh_sync.py`. Do not run it until G2 is granted.

---

## Post-Design Constitution Re-Check

Re-evaluated after Phase 1 (right-hand column of the Constitution Check table above). No new violations. Design introduces no new dependency, no persistence, no change to any file constitution Art. IV.3 puts off-limits, and no criterion beyond the ten approved at G1.
