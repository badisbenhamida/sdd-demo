#!/usr/bin/env python3
"""spec_drift.py — enforce the criterion → test traceability chain.

Fails (exit 1) when:
  1. A spec criterion has no test declaring `Implements: <ID>`.
  2. A test declares an ID that is unknown or [RETIRED] in the spec.

Run:  python scripts/spec_drift.py
CI:   invoked by pipelines/spec-drift.yml on every PR.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC_GLOB = "specs/**/spec.md"
TEST_GLOB = "tests/**/*.py"

CRITERION_RE = re.compile(r"\|\s*(GRT-\d{3})\s*\|")
RETIRED_RE = re.compile(r"\[RETIRED\].*?(GRT-\d{3})|(GRT-\d{3}).*?\[RETIRED\]")
IMPLEMENTS_RE = re.compile(r"Implements:\s*((?:GRT-\d{3}(?:,\s*)?)+)")


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


def main() -> int:
    active, retired = collect_criteria()
    covered = collect_coverage()

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
