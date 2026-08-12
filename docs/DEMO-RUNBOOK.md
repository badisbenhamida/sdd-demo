# Demo Runbook — SDD End-to-End with Claude Code + Spec Kit + GitHub

**Claim demonstrated:** a BRD becomes governed, traceable, tested code —
AI does the drudgery, a named human owns every gate, and the machine
enforces the chain. Duration: ~40 min live (or ~25 with fallbacks).

---

## Part 0 — Setup (complete ALL of this at least a day before demo)

### 0.1 Tooling
```bash
curl -fsSL https://claude.ai/install.sh | bash        # Claude Code
curl -LsSf https://astral.sh/uv/install.sh | sh       # uv / uvx
brew install gh && gh auth login                      # GitHub CLI
```
Spec Kit: **pin a release tag** (main breaks flags without notice):
```bash
export SPECKIT_REF="vX.Y.Z"   # record the tag you pinned in this file
```

### 0.2 Repo environment
```bash
cd ~/_work_/sdd-demo
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```
The venv is mandatory, not hygiene — CLAUDE.md pins the agent to
.venv/bin/python so a multi-Python machine can't derail a live session.

### 0.3 Branch geography
| Branch | Role |
|---|---|
| `main` | Trunk. Branch protection attached. Pre-process state before the real demo. |
| `reference` | Finished answer key. Comparison exhibit and live-demo fallback. |
| `demo-start` | Frozen starting line: BRD + constitution + tooling, no process outputs. |
| `demo-live` | Disposable. Recreated per run. |

Reset ritual before every run:
```bash
git checkout demo-start && git pull
git checkout -B demo-live && git push -u origin demo-live --force
git status --short             # MUST be empty — untracked ghosts here get
                               # silently adopted by the scaffolding commit
gh issue list --label story    # close leftovers from the previous run
                               # (lists OPEN only — those are the ones that
                               # matter; a leftover open issue gets adopted
                               # and closed by the NEXT run's evidence.
                               # Closed issues from earlier runs are inert.)
```
Full model, rules, and the demo-start rebuild ritual: docs/BRANCHING.md.
Rule that matters most: any PR changing scripts/, workflows, CLAUDE.md,
or the constitution on main obligates a demo-start rebuild.

### 0.4 GitHub — in this exact order
1. Repo pushed; all four branches on origin. `story` label exists.
2. Workflow present on `main` (`.github/workflows/spec-drift.yml`).
3. **Run the check once** via a throwaway PR — GitHub only offers a
   check as "required" after its first run.
4. **Branch protection on `main`**: required status check = `gates`
   job; require a PR before merging. This rule — not the YAML — is
   what disables the merge button on red.
5. **Verify with a second throwaway PR**: check queues automatically,
   merge button dead until green. Do not skip the verification.

### 0.5 Spec Kit init (on demo-live, after the reset ritual)
```bash
uvx --from git+https://github.com/github/spec-kit.git@$SPECKIT_REF \
    specify init . --integration claude
# non-empty-directory warning → y (no filename collisions; git is the net)
git add -A && git commit -m "chore: spec kit scaffolding"
```
Confirm: `claude` → `/speckit` autocompletes, and the agent
acknowledges memory/constitution.md (wired via CLAUDE.md).

---

## Part 1 — The demo

### Act 1 — The business input (3 min)
Show `docs/brd/BRD-2026-014-greeting-service.md`.
> "This is what engineering receives: prose. BR-3 says the system
> should 'handle' unsupported languages. Handle how? Today that gets
> discovered in sprint 3. Watch where it gets discovered instead."

### Act 2 — Constitution (3 min)
```
/speckit.constitution Read memory/constitution.md and mirror it into
the project constitution. Preserve all four articles verbatim — do not
restructure or reword; template headings around the content are fine.
Then commit: "constitution: mirrored into .specify (G0)".
```
If offered options, choose **Mirror existing** — authority flows
memory/ → .specify/, never the reverse.

