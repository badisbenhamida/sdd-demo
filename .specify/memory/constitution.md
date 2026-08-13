<!--
Sync Impact Report
==================
Version change: (none — unfilled template) → 1.0.0
Rationale: MAJOR/initial. First concrete ratification of this file; the
prior contents were the unpopulated Spec Kit scaffold with zero defined
principles. This is a verbatim mirror of the human-authored source at
memory/constitution.md.

Modified principles:
  [PRINCIPLE_1_NAME] → Article I — Specs are the contract
  [PRINCIPLE_2_NAME] → Article II — Traceability is enforced, not encouraged
  [PRINCIPLE_3_NAME] → Article III — Human gates
  [PRINCIPLE_4_NAME] → Article IV — Agent conduct

Added sections:
  Provenance rule (blockquote, verbatim from source)
  Governance (mirroring direction + amendment procedure)

Removed sections:
  [PRINCIPLE_5_NAME] / [PRINCIPLE_5_DESCRIPTION] — the source constitution
    defines exactly four articles; a fifth was not invented.
  [SECTION_2_NAME] / [SECTION_3_NAME] — omitted for the same reason. Adding
    them would require authoring governance content absent from the source,
    which Article IV.3 forbids.

Deferred TODOs:
  TODO(RATIFICATION_DATE): The original human adoption date is not
    recoverable from this repository. memory/constitution.md first appears
    in the rebuilt demo history (2026-08-12), which is a reset commit, not
    the adoption event. A human must supply the real date.
-->

# SDD Demo Constitution

> **Provenance rule: this document is human-authored and human-amended
> only. No agent may generate or modify it. Amendments require a PR
> approved by two engineering leads.**

## Core Principles

### Article I — Specs are the contract

1. Every service begins with an EARS specification derived from the
   approved BRD. The spec lives in this repository under `specs/`.
2. Each acceptance criterion carries a stable ID (`GRT-###`). IDs are
   never reused. Retired criteria are marked `[RETIRED]`, not deleted.
3. GitHub Issues are derived from the spec, never the reverse.
   Requirement changes happen here, via PR.

### Article II — Traceability is enforced, not encouraged

1. Every criterion must be covered by at least one test that declares
   `Implements: GRT-###`.
2. The `spec-drift` workflow, marked as a required status check on
   `main`, fails any PR where criteria are uncovered or tests reference
   retired/unknown criteria.
3. Commits implementing a criterion reference its ID in the message.

### Article III — Human gates

1. **G1 — Spec approval.** A human (PO/BA) approves the spec, including
   resolution of every item in the Ambiguity Log, before planning.
2. **G2 — Plan approval.** A human (tech lead) approves the plan before
   implementation.
3. **G3 — Merge authority.** Every PR requires human review under
   branch protection. Agents never merge.
4. Issue sync runs in dry-run first; a human approves the batch before
   issues are created. Issue state updates derive from evidence
   (`--update`), never from hand-marking.

### Article IV — Agent conduct

1. Agents cite criterion IDs when recommending or implementing changes.
2. Agent-generated artifacts are labeled as drafts until human-approved.
3. Agents do not modify: this constitution, approved specs (except via
   PR), GitHub Issues (outside the sync tool), or workflow/branch
   protection definitions.

## Governance

This file is a **mirror**, not a source. The authoritative, human-authored
constitution lives at `memory/constitution.md`. Changes flow in one
direction only — from `memory/` into `.specify/memory/` — never the
reverse. An agent that finds this mirror out of date re-mirrors it; an
agent that wants the text changed asks a human to amend the source.

Amendment procedure is set by the source document itself: a PR approved by
two engineering leads. No agent may author or approve that PR.

Versioning policy for this mirror follows semantic versioning against the
articles it carries. MAJOR: an article is removed or redefined in a
backward-incompatible way. MINOR: an article or clause is added, or its
guidance materially expanded. PATCH: wording, typo, and formatting
clarifications that do not change what the articles require.

Compliance review: the four articles are enforced in CI, not by
attestation. The `spec-drift` required status check on `main` enforces
Article II; branch protection enforces Article III.3. Every PR review
verifies compliance with the remainder.

**Version**: 1.0.0 | **Ratified**: TODO(RATIFICATION_DATE): original human adoption date unknown; see Sync Impact Report | **Last Amended**: 2026-08-12
