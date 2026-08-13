# Project instructions (loaded every Claude Code session)

## Governance
- Read and comply with memory/constitution.md in every session. It is
  human-authored and must never be created or modified by an agent.
  If Spec Kit is initialized, its mirror lives at
  .specify/memory/constitution.md; changes flow ONLY from memory/ to
  .specify/, never the reverse.
- Specs are the contract. Do not modify an approved spec.md, tasks.md,
  or any constitution file unless the user explicitly directs it.
- If completing a task would require deviating from the approved spec,
  stop and ask before proceeding.
- Task checkboxes in tasks.md are never hand-marked — not even when a
  skill's "done when" step says to mark them [X]. Completion is evidenced
  by spec_drift coverage plus commits citing criterion IDs, and issue
  state comes from gh_sync.py --update. Hand-marking is the one thing
  constitution Art. III.4 rules out by name.

## Traceability
- Every acceptance criterion carries a stable ID (GRT-###). Task
  numbers (T#.#) reshuffle on regeneration; criterion IDs do not.
  When the two conflict, the criterion ID is authoritative.
- Cite criterion IDs in code comments, test annotations
  ("# Implements: GRT-###"), and every commit message.
- Test first: the annotated acceptance test is written before or
  alongside the implementation it covers.
- spec_drift.py harvests criterion IDs from markdown TABLE CELLS: the ID
  stands alone between two pipes (`| GRT-001 | ... |`). An ID in a bullet
  list, in prose, or sharing a cell with other text is not harvested. A
  spec yielding zero criteria fails the gate rather than passing it.
- Retirement is line-scoped: `[RETIRED]` and the ID it retires must sit
  on the SAME physical line, normally the same table row. A marker on the
  line above or below does not register, and the criterion stays active
  — so the gate keeps demanding a test for it.

## Format contracts (tooling parses these; deviation is silent)
- tasks.md is parsed by scripts/gh_sync.py:
  - story: `## Story S<n> — <title>`, then `Implements: GRT-###, ...`
    on its own line (em dash or plain hyphen both parse).
  - task: `- [ ] T<s>.<n> <title> (GRT-###) [P1..P4]` — the line MUST end
    with the priority bracket.
  - a task may cite only criteria its story implements; --apply refuses
    otherwise, because --update reads the story's Implements line.
- The Spec Kit tasks template documents a different shape
  (`- [ ] T001 [P] [US1] ...`). The house format wins. The project
  override lives at .specify/templates/tasks-template.md — if a template
  refresh reverts it, restore it: a tasks.md in Spec Kit's default form
  parses to zero tasks.

## Definition of done (any implementation task)
1. .venv/bin/python -m pytest tests/ -q passes.
2. .venv/bin/python scripts/spec_drift.py --criterion GRT-### exits 0
   for each of this task's criteria. A full run still exits non-zero
   while OTHER criteria remain uncovered — that is the burndown working,
   not a failure of this task. Judge this task by the --criterion run,
   and the feature by the full run.
3. Work is committed with the criterion ID in the message; the working
   tree is left clean. Commit at the end of every unit of work — never
   leave a session's artifacts uncommitted.
4. A change to scripts/ or .github/workflows/ is not done until
   docs/DEMO-RUNBOOK.md and SETUP.md reflect it.

## Branches
- This repo uses the four-branch model in docs/BRANCHING.md: main and
  reference are never force-pushed or reset; demo-start and demo-live
  are disposable and recreated by ritual. Never commit demo/rehearsal
  output to main directly — it arrives via the demo-live PR.
- After any merged change to scripts/, workflows, CLAUDE.md, or the
  constitution, remind the user to rebuild demo-start (docs/BRANCHING.md).

## Environment
- Always use .venv/bin/python for Python commands in this repo. If
  .venv does not exist: python3 -m venv .venv && .venv/bin/pip install
  -r requirements.txt. Never install into the system Python.
- GitHub operations go through the gh CLI (authenticated via
  `gh auth login`); never handle raw tokens.
