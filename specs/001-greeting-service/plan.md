# Implementation Plan: Global Greeting Service

**Branch**: `demo-live` | **Date**: 2026-08-12 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/001-greeting-service/spec.md` (APPROVED, G1 met 2026-08-12)

**Status**: 🔶 **DRAFT — G2 PENDING.** Agent-generated artifact, labelled draft per
constitution Article IV.2. Requires tech-lead approval (Article III.2) before
implementation begins.

## Summary

Expose the eight approved criteria (GRT-001…GRT-008) as a small stateless FastAPI service.
A caller asks for a greeting in a named language; the service answers from an in-memory
catalogue loaded once at startup from `config/locales.yml`, or returns one of two distinct
errors. No database, no user identity, no runtime content management.

The whole feature is one read-only endpoint plus a health endpoint. The design work is
almost entirely in the error paths, because AMB-002 and AMB-009 made them contractual.

## Technical Context

**Language/Version**: Python 3.12 (CI pins 3.12 in `.github/workflows/spec-drift.yml`)

**Primary Dependencies**: FastAPI (service), PyYAML (locale loading), Uvicorn (ASGI host),
httpx (test client). All five already present in `requirements.txt` — no new dependencies.

**Storage**: None. Locale templates load exclusively from `config/locales.yml` at startup
and are held in memory. This is the mechanism for AMB-008 (build-time fixed content).

**Testing**: pytest, via `.venv/bin/python -m pytest tests/ -q`. Tests live flat in
`tests/`; verified that `scripts/spec_drift.py` (`TEST_GLOB = "tests/**/*.py"`) collects
them there.

**Target Platform**: Linux server (CI: `ubuntu-latest`)

**Project Type**: Single-project web service

**Performance Goals**: None. AMB-006 was resolved as "no numeric targets in this release";
inventing latency or throughput figures here would create commitments the business
declined to make.

**Constraints**: Stateless — the service accepts no user identifier and performs no
lookup (GRT-006). Greeting text has exactly one source (GRT-002, AMB-008).

**Scale/Scope**: 5 languages (GRT-007), 2 endpoints, no persistence.

> ⚠️ **Environment note, not a blocker**: the repo's `.venv` is Python **3.13.2**, while
> this plan and CI target **3.12**. Nothing here depends on version-specific behaviour, but
> local runs and CI are not on identical interpreters. Flagging for the G2 reviewer to
> accept or correct; recreating `.venv` on 3.12 would remove the skew.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

| Article | Requirement | Status |
|---------|-------------|--------|
| I.1 | Spec derived from approved BRD, lives in `specs/` | ✅ `specs/001-greeting-service/spec.md`, from BRD-2026-014 |
| I.2 | Stable `GRT-###` IDs, never reused | ✅ GRT-001…GRT-008 active; GRT-009 reserved, unused |
| I.3 | Issues derived from spec, not the reverse | ✅ No issues created by this plan |
| II.1 | Every criterion covered by a test declaring `Implements: GRT-###` | ✅ Planned — see Criterion → Test Map; **verified only when tests exist** |
| II.2 | `spec-drift` required check passes | 🔶 Currently 0/8 covered — expected pre-implementation, must be green before merge |
| II.3 | Commits reference criterion IDs | ✅ Practice established in this feature's history |
| III.1 | G1 spec approval | ✅ Met 2026-08-12 |
| III.2 | G2 plan approval | 🔶 **This document. Pending.** |
| III.3 | G3 human merge, agents never merge | ✅ No merge performed or planned by agent |
| IV.1 | Agents cite criterion IDs | ✅ Throughout this plan and its artifacts |
| IV.2 | Agent artifacts labelled draft until approved | ✅ Header marks this DRAFT |
| IV.3 | Agents do not modify constitution, approved specs, issues, workflows | ✅ `spec.md` is untouched by this plan; no workflow changes proposed |

**Gate result**: no violations. Complexity Tracking table below is empty by design.

**Post-Phase-1 re-check**: unchanged — the design adds no project, no persistence layer,
and no dependency beyond what `requirements.txt` already lists. Article II remains the only
open item, and it closes when the tests in the Criterion → Test Map are written.

## Criterion → Test Map