### Act 3 — BRD → spec (7 min) — the money act
```
/speckit.specify Transform docs/brd/BRD-2026-014-greeting-service.md
into a specification. Requirements: (1) EARS notation; (2) stable
criterion IDs GRT-###, never reused; (3) a traceability column mapping
each criterion to its BRD requirement; (4) an Ambiguity Log: every gap
in the BRD as a question for the business with a proposed resolution
marked PENDING HUMAN APPROVAL. Do not invent requirements the BRD
doesn't imply. Commit when done: "spec: draft from BRD-2026-014,
pending G1".
```
Expect several ambiguities — runs have produced 5 to 9 from this same
BRD; the count and decomposition legitimately vary per generation.
Typical themes: unsupported-language handling, launch language set,
interface/auth, meaning of monitorable, response format. Bonus
artifacts (checklists/, contracts/) are normal.

### Act 4 — Gate G1 (4 min)
Read the ACTUAL log on screen and rule on every line it contains — the
generated log governs, not this script. The block below is an EXAMPLE
of ruling style from a prior run; adapt items, add rulings for
anything new, drop items that didn't appear:
```
As the Product Owner I'm resolving the ambiguity log in full:
- unsupported locale → explicit HTTP 400, machine-readable code
  UNSUPPORTED_LOCALE, include the supported-locale list. No silent fallback.
- launch locales → config/locales.yml decides; ship en-US, fr-FR,
  de-DE, ja-JP; en-US is the default when none is requested.
- interface → HTTP API; auth and network policy are platform-layer,
  out of scope — record the ruling in the log.
- monitorable → healthcheck reflecting config load state (503 → 200);
  logging/metrics deferred.
- response format → JSON with fields "message" and "locale".
Resolve any items beyond these on their merits; out-of-scope is a valid
ruling but stays recorded. Update the spec, record the resolver
(PO: <name>), set every status to Resolved, mark the spec Approved —
Gate G1, leave nothing PENDING, and commit:
"spec: G1 approved, ambiguity log resolved (PO)".
```
Verify: `grep -i pending specs/**/spec.md` → empty.

### Act 5 — Plan and tasks, Gate G2 (5 min)
```
/speckit.plan Python 3.12, FastAPI, pytest. Locale templates shall
load exclusively from config/locales.yml (file is created at
implementation time — it does not exist yet). No database. Commit when done:
"plan: G2 pending".
```
```
/speckit.tasks Group tasks into user stories. CONTRACT — scripts/
gh_sync.py parses this file and fails on any deviation: stories as
"## Story S<n> — <title>" followed by "Implements: GRT-###, ..."; tasks
as "- [ ] T<s>.<n> <title> (GRT-###) [P1..P4]". Every story and task
carries the criterion IDs it implements. Commit when done:
"tasks: G2 pending".
```
Review; adjust one grouping (G2 is real); then:
`Approved — Gate G2. Commit: "plan+tasks: G2 approved".`
Give the generated `contracts/` ten seconds of screen time.

### Act 6 — Issues appear in GitHub (4 min)
```bash
.venv/bin/python scripts/gh_sync.py          # DRY RUN on screen
```
> "A human reviews the batch before anything touches the tracker. And
> if tasks.md drifted from the format contract, the tool fails loudly
> instead of syncing nothing."
```bash
.venv/bin/python scripts/gh_sync.py --apply
```
Open one of the issues **just created** — the highest numbers. Story
titles repeat every run (`--apply` does not deduplicate), so after a
few runs the tracker holds several `S1 — …` issues that differ only by
number. Closed issues from earlier runs stay closed and are inert:
`--update` queries open issues only, so they are never rewritten.
> "'Implements: <IDs>' in the body, tasks as a checklist. One-way by
> design: requirement changes are PRs, not issue edits."

### Act 7 — Implementation (12 min)

**7a — one criterion, anatomy visible (4 min):**

