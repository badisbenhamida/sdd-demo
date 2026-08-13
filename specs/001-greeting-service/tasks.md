# Tasks: Global Greeting Service

**Input**: Design documents from `/specs/001-greeting-service/`

**Prerequisites**: [spec.md](./spec.md) (approved at G1), [plan.md](./plan.md),
[research.md](./research.md), [data-model.md](./data-model.md),
[contracts/greeting-api.yaml](./contracts/greeting-api.yaml)

**Status**: **Draft — G2 pending.** Constitution Art. III.2 requires a tech
lead to approve the plan before implementation. No task below may start
until that gate closes.

**Tests**: Required, not optional. Constitution Art. II.1 requires every
criterion to be covered by a test declaring `Implements: GRT-###`, and
CLAUDE.md requires that test to be written before or alongside the
implementation it covers. Each story below therefore opens with its
failing test.

## Format contract

`scripts/gh_sync.py` parses this file to derive GitHub Issues. It is the
authority on format, and a line that deviates is **silently dropped**
rather than reported — so the shape below is exact, not stylistic:

- Story heading: `## Story S<n> — <title>` — the separator is an em dash
  (`—`, U+2014), not a hyphen. `STORY_RE` at `scripts/gh_sync.py:35`
  requires it. *(The parser's own error hint at line 151 prints a hyphen;
  the regex governs. Noted so nobody "fixes" this file to match the hint.)*
- Story criteria: `Implements: GRT-###, ...` on its own line, directly
  under the heading.
- Task: `- [ ] T<s>.<n> <title> (GRT-###) [P<n>]` — the line must end with
  the priority bracket, and the criterion IDs are the last parenthesised
  group before it.

Two invariants this file maintains deliberately:

1. **Every task's criteria are a subset of its story's criteria.**
   `gh_sync.py --update` collects criterion IDs from the *entire* issue
   body — story line and task lines together — so a stray ID in a task
   would silently widen the story's closure condition and keep the issue
   open against a criterion it does not own.
2. **No task-format line appears outside a story block.** Any such line
   after a story heading is absorbed into that story. Dependency and
   parallelism sections below therefore reference task IDs in prose only.

## Path conventions

Single project per plan.md: `src/` and `tests/` at repository root,
`config/` at repository root for business-owned data.

---

## Phase 1: Setup

No setup tasks. `.venv`, `requirements.txt` (fastapi, pyyaml, uvicorn,
httpx, pytest), CI (`.github/workflows/spec-drift.yml`, Python 3.12) and
the drift gate are already provisioned in this repository, and plan.md
adds no dependency. Recorded explicitly so the empty phase reads as a
finding rather than an omission.

## Phase 2: Foundational

No separate foundational phase. The only shared prerequisite — the locale
loader — is owned by Story S1, which is the MVP and the first story that
needs it. Splitting it out would create a phase that no story could ship
without, defeating independent delivery.

---

## Phase 3: User Stories

Four stories. Every approved criterion appears in exactly one story, so
no two issues compete to close the same criterion.

## Story S1 — Single greeting interface serving the default language
Implements: GRT-002, GRT-003, GRT-004

**Goal**: One endpoint, reachable by every regional application, that
returns the English greeting loaded from `config/locales.yml` — identical
for every caller. This is the MVP: shippable on its own, and the slice
that proves the interface, the config source, and the response schema.

**Independent test**: `GET /greeting` with no parameters returns the
English text from config; repeated calls return byte-identical text; the
greeting route is the only greeting interface served.

**Why these criteria together**: GRT-004 (identical text for every caller)
is not a behaviour to code but a property of loading one immutable table
at startup — research R-4. It is proven the moment the endpoint returns
config text, so it belongs with the endpoint that first does.

- [ ] T1.1 Create config/locales.yml with an en entry and at least two further languages per data-model.md (GRT-002) [P1]
- [ ] T1.2 Write the failing default-greeting test in tests/test_greeting.py annotated Implements GRT-002 (GRT-002) [P1]
- [ ] T1.3 Write the failing caller-independence test in tests/test_greeting.py asserting byte-identical text across repeated calls, annotated Implements GRT-004 (GRT-004) [P1]
- [ ] T1.4 Write the failing single-interface test in tests/test_health.py asserting one greeting route with no per-region variant, annotated Implements GRT-003 (GRT-003) [P1]
- [ ] T1.5 Implement the locale loader in src/config.py reading config/locales.yml once at startup, with no greeting text in code per research R-6 (GRT-004) [P1]
- [ ] T1.6 Implement GET /greeting in src/main.py returning message, language, requested_language and fallback per contracts/greeting-api.yaml (GRT-002, GRT-003) [P1]
- [ ] T1.7 Enforce the loader validation rules in src/config.py rejecting a missing file, an empty table, an absent en entry, or an empty message (GRT-004) [P2]

## Story S2 — Greeting in the caller's requested language
Implements: GRT-001

**Goal**: A caller names a language explicitly and gets that language's
text. Builds directly on S1's endpoint and schema.

**Independent test**: `GET /greeting?lang=<configured language>` returns
that language's text with `fallback` false.

- [ ] T2.1 Write the failing supported-language test in tests/test_greeting.py annotated Implements GRT-001, parameterised over configured languages rather than a hardcoded one (GRT-001) [P1]
- [ ] T2.2 Implement language resolution in src/greetings.py returning the requested language's text when it is configured (GRT-001) [P1]
- [ ] T2.3 Accept the explicit lang query parameter on GET /greeting in src/main.py per design D-1 (GRT-001) [P1]

