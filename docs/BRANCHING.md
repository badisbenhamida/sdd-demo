# Branching Model

Four branches, four jobs. The repo's purpose is to be demonstrated
repeatedly, so the model separates *durable state* (main, reference)
from *per-run state* (demo-start, demo-live).

| Branch | Contains | Force-push | Recreated |
|---|---|---|---|
| `main` | Finished reference state. Branch protection + required `gates` check attached. All tooling/doc changes land here via PR. | **Never** | Never |
| `reference` | Same content as the finished state, under an explicit name — the answer key and live-demo fallback (`git checkout reference` mid-demo if the live run derails). | **Never** | Only deliberately, from main |
| `demo-start` | The frozen starting line: BRD, constitution, scripts, workflow, CLAUDE.md, docs — and **none** of the process outputs (`specs/`, `src/`, `tests/`, `config/`, `.specify/`, `.claude/`). Purely derived from main. | Yes (by rebuild) | After any tooling change on main |
| `demo-live` | Where a demo or rehearsal actually runs. Disposable by definition. | Yes | Every run |

## The two rituals

**Reset (before every demo run):**
```bash
git checkout demo-start && git pull
git checkout -B demo-live && git push -u origin demo-live --force
gh issue list --label story        # close leftovers from the previous run
```
Spec Kit init happens fresh on demo-live each run (Runbook Part 0.5) —
the scaffolding is per-run state, which also re-verifies the pinned
SPECKIT_REF as a side effect.

**Rebuild demo-start (after any PR that changes scripts/, workflows,
CLAUDE.md, or the constitution on main):**
```bash
git checkout main && git pull
git checkout -B demo-start
git rm -r specs src tests config 2>/dev/null; git rm -r .specify .claude 2>/dev/null
git commit -m "demo: reset point rebuilt from main @ $(git rev-parse --short main)"
git push -f origin demo-start
git checkout main
```
This rule is absolute, not judgment-based: a change to main that isn't
propagated leaves the next demo running on stale tooling — the class of
surprise this model exists to prevent.

## Rules

1. `main` and `reference` hold unrecoverable state — never `-B`, never
   `push -f`.
2. `demo-start` and `demo-live` hold nothing unique — always safe to
   recreate.
3. Every demo's PR targets `main` from `demo-live`; the merged run
   becomes part of main's history. (Consequence: subsequent demo PRs
   show a replacement diff, not pure addition — acceptable by choice.)
4. Ordinary development (tooling fixes, doc updates) uses normal
   short-lived branches off main through the PR gate, like any repo.
6. **Merge methods:** docs/tooling PRs → squash (one logical change,
   one commit). Demo-run PRs (demo-live → main) → **merge commit** —
   the per-criterion commit trail is the deliverable, and
   gh_sync --update reads GRT IDs from individual commit messages;
   squashing destroys both.
7. **Clean-tree guard:** after the reset ritual and BEFORE
   `specify init`, `git status --short` must be empty. Untracked
   leftovers (e.g., from an archive extract) get silently adopted by
   the scaffolding commit's `git add -A`.