This is the plan's contract with Article II.1. Every active criterion has a named home
before any code is written. Test-first: the annotated test is written before or alongside
its implementation (CLAUDE.md).

| Criterion | Behaviour | Test file | Notes |
|-----------|-----------|-----------|-------|
| GRT-001 | Supported language → greeting in that language | `tests/test_greeting.py` | Parametrised over all five languages |
| GRT-002 | Identical text to every caller for the same language | `tests/test_greeting.py` | Two independent requests → byte-identical text |
| GRT-003 | Single interface usable by all regional apps | `tests/test_contract.py` | One documented endpoint; no per-caller variation |
| GRT-004 | Unsupported language → `UNSUPPORTED_LANGUAGE`, no greeting | `tests/test_errors.py` | Asserts code **and** absence of greeting body |
| GRT-005 | Health indicator reflects ability to serve | `tests/test_health.py` | Healthy path + catalogue-empty path |
| GRT-006 | Language taken from request, never looked up | `tests/test_greeting.py` | Asserts no user identifier is accepted |
| GRT-007 | Supports en, fr, de, es, ja | `tests/test_locales.py` | Exactly these five load from `config/locales.yml` |
| GRT-008 | Missing language → `MISSING_LANGUAGE`, distinct from GRT-004 | `tests/test_errors.py` | Asserts the two codes differ |

## Project Structure

### Documentation (this feature)

```text
specs/001-greeting-service/
├── plan.md              # This file
├── spec.md              # APPROVED contract (not modified by this plan)
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── greeting-api.md  # Phase 1 output
├── checklists/
│   └── requirements.md  # From /speckit-specify
└── tasks.md             # Phase 2 — NOT created by this command
```

### Source Code (repository root)

```text
config/
└── locales.yml                  # Sole source of greeting text (AMB-008, GRT-002)

src/
└── greeting_service/
    ├── __init__.py
    ├── app.py                   # FastAPI app, routes, error handlers
    ├── locales.py               # Load + validate config/locales.yml
    └── errors.py                # UNSUPPORTED_LANGUAGE / MISSING_LANGUAGE shapes

tests/
├── test_greeting.py             # GRT-001, GRT-002, GRT-006
├── test_errors.py               # GRT-004, GRT-008
├── test_health.py               # GRT-005
├── test_locales.py              # GRT-007
└── test_contract.py             # GRT-003
```

**Structure Decision**: Single project. The feature is two endpoints with no persistence,
so a backend/frontend split or a separate API package would add structure without
carrying weight. Tests sit flat in `tests/` because `scripts/spec_drift.py` globs
`tests/**/*.py` and a flat layout is what the existing `pytest tests/ -q` command in
CLAUDE.md and CI expects.

## Design Decisions Requiring G2 Attention

Three decisions in this plan are judgement calls the spec does not dictate. The G2 reviewer
should confirm or overrule them; details and alternatives are in
[research.md](./research.md).

1. **FastAPI's automatic 422 must be intercepted.** A required query parameter makes
   FastAPI return its own `422` validation error, which carries no `MISSING_LANGUAGE` code
   and would silently fail GRT-008. The plan makes `language` optional at the framework
   level and validates it in application code. This is the single most likely way to
   implement the feature and still violate the spec.
2. **HTTP status mapping.** `MISSING_LANGUAGE` → 400, `UNSUPPORTED_LANGUAGE` → 404. Both
   responses carry a machine-readable `code`, and the contract instructs callers to key on
   `code` rather than status, so the mapping can change without breaking GRT-004/GRT-008.
3. **Health semantics.** The service fails fast if `config/locales.yml` cannot be loaded at
   startup, and `/health` reports healthy only while a non-empty catalogue is loaded. This
   satisfies the spec's edge case "running but cannot serve greetings" without inventing
   readiness/liveness machinery the BRD never asked for.

## Out of Scope for This Plan

Carried from the approved spec — not designed here, and no code should appear for them:

- Personalization, translation workflow, content management (BRD §3)
- Per-application access control (AMB-004)
- Metrics, structured logging, alerting beyond `/health` (AMB-005) — GRT-009 stays reserved
- Quantitative performance or availability targets (AMB-006)

## Complexity Tracking

> No Constitution Check violations. Table intentionally empty.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| *(none)* | — | — |
