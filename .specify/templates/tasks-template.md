---

description: "Task list template — HOUSE FORMAT, parsed by scripts/gh_sync.py"
---

# Tasks: [FEATURE NAME]

**Input**: Design documents from `/specs/[###-feature-name]/`

**Prerequisites**: plan.md (required), spec.md (required for criterion IDs), research.md, data-model.md, contracts/

**Status**: Draft — G2 pending until a human tech lead approves the plan (constitution Art. III.2).

<!--
  ============================================================================
  PROJECT OVERRIDE. This replaces the Spec Kit default template.

  Spec Kit's stock template documents tasks as:
      - [ ] T001 [P] [US1] Description with file path
  That form parses to ZERO tasks in scripts/gh_sync.py and the sync
  errors out. The house format below is the one the tooling reads.

  If a Spec Kit upgrade reverts this file, restore it — see CLAUDE.md,
  "Format contracts". Do not loosen the parser to match a template.
  ============================================================================
-->

## Format contract (exact — the parser is the authority)

`scripts/gh_sync.py` derives GitHub Issues from this file. A line that
deviates is **reported and refused**, not silently accepted:

- **Story heading**: `## Story S<n> — <title>`
  An em dash (`—`) or a plain hyphen (`-`) both parse.
- **Story criteria**: `Implements: GRT-###, ...` on its own line,
  directly under the heading.
- **Task**: `- [ ] T<s>.<n> <title> (GRT-###) [P<n>]`
  The line MUST end with the priority bracket. Criterion IDs are the last
  parenthesised group before it. Avoid parentheses inside the title.

Two invariants to maintain deliberately:

1. **Every task's criteria are a subset of its story's criteria.**
   `--update` reads the story's own `Implements:` line, so an ID cited
   only by a task is tracked nowhere. `--apply` refuses until fixed.
2. **No task-format line appears outside a story block.** Any such line
   after a story heading is absorbed into that story — so dependency and
   parallelism sections must reference task IDs in prose only.

## Path conventions

Per plan.md. Single project: `src/` and `tests/` at repository root.

---

## Phase 1: Setup

Project initialization. If the repository already provides the toolchain,
say so explicitly rather than leaving the phase blank — an empty phase
should read as a finding, not an omission.

## Phase 2: Foundational

Blocking prerequisites shared by every story. Prefer folding these into
the first story that needs them; a phase no story can ship without
defeats independent delivery.

---

## Phase 3: User Stories

One story per deliverable increment, in priority order. Every approved
criterion should appear in exactly one story, so that no two issues
compete to close the same criterion.

## Story S1 — [Title]
Implements: GRT-###, GRT-###

**Goal**: [What ships when this story is done.]

**Independent test**: [How to verify this story alone, without the others.]

- [ ] T1.1 [Write the failing acceptance test in tests/<file>, annotated Implements GRT-###] (GRT-###) [P1]
- [ ] T1.2 [Implement the behaviour in src/<file>] (GRT-###) [P1]

## Story S2 — [Title]
Implements: GRT-###

**Goal**: [What ships when this story is done.]

**Independent test**: [How to verify this story alone.]

- [ ] T2.1 [Write the failing acceptance test in tests/<file>, annotated Implements GRT-###] (GRT-###) [P2]
- [ ] T2.2 [Implement the behaviour in src/<file>] (GRT-###) [P2]

---

## Phase 4: Polish and cross-cutting concerns

Prefer folding cross-cutting work into the story that owns it, at P2–P4.
A separate polish story needs an `Implements:` line, which forces either
duplicating criteria across issues or attaching work to a criterion it
does not serve.

---

## Dependencies

Story order and, within each story, test-before-implementation ordering
(CLAUDE.md). Reference task IDs in prose here — a task-format line in this
section would be absorbed into the last story above.

## Parallel opportunities

Which stories and tasks are genuinely independent, and which share a file
and therefore must not run concurrently. Prose only, same reason.

## Implementation strategy

MVP scope (usually the first story alone), then the increments that
follow. State what the drift gate should report after each story lands —
it stays red until the last criterion is covered, which is correct.

## Traceability

| Criterion | Story | Tasks |
|---|---|---|
| GRT-### | S# | #.#, #.# |

Every approved criterion covered, each by exactly one story, and no
criterion invented here that `spec.md` does not carry.
