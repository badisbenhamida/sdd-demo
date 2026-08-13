<!--
Sync Impact Report
==================
Version change: (unfilled template) → 1.0.0

This file is a MIRROR of the human-authored `memory/constitution.md`.
Article text is reproduced verbatim; only template scaffolding was applied.
Changes flow ONLY from `memory/` to `.specify/`, never the reverse.

Modified principles:
  [PRINCIPLE_1_NAME] → Article I — Specs are the contract
  [PRINCIPLE_2_NAME] → Article II — Traceability is enforced, not encouraged
  [PRINCIPLE_3_NAME] → Article III — Human gates
  [PRINCIPLE_4_NAME] → Article IV — Agent conduct

Added sections:
  Provenance rule (verbatim preamble from the source constitution)

Removed sections:
  [PRINCIPLE_5_NAME] — the source constitution has exactly four articles
  [SECTION_2_NAME] / [SECTION_3_NAME] — no corresponding content in the
    source; omitted rather than authored, since no agent may originate
    constitution content (Article IV.3)

Deferred items:
  RATIFICATION_DATE — the source document carries no explicit adoption
    date; 2026-08-12 is derived from the first commit of
    memory/constitution.md (9f20142). Correct here only by amending the
    source document first.
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

This file is a read-only mirror. The authoritative constitution is
`memory/constitution.md`; changes flow only from `memory/` into
`.specify/memory/`, never the reverse. Amending the mirror alone has no
governing effect.

Amendment procedure, per the provenance rule above: this document is
human-authored and human-amended only; no agent may generate or modify
it, and amendments require a PR approved by two engineering leads.

Versioning of this mirror follows semantic versioning: MAJOR for
removal or incompatible redefinition of an article, MINOR for a new or
materially expanded article, PATCH for clarifications that do not change
meaning. The version tracks the mirrored content, not the mirroring
mechanism.

Compliance review: the `spec-drift` required status check on `main`
enforces Article II on every PR; Article III gates (G1, G2, G3) are
verified by the human approvers named in each gate.

**Version**: 1.0.0 | **Ratified**: 2026-08-12 | **Last Amended**: 2026-08-12
