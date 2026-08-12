# Feature Specification: Global Greeting Service

**Feature Directory**: `specs/001-greeting-service`

**Feature Branch**: `demo-live`

**Created**: 2026-08-12

**Status**: Draft — PENDING G1 (spec approval by PO/BA)

**Source**: [BRD-2026-014](../../docs/brd/BRD-2026-014-greeting-service.md) — Global Greeting Service (approved by business 2026-07-28)

**Input**: Transform BRD-2026-014 into an EARS specification with stable `GRT-###` criterion IDs, BRD traceability, and an Ambiguity Log.

> **This spec is a DRAFT and is not the contract until a human approves it.**
> Per constitution Article III.1 (G1), a human (PO/BA) must approve this spec
> **including resolution of every item in the Ambiguity Log** before planning
> begins. Criteria marked *Pending* below are blocked on those resolutions.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Regional app greets a user in their language (Priority: P1)

A customer-facing regional application needs to greet a user. Instead of holding its
own greeting text, it asks the Greeting Service for a greeting matching the user's
language preference and displays what it receives.

**Why this priority**: This is the reason the service exists (BR-1). Delivered alone it
already removes duplicated greeting text from one application, so it is a viable MVP.

**Independent Test**: Request a greeting for a supported language and confirm the
returned greeting is in that language, and that two different calling applications
requesting the same language receive the same text.

**Acceptance Scenarios**:

1. **Given** the service supports a language, **When** a calling application requests a
   greeting for that language, **Then** a greeting in that language is returned.
2. **Given** two different regional applications, **When** both request a greeting for
   the same language, **Then** both receive identical greeting text.

---

### User Story 2 - Unsupported language does not break the caller (Priority: P2)

A regional application requests a greeting for a language the service does not carry.
The caller still receives a usable, predictable response rather than a failure.

**Why this priority**: BR-3 makes this explicit, but it only has value once US1 exists.

**Independent Test**: Request a greeting for a language known to be unsupported and
confirm the response matches the behaviour agreed in AMB-002.

**Acceptance Scenarios**:

1. **Given** the service does not support the requested language, **When** a greeting is
   requested for it, **Then** the service responds with the agreed unsupported-language
   behaviour and does not return an empty or undefined greeting.

---

### User Story 3 - Operations confirms the service is healthy (Priority: P3)

An operator (or an automated monitor) checks whether the Greeting Service is running and
able to serve greetings, without needing to request a greeting on a real user's behalf.

**Why this priority**: BR-4 and §4 require it for operability, but it delivers no
end-user value on its own.

**Independent Test**: Query the health indicator and confirm it reports service state.

**Acceptance Scenarios**:

1. **Given** the service is running and able to serve greetings, **When** operations
   queries the health indicator, **Then** it reports a healthy state.

---

### Edge Cases

Each edge case below is either covered by a criterion or logged as an ambiguity — none
are resolved by assumption in this draft.

- A language the service does not support → GRT-004, behaviour pending **AMB-002**.
- No language preference supplied at all (distinct from an unsupported one) → **AMB-009**.
- A malformed or unrecognisable language value → **AMB-002** (whether this is treated
  the same as "unsupported" is part of that question).
- The service is running but cannot serve greetings (e.g. greeting text unavailable) →
  the health indicator must distinguish this; scope of "healthy" pending **AMB-005**.

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
| GRT-004 | If a greeting is requested for a language the service does not support, then the Greeting Service shall respond with the agreed unsupported-language behaviour and shall not return an empty or undefined greeting. | UB | BR-3 | **Pending AMB-002, AMB-007** |
| GRT-005 | The Greeting Service shall expose a health indicator that operations can query to determine whether the service is able to serve greetings. | U | BR-4; §4 Success Criteria ("verify service health") | Confirmed |

> **Format note**: criterion IDs in the table above are deliberately unformatted (no bold,
> no backticks). `scripts/spec_drift.py` collects criteria with `\|\s*(GRT-\d{3})\s*\|`,
> so any decoration around the ID makes the criterion invisible to the required status
> check. Keep the ID cell bare.

**Reserved, not yet specified.** The IDs below are reserved so that resolving an ambiguity
does not renumber anything above. They carry no requirement until a human approves the
corresponding resolution, and they are written in prose rather than a table cell so the
drift check does not treat them as active, uncovered criteria.

- `GRT-006` — how the user's language preference is conveyed to the service (blocked on AMB-001)
- `GRT-007` — the set of languages supported at launch (blocked on AMB-003)
- `GRT-008` — behaviour when no language preference is supplied (blocked on AMB-009)
- `GRT-009` — observability signals beyond the health indicator (blocked on AMB-005)

### Key Entities

- **Greeting**: the text returned to a calling application. Attributes: the language it
  is written in, and the text itself. The BRD does not describe any other attribute —
  personalization (names, time-of-day variants) is explicitly out of scope (§3).
- **Language preference**: the caller's indication of which language the greeting should
  be in. How this is expressed and carried is unresolved (**AMB-001**).
- **Calling application**: a regional customer-facing application that consumes the
  service (BR-2).

---

## Success Criteria *(mandatory)*

- **SC-001**: A regional application can retrieve a greeting for a supported language
  through the standard interface without implementing any greeting text of its own.
  *(§4, BR-2)*