## Story S3 — Unsupported language falls back and says so
Implements: GRT-005

**Goal**: A language the service does not carry still yields a usable
greeting, with the gap made machine-detectable rather than silent.

**Independent test**: `GET /greeting?lang=xx` returns HTTP 200, the
English text, `requested_language` of `xx`, and `fallback` true — the
same response every time.

**Watch this one**: it returns **200, not 400**. The G1 ruling on AMB-003
is fallback-with-notice. `docs/DEMO-RUNBOOK.md:120` sketches the opposite
and does not govern — see the divergence note in plan.md before changing
a test here.

- [ ] T3.1 Write the failing unsupported-language test in tests/test_greeting.py annotated Implements GRT-005, asserting HTTP 200 with fallback true and requested_language echoed (GRT-005) [P2]
- [ ] T3.2 Implement fallback to the default language in src/greetings.py setting fallback true and echoing the requested value (GRT-005) [P2]
- [ ] T3.3 Return HTTP 200 on the fallback path in src/main.py rather than an error status, per the AMB-003 ruling (GRT-005) [P2]
- [ ] T3.4 Extend the unsupported-language test in tests/test_greeting.py to assert an identical response on repeat (GRT-005) [P3]

## Story S4 — Availability indication for operations
Implements: GRT-006

**Goal**: Operations can determine whether the service is available
without inspecting application behaviour or asking the owning team.

**Independent test**: `GET /health` reports available when the locale
table loaded, and unavailable when it did not.

**Scope guard**: availability only. No counters, no uptime, no locale
list — the G1 ruling on AMB-004 deferred metrics and structured logging
to a separate BRD. Adding them here is scope creep past an approved gate.

- [ ] T4.1 Write the failing health test in tests/test_health.py annotated Implements GRT-006 asserting HTTP 200 with status ok (GRT-006) [P3]
- [ ] T4.2 Implement GET /health in src/main.py returning status ok with HTTP 200 when the locale table loaded (GRT-006) [P3]
- [ ] T4.3 Return status unavailable with HTTP 503 when the locale table did not load, in src/main.py (GRT-006) [P3]
- [ ] T4.4 Add the unavailable-path test in tests/test_health.py exercising a missing config file (GRT-006) [P4]

---

## Phase 4: Polish and cross-cutting concerns

No separate polish story. Cross-cutting work is folded into the story
that owns it at P2–P4, so that every task closes against a criterion
somebody approved. A polish story would need an `Implements:` line, and
inventing one would either duplicate criteria across issues or attach
work to a criterion it does not serve.

---

## Dependencies

Story order: **S1 → S2 → S3 → S4**.

S1 is a hard prerequisite for the rest: it creates `config/locales.yml`,
`src/config.py`, `src/main.py`, and the response schema every later story
extends. S2, S3 and S4 depend on S1 but not on each other — once S1
lands, the remaining three can proceed in any order or concurrently.

Within stories, the test task precedes the implementation task it covers,
per CLAUDE.md. In S1, task 1.1 precedes 1.5 which precedes 1.6; 1.7
follows 1.5. In S2, 2.1 precedes 2.2 and 2.3. In S3, 3.1 precedes 3.2 and
3.3; 3.4 follows 3.1. In S4, 4.1 precedes 4.2 and 4.3; 4.4 follows 4.3.

## Parallel opportunities

Task IDs are referenced in prose here deliberately — writing them in task
format would make this parser absorb them into Story S4.

- Within S1, the three test tasks 1.2, 1.3 and 1.4 are independent of one
  another and can be written concurrently; 1.4 touches a different file
  from 1.2 and 1.3.
- After S1 merges, stories S2, S3 and S4 are mutually independent. S4
  touches only `tests/test_health.py` and the health route, so it shares
  no file with S3's greeting-resolution work.
- Tasks 2.2 and 3.2 both edit `src/greetings.py` and must not be run
  concurrently despite their stories being independent.

## Implementation strategy

**MVP scope: Story S1 alone.** It delivers a working greeting interface
that every regional application can call, which is BRD §4's first success
criterion, and it satisfies three of six criteria (GRT-002, GRT-003,
GRT-004). Stopping there would leave a service that greets everyone in
English — incomplete against BR-1, but genuinely useful and demonstrable.

Then S2 completes BR-1, S3 completes BR-3, S4 completes BR-4.

The drift gate reports progress mechanically at each step: 3/6 covered
after S1, 4/6 after S2, 5/6 after S3, 6/6 after S4. It stays red until the
last story lands, which is correct — the feature is not done until every
approved criterion has evidence.

## Traceability

| Criterion | Story | Tasks |
|---|---|---|
| GRT-001 | S2 | 2.1, 2.2, 2.3 |
| GRT-002 | S1 | 1.1, 1.2, 1.6 |
| GRT-003 | S1 | 1.4, 1.6 |
| GRT-004 | S1 | 1.3, 1.5, 1.7 |
| GRT-005 | S3 | 3.1, 3.2, 3.3, 3.4 |
| GRT-006 | S4 | 4.1, 4.2, 4.3, 4.4 |

All six approved criteria are covered, each by exactly one story. No task
cites a criterion outside its story. No criterion is invented here — the
set matches `spec.md` exactly, and `scripts/spec_drift.py` will hold it
to that.
