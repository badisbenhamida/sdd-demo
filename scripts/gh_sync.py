#!/usr/bin/env python3
"""gh_sync.py — derive GitHub Issues from tasks.md (spec → GitHub, one way).

Governance: dry-run is the default; a human reviews the batch, then
re-runs with --apply. Stories become Issues labeled "story"; tasks
become checklist items in the story's body, each carrying its GRT
criterion IDs.

Update mode (run AFTER the merge, when the drift gate is green):
  --update maps evidence back onto the issues: for every open "story"
  issue, it (a) comments with the commits whose messages cite the
  story's criteria, (b) closes the issue when all of them are covered by
  annotated tests. Direction of authority is preserved: evidence (git)
  -> issue state, never the reverse.

Which tasks.md: --feature wins, else .specify/feature.json (machine-local,
gitignored), else the single specs/*/tasks.md when there is exactly one.

Auth: the `gh` CLI (https://cli.github.com) — `gh auth login` once;
no tokens live in this script.

Dry run:  python scripts/gh_sync.py
Apply:    python scripts/gh_sync.py --apply
Update:   python scripts/gh_sync.py --update
          (add GH_REPO=owner/name to target a repo other than the cwd's)

Two invariants this tool enforces rather than assumes
-----------------------------------------------------
1. A checkbox line under a story that does not match the task contract is
   REPORTED, not skipped. It used to be dropped in silence, so a single
   malformed line produced an Issue quietly short by one checklist item
   and nobody learned the task existed.
2. A task may only cite criteria its story implements. --update reads the
   story's own "Implements:" line, so a stray ID in a task no longer
   widens that issue's closure condition; --apply refuses to run until
   the mismatch is fixed, because the two halves must agree.
"""

from __future__ import annotations  # PEP 604 unions below must not need 3.10

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# An em dash is house style, but a plain hyphen parses too: it is what
# most keyboards produce, it is invisible in a diff, and this script's own
# error message used to print the hyphen form — so following the error
# message used to guarantee the failure it was diagnosing.
STORY_RE = re.compile(r"^## Story (S\d+) [—-] (.+)$")
IMPLEMENTS_RE = re.compile(r"^Implements: (.+)$")
TASK_RE = re.compile(r"^- \[.\] (T\d+\.\d+) (.+?) \(([^)]+)\) \[(P\d)\]$")
CHECKBOX_RE = re.compile(r"^- \[.\] ")
GRT_RE = re.compile(r"GRT-\d{3}")

# The story's own criteria line inside an Issue body, as issue_body() writes
# it. --update reads THIS and not the whole body: the body also lists every
# task's criteria, so scanning it wholesale made an issue's closure
# condition the union of story and task IDs — silently widened by any task
# citing something its story does not own.
BODY_IMPLEMENTS_RE = re.compile(r"^\*\*Implements:\*\* (.+)$", re.M)

CONTRACT_HELP = (
    '  story:  "## Story S<n> — <title>" then "Implements: GRT-###, ..."\n'
    '          (an em dash "—" or a plain hyphen "-" both parse)\n'
    '  task:   "- [ ] T<s>.<n> <title> (GRT-###) [P1..P4]"\n'
    "          the line must END with the priority bracket"
)


def gh(*args: str) -> subprocess.CompletedProcess:
    cmd = ["gh", *args]
    repo = os.environ.get("GH_REPO")
    if repo:
        cmd += ["--repo", repo]
    return subprocess.run(cmd, capture_output=True, text=True)


def resolve_tasks_path(feature: str | None) -> Path:
    """Locate tasks.md without hardcoding a feature directory.

    feature.json is machine-local and gitignored (.specify/.gitignore), so
    CI reaches this through the single-feature fallback, not the pointer.
    """
    if feature:
        candidate = Path(feature)
        if not candidate.is_absolute():
            candidate = ROOT / candidate
        return candidate if candidate.name == "tasks.md" else candidate / "tasks.md"

    pointer = ROOT / ".specify" / "feature.json"
    if pointer.exists():
        try:
            directory = json.loads(pointer.read_text(encoding="utf-8")).get(
                "feature_directory"
            )
            if directory:
                return ROOT / directory / "tasks.md"
        except (json.JSONDecodeError, OSError):
            pass  # fall through to discovery; a stale pointer must not block CI

    found = sorted(p for p in ROOT.glob("specs/*/tasks.md"))
    if len(found) == 1:
        return found[0]
    if not found:
        return ROOT / "specs" / "tasks.md"  # reported as missing by caller
    raise SystemExit(
        "ERROR: {} feature directories contain a tasks.md:\n{}\n"
        "Disambiguate with --feature specs/<dir>.".format(
            len(found),
            "\n".join("  " + p.relative_to(ROOT).as_posix() for p in found),
        )
    )


