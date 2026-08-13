#!/usr/bin/env python3
"""spec_drift.py — enforce the criterion → test traceability chain.

Fails (exit 1) when:
  1. A spec criterion has no test declaring `Implements: <ID>`.
  2. A test declares an ID that is unknown or [RETIRED] in the spec.
  3. No criteria are harvested at all (see "Vacuous pass" below).

Run:  python scripts/spec_drift.py
      python scripts/spec_drift.py --criterion GRT-005
CI:   invoked by .github/workflows/spec-drift.yml on every PR.

Vacuous pass — why rule 3 exists
--------------------------------
Criterion IDs are harvested from markdown TABLE CELLS: the ID must stand
alone between two pipes, as in `| GRT-001 | When ... | BR-1 |`. A spec
that lists its criteria any other way — a bullet list, prose, or an ID
sharing a cell with other text — yields ZERO criteria.

An empty criteria set trivially satisfies rules 1 and 2, so before rule 3
existed this script printed "PASS" and exited 0 on a spec it could not
read. Since this is the required status check on `main`, the failure mode
was inverted: the worse the spec's format, the more likely the gate went
green. Rule 3 makes an unreadable spec loud instead of silent.

Retirement is line-scoped
-------------------------
RETIRED_RE is deliberately not compiled with re.DOTALL, so `[RETIRED]`
and the criterion ID it retires must appear on the SAME physical line —
normally the same table row. A marker on the line above or below does not
register and the criterion stays active.
"""

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC_GLOB = "specs/**/spec.md"
TEST_GLOB = "tests/**/*.py"

CRITERION_RE = re.compile(r"\|\s*(GRT-\d{3})\s*\|")
RETIRED_RE = re.compile(r"\[RETIRED\].*?(GRT-\d{3})|(GRT-\d{3}).*?\[RETIRED\]")
IMPLEMENTS_RE = re.compile(r"Implements:\s*((?:GRT-\d{3}(?:,\s*)?)+)")
CRITERION_ID_RE = re.compile(r"^GRT-\d{3}$")

FORMAT_HELP = """Criterion IDs are harvested from markdown table cells: the ID must stand
alone between two pipes, e.g.

  | ID      | Acceptance criterion (EARS) | Traces to |
  |---------|-----------------------------|-----------|
  | GRT-001 | When ... shall ...          | BR-1      |

An ID in a bullet list, in prose, or sharing a cell with other text is
not harvested."""


def collect_criteria() -> tuple[set[str], set[str]]:
    active, retired = set(), set()
    for spec in ROOT.glob(SPEC_GLOB):
        text = spec.read_text(encoding="utf-8")
        for m in RETIRED_RE.finditer(text):
            retired.add(m.group(1) or m.group(2))
        for m in CRITERION_RE.finditer(text):
            if m.group(1) not in retired:
                active.add(m.group(1))
    return active, retired


def collect_coverage() -> dict[str, list[str]]:
    covered: dict[str, list[str]] = {}
    for test in ROOT.glob(TEST_GLOB):
        for m in IMPLEMENTS_RE.finditer(test.read_text(encoding="utf-8")):
            for cid in re.findall(r"GRT-\d{3}", m.group(1)):
                covered.setdefault(cid, []).append(test.name)
    return covered


def report_no_criteria() -> int:
    """Rule 3. An unreadable spec must fail, not pass silently."""
    specs = sorted(p.relative_to(ROOT).as_posix() for p in ROOT.glob(SPEC_GLOB))
    print(f"ERROR: no criteria harvested from {SPEC_GLOB}.")
    if specs:
        print(f"Matched {len(specs)} spec file(s), none contributing an ID:")
        for path in specs:
            print(f"  {path}")
    else:
        print(f"No file matched {SPEC_GLOB} under {ROOT}.")
    print()
    print(FORMAT_HELP)
    print()
    print("Failing rather than passing: an empty criteria set would satisfy")
    print("every other check in this script and turn the required status")
    print("check green without verifying anything.")
    return 1


def check_one(criterion: str, active: set[str], retired: set[str],
              covered: dict[str, list[str]]) -> int:
    """--criterion mode: verdict on a single criterion.

    Exists because the full run exits 1 while ANY criterion is uncovered,
    which makes it useless for the per-task definition of done during
    incremental work (CLAUDE.md). This answers the narrower question the
    task actually asks.
    """
    if criterion in retired:
        print(f"PASS: {criterion} is retired; no covering test required.")
        return 0
    if criterion not in active:
        print(f"FAIL: {criterion} is not an active criterion in the spec.")
        print(f"Active: {', '.join(sorted(active)) or '(none)'}")
        return 1
    tests = sorted(set(covered.get(criterion, [])))
    if tests:
        print(f"PASS: {criterion} covered by {', '.join(tests)}")
        return 0
    print(f"FAIL: {criterion} has no test declaring 'Implements: {criterion}'.")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Enforce the criterion -> test traceability chain.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--criterion",
        metavar="GRT-###",
        help="check one criterion and ignore the rest; exits 0 when that "
             "criterion is covered, even if others are not. Use for the "
             "per-task definition of done during incremental work.",
    )
    args = parser.parse_args()

    if args.criterion and not CRITERION_ID_RE.match(args.criterion):
        print(f"ERROR: '{args.criterion}' is not a criterion ID (expected GRT-###).")
        return 2

    active, retired = collect_criteria()
    covered = collect_coverage()

    if not active and not retired:
        return report_no_criteria()

    if args.criterion:
        return check_one(args.criterion, active, retired, covered)

    uncovered = sorted(active - covered.keys())
    orphaned = sorted(set(covered) - active)

    print(f"Criteria: {len(active)} active, {len(retired)} retired")
    print(f"Covered:  {len(set(covered) & active)}/{len(active)}")

    ok = True
    if uncovered:
        ok = False
        print("\nDRIFT — criteria with no covering test:")
        for cid in uncovered:
            print(f"  {cid}")
    if orphaned:
        ok = False
        print("\nDRIFT — tests reference unknown/retired criteria:")
        for cid in orphaned:
            print(f"  {cid}  (in {', '.join(covered[cid])})")

    print("\nPASS: spec and tests agree." if ok else "\nFAIL: spec drift detected.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