Do NOT hardcode an ID — each run's spec assigns IDs differently.
Reference the behavior and let the agent read the contract:
```
Implement the criterion covering unsupported-language rejection. Read
its ID, status code, and error shape from the APPROVED SPEC — the spec
is authoritative, not this prompt. Acceptance test first, annotated
"# Implements: <that ID>". Run the definition-of-done gates, then
commit "feat: <behavior> (<ID>)".
```
The drift gate shows **red — 1/N covered** (N = this run's criterion
count). Narrate, don't flinch:
> "Red isn't failure — it's a live burndown of spec coverage."

**7b — the rest, batch speed (6 min):**
```
/speckit.implement Complete all remaining tasks. The criterion
implemented in 7a and the foundation it created are done — skip them
rather than redoing them. Per CLAUDE.md: test first with Implements annotations, venv
python only, definition-of-done gates per task, commit per task with
the criterion ID, stop and ask if anything requires deviating from the
approved spec.
```
Watch the uncovered list burn down; end on **N/N PASS**.

**7c — break it on purpose (2 min):**

Check the spec for the next unused ID first (with N criteria, it's
GRT-<N+1 padded>):
```
Add a new criterion <NEXT-ID> to the spec: WHEN more than 10 requests
per second arrive from one client, the service shall return HTTP 429.
Run the drift gate.
```
**Red**: the new criterion uncovered.
> "The spec moved and the code didn't — caught by a machine, not a
> retro. This exact check blocks every pull request."
```
Implement <NEXT-ID>: test first, then the implementation, gates, commit
"feat: per-client rate limiting (<NEXT-ID>)".
```
**Green.**

### Act 8 — The PR gate + the issues catch up (5 min)
```bash
git push
gh pr create --base main --title "Demo run: greeting service" --fill
```
On screen: the `gates` check runs automatically (that's the Part 0.4
protection rule), "Required" badge visible, merge button disabled until
green. A red ✗ on a mid-history commit is normal (checks ran against an
incomplete state); the verdict that governs is the check at HEAD.
Approve and merge as yourself — **"Create a merge commit", never
squash**: the per-act, per-criterion commit trail IS the deliverable,
and gh_sync --update reads criterion IDs from individual commit
messages (docs/BRANCHING.md rule 6).
> "Gate G3. A named human owned every gate you've seen — and two of
> the three are enforced by the platform, not by trust."

Then close the loop mechanically:
```bash
git checkout main && git pull
.venv/bin/python scripts/gh_sync.py --update
```
Open a story issue **from this run** (again, the highest numbers —
earlier runs' issues are closed with the same titles): evidence comment
(criteria, tests, commits), issue closed because coverage is complete.

The commit list may include commits from earlier merged runs. Criterion
IDs are stable across runs and `--update` reads the whole git log, so a
prior run's `feat: … (GRT-00N)` is genuine evidence for the same
criterion. If asked, that is the honest answer — it does not affect
closing, which is driven by annotated tests, not commits.
> "The tracker just caught up with reality — evidence flowed from git
> to the issues, never the reverse."

### Act 9 — Close the loop (2 min)
> "BR-3 in the business's own document → its criterion ID → an issue → commits →
> passing tests → a green required check. 'Is BR-3 built and verified?'
> is now machine-answerable. And every spec, ruling, and drift
> correction accumulated in the repo — the corpus the next BRD's
> transformation retrieves. The system gets smarter as a byproduct of
> shipping."

---

## Contingency table
| Failure | Fallback |
|---|---|
| Spec Kit output format differs | Narrate it: "the constitution and templates converge the tool on the house format." Compare against `reference`. |
| Actions runner delayed | Run both gates locally on screen; show a prior green run. |
| Claude Code stalls | `git checkout reference` and walk the finished artifacts — all nine acts still narrate. |
| gh_sync parses 0 | It fails loudly with the contract printed. Have Claude Code reformat tasks.md; 60 seconds, and the failure message is itself a governance talking point. |
| Wi-Fi dies | Acts 1–5 and 7 are fully local. Only 6 and 8 need the network. |

## Three sentences that carry the demo
1. "The agent surfaces the questions; humans answer them."
2. "The spec is the contract; the tracker records the work of fulfilling it."
3. "Traceability isn't a slide — it's a required check that can block a merge."
