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

## Traceability
- Every acceptance criterion carries a stable ID (GRT-###). Task
  numbers (T#.#) reshuffle on regeneration; criterion IDs do not.
  When the two conflict, the criterion ID is authoritative.
- Cite criterion IDs in code comments, test annotations
  ("# Implements: GRT-###"), and every commit message.
- Test first: the annotated acceptance test is written before or
  alongside the implementation it covers.

## Definition of done (any implementation task)
1. .venv/bin/python -m pytest tests/ -q passes.
2. .venv/bin/python scripts/spec_drift.py no longer lists this task's
   criteria as uncovered.
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
