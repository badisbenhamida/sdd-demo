# Business Requirements Document — Amendment A1

**Amends:** BRD-2026-014 (Global Greeting Service)
**Amendment ID:** BRD-2026-014-A1
**Title:** Per-client request rate limiting
**Requested by:** Engineering (raised 2026-08-12)
**Drafted by:** AI agent — **DRAFT, NOT APPROVED**
**Status:** **Awaiting business review (Priya, BA) and approval (Marco, PO)**
**Date drafted:** 2026-08-12

---

> **This is an agent-drafted artifact and carries no authority** (constitution
> Art. IV.2). It amends nothing until a human approves it. The approved
> BRD-2026-014 is untouched, and `specs/001-greeting-service/spec.md` is
> untouched: no `GRT-011` exists, and the drift gate remains green at 10/10.

## 1. Why this amendment exists

Engineering asked for a new acceptance criterion: *when more than 10 requests
per second arrive from one client, the service shall return HTTP 429.*

That behaviour cannot be added to the spec directly. Every acceptance criterion
must trace to a BRD requirement (constitution Art. I.1), and BRD-2026-014
carries four — greeting by language preference (BR-1), availability to regional
applications (BR-2), unsupported-language handling (BR-3), monitorability
(BR-4). None implies rate limiting, so the criterion would have an empty
`Traces to` cell and would break the spec's no-orphans traceability claim.

The spec also already ruled on this territory and named the route back. At
Gate G1 on 2026-08-12, Ambiguity Log item **AMB-008** asked the business whether
the service is held to an availability target. The Product Owner ruled:

> **no contractual target for this release**, and therefore no criteria added.
> Calling applications own their own timeout and degradation behaviour. This is
> **ruled out of scope and recorded, not dropped**: the risk that a shared
> render-path dependency has no stated target was raised, considered, and
> accepted by the business. **Revisiting it requires a BRD amendment, which
> would add criteria here.**

This document is that amendment. The G1 ruling is not being circumvented — it
is being followed.

## 2. Business context

The Greeting Service sits in the render path of every regional application's
page load. It holds no per-user state and serves from an in-memory catalog, so
the concern is not cost of computation but blast radius: a single misbehaving
or misconfigured caller can consume capacity that every other regional
application depends on. BR-2 commits the greeting to *all* regional
applications, and one caller's defect should not be able to withdraw that
commitment from the others.

Whether that risk is worth controlling at the application layer — and at what
threshold — is a business decision, not an engineering one. That is what this
amendment asks.

## 3. Proposed new business requirement

- **BR-5.** The service shall protect its availability to all regional
  applications by limiting how much of its capacity any single calling
  application can consume, rejecting excess requests in a way the caller can
  detect and retry.

Written in BRD prose deliberately, to match the register of BR-1…BR-4. The
specific numbers and mechanics belong in the spec's Ambiguity Log, where they
get a recorded human ruling rather than an assumed default — see §4.

## 4. Questions the business must answer before a criterion can be written

Engineering's request specified "more than 10 requests per second from one
client" and "HTTP 429". Both are defensible, and neither is yet decidable from
the BRD. If A1 is approved, these become Ambiguity Log items (provisionally
**AMB-009**…**AMB-013**) resolved at a re-run of Gate G1.

| # | Question | Why it cannot be assumed |
|---|---|---|
| A1-Q1 | **What identifies "one client"?** A source IP, a calling application identity, an API key, or a tenant? | The service has no notion of a caller today. Resolution is a pure function of the requested locale and reads no caller identity — that is what makes GRT-004 (identical text to every caller) true by construction. Introducing client identity touches that guarantee, and AMB-003 ruled authentication out of scope as platform-layer, so there is currently no authenticated identity to key a limit on. Source IP is the only identifier available today, and behind a shared proxy it would group unrelated regional applications together. |
| A1-Q2 | **Is 10 requests per second the right threshold?** | No traffic figures exist in the BRD. Ten per second is below what a single regional application's page load could generate during a traffic spike, so the limit could reject legitimate load from a well-behaved caller. The business should set this against expected regional volumes. |
| A1-Q3 | **Is a burst allowance permitted?** A hard 10/second, or an average with a short burst tolerance? | Page loads arrive in bursts. A hard per-second ceiling rejects normal bursty traffic that an averaged limit would accept. |
| A1-Q4 | **Does rejection contradict the AMB-001 posture?** | G1 ruled that no calling application should need error handling to display a greeting — that is why an unsupported language returns 200 with a fallback rather than an error. A 429 would introduce the **first error path** that every caller must handle. This is not necessarily wrong, but it reverses a deliberate ruling and the business should make that trade knowingly. |
| A1-Q5 | **Should the limit be enforced here at all, or at the platform layer?** | AMB-003 ruled authentication and network exposure to be platform concerns. Rate limiting is conventionally handled at the same layer — a gateway or ingress — where it can protect the service before traffic reaches it. Enforcing in-process still consumes the capacity being protected. If the business rules "platform layer", A1 closes with **no criterion added**, which is a valid outcome and stays on the record. |

**A1-Q5 is the load-bearing question.** If it resolves to "platform layer",
questions Q1–Q4 fall away and this amendment ends without touching the spec.

## 5. Impact if A1 is approved

| Artifact | Effect |
|---|---|
| `docs/brd/BRD-2026-014-greeting-service.md` | Gains BR-5; A1 folded in or referenced. Human edit — no agent may make it. |
| `specs/.../spec.md` | New criterion **GRT-011** (next free ID; GRT-010 is the highest and IDs are never reused). New Ambiguity Log items AMB-009…AMB-013. **G1 must be re-run** — the spec was approved as a ten-criterion document. |
| `specs/.../plan.md`, `research.md`, `data-model.md` | Rate limiting needs per-client request state over time. Today the service holds no state beyond the startup catalog and has no clock, so this is a genuine architecture change, not a parameter. **G2 must be re-run.** |
| `specs/.../contracts/greeting-api.yaml` | Gains a `429` response on `/greeting` — an integration-contract change affecting every calling application. |
| `specs/.../tasks.md` | New story S5 implementing GRT-011, with its own tests. |
| Drift gate | Goes **red the moment GRT-011 is added** and stays red until a test declares `Implements: GRT-011`. Since spec-drift is the required check on `main`, the branch is unmergeable in between. Sequence the spec change and the implementation in the same PR. |

## 6. Recommended sequence

1. **Priya (BA)** reviews this draft, decides whether BR-5 states the business
   need correctly, and folds it into BRD-2026-014 — or rejects A1.
2. **Marco (PO)** rules on A1-Q1…A1-Q5, starting with Q5. A ruling of
   "platform layer" ends the process here, recorded.
3. If a criterion is warranted: add **GRT-011** to the spec with the rulings as
   resolved Ambiguity Log items, and **re-run Gate G1**.
4. **Dana (Tech Lead)** updates plan, contract, and tasks; **re-run Gate G2**.
5. Implement test-first, gate per criterion, and open the PR for **G3**.

Steps 3–5 are agent-assistable on direction. Steps 1 and 2 are not.

## 7. Current state — nothing has changed

- BRD-2026-014: **unmodified**
- `specs/001-greeting-service/spec.md`: **unmodified**, still 10 approved criteria
- Drift gate: **10/10, PASS** — verified after drafting this document
- `GRT-011`: **does not exist** and is reserved, not assigned
