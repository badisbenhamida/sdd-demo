#!/usr/bin/env python3
"""constitution_check.py — verify the .specify mirror matches memory/.

CLAUDE.md: the constitution is human-authored in `memory/constitution.md`
and mirrored into `.specify/memory/constitution.md`. Changes flow ONLY
memory/ -> .specify/, never the reverse.

Until this check existed, nothing enforced that. The asymmetry is the
problem: the source is off-limits to agents, while the mirror is written
by `/speckit.constitution` and sits in a directory agents edit freely. A
mirror that drifts — or is edited in place, which constitution Article
IV.3 forbids — looked identical to one that did not.

What is compared
----------------
For every article in the source: its heading text and its body, ignoring
heading LEVEL (the mirror demotes `## Article` to `### Article` to sit
under the template's "Core Principles") and trailing whitespace. Also
requires the provenance blockquote to survive into the mirror.

Template scaffolding around the articles — a Sync Impact Report comment,
a Governance section, a version line — is expected and ignored. This
checks that the governing text is intact, not that the files are equal.

Absent mirror is not a failure: `.specify/` is optional tooling and is
stripped from the demo-start branch by design (docs/BRANCHING.md). The
source, however, is mandatory.

Run:  python scripts/constitution_check.py
CI:   invoked by .github/workflows/spec-drift.yml before the drift gate.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "memory" / "constitution.md"
MIRROR = ROOT / ".specify" / "memory" / "constitution.md"

# Any heading level: the source uses "## Article", the mirror "### Article".
ARTICLE_RE = re.compile(r"^#{2,4}\s+(Article\s+[IVXLC]+\s*[—-]\s*.+?)\s*$", re.M)
NEXT_HEADING_RE = re.compile(r"^#{1,6}\s", re.M)


def articles(text: str) -> dict[str, str]:
    """Map article heading -> body, body ending at the next heading."""
    out: dict[str, str] = {}
    parts = ARTICLE_RE.split(text)
    for i in range(1, len(parts), 2):
        heading, rest = parts[i], parts[i + 1]
        cut = NEXT_HEADING_RE.search(rest)
        body = rest[: cut.start()] if cut else rest
        out[normalise(heading)] = normalise(body)
    return out


def normalise(text: str) -> str:
    """Strip trailing whitespace per line and collapse blank edges."""
    return "\n".join(line.rstrip() for line in text.strip().splitlines())


def blockquote(text: str) -> str:
    return normalise("\n".join(l for l in text.splitlines() if l.startswith(">")))


def main() -> int:
    if not SOURCE.exists():
        print(f"ERROR: {SOURCE.relative_to(ROOT)} is missing.")
        print("The constitution is mandatory and human-authored (CLAUDE.md).")
        return 1

    source_text = SOURCE.read_text(encoding="utf-8")
    source_articles = articles(source_text)

    if not source_articles:
        print(f"ERROR: no articles found in {SOURCE.relative_to(ROOT)}.")
        print('Expected headings of the form "## Article I — <title>".')
        return 1

    if not MIRROR.exists():
        print(f"No mirror at {MIRROR.relative_to(ROOT)} — nothing to compare.")
        print(f"Source holds {len(source_articles)} article(s). PASS.")
        return 0

    mirror_text = MIRROR.read_text(encoding="utf-8")
    mirror_articles = articles(mirror_text)

    failures: list[str] = []

    missing = [h for h in source_articles if h not in mirror_articles]
    extra = [h for h in mirror_articles if h not in source_articles]
    for heading in missing:
        failures.append(f"missing from the mirror: {heading}")
    for heading in extra:
        failures.append(f"present only in the mirror (agent-authored?): {heading}")

    for heading, body in source_articles.items():
        if heading in mirror_articles and mirror_articles[heading] != body:
            failures.append(f"body differs: {heading}")

    source_quote = blockquote(source_text)
    if source_quote and source_quote not in normalise(mirror_text):
        failures.append("the provenance blockquote did not survive into the mirror")

    print(f"Articles: {len(source_articles)} in source, {len(mirror_articles)} in mirror")

    if failures:
        print("\nDRIFT — the mirror does not match memory/constitution.md:")
        for failure in failures:
            print(f"  {failure}")
        print("\nFAIL: fix by re-mirroring FROM memory/constitution.md.")
        print("Never the reverse: the source is human-authored and human-amended")
        print("only (constitution Art. IV.3, CLAUDE.md Governance).")
        return 1

    print("\nPASS: the mirror matches memory/constitution.md.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
