# Implementation Plan: Global Greeting Service

**Branch**: `demo-live` | **Date**: 2026-08-12 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-greeting-service/spec.md`
(Status: Approved — Gate G1, PO: Marco, 2026-08-12)

**Status**: **Approved — Gate G2** (Tech Lead: Dana, 2026-08-12). Per
constitution Art. III.2 a human tech lead approved this plan before
implementation. Implementation may begin against `tasks.md`.

**Gate G2 record**: approved as written, including design decisions
D-1…D-8 and the AMB-005 interface mechanism deferred here from G1. The
one item research.md left to the approver — startup behaviour on bad
config (R-6) — is ruled by this approval: the service **starts in an
unhealthy state** rather than aborting, so operations gets a definite
answer from `/health` instead of a crash-looping container.

## Summary

Deliver the six approved criteria (GRT-001…GRT-006) as a small stateless
HTTP service. A caller names a language explicitly; the service returns
the greeting text for it, falls back to English and says so when the
language is unsupported, and exposes a health indication for operations.

Greeting text lives exclusively in `config/locales.yml`, loaded once at
startup. There is no database and no greeting text embedded in code —
that single-source rule is what makes GRT-004 (identical text for every
caller) true by construction rather than by discipline.

## Technical Context

**Language/Version**: Python 3.12 (matches `.github/workflows/spec-drift.yml`)

**Primary Dependencies**: FastAPI (HTTP interface), PyYAML (config load),
Uvicorn (ASGI server), httpx (test client). All already present in
`requirements.txt`; this plan adds no new dependency.

**Storage**: None. No database. State is a read-only locale table loaded
from `config/locales.yml` at startup.

**Testing**: pytest, driving the app through FastAPI's `TestClient`
(httpx) in-process — no network, no running server needed in CI.

**Target Platform**: Linux server (containerised or bare ASGI). CI runs
`ubuntu-latest`.

**Project Type**: Single-project web service.

**Performance Goals**: None specified. AMB-007 was ruled at G1 as "no
formal service-level objective in this release", so this plan sets no
throughput or latency target and adds no performance-tuning work.

**Constraints**:
- Locale templates load **exclusively** from `config/locales.yml`. No
  greeting text is hardcoded anywhere, including as an emergency default.
- `config/locales.yml` does not exist yet; it is created during
  implementation as part of the task that first needs it.
- No database, no external service call on the request path.

**Scale/Scope**: Two endpoints, three source modules, one config file.
The supported-language set is business-owned configuration (AMB-001) and
can grow without code change — that is the design's main flexibility
requirement.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

| Article | Requirement | This plan | Verdict |
|---|---|---|---|
| I.1 | Spec derived from approved BRD, lives under `specs/` | `specs/001-greeting-service/spec.md`, from BRD-2026-014 | PASS |
| I.2 | Stable `GRT-###` IDs, never reused | Six criteria, unchanged since draft; plan adds none | PASS |
| I.3 | Issues derived from spec, never the reverse | Plan changes no requirement; `tasks.md` (next command) is the issue source | PASS |
| II.1 | Every criterion covered by a test declaring `Implements: GRT-###` | Test Strategy below assigns a named test to all six | PASS (verified at implementation, not now) |
| II.2 | `spec-drift` required check fails on uncovered criteria | Unchanged; currently red at 0/6, by design | PASS |
| II.3 | Commits reference criterion IDs | Task commits will cite their GRT ID | PASS |
| III.1 | G1 spec approval by human, ambiguity log resolved | Approved 2026-08-12 by PO Marco, all 7 items ruled | PASS |
| III.2 | G2 plan approval by human tech lead before implementation | Approved 2026-08-12 by Tech Lead Dana | PASS |
| III.3 | Human review under branch protection; agents never merge | Unchanged | PASS |
| IV.1 | Agents cite criterion IDs | Every design decision below cites its criterion | PASS |
| IV.2 | Agent artifacts labelled draft until approved | Drafted as such; approved by a named human at G2 | PASS |
| IV.3 | Agents do not modify constitution, approved specs, issues, workflows | This plan modifies none of them | PASS |

**Result**: No violations, and no gate left open. G1 and G2 are both
closed by named humans; G3 (merge authority) remains ahead, as it must —
the agent does not merge.

**Post-design re-check**: Re-run after Phase 1 below. No new violation
introduced; the design adds no project, no persistence layer, and no
dependency beyond what `requirements.txt` already declares.

## Design Decisions

Recorded here because AMB-005 was ruled at G1 as "the concrete mechanism
is a design decision recorded at G2, not a business ruling". This section
is that record. Full rationale and rejected alternatives: [research.md](./research.md).

