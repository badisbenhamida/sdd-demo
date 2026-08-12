<!--
Sync Impact Report
==================
Version change: (unversioned template placeholder) → 1.0.0
Source of truth: memory/constitution.md (human-authored). This file is a
  GENERATED MIRROR. Changes flow ONLY memory/ → .specify/, never the reverse.
  Amend the source, then re-run the mirror; never edit this file directly.

Principles (all four articles mirrored verbatim from the source):
  + Article I — Specs are the contract
  + Article II — Traceability is enforced, not encouraged
  + Article III — Human gates
  + Article IV — Agent conduct

Added sections:
  + Provenance rule blockquote (verbatim from source)
  + Governance (mirror-local: restates the source amendment procedure and
    records the mirror direction; adds no new governance rules)

Removed / omitted template sections:
  - [PRINCIPLE_5_NAME] — the source defines exactly four articles
  - [SECTION_2_NAME] / [SECTION_3_NAME] — no corresponding source content;
    left out rather than invented, per "do not restructure or reword"

Bracket tokens intentionally retained (source content, NOT placeholders):
  - `[RETIRED]` in Article I.2 — a literal marker defined by the constitution
  - `GRT-###` / `Implements: GRT-###` — literal criterion-ID formats

Deferred items:
  - TODO(CONSTITUTION_VERSION): version/ratification metadata does not exist in
    memory/constitution.md. 1.0.0 and the 2026-08-12 ratification date are
    derived from git (commit 9f20142, the commit that introduced the source
    file). If leads want this metadata authoritative, a human must add it to
    memory/constitution.md; until then it is mirror-local bookkeeping.
-->

# Engineering Constitution

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

This file is a generated mirror of `memory/constitution.md`, which is the
authoritative, human-authored document. Where the two differ, the source in
`memory/` governs.

**Amendment procedure.** Per the Provenance rule above, amendments are made to
`memory/constitution.md` by a human, via a PR approved by two engineering
leads. The mirror is then regenerated. No agent may author an amendment in
either location, and no change may flow from `.specify/` back to `memory/`.

**Versioning policy.** Semantic versioning of this mirror: MAJOR for backward
incompatible governance or article removals/redefinitions, MINOR for a new
article or materially expanded guidance, PATCH for clarifications and
non-semantic refinements. The version tracks the mirrored content, not the
mirroring operation.

**Compliance review.** Article II.2 makes the `spec-drift` workflow a required
status check on `main`; Article III.3 makes human review a merge gate. PR
review verifies compliance with all four articles.

**Version**: 1.0.0 | **Ratified**: 2026-08-12 | **Last Amended**: 2026-08-12
