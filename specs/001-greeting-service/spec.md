# Feature Specification: Global Greeting Service

**Feature Directory**: `specs/001-greeting-service`

**Feature Branch**: `demo-live`

**Created**: 2026-08-12

**Ambiguities resolved**: 2026-08-12 (all 9 items — see Ambiguity Log)

**Status**: ✅ **APPROVED — G1 met**

**Approved by**: Badis Ben Hamida <badis@ben-hamida.com> on 2026-08-12

**Source**: [BRD-2026-014](../../docs/brd/BRD-2026-014-greeting-service.md) — Global Greeting Service (approved by business 2026-07-28)

**Input**: Transform BRD-2026-014 into an EARS specification with stable `GRT-###` criterion IDs, BRD traceability, and an Ambiguity Log.

> **G1 met** (constitution Article III.1): every Ambiguity Log item carries a human
> decision, and the spec itself was approved on 2026-08-12. This document is no longer a
> draft — it is **the contract**. Per CLAUDE.md it must not be modified without explicit
> direction, and requirement changes arrive as BRD amendments via PR (Article I.3).
>
> **Recorded at sign-off**: two decisions were supplied by the approver rather than
> derived from BRD-2026-014, and were approved with that understanding — the AMB-003
> launch language set (the BRD names no languages), and the AMB-002 reversal from fallback
> to an explicit error (which obliges every regional application to handle
> `UNSUPPORTED_LANGUAGE`).
>
> Planning may now proceed. Note that G2 (plan approval, Article III.2) is a separate gate.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Regional app greets a user in their language (Priority: P1)

A customer-facing regional application needs to greet a user. Instead of holding its
own greeting text, it asks the Greeting Service for a greeting in the language it
supplies, and displays what it receives.

**Why this priority**: This is the reason the service exists (BR-1). Delivered alone it
already removes duplicated greeting text from one application, so it is a viable MVP.

**Independent Test**: Request a greeting for each supported language and confirm the
returned greeting is in that language, and that two different calling applications
requesting the same language receive identical text.

**Acceptance Scenarios**:

1. **Given** the service supports a language, **When** a calling application requests a
   greeting for that language, **Then** a greeting in that language is returned.
2. **Given** two different regional applications, **When** both request a greeting for
   the same language, **Then** both receive identical greeting text.

---

### User Story 2 - A caller learns it asked for something unavailable (Priority: P2)

A regional application requests a greeting for a language the service does not carry, or
omits the language entirely. It receives a specific error telling it which of those two
things went wrong, and decides for itself what to display.

**Why this priority**: BR-3 makes unsupported-language handling explicit, but it only has
value once US1 exists. The business chose errors over fallback so that no user is ever
silently shown the wrong language.

**Independent Test**: Request a greeting for a language known to be unsupported, and
separately with no language at all, and confirm each returns its own distinct error.

**Acceptance Scenarios**:

1. **Given** the service does not support the requested language, **When** a greeting is
   requested for it, **Then** an `UNSUPPORTED_LANGUAGE` error is returned and no greeting.
2. **Given** a request carrying no language preference, **When** it reaches the service,
   **Then** a `MISSING_LANGUAGE` error is returned and no greeting.

---

### User Story 3 - Operations confirms the service is healthy (Priority: P3)

An operator (or an automated monitor) checks whether the Greeting Service is running and
able to serve greetings, without requesting a greeting on behalf of a real user.

**Why this priority**: BR-4 and §4 require it for operability, but it delivers no
end-user value on its own.

**Independent Test**: Query the health indicator and confirm it reports service state.

**Acceptance Scenarios**:

1. **Given** the service is running and able to serve greetings, **When** operations
   queries the health indicator, **Then** it reports a healthy state.

---

### Edge Cases

- A language the service does not support → GRT-004 (`UNSUPPORTED_LANGUAGE`, no greeting).
- No language preference supplied at all → GRT-008 (`MISSING_LANGUAGE`, distinct from the
  above so a misconfigured caller is distinguishable from genuine unsupported demand).
- A malformed or unrecognisable language value → treated as unsupported (GRT-004); it is
  a value the service does not support.
- The service is running but cannot serve greetings → the health indicator must not
  report healthy (GRT-005).

---

## Requirements *(mandatory)*

### Acceptance Criteria

