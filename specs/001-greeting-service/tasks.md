# Tasks: Global Greeting Service

**Feature**: `specs/001-greeting-service` | **Date**: 2026-08-12
**Spec**: [spec.md](./spec.md) — APPROVED, G1 met | **Plan**: [plan.md](./plan.md) — G2 pending

**Status**: 🔶 **DRAFT — G2 PENDING.** Agent-generated artifact per constitution
Article IV.2. Requires tech-lead approval together with plan.md before implementation.

> **This file is parsed by `scripts/gh_sync.py`.** Stories become GitHub Issues; tasks
> become checklist items in the issue body. The parser is strict and silent on partial
> matches — a malformed line is skipped, not reported. Verified against a dry run before
> commit.
>
> Format contract, enforced by the regexes in `scripts/gh_sync.py`:
> - Story heading uses an **em dash**: `## Story S<n> — <title>`
> - `Implements: GRT-###, ...` on its own line, at line start, no markup, one per story
> - Task lines: `- [ ] T<s>.<n> <title> (GRT-###) [P1..P4]`, no trailing whitespace
>
> Do not loosen the parser to fit this file.

**Ordering**: test-first throughout, per CLAUDE.md — the annotated test is written before
the implementation it covers. Story S1 is foundational; S2 depends on it. S3 and S4 are
independent of each other once S2 exists.

**Coverage**: all eight active criteria (GRT-001…GRT-008) appear below. GRT-009 is reserved
and unused (AMB-005), so no task implements it.

---

## Story S1 — Locale catalogue loaded from config/locales.yml
Implements: GRT-007

Foundation for everything else. `config/locales.yml` is the sole source of both the
greeting text and the supported-language set, so the two cannot drift apart.

- [ ] T1.1 Write tests/test_locales.py asserting exactly en, fr, de, es and ja load from config/locales.yml (GRT-007) [P1]
- [ ] T1.2 Add config/locales.yml containing the five approved languages and their greeting text (GRT-007) [P1]
- [ ] T1.3 Implement src/greeting_service/locales.py to load and validate the catalogue once at startup (GRT-007) [P1]
- [ ] T1.4 Abort startup when config/locales.yml is missing, unparseable or has an empty greeting (GRT-007) [P1]

---

## Story S2 — Greeting retrieval for supported languages
Implements: GRT-001, GRT-002, GRT-003, GRT-006

The reason the service exists. One endpoint, text returned verbatim from the catalogue,
no user identity involved.

- [ ] T2.1 Write tests/test_greeting.py covering every supported language returning its own greeting (GRT-001) [P1]
- [ ] T2.2 Extend tests/test_greeting.py to assert two independent callers receive byte-identical text (GRT-002) [P1]
- [ ] T2.3 Extend tests/test_greeting.py to assert a caller-supplied user identifier does not affect the response (GRT-006) [P1]
- [ ] T2.4 Write tests/test_contract.py asserting one documented endpoint serves all callers with no per-caller variation (GRT-003) [P1]
- [ ] T2.5 Implement the greeting endpoint in src/greeting_service/app.py returning catalogue text verbatim (GRT-001, GRT-002, GRT-003) [P1]
- [ ] T2.6 Read the language from the request only, with no user lookup and no stored state (GRT-006) [P1]

---

## Story S3 — Distinct error responses for unsupported and missing language
Implements: GRT-004, GRT-008

The business chose errors over fallback, and chose to keep the two failures
distinguishable. T3.3 is the trap flagged as D1 in plan.md.

- [ ] T3.1 Write tests/test_errors.py asserting an unsupported language returns UNSUPPORTED_LANGUAGE with no greeting field (GRT-004) [P2]
- [ ] T3.2 Extend tests/test_errors.py to assert a request with no language returns MISSING_LANGUAGE (GRT-008) [P2]
- [ ] T3.3 Extend tests/test_errors.py to assert the two error codes are distinct and neither response carries fallback text (GRT-004, GRT-008) [P2]
- [ ] T3.4 Declare the language parameter optional at framework level so FastAPI cannot pre-empt the error with its own 422 (GRT-008) [P2]
- [ ] T3.5 Implement both error shapes in src/greeting_service/errors.py and wire them into the endpoint (GRT-004, GRT-008) [P2]

---

## Story S4 — Health indicator for operations
Implements: GRT-005

Operations must be able to tell a service that can serve greetings from one that cannot.

- [ ] T4.1 Write tests/test_health.py asserting healthy is reported while a non-empty catalogue is loaded (GRT-005) [P3]
- [ ] T4.2 Extend tests/test_health.py to assert an empty catalogue is not reported as healthy (GRT-005) [P3]
- [ ] T4.3 Implement the health endpoint in src/greeting_service/app.py reporting on catalogue state (GRT-005) [P3]

---

## Criterion coverage

Every active criterion is claimed by at least one task, and no task exists without a
criterion. This is the Article II.1 obligation discharged at task level.

| Criterion | Story | Tasks |
|-----------|-------|-------|
| GRT-001 | S2 | T2.1, T2.5 |
| GRT-002 | S2 | T2.2, T2.5 |
| GRT-003 | S2 | T2.4, T2.5 |
| GRT-004 | S3 | T3.1, T3.3, T3.5 |
| GRT-005 | S4 | T4.1, T4.2, T4.3 |
| GRT-006 | S2 | T2.3, T2.6 |
| GRT-007 | S1 | T1.1, T1.2, T1.3, T1.4 |
| GRT-008 | S3 | T3.2, T3.3, T3.4, T3.5 |

## Definition of done

Per CLAUDE.md, for every implementation task above:

1. `.venv/bin/python -m pytest tests/ -q` passes.
2. `.venv/bin/python scripts/spec_drift.py` no longer lists the task's criteria as
   uncovered — target is `Covered: 8/8`.
3. Committed with the criterion ID in the message; working tree left clean.

Issues are created from this file only after G2 approval, via a `gh_sync.py` dry run that a
human reviews before `--apply` (constitution Article III.4).