def parse(tasks_path: Path) -> tuple[list[dict], list[tuple[int, str]]]:
    """Return (stories, malformed_lines).

    malformed_lines holds checkbox lines that appeared under a story but
    did not match the task contract. They are returned rather than
    ignored so the caller can refuse to sync a partially-read file.
    """
    stories: list[dict] = []
    malformed: list[tuple[int, str]] = []
    current = None
    for number, line in enumerate(
        tasks_path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if m := STORY_RE.match(line):
            current = {"id": m[1], "title": m[2], "criteria": "", "tasks": []}
            stories.append(current)
        elif current and (m := IMPLEMENTS_RE.match(line)):
            current["criteria"] = m[1]
        elif current and (m := TASK_RE.match(line)):
            current["tasks"].append(
                {"id": m[1], "title": m[2], "criteria": m[3], "priority": m[4]}
            )
        elif current and CHECKBOX_RE.match(line):
            malformed.append((number, line))
    return stories, malformed


def criteria_problems(stories: list[dict]) -> list[str]:
    """Tasks may only cite criteria their story implements.

    Enforced at --apply because --update reads the story line alone: a
    task citing an outside ID would otherwise be tracked nowhere, having
    previously been tracked by accident.
    """
    problems: list[str] = []
    for story in stories:
        story_ids = set(GRT_RE.findall(story["criteria"]))
        if not story_ids:
            problems.append(
                f"{story['id']} has no criterion IDs on its 'Implements:' line"
            )
        for task in story["tasks"]:
            outside = set(GRT_RE.findall(task["criteria"])) - story_ids
            if outside:
                problems.append(
                    "{} cites {} which {} does not implement".format(
                        task["id"], ", ".join(sorted(outside)), story["id"]
                    )
                )
    return problems


def issue_body(s: dict, source: str = "specs/001-greeting-service/tasks.md") -> str:
    lines = [
        f"Derived from `{source}` — do not edit",
        "acceptance criteria here; requirement changes are PRs against the spec.",
        "",
        f"**Implements:** {s['criteria']}",
        "",
        "### Tasks",
    ]
    for t in s["tasks"]:
        lines.append(f"- [ ] **{t['id']}** {t['title']} ({t['criteria']}) [{t['priority']}]")
    return "\n".join(lines)


def covered_criteria() -> set[str]:
    """Criteria with covering annotated tests (mirrors spec_drift)."""
    covered: set[str] = set()
    impl = re.compile(r"Implements:\s*((?:GRT-\d{3}(?:,\s*)?)+)")
    for test in ROOT.glob("tests/**/*.py"):
        for m in impl.finditer(test.read_text(encoding="utf-8")):
            covered.update(GRT_RE.findall(m.group(1)))
    return covered


def local_commits_by_criterion() -> dict[str, list[str]]:
    out = subprocess.run(
        ["git", "-C", str(ROOT), "log", "--pretty=%h|%s"],
        capture_output=True, text=True, check=True,
    ).stdout
    mapping: dict[str, list[str]] = {}
    for line in out.splitlines():
        sha, _, subject = line.partition("|")
        for cid in GRT_RE.findall(subject):
            mapping.setdefault(cid, []).append(sha)
    return mapping


def story_criteria(body: str) -> set[str]:
    """The story's OWN criteria, from its '**Implements:**' line only."""
    m = BODY_IMPLEMENTS_RE.search(body or "")
    return set(GRT_RE.findall(m.group(1))) if m else set()


def update_issues() -> int:
    result = gh("issue", "list", "--label", "story", "--state", "open",
                "--json", "number,title,body")
    if result.returncode != 0:
        print(f"ERROR listing issues: {result.stderr.strip()}")
        print("Hint: gh auth login; run inside the repo or set GH_REPO=owner/name.")
        return 1
    issues = json.loads(result.stdout or "[]")
    if not issues:
        print("No open 'story' issues with criterion linkage — run --apply first.")
        return 1

    covered = covered_criteria()
    commits = local_commits_by_criterion()

    for issue in issues:
        crits = story_criteria(issue.get("body") or "")
        num = str(issue["number"])
        if not crits:
            print(f"#{num} {issue['title'][:50]}: no '**Implements:**' line — skipped")
            continue
        done = crits <= covered
        shas = sorted({s for c in sorted(crits) for s in commits.get(c, [])})
        evidence = [
            "**Evidence update (mechanical — derived from git, not hand-marked):**",
            f"- Criteria: {', '.join(sorted(crits))}",
            f"- Covered by annotated tests: {'all' if done else ', '.join(sorted(crits & covered)) or 'none'}",
        ]
        if shas:
            evidence.append(f"- Implementing commits: {', '.join(shas)}")
        if not done:
            evidence.append(f"- Awaiting evidence: {', '.join(sorted(crits - covered))}")
        gh("issue", "comment", num, "--body", "\n".join(evidence))
        if done:
            gh("issue", "close", num, "--reason", "completed")
            print(f"#{num} {issue['title'][:50]}: evidence commented, closed")
        else:
            print(f"#{num} {issue['title'][:50]}: awaiting {', '.join(sorted(crits - covered))}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Derive GitHub Issues from tasks.md (spec -> GitHub, one way).",
    )
    parser.add_argument("--apply", action="store_true",
                        help="create the Issues (default is a dry run)")
    parser.add_argument("--update", action="store_true",
                        help="post-merge: comment evidence and close covered issues")
    parser.add_argument("--feature", metavar="PATH",
                        help="feature directory or tasks.md path to sync")
    args = parser.parse_args()

    if args.update:
        return update_issues()

    tasks_path = resolve_tasks_path(args.feature)
    if not tasks_path.exists():
        print(f"ERROR: {tasks_path} not found.")
        print("Pass --feature specs/<dir>, or run /speckit.tasks first.")
        return 1

    rel = tasks_path.relative_to(ROOT) if tasks_path.is_relative_to(ROOT) else tasks_path
    stories, malformed = parse(tasks_path)

    if not stories or not any(s["tasks"] for s in stories):
        print(f"ERROR: parsed 0 stories/tasks from {rel}.")
        print("The file does not match the format contract this parser expects:")
        print(CONTRACT_HELP)
        print("Reformat tasks.md to the contract (do not loosen the parser).")
        return 1

    # Partial deviations used to vanish. Surface them before anything syncs.
    if malformed:
        print(f"WARNING: {len(malformed)} checkbox line(s) under a story did not")
        print("match the task contract and were NOT parsed:")
        for number, line in malformed:
            print(f"  {rel}:{number}: {line.strip()}")
        print(CONTRACT_HELP)
        print()

    problems = criteria_problems(stories)
    if problems:
        print("WARNING: criterion linkage problems:")
        for problem in problems:
            print(f"  {problem}")
        print("A task may only cite criteria its story implements — --update")
        print("reads the story's 'Implements:' line, so an outside ID is")
        print("tracked nowhere.")
        print()

    print(f"{'APPLY' if args.apply else 'DRY RUN'} — derived from {rel}\n")
    for s in stories:
        print(f"[Issue] {s['id']} — {s['title']}   (Implements: {s['criteria']})")
        for t in s["tasks"]:
            print(f"   - [ ] {t['id']} {t['title']}  ({t['criteria']}, {t['priority']})")
    print(f"\nTotal: {len(stories)} issues, {sum(len(s['tasks']) for s in stories)} checklist tasks")

    if not args.apply:
        if malformed or problems:
            print("\nResolve the warnings above before --apply.")
        else:
            print("\nNo changes made. Re-run with --apply after human review.")
        return 0

    if malformed or problems:
        print("\nREFUSING to apply: fix the warnings above first.")
        print("Syncing now would create Issues that misrepresent tasks.md.")
        return 1

    for s in stories:
        result = gh("issue", "create", "--title", f"{s['id']} — {s['title']}",
                    "--body", issue_body(s, str(rel)), "--label", "story")
        if result.returncode != 0:
            print(f"ERROR creating issue for {s['id']}: {result.stderr.strip()}")
            print("Hint: gh auth login; create a 'story' label or drop --label.")
            return 1
        print(f"Created {result.stdout.strip()}  ({s['id']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
