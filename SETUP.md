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
uvicorn src.greeting_service.app:app --reload   # then GET /greet?locale=fr-FR
```

## 2. GitHub — repo, workflow, and the enforcement chain (in this order)

1. Create the repo and push:
   ```bash
   gh repo create sdd-demo --private --source=. --push
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
```
One-way by design: issues derive from the spec; issue state derives
from evidence. Editing acceptance criteria in an issue changes nothing
— the spec in the repo is the contract (constitution Art. I.3).

## 5. Sandbox hygiene

Use a throwaway repo for demos so `--apply` runs are consequence-free.
Re-runs of `--apply` create duplicate issues (no dedup by design —
review the dry run first); close stale ones with
`gh issue list --label story` + `gh issue close`.