- **SC-002**: Greeting text for a given language is identical across every regional
  application that requests it. *(§1, BR-1)*
- **SC-003**: Operations can determine whether the service is healthy without requesting
  a greeting on behalf of a real user. *(§4, BR-4)*
- **SC-004**: A request for an unsupported language leaves the calling application with a
  displayable outcome rather than a failure. *(BR-3; exact measure pending AMB-002)*

> The BRD states no quantitative targets (latency, availability, throughput, volume).
> None have been invented here — see **AMB-006**.

---

## Ambiguity Log

Every gap found in BRD-2026-014. Each item is a question for the business with a
**proposed** resolution. Per constitution Article III.1, **every item must be resolved by
a human before planning (G2) begins**. Nothing here is settled.

**Status legend**: 🔶 **PENDING HUMAN APPROVAL** — proposed resolution not yet accepted.

| ID | BRD ref | Question for the business | Proposed resolution | Status |
|----|---------|---------------------------|---------------------|--------|
| **AMB-001** | BR-1 | How is the user's language preference conveyed to the service? The BRD says the greeting must be "appropriate to the user's language preference" but never says whether the caller supplies it, or the service looks it up. | The calling application supplies the language preference explicitly with each request; the service performs no user lookup and holds no user state. | 🔶 PENDING HUMAN APPROVAL |
| **AMB-002** | BR-3 | What exactly should happen when a language is not supported? "Handle situations" admits at least two incompatible readings: fall back to a default language, or return an explicit error for the caller to handle. | Fall back to a default language and return a greeting, while signalling that a fallback occurred so callers can distinguish it from an exact match. | 🔶 PENDING HUMAN APPROVAL |
| **AMB-003** | BR-1, BR-2 | Which languages must be supported at launch? The BRD names none, and "all regional applications" does not identify the regions. | Business to supply the launch language list. Until then the spec commits to no specific language set. | 🔶 PENDING HUMAN APPROVAL |
| **AMB-004** | BR-2 | Does "available to all regional applications" imply any access control, or is the service open to any internal caller? | Open to internal callers with no per-application authorisation in this release; access control is not a stated business requirement. | 🔶 PENDING HUMAN APPROVAL |
| **AMB-005** | BR-4 | What does "monitorable by operations" require beyond a health check — metrics, structured logs, alerting thresholds? §4 mentions only health verification. | A health indicator satisfies BR-4 for this release (GRT-005); metrics and alerting are deferred until operations states a need. | 🔶 PENDING HUMAN APPROVAL |
| **AMB-006** | §4 | Are there performance, availability, or volume targets? The BRD's success criteria are entirely qualitative. | No numeric targets in this release; the service is expected to meet the platform's existing default expectations. | 🔶 PENDING HUMAN APPROVAL |
| **AMB-007** | BR-3 | BR-3 says the system "should" handle unsupported languages, while BR-1/BR-2/BR-4 say "shall"/"must". Is unsupported-language handling mandatory or optional? | Treat as mandatory — a caller receiving an undefined greeting is a user-visible defect. GRT-004 is written as mandatory on this basis. | 🔶 PENDING HUMAN APPROVAL |
| **AMB-008** | §3, BR-1 | Where does the greeting text come from and who owns it? §3 puts translation workflow and content management out of scope, but the service cannot return greetings without text. | Greeting text is supplied to the service as fixed content at build time; no runtime content management, consistent with §3. | 🔶 PENDING HUMAN APPROVAL |
| **AMB-009** | BR-1 | What happens when a caller supplies **no** language preference at all? This is distinct from supplying an unsupported one, and the BRD addresses neither. | Treat a missing preference the same as an unsupported language and apply the AMB-002 outcome. | 🔶 PENDING HUMAN APPROVAL |

---

## Assumptions

Only assumptions forced by the BRD's own scope statements are recorded here. Every other
gap is in the Ambiguity Log rather than assumed away.

- Personalization (user names, time-of-day variants) is out of scope — stated in §3.
- Translation workflow and content management are out of scope — stated in §3.
- Callers are internal regional applications, not end users directly — implied by BR-2
  ("regional applications") and §1 ("customer-facing applications").
- The BRD is approved and stable (§ header, "Approved by business — handed off to
  engineering", 2026-07-28); requirement changes arrive as BRD amendments, and per
  constitution Article I.3 flow into this spec via PR.

---

## Out of Scope

Carried directly from BRD §3 — not expanded:

- Personalization (user names, time-of-day variants)
- Translation workflow / content management

---

## Traceability Summary

Every BRD requirement maps to at least one criterion; no criterion exists without a BRD
source (constitution Article I.1).

| BRD requirement | Covered by | Gaps raised |
|-----------------|------------|-------------|
| BR-1 — greeting appropriate to language preference | GRT-001, GRT-002 | AMB-001, AMB-003, AMB-009 |
| BR-2 — available to all regional applications | GRT-003 | AMB-003, AMB-004 |
| BR-3 — handle unsupported language | GRT-004 | AMB-002, AMB-007 |
| BR-4 — monitorable by operations | GRT-005 | AMB-005 |
| §4 — standard interface, health verification | GRT-003, GRT-005 | AMB-006 |
| §1 — consistent tone, no duplicated translation | GRT-002 | AMB-008 |
