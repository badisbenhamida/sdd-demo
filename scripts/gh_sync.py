#!/usr/bin/env python3
"""gh_sync.py — derive GitHub Issues from tasks.md (spec → GitHub, one way).

Governance: dry-run is the default; a human reviews the batch, then
re-runs with --apply. Stories become Issues labeled "story"; tasks
become checklist items in the story's body, each carrying its GRT
criterion IDs.

Update mode (run AFTER the merge, when the drift gate is green):
  --update maps evidence back onto the issues: for every open "story"
  issue whose body carries GRT IDs, it (a) comments with the commits
  whose messages cite those IDs, (b) closes the issue when all its
  criteria are covered by annotated tests. Direction of authority is
  preserved: evidence (git) -> issue state, never the reverse.

Auth: the `gh` CLI (https://cli.github.com) — `gh auth login` once;
no tokens live in this script.

Dry run:  python scripts/gh_sync.py
Apply:    python scripts/gh_sync.py --apply
Update:   python scripts/gh_sync.py --update
          (add GH_REPO=owner/name to target a repo other than the cwd's)
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASKS = ROOT / "specs" / "001-greeting-service" / "tasks.md"

STORY_RE = re.compile(r"^## Story (S\d+) — (.+)$")
IMPLEMENTS_RE = re.compile(r"^Implements: (.+)$")
TASK_RE = re.compile(r"^- \[.\] (T\d+\.\d+) (.+?) \(([^)]+)\) \[(P\d)\]$")
GRT_RE = re.compile(r"GRT-\d{3}")


def gh(*args: str) -> subprocess.CompletedProcess:
    cmd = ["gh", *args]
    repo = os.environ.get("GH_REPO")
    if repo:
        cmd += ["--repo", repo]
    return subprocess.run(cmd, capture_output=True, text=True)


def parse() -> list[dict]:
    stories, current = [], None
    for line in TASKS.read_text(encoding="utf-8").splitlines():
        if m := STORY_RE.match(line):
            current = {"id": m[1], "title": m[2], "criteria": "", "tasks": []}
            stories.append(current)
        elif current and (m := IMPLEMENTS_RE.match(line)):
            current["criteria"] = m[1]
        elif current and (m := TASK_RE.match(line)):
            current["tasks"].append(
                {"id": m[1], "title": m[2], "criteria": m[3], "priority": m[4]}
            )
    return stories


def issue_body(s: dict) -> str:
    lines = [
        "Derived from `specs/001-greeting-service/tasks.md` — do not edit",
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
        crits = set(GRT_RE.findall(issue.get("body") or ""))
        if not crits:
            continue
        num = str(issue["number"])
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
    if "--update" in sys.argv:
        return update_issues()

    apply = "--apply" in sys.argv
    stories = parse()

    if not stories or not any(s["tasks"] for s in stories):
        print(f"ERROR: parsed 0 stories/tasks from {TASKS.relative_to(ROOT)}.")
        print("The file does not match the format contract this parser expects:")
        print('  story:  "## Story S<n> - <title>" then "Implements: GRT-###, ..."')
        print('  task:   "- [ ] T<s>.<n> <title> (GRT-###) [P1..P4]"')
        print("Reformat tasks.md to the contract (do not loosen the parser).")
        return 1

    print(f"{'APPLY' if apply else 'DRY RUN'} — derived from {TASKS.relative_to(ROOT)}\n")
    for s in stories:
        print(f"[Issue] {s['id']} — {s['title']}   (Implements: {s['criteria']})")
        for t in s["tasks"]:
            print(f"   - [ ] {t['id']} {t['title']}  ({t['criteria']}, {t['priority']})")
    print(f"\nTotal: {len(stories)} issues, {sum(len(s['tasks']) for s in stories)} checklist tasks")

    if not apply:
        print("\nNo changes made. Re-run with --apply after human review.")
        return 0

    for s in stories:
        result = gh("issue", "create", "--title", f"{s['id']} — {s['title']}",
                    "--body", issue_body(s), "--label", "story")
        if result.returncode != 0:
            print(f"ERROR creating issue for {s['id']}: {result.stderr.strip()}")
            print("Hint: gh auth login; create a 'story' label or drop --label.")
            return 1
        print(f"Created {result.stdout.strip()}  ({s['id']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
