---

description: "Task list — HOUSE FORMAT, parsed by scripts/gh_sync.py"
---

# Tasks: Global Greeting Service

**Input**: Design documents from `specs/001-greeting-service/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md) (G1-approved), [research.md](./research.md), [data-model.md](./data-model.md), [contracts/](./contracts/)

**Status**: **Approved — Gate G2 passed** 2026-08-12 by **Tech Lead: Dana** (constitution Art. III.2), together with [plan.md](./plan.md). Implementation may begin, and `gh_sync.py --apply` may run once a human has reviewed the dry-run batch (Art. III.4). Merging remains G3 and is a human decision under branch protection (Art. III.3).

## Format contract (exact — the parser is the authority)

`scripts/gh_sync.py` derives GitHub Issues from this file. A deviating line is **reported and refused**, not silently accepted:

- **Story heading**: `## Story S<n> — <title>` (em dash or plain hyphen both parse)
- **Story criteria**: `Implements: GRT-###, ...` on its own line, directly under the heading
- **Task**: `- [ ] T<s>.<n> <title> (GRT-###) [P<n>]` — the line MUST end with the priority bracket

Two invariants maintained deliberately below: every task's criteria are a subset of its story's, and no task-format line appears outside a story block. The Dependencies, Parallel opportunities, and Implementation strategy sections therefore reference task IDs **in prose only** — a checkbox line there would be absorbed into Story S4 and misreported as one of its tasks.

**Checkboxes are never hand-marked** (CLAUDE.md; constitution Art. III.4). Completion is evidenced by `spec_drift.py` coverage plus commits citing criterion IDs; issue state comes from `gh_sync.py --update`.

## Path conventions

Per plan.md — single project, `src/` and `tests/` at repository root. `pytest.ini` already sets `pythonpath = .`, so tests import the app as `from src.main import app`.

---

## Phase 1: Setup

**No setup tasks — deliberately, not by omission.** The repository already provides everything this feature needs: Python 3.12 is pinned in `.github/workflows/spec-drift.yml`; FastAPI, PyYAML, uvicorn, httpx, and pytest are pinned in `requirements.txt`; `pytest.ini` is configured; `src/` and `tests/` exist and are empty. No new dependency is introduced by this plan, so there is nothing to initialise.

## Phase 2: Foundational

Folded into Story S1 rather than standing alone. The configuration loader and the app surface are prerequisites for every other story, but a free-floating foundational phase would be work no story can ship without — defeating independent delivery. S1 is therefore a real increment: once it lands, the service starts, loads its catalog, and answers on one endpoint.

---

## Phase 3: User stories

Four stories in priority order. Every one of the ten approved criteria appears in exactly one story, so no two issues compete to close the same criterion.

## Story S1 — Configuration-driven service foundation
Implements: GRT-003, GRT-010

**Goal**: The service starts, builds its locale catalog exclusively from `config/locales.yml`, and exposes one greeting endpoint that every regional application uses. Adding a language becomes a configuration change, not a code change.

**Independent test**: Start the service and confirm one `/greeting` endpoint answers; add a locale entry to `config/locales.yml`, restart, and confirm the new locale is served with no file under `src/` modified.

- [ ] T1.1 Write failing test for catalog loaded from config/locales.yml in tests/test_config.py, annotated Implements GRT-010 (GRT-010) [P1]
- [ ] T1.2 Write failing test asserting no greeting literal is hardcoded in src, in tests/test_config.py (GRT-010) [P1]
- [ ] T1.3 Create config/locales.yml with default en-US and launch locales en-US, fr-FR, de-DE, ja-JP (GRT-010) [P1]
- [ ] T1.4 Implement catalog loader and validation rules in src/config.py per data-model.md (GRT-010) [P1]
- [ ] T1.5 Write failing test for a single greeting endpoint in tests/test_api.py, annotated Implements GRT-003 (GRT-003) [P1]
- [ ] T1.6 Create FastAPI app in src/main.py with a startup lifespan handler that loads the catalog once (GRT-003) [P1]

## Story S2 — Greeting in the requested language
Implements: GRT-001, GRT-002, GRT-004, GRT-009

**Goal**: A regional application receives a greeting in the language it asked for, the configured default when it asks for none, and identical text to every other caller. A difference in letter case alone never changes the outcome.

**Independent test**: Request `fr-FR` and confirm French text; request with no locale and confirm the default; request `FR-fr` and confirm the same French text with the configured spelling echoed back; request twice and confirm byte-identical responses.

- [ ] T2.1 Write failing test for a supported locale returning that language in tests/test_greeting.py, annotated Implements GRT-001 (GRT-001) [P1]
- [ ] T2.2 Write failing test for identical text across repeated callers in tests/test_greeting.py (GRT-004) [P1]
- [ ] T2.3 Write failing test for the default locale when none is requested, asserting fallback is false, in tests/test_defaults.py (GRT-002) [P1]
- [ ] T2.4 Write failing test for case-insensitive locale matching in tests/test_greeting.py, annotated Implements GRT-009 (GRT-009) [P1]
- [ ] T2.5 Implement pure locale lookup returning text and served locale in src/greetings.py (GRT-001, GRT-002) [P1]
- [ ] T2.6 Fold catalog keys to lowercase at load in src/config.py and at lookup in src/greetings.py, echoing configured spelling (GRT-009) [P1]
- [ ] T2.7 Wire GET /greeting in src/main.py to return message, locale, requested_locale and fallback per contracts/greeting-api.yaml (GRT-001, GRT-004) [P1]

## Story S3 — Unsupported language falls back, visibly
Implements: GRT-005, GRT-006