Criterion IDs (`GRT-###`) are **stable and never reused** (constitution Article I.2).
Retired criteria are marked `[RETIRED]`, not deleted. Task numbers may reshuffle on
regeneration; these IDs do not.

All criteria are written in EARS notation. Pattern legend: **U** ubiquitous
("The system shall…"), **EV** event-driven ("When…, the system shall…"),
**UB** unwanted behaviour ("If…, then the system shall…").

| ID | EARS | Pattern | Traceability (BRD) | Status |
|----|------|---------|--------------------|--------|
| GRT-001 | When a calling application requests a greeting for a language the service supports, the Greeting Service shall return a greeting in that language. | EV | BR-1 | Confirmed |
| GRT-002 | The Greeting Service shall return identical greeting text to every calling application that requests the same language. | U | BR-1; §1 Business Context (inconsistent tone, duplicated translation) | Confirmed |
| GRT-003 | The Greeting Service shall expose greeting retrieval through a single interface usable by all regional applications. | U | BR-2; §4 Success Criteria ("standard interface") | Confirmed |
| GRT-004 | If a greeting is requested for a language the service does not support, then the Greeting Service shall return an UNSUPPORTED_LANGUAGE error and shall not return a greeting. | UB | BR-3 (via AMB-002, AMB-007) | Confirmed |
| GRT-005 | The Greeting Service shall expose a health indicator that operations can query to determine whether the service is able to serve greetings. | U | BR-4; §4 Success Criteria ("verify service health") | Confirmed |
| GRT-006 | When a calling application requests a greeting, the Greeting Service shall take the language preference from the request itself and shall not look it up from any user record. | EV | BR-1 (via AMB-001) | Confirmed |
| GRT-007 | The Greeting Service shall support the languages English, French, German, Spanish, and Japanese. | U | BR-1, BR-2 (via AMB-003) | Confirmed |
| GRT-008 | If a greeting is requested without any language preference, then the Greeting Service shall return a MISSING_LANGUAGE error, distinct from UNSUPPORTED_LANGUAGE, and shall not return a greeting. | UB | BR-1 (via AMB-009) | Confirmed |

> **Format note**: criterion IDs in the table above are deliberately unformatted (no bold,
> no backticks). `scripts/spec_drift.py` collects criteria with `\|\s*(GRT-\d{3})\s*\|`,
> so any decoration around the ID makes the criterion invisible to the required status
> check. Keep the ID cell bare.

**Reserved, not yet specified.** Written in prose rather than a table cell so the drift
check does not treat it as an active, uncovered criterion:

- `GRT-009` — observability signals beyond the health indicator. **Not required in this
  release** (AMB-005 resolved: the health indicator alone satisfies BR-4). The ID stays
  reserved so that adding metrics later never renumbers anything above.

### Key Entities

- **Greeting**: the text returned to a calling application. Attributes: the language it
  is written in, and the text itself. Personalization (names, time-of-day variants) is
  explicitly out of scope (§3).
- **Language preference**: the language the caller asks for, supplied explicitly on each
  request (AMB-001). The service holds no user state.
- **Calling application**: a regional customer-facing application that consumes the
  service (BR-2). Not individually identified or authorised (AMB-004).

---

## Success Criteria *(mandatory)*

- **SC-001**: A regional application can retrieve a greeting for a supported language
  through the standard interface without implementing any greeting text of its own.
  *(§4, BR-2)*
- **SC-002**: Greeting text for a given language is identical across every regional
  application that requests it. *(§1, BR-1)*
- **SC-003**: Operations can determine whether the service is healthy without requesting
  a greeting on behalf of a real user. *(§4, BR-4)*
- **SC-004**: A request for an unsupported language, or one with no language at all,
  returns a specific error the calling application can detect and act on — no user is
  ever shown a greeting in a language they did not ask for. *(BR-3, via AMB-002)*

> The BRD states no quantitative targets (latency, availability, throughput, volume), and
> none have been invented — AMB-006 resolved as "no numeric targets in this release".

---

## Ambiguity Log

Every gap found in BRD-2026-014, each now carrying a human decision (2026-08-12).
Per constitution Article III.1 these had to be resolved before planning.

**Status legend**: ✅ **RESOLVED** — decision made by the approver.
Where the decision differs from what I proposed, the row says so explicitly.

