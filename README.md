# SDD Demo — BRD to Deployed Code, Traceably (GitHub edition)

A walking skeleton demonstrating an AI-assisted SDLC anchored in
Spec-Driven Development on a pure GitHub stack. It proves one claim
end to end:

> **Every business requirement is traceable to running, tested code —
> and the chain is machine-enforced, with humans at every gate.**

Chain: `BRD section → EARS criterion (GRT-###) → GitHub Issue → commit → test → required check`

## Repository map

```
docs/brd/            BRD-2026-014 — the business input (prose, gaps intact)
memory/              constitution.md — human-authored governance (never agent-generated)
specs/001-.../       spec.md (EARS + Ambiguity Log) · tasks.md (issue-sync source)
src/                 the greeting service (FastAPI)
tests/               acceptance tests annotated `Implements: GRT-###`
scripts/             spec_drift.py (traceability gate) · gh_sync.py (dry-run-first sync)
.github/workflows/   spec-drift.yml (required status check on PRs to main)
config/              locales.yml — the only place greeting text lives (GRT-006)
CLAUDE.md            standing agent instructions (constitution, IDs, definition of done)
docs/BRANCHING.md    the four-branch model (main / reference / demo-start / demo-live)
```

## The end-to-end flow, by persona

Four personas: **Priya** (Business Analyst), **Marco** (Product Owner),
**Dana** (Tech Lead), **Sam** (Developer). The AI agent assists at every
step; a named human owns every gate.

### Step 1 — Business hands off the BRD *(Priya)*
`docs/brd/BRD-2026-014-greeting-service.md` arrives as prose — with the
usual gaps ("the system should handle unsupported languages") left in
deliberately. Nothing about the business's process changes.

### Step 2 — Agent-assisted BRD → spec transformation *(Priya + agent)*
The agent drafts `specs/001-greeting-service/spec.md`: six EARS criteria
with stable IDs (GRT-001…006), each traced back to a BRD requirement —
plus an **Ambiguity Log** of what the BRD didn't say. Priya routes each
ambiguity to the person who can resolve it. *The agent surfaces
questions; humans answer them.*

### Step 3 — Gate G1: Spec approval *(Marco)*
Marco reviews the spec as a PR — every ambiguity resolved, every
criterion testable — and approves. Downstream work is blocked until
this human gate passes (constitution Art. III.1).

### Step 4 — Plan and task breakdown *(Dana + agent)*
The agent derives `tasks.md`: 3 stories, 5 tasks, each carrying the
criterion IDs it implements. Dana adjusts grouping, sequencing, sizing
— the judgment calls — and approves (Gate G2).

### Step 5 — Issues appear in GitHub *(Dana)*
```
python scripts/gh_sync.py            # DRY RUN — human reviews the batch
python scripts/gh_sync.py --apply    # creates 'story' Issues with task checklists
```
Issues land with `Implements: GRT-###` in their bodies. One-way by
design: Issues track the work; the repo holds the contract. Boards and
projects — unchanged.

### Step 6 — Implementation *(Sam + agent)*
Sam picks up the GRT-003 task. The agent implements against the
criterion — constrained by the constitution via CLAUDE.md, citing the
ID in code comments and the commit message
(`feat: reject unsupported locales (GRT-003)`). The test declares
`# Implements: GRT-003`.

### Step 7 — Gate G3: PR + machine-enforced traceability *(Sam, Dana, CI)*
The PR triggers `.github/workflows/spec-drift.yml`:
```
Criteria: 6 active, 0 retired
Covered:  6/6
PASS: spec and tests agree.
```
If Sam had skipped the test — or the spec changed without tests
following — the required check fails and branch protection disables
the merge button:
```
DRIFT — criteria with no covering test:
  GRT-007
FAIL: spec drift detected.       (exit 1 → merge blocked)
```
Dana reviews and merges. Agents never merge (Art. III.3).

### Step 8 — The board catches up with reality *(Dana)*
```
python scripts/gh_sync.py --update
```
Each story issue gets a mechanical evidence comment — its criteria,
the covering tests, the implementing commits — and closes only when
all its criteria are covered. Truth flows from git to the issues,
never the reverse.

### Step 9 — The business closes the loop *(Priya)*
"Is BR-3 built and verified?" now has a machine answer: BR-3 → GRT-003
→ Issue S2 → commit → passing test → green required check. Issue
trackers record that *work happened*; this records that *the
requirement is satisfied*.

## Where "AI learns from enterprise knowledge" lives here

Three layers, produced as a byproduct of normal work:
- **Normative** — `memory/constitution.md`: policy injected into every
  agent session via CLAUDE.md. Human-authored, always.
- **Precedent** — the accumulating corpus of specs, ambiguity
  resolutions, and decisions. The next BRD's transformation retrieves
  how the last ones were interpreted.
- **Evidence** — drift history and test outcomes: the signal that a
  spec was wrong or incomplete, corrected in the repo, not in someone's
  memory.

## Try it

See [SETUP.md](SETUP.md). Quick local loop:
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m pytest tests/ -q && python scripts/spec_drift.py
python scripts/gh_sync.py
uvicorn src.greeting_service.app:app --reload
curl 'localhost:8000/greet?locale=ja-JP'
```

## Scope statement

This covers **requirements-to-code** (BRD → spec → issues → code →
tests → gate), not the full SDLC — no release management, incident
response, or portfolio planning. Deliberate: prove the plumbing on a
service small enough that nobody argues about the business logic.