**Goal**: A request for a language the service does not carry returns a default-language greeting rather than an error, marked so the calling application can detect the substitution and log the gap. This is the G1 ruling on AMB-001.

**Independent test**: Request `pt-BR` and confirm HTTP 200 — not 4xx — carrying the default greeting, `fallback` true, and `requested_locale` echoing `pt-BR`; confirm the substitution is detectable without reading `message`.

- [ ] T3.1 Write failing test that an unsupported locale returns HTTP 200 with the default greeting in tests/test_fallback.py, annotated Implements GRT-005 (GRT-005) [P2]
- [ ] T3.2 Write failing test that the response sets fallback true and echoes requested_locale in tests/test_fallback.py (GRT-006) [P2]
- [ ] T3.3 Implement default-locale substitution for unknown locales in src/greetings.py (GRT-005) [P2]
- [ ] T3.4 Set the fallback flag and requested_locale on substituted responses in src/main.py (GRT-006) [P2]

## Story S4 — Operations can verify service health
Implements: GRT-007, GRT-008

**Goal**: Operations can determine at any time whether the service can actually serve greetings, distinguishing a healthy service from one that is running but failed to load its configuration. This is the G1 ruling on AMB-004.

**Independent test**: Query `/health` with configuration present and confirm 200 with the loaded-locale count; start the service with `config/locales.yml` absent and confirm the process stays up and reports 503.

- [ ] T4.1 Write failing test that GET /health reports healthy with locales_loaded in tests/test_health.py, annotated Implements GRT-007 (GRT-007) [P3]
- [ ] T4.2 Write failing test that a running service with unloadable config reports 503 in tests/test_health.py (GRT-008) [P3]
- [ ] T4.3 Implement GET /health in src/main.py returning status and locales_loaded per contracts/greeting-api.yaml (GRT-007) [P3]
- [ ] T4.4 Return 503 from health and greeting while the catalog is not loaded, without crashing at startup, in src/main.py (GRT-008) [P3]

---

## Phase 4: Polish and cross-cutting concerns

**No separate polish story — deliberately.** A polish story would need its own `Implements:` line, forcing either duplicated criteria across issues or work attached to a criterion it does not serve. Cross-cutting work is folded into the story that owns it: the no-hardcoded-literal guard is T1.2 under S1, and contract conformance is checked inside each story's endpoint task.

Validation that spans all stories lives in [quickstart.md](./quickstart.md) (V-1…V-8) and is run once at the end, not tracked as a task here.

---

## Dependencies

Prose only — a task-format line in this section would be absorbed into Story S4.

- **S1 blocks everything.** Both S1 criteria are prerequisites: nothing can be served before the catalog loads (T1.4) and the app exists (T1.6).
- **S2 depends on S1**, then **S3 depends on S2** — fallback substitutes the default, so default resolution (T2.5) must work before T3.3 has anything to substitute.
- **S4 depends only on S1**, not on S2 or S3. Health reflects catalog load state, which S1 establishes. S4 can therefore be built in parallel with S2 and S3.
- **Within every story, tests precede implementation** (CLAUDE.md: test first). Concretely: T1.1 and T1.2 before T1.4; T1.5 before T1.6; T2.1 through T2.4 before T2.5; T3.1 and T3.2 before T3.3; T4.1 and T4.2 before T4.3.

## Parallel opportunities

- **S2 and S4 can proceed concurrently** once S1 lands — they share no file except `src/main.py`, which is the one genuine contention point.
- **`src/main.py` is touched by T1.6, T2.7, T3.4, T4.3, and T4.4.** These must not run concurrently. It is the single-file bottleneck of this plan and the reason S2 and S4 cannot be fully parallelised despite being logically independent.
- **All test-writing tasks within a story are independent of each other** and can be written in parallel, with one exception: T2.1, T2.2, and T2.4 all write `tests/test_greeting.py` and so must be sequenced.
- `src/config.py` is touched by T1.4 and T2.6; `src/greetings.py` by T2.5, T2.6, and T3.3.

## Implementation strategy

**MVP is S1 + S2.** S1 alone starts a service that can load configuration and answer on one endpoint, but does not yet return a greeting anyone asked for — it is a foundation, not a demo. S1 plus S2 delivers the BRD's core claim: a regional application gets a greeting in the user's language. Stop and validate there.

Then **S3** (unsupported-language handling, BR-3), then **S4** (monitorability, BR-4). Each is an independent increment that does not break the ones before it.

Expected drift-gate state after each story — it stays red until the last criterion is covered, which is the burndown working, not a failure:

- After S1: `spec_drift.py` reports 2/10 covered. Red.
- After S2: 6/10. Red.
- After S3: 8/10. Red.
- After S4: **10/10. Green** — and `pytest tests/ -q` passes, closing the feature.

Judge a single task with `spec_drift.py --criterion GRT-###`, which exits 0 for that criterion alone; judge the feature with the full run.

## Traceability

Every approved criterion is covered, each by exactly one story, and no criterion appears here that `spec.md` does not carry.

| Criterion | Story | Tasks |
|---|---|---|
| GRT-001 | S2 | 2.1, 2.5, 2.7 |
| GRT-002 | S2 | 2.3, 2.5 |
| GRT-003 | S1 | 1.5, 1.6 |
| GRT-004 | S2 | 2.2, 2.7 |
| GRT-005 | S3 | 3.1, 3.3 |
| GRT-006 | S3 | 3.2, 3.4 |
| GRT-007 | S4 | 4.1, 4.3 |
| GRT-008 | S4 | 4.2, 4.4 |
| GRT-009 | S2 | 2.4, 2.6 |
| GRT-010 | S1 | 1.1, 1.2, 1.3, 1.4 |