| ID | BRD ref | Question for the business | Agreed resolution | Status |
|----|---------|---------------------------|-------------------|--------|
| **AMB-001** | BR-1 | How is the user's language preference conveyed to the service? | The calling application supplies the language preference explicitly with each request; the service performs no user lookup and holds no user state. → **GRT-006** | ✅ RESOLVED (as proposed) |
| **AMB-002** | BR-3 | What should happen when a language is not supported — fall back, or error? | **Return an explicit `UNSUPPORTED_LANGUAGE` error.** No fallback: the caller decides what to display, so no user is silently served the wrong language. → **GRT-004** | ✅ RESOLVED — **reverses my proposed fallback**. Every calling app must handle this error. |
| **AMB-003** | BR-1, BR-2 | Which languages must be supported at launch? | English, French, German, Spanish, Japanese. → **GRT-007** | ✅ RESOLVED — ⚠️ **supplied by the approver, not derived from the BRD**, which names no languages. Confirm with the sponsor at G1. |
| **AMB-004** | BR-2 | Does "available to all regional applications" imply access control? | Open to internal callers with no per-application authorisation in this release; access control is not a stated business requirement. *(No criterion — a scope exclusion, not a behaviour.)* | ✅ RESOLVED (as proposed) |
| **AMB-005** | BR-4 | What does "monitorable by operations" require beyond a health check? | The health indicator satisfies BR-4 for this release (GRT-005); metrics and alerting deferred. `GRT-009` stays reserved and unused. | ✅ RESOLVED (as proposed) |
| **AMB-006** | §4 | Are there performance, availability, or volume targets? | No numeric targets in this release; the service meets the platform's existing default expectations. *(No criterion.)* | ✅ RESOLVED (as proposed) |
| **AMB-007** | BR-3 | Is BR-3's "should" mandatory or optional? | Mandatory. BR-3's "should" is BRD prose, not an RFC-2119 optional. GRT-004 is binding and requires a covering test. | ✅ RESOLVED (as proposed) |
| **AMB-008** | §3, BR-1 | Where does the greeting text come from, given §3 excludes content management? | Greeting text is supplied to the service as fixed content at build time; no runtime content management, consistent with §3. Changing text requires a release. *(No criterion — a constraint; see Assumptions.)* | ✅ RESOLVED (as proposed) |
| **AMB-009** | BR-1 | What happens when a caller supplies **no** language preference at all? | A **distinct** `MISSING_LANGUAGE` error, separate from `UNSUPPORTED_LANGUAGE`, so an integration bug is distinguishable from genuine unsupported-locale demand. → **GRT-008** | ✅ RESOLVED — **differs from my proposal**, which folded this into the unsupported case. |

---

## Assumptions

- Personalization (user names, time-of-day variants) is out of scope — stated in §3.
- Translation workflow and content management are out of scope — stated in §3, reaffirmed
  by AMB-008: greeting text is fixed at build time and changing it requires a release.
  The business cannot correct greeting text without an engineering release.
- Callers are internal regional applications, not end users directly — implied by BR-2
  and §1.
- No access control (AMB-004): any internal caller may retrieve a greeting.
- The BRD is approved and stable (2026-07-28); requirement changes arrive as BRD
  amendments and flow into this spec via PR (constitution Article I.3).

---

## Out of Scope

Carried directly from BRD §3 — not expanded:

- Personalization (user names, time-of-day variants)
- Translation workflow / content management

Added by resolution, not by the BRD:

- Per-application access control (AMB-004)
- Metrics, structured logging, and alerting beyond the health indicator (AMB-005)
- Quantitative performance or availability targets (AMB-006)

---

## Traceability Summary

Every BRD requirement maps to at least one criterion; no criterion exists without a BRD
source (constitution Article I.1).

| BRD requirement | Covered by | Resolved gaps |
|-----------------|------------|---------------|
| BR-1 — greeting appropriate to language preference | GRT-001, GRT-002, GRT-006, GRT-007, GRT-008 | AMB-001, AMB-003, AMB-009 |
| BR-2 — available to all regional applications | GRT-003, GRT-007 | AMB-003, AMB-004 |
| BR-3 — handle unsupported language | GRT-004 | AMB-002, AMB-007 |
| BR-4 — monitorable by operations | GRT-005 | AMB-005 |
| §4 — standard interface, health verification | GRT-003, GRT-005 | AMB-006 |
| §1 — consistent tone, no duplicated translation | GRT-002 | AMB-008 |
