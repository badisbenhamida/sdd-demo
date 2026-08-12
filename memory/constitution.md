# Engineering Constitution

> **Provenance rule: this document is human-authored and human-amended
> only. No agent may generate or modify it. Amendments require a PR
> approved by two engineering leads.**

## Article I — Specs are the contract

1. Every service begins with an EARS specification derived from the
   approved BRD. The spec lives in this repository under `specs/`.
2. Each acceptance criterion carries a stable ID (`GRT-###`). IDs are
   never reused. Retired criteria are marked `[RETIRED]`, not deleted.
3. GitHub Issues are derived from the spec, never the reverse.
   Requirement changes happen here, via PR.

## Article II — Traceability is enforced, not encouraged

1. Every criterion must be covered by at least one test that declares
   `Implements: GRT-###`.
2. The `spec-drift` workflow, marked as a required status check on
   `main`, fails any PR where criteria are uncovered or tests reference
   retired/unknown criteria.
3. Commits implementing a criterion reference its ID in the message.

## Article III — Human gates

1. **G1 — Spec approval.** A human (PO/BA) approves the spec, including
   resolution of every item in the Ambiguity Log, before planning.
2. **G2 — Plan approval.** A human (tech lead) approves the plan before
   implementation.
3. **G3 — Merge authority.** Every PR requires human review under
   branch protection. Agents never merge.
4. Issue sync runs in dry-run first; a human approves the batch before
   issues are created. Issue state updates derive from evidence
   (`--update`), never from hand-marking.

## Article IV — Agent conduct

1. Agents cite criterion IDs when recommending or implementing changes.
2. Agent-generated artifacts are labeled as drafts until human-approved.
3. Agents do not modify: this constitution, approved specs (except via
   PR), GitHub Issues (outside the sync tool), or workflow/branch
   protection definitions.
