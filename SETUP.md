# Environment Setup

Everything runs locally except GitHub itself (a free account is enough —
Actions and branch protection work on free private repos).

## 1. Local prerequisites

| Tool | Purpose | Install |
|------|---------|---------|
| Python 3.11+ | service, tests, scripts | python.org or pyenv |
| Git | version control, PR gates | git-scm.com |
| gh (GitHub CLI) | issue sync, auth | `brew install gh`, then `gh auth login` |
| uv (includes uvx) | runs the Spec Kit CLI | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| An AI coding agent | Claude Code, etc. | per vendor |

Required — the virtual environment (agents are pinned to it via CLAUDE.md):
```bash
cd ~/_work_/sdd-demo
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m pytest tests/ -q          # 6 passed
python scripts/spec_drift.py        # PASS: spec and tests agree
python scripts/gh_sync.py           # DRY RUN of the issue batch
```

Optional verification — the tests already exercise the service in-process;
this only proves it binds a real port:
```bash
uvicorn src.greeting_service.app:app --reload   # then GET /greet?locale=fr-FR
```

## 2. GitHub — repo, workflow, and the enforcement chain (in this order)

1. Make the directory a repo, then publish it. `--source=.` publishes an
   existing local repo (it does not scaffold a new one), so the commit and
   branch rename must come first:
   ```bash
   git init
   git add -A && git commit -m "SDD demo: finished reference state"
   git branch -M main
   gh repo create sdd-demo --private --source=. --push
   ```
   Then lay down the branch geography from `docs/BRANCHING.md` — `reference`
   as the answer key, `demo-start` as the frozen starting line:
   ```bash
   git checkout -b reference && git push -u origin reference
   git checkout main
   git checkout -B demo-start
   git rm -r specs src tests config 2>/dev/null; git rm -r .specify .claude 2>/dev/null
   git commit -m "demo: reset point rebuilt from main @ $(git rev-parse --short main)"
   git push -u origin demo-start
   git checkout main
   ```
2. Create the label the sync uses:
   ```bash
   gh label create story --description "Spec-derived story" --color 534AB7
   ```
3. The workflow (`.github/workflows/spec-drift.yml`) runs on PRs to
   `main` and on merges. **Make one throwaway PR first** — GitHub only
   offers a check as "required" after it has run at least once.
4. **Make the gate blocking** — Settings → Branches → Add branch
   protection rule for `main` (or Settings → Rules → Rulesets):
   - Require status checks to pass → select the `gates` job.
   - Require a pull request before merging (approvals count optional
     for a solo sandbox).
   - Optionally "Do not allow bypassing" so admins are bound too.
   This rule — not the workflow file — is what disables the merge
   button on red. The YAML defines the check; the protection rule
   makes it governance.
5. **Verify with a second throwaway PR**: the check runs automatically
   and the merge button stays disabled until green. Do not skip.

## 3. Spec Kit (optional richer tooling)

Pin a release tag — main breaks flags without notice:
```bash
export SPECKIT_REF="vX.Y.Z"   # record the tag you pinned here
uvx --from git+https://github.com/github/spec-kit.git@$SPECKIT_REF \
    specify init . --integration claude
```
Confirm in Claude Code: `/speckit` autocompletes. Spec Kit also ships a
`speckit-taskstoissues` skill — the agent-side alternative to
`scripts/gh_sync.py`. The script remains the transparent, CI-friendly
equivalent that enforces the tasks.md format contract and carries
criterion IDs; verify the skill preserves those IDs before switching.

## 4. The three sync modes

```bash
python scripts/gh_sync.py            # dry run — human reviews the batch
python scripts/gh_sync.py --apply    # creates 'story' Issues with task checklists
python scripts/gh_sync.py --update   # post-merge: comments evidence
                                     # (criteria, covering tests, commits)
                                     # and closes fully-covered issues
python scripts/gh_sync.py --feature specs/<dir>   # pick the feature explicitly
```
One-way by design: issues derive from the spec; issue state derives
from evidence. Editing acceptance criteria in an issue changes nothing
— the spec in the repo is the contract (constitution Art. I.3).

Which `tasks.md` gets synced: `--feature` wins, else the pointer in
`.specify/feature.json` (machine-local and gitignored, so CI never sees
it), else the single `specs/*/tasks.md` when exactly one exists. With two
or more features and no pointer, the tool stops and asks for `--feature`
rather than guessing.

**The sync refuses to run on a file it only partly understands.** A
checkbox line under a story that does not match the task contract is
reported with its line number, and a task citing a criterion its story
does not implement is reported too — `--apply` exits 1 until both are
clean. Previously such lines were skipped in silence, producing Issues
quietly short of the tasks they claimed to carry. Story headings accept
either an em dash or a plain hyphen.

## 5. The gates, and running them one at a time

CI runs three, in this order (`.github/workflows/spec-drift.yml`):

```bash
python scripts/constitution_check.py   # Gate 0 — .specify mirror == memory/
python scripts/spec_drift.py           # Gate 1 — criterion ⇄ test traceability
python -m pytest tests/ -q             # Gate 2 — the tests themselves
```

**Gate 0** exists because the mirror is agent-writable while
`memory/constitution.md` is not. It compares each article's heading and
body (ignoring heading level and the template scaffolding around them)
and fails on divergence in either direction. No `.specify/` present — as
on `demo-start` — is a pass, not a failure: the mirror is optional
tooling, the source is not.

**Gate 1** harvests criterion IDs from markdown **table cells**: the ID
must stand alone between two pipes (`| GRT-001 | … |`). An ID in a bullet
list or sharing a cell with other text is not harvested, and a spec that
yields *zero* criteria now fails loudly — an empty criteria set would
otherwise satisfy every other check and turn the required status check
green without verifying anything.

During incremental work the full Gate 1 run exits non-zero while any
criterion is uncovered, which makes it useless as a per-task check. Ask
the narrower question instead:

```bash
python scripts/spec_drift.py --criterion GRT-005   # exits 0 if that one is covered
```

## 6. Sandbox hygiene

Use a throwaway repo for demos so `--apply` runs are consequence-free.
Re-runs of `--apply` create duplicate issues (no dedup by design —
review the dry run first); close stale ones with
`gh issue list --label story` + `gh issue close`.