| # | Decision | Serves | Rationale in brief |
|---|---|---|---|
| D-1 | Language preference is an explicit query parameter `lang`, not a negotiated `Accept-Language` header | GRT-001, GRT-003 | AMB-005 ruled the preference is "passed explicitly by the caller". Header negotiation is implicit and quality-weighted; a query parameter is unambiguous and trivially testable |
| D-2 | One endpoint `GET /greeting` serves every regional application | GRT-003 | "A single interface that every regional calling application can use" — no per-region route, no per-caller variant |
| D-3 | Response is JSON with `message`, `language`, `requested_language`, `fallback` | GRT-001, GRT-002, GRT-005 | A stable schema on every path lets a caller detect fallback without parsing prose or branching on status code |
| D-4 | Unsupported language returns **HTTP 200** with `fallback: true`, not an error status | GRT-005 | The G1 ruling on AMB-003 is fallback-with-notice: the end user still sees a greeting. An error status would contradict the approved criterion. See the divergence note below |
| D-5 | Locales load once at startup from `config/locales.yml`; no per-request file read | GRT-004 | One immutable in-memory table for the process life makes identical text for every caller structural. Also keeps the request path free of I/O |
| D-6 | Default language is `en`; its **text** comes from config like any other locale | GRT-002 | AMB-002 ruled English. The identifier is a constant; the text is not, honouring "exclusively from `config/locales.yml`" |
| D-7 | `GET /health` reports 200 when the locale table loaded and 503 when it did not | GRT-006 | A service with no locale table cannot serve any greeting, so config-load state *is* availability. Stays inside AMB-004's availability-only scope — no metrics, no counters |
| D-8 | Missing or malformed `config/locales.yml` is not masked by an in-code default | GRT-004, GRT-006 | The "exclusively from config" constraint has a consequence: there is no safe hardcoded greeting to fall back to. The service reports unhealthy instead of serving text from an unknown source |

### Divergence note (D-4)

`docs/DEMO-RUNBOOK.md:120` sketches an alternative where an unsupported
language returns HTTP 400 with `UNSUPPORTED_LOCALE` and no fallback. The
approved spec rules the opposite way (AMB-003, PO: Marco). **The approved
spec governs.** If the tech lead prefers refusal semantics, that is a
change to GRT-005 and must go back through the PO at G1 — it is not a
plan-level decision to make here.

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
└── tasks.md             # Phase 2 — created by /speckit.tasks, NOT here
```

### Source Code (repository root)

```text
src/
├── __init__.py
├── main.py          # FastAPI app; GET /greeting, GET /health
├── config.py        # loads and validates config/locales.yml at startup
└── greetings.py     # language resolution + fallback decision

config/
└── locales.yml      # greeting text, keyed by language. Created during implementation

tests/
├── test_greeting.py # GRT-001, GRT-002, GRT-004, GRT-005
└── test_health.py   # GRT-003, GRT-006
```

**Structure Decision**: Single project, flat `src/` with three modules.
The template's `models/ services/ cli/ lib/` layout is deliberately not
used: there is no persistence, no CLI, and one entity. Four package
directories for ~150 lines of code would be structure without content.
`config/` sits at repository root rather than inside `src/` because the
locale table is business-owned data (AMB-001), not application code.

## Test Strategy

Article II.1 requires every criterion to be covered by a test declaring
`Implements: GRT-###`. This is the mapping `scripts/spec_drift.py` will
verify; it turns the gate from red (0/6) to green.

| Criterion | Covering test | Asserts |
|---|---|---|
| GRT-001 | `test_greeting.py::test_supported_language_returns_that_language` | Requesting a supported language returns that language's text, `fallback` false |
| GRT-002 | `test_greeting.py::test_no_preference_returns_default_english` | Omitting `lang` returns the English text, `language` is `en` |
| GRT-003 | `test_health.py::test_single_interface_serves_all_callers` | One endpoint answers callers regardless of origin; no per-region route exists |
| GRT-004 | `test_greeting.py::test_same_language_same_text_for_every_caller` | Repeated and differing callers get byte-identical text for one language |
| GRT-005 | `test_greeting.py::test_unsupported_language_falls_back_and_says_so` | Unsupported language returns 200, English text, `fallback` true, `requested_language` echoed; identical on repeat |
| GRT-006 | `test_health.py::test_health_reports_available` | Health reports available when the locale table loaded |

Test-first, per CLAUDE.md: each annotated test is written before or
alongside the implementation it covers. Tests drive the app in-process
through `TestClient`, so CI needs no running server.

**Note on GRT-003**: "a single interface" is a negative claim — that no
second, per-region interface exists. The test asserts the served route
set, which is the strongest mechanical check available. A reviewer, not
a test, is the real guard against a second interface appearing later.

## Complexity Tracking

No Constitution Check violations. No entries.

## Phase Status

- [x] Phase 0 — Research complete → [research.md](./research.md)
- [x] Phase 1 — Design complete → [data-model.md](./data-model.md), [contracts/greeting-api.yaml](./contracts/greeting-api.yaml), [quickstart.md](./quickstart.md)
- [x] **G2 — Tech lead approval of this plan** (constitution Art. III.2) — Dana, 2026-08-12
- [x] Phase 2 — Task breakdown → [tasks.md](./tasks.md), 4 stories, 18 tasks
- [ ] Implementation — unblocked; start at Story S1
- [ ] G3 — Merge authority: human review under branch protection (Art. III.3)
