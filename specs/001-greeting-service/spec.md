# Feature Specification: Global Greeting Service

**Feature Branch**: `demo-live`

**Created**: 2026-08-12

**Status**: **Approved — Gate G1** (PO: Marco, 2026-08-12)

**Input**: BRD-2026-014 — Global Greeting Service (approved by business 2026-07-28)

**Source of truth**: `docs/brd/BRD-2026-014-greeting-service.md`. Every
acceptance criterion below traces to a BRD requirement. Nothing in this
spec adds a requirement the BRD does not state or directly imply; where
the BRD was silent, the gap was recorded in the Ambiguity Log and ruled
on by a named human at G1.

## Gate G1 — Approval record

| Gate | Owner | Decision | Date |
|---|---|---|---|
| G1 — Spec approval (constitution Art. III.1) | Product Owner: Marco | Approved. All seven Ambiguity Log items ruled on; no item left open. | 2026-08-12 |

Every criterion below is now **Firm**: the BRD determines the behaviour,
or a G1 ruling has supplied the parameter the BRD left open. Criterion
IDs are stable and are not reissued if a criterion is later withdrawn.

Downstream work (planning, G2) is unblocked by this approval.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Greeting in the user's language (Priority: P1)

A regional customer-facing application needs to greet its user. Instead
of holding its own greeting text, it asks the Greeting Service for a
greeting appropriate to that user's language preference and displays
what comes back.

**Why this priority**: This is the whole business purpose of BR-1 and
the reason the initiative exists — one greeting, one tone, one
translation cost across every regional app. Without it there is no
feature.

**Independent Test**: A caller requests a greeting for a supported
language and receives that language's greeting text; a second caller in
a different region requesting the same language receives identical text.

**Acceptance Scenarios**:

1. **Given** the Greeting Service supports a language, **When** a
   calling application requests a greeting for that language, **Then**
   the greeting text for that language is returned.
2. **Given** two calling applications in different regions, **When**
   both request a greeting for the same language, **Then** both receive
   the same greeting text.
3. **Given** a calling application expresses no language preference,
   **When** it requests a greeting, **Then** the greeting is returned in
   the default language, English.

---

### User Story 2 - Unsupported language requested (Priority: P2)

A regional application requests a greeting in a language the service
does not carry. Per the G1 ruling on AMB-003, the end user still sees a
greeting — in the default language — and the caller is told that a
fallback occurred, so the gap is detectable and reportable rather than
silent.

**Why this priority**: BR-3 states this explicitly, and an unhandled
unsupported language would surface to end users as broken UI. It is
second only to the core retrieval path.

**Independent Test**: A caller requests a greeting for a language the
service does not support, receives the default-language greeting plus an
explicit fallback indication, and gets the identical response on every
repetition.

**Acceptance Scenarios**:

1. **Given** a language the Greeting Service does not support, **When** a
   calling application requests a greeting for it, **Then** the
   default-language greeting is returned and the response indicates that
   a fallback occurred.
2. **Given** the same unsupported language requested repeatedly, **When**
   each request is made, **Then** the response is the same every time.

---

### User Story 3 - Operations verifies service health (Priority: P3)

Operations needs to confirm the Greeting Service is up, both routinely
and during an incident, without inspecting application behaviour or
asking the owning team.

**Why this priority**: BR-4 and the BRD's second success criterion
require it, but it delivers no end-user greeting on its own, so it
follows the two functional journeys.

**Independent Test**: Operations queries the service's health indication
and can distinguish an available service from an unavailable one.

**Acceptance Scenarios**:

1. **Given** the Greeting Service is running normally, **When**
   operations queries its health indication, **Then** the service
   reports itself available.

---

### Edge Cases

- A calling application supplies a language identifier that is not
  merely unsupported but unrecognised or malformed — covered by GRT-005,
  which treats "cannot be served in the requested language" as one
  deterministic outcome.
- A calling application supplies no language preference at all — covered
  by GRT-002, with English as the default per the AMB-002 ruling.
- Two regional applications integrate at different times and one caches
  greeting text — consistency is asserted at the service boundary by
  GRT-004; caller-side caching is outside this service's control and is
  not specified here.

## Requirements *(mandatory)*

### Acceptance Criteria (EARS)

Criterion IDs are stable and never reused. Task numbers may reshuffle on
regeneration; these IDs do not. Every criterion below must be covered by
a test declaring `Implements: GRT-###` before it can ship.

| ID | Acceptance criterion (EARS) | Traces to | Status |
|---|---|---|---|
| GRT-001 | When a calling application requests a greeting and supplies a supported language preference, the Greeting Service shall return the greeting text for that language. | BR-1 | Firm |
| GRT-002 | When a calling application requests a greeting without supplying a language preference, the Greeting Service shall return the greeting text in the configured default language, which is English. | BR-1; AMB-002 ruling | Firm |
| GRT-003 | The Greeting Service shall expose greeting retrieval through a single interface that every regional calling application can use. | BR-2; §4 success criterion 1 | Firm |
| GRT-004 | The Greeting Service shall return the same greeting text for a given language to every calling application, regardless of the region it serves. | BR-2; §1 business context | Firm |
| GRT-005 | If a calling application requests a greeting in a language the Greeting Service does not support, then the Greeting Service shall return the greeting in the default language and indicate in its response that a fallback occurred. | BR-3; AMB-003 ruling | Firm |
| GRT-006 | The Greeting Service shall expose a health indication that operations can query to determine whether the service is available. | BR-4; §4 success criterion 2; AMB-004 ruling | Firm |

**Status column**: *Firm* — the behaviour is fully determined, either by
the BRD directly or by a recorded G1 ruling. No criterion carries an
unresolved parameter. Should a future ruling withdraw a criterion, its
ID is retired rather than reissued.

### Out of Scope

Carried verbatim in intent from BRD §3:

- Personalization (user names, time-of-day variants)
- Translation workflow / content management

Confirmed by G1 rulings, the following are also out of scope for this
release and are recorded here so the boundary is citable later:

- The concrete list of supported languages, which is business-owned
  configuration input rather than spec content (AMB-001).
- Usage metrics, per-language demand reporting, and structured logging,
  which require a separate BRD (AMB-004).
- Per-caller authentication and network policy, which sit at the
  platform layer (AMB-006).
- A formal availability or response-time objective (AMB-007).

### Key Entities

- **Greeting**: the text returned to a calling application, identified by
  the language it is written in. The BRD defines no other attribute.
- **Language preference**: the caller-supplied indication of which
  language a greeting is wanted in, passed explicitly by the caller per
  the AMB-005 ruling. Its permitted values come from business-owned
  configuration (AMB-001), not from this spec.
- **Calling application**: a regional customer-facing application that
  consumes greetings. The BRD names no other consumer type.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A regional application can retrieve a greeting for a
  supported language through the common interface without implementing
  any greeting text of its own. *(BRD §4, criterion 1)*
- **SC-002**: Operations can determine whether the service is available
  by querying it directly, with no assistance from the owning team.
  *(BRD §4, criterion 2)*
- **SC-003**: For a given language, every regional application receives
  byte-identical greeting text — measured as zero text variants per
  language across all consumers. *(BRD §1: eliminates inconsistent tone
  and duplicated translation cost)*
- **SC-004**: Every request for a greeting, supported language or not,
  yields a documented outcome — measured as zero undocumented or
  unhandled responses across the acceptance test set. *(BR-3)*

## Ambiguity Log

Every gap the BRD left open, posed as a question to the business and
ruled on at G1. Per constitution Article III.1, G1 approval required
resolution of every item in this log; all seven are Resolved. Rulings
are recorded permanently and are citable by downstream work.

| ID | Question for the business | Gap in BRD | Affects | Ruling | Resolver | Status |
|---|---|---|---|---|---|---|
| AMB-001 | Which languages must be supported at launch, and who owns that list thereafter? | BR-1 says "the user's language preference" but names no language set; §3 puts translation content management out of scope, so the list must come from somewhere else. | GRT-001, GRT-005 | The supported-language set is business-owned configuration supplied to the service, not content this feature authors or manages — consistent with §3. The spec and its acceptance tests stay language-agnostic and exercise the default plus at least two further languages. The concrete launch list is a configuration deliverable owned by the business and tracked outside this spec. | PO: Marco | **Resolved** |
| AMB-002 | What should the service return when a calling application expresses no language preference at all? | BR-1 addresses the case where a preference exists and is silent on its absence. | GRT-002 | Return the configured default language rather than an error, so a caller with no preference still renders a greeting. The default is **English**. | PO: Marco | **Resolved** |
| AMB-003 | For an unsupported language, should the service fall back to the default greeting or refuse the request? | BR-3 says only that the system "should handle" it; "handle" admits both readings, with materially different consequences for the end user. | GRT-005 | Fall back to the default language **and** state in the response that a fallback occurred. The end user always sees a greeting; the caller can still detect and report the gap. Refusing outright was rejected because it surfaces as broken UI. | PO: Marco | **Resolved** |
| AMB-004 | Does "monitorable by operations" mean an availability check only, or also usage metrics, per-language demand, and structured logs? | BR-4 says "monitorable" without defining what operations must be able to observe; §4 mentions only health verification. | GRT-006 | Scope this release to an availability indication, matching the one observability outcome the BRD's own success criteria state. Metrics, per-language demand reporting, and structured logging are deferred to a separate BRD. | PO: Marco | **Resolved** |
| AMB-005 | How should a calling application express its language preference, and does an agreed interface contract already exist for regional apps? | BR-2 requires availability to "all regional applications" and §4 calls for "a standard interface", but no contract, protocol, or preference-passing convention is named. | GRT-003 | One interface contract is published and adopted by all regional apps, with the language preference passed explicitly by the caller. The business confirms no regional app is bound to an incompatible existing contract. The concrete mechanism is a design decision recorded at G2, not a business ruling. | PO: Marco | **Resolved** |
| AMB-006 | Who is permitted to call the service, and is any caller authentication required? | The BRD names regional applications as consumers but states no access-control requirement, and none can be inferred from greeting text being non-sensitive. | GRT-003 | Greetings are non-sensitive; no per-caller authentication is required in this release. Access control is a platform-layer concern handled by network placement, explicitly out of scope for this spec. Ruled knowingly rather than inherited by silence. | PO: Marco | **Resolved** |
| AMB-007 | What availability and response-time expectations apply, given every regional app will depend on this service? | The BRD sets no service level, yet BR-2 makes this a shared dependency of all regional applications. | GRT-006 | No formal service-level objective in this release; the health indication under GRT-006 is the only operational commitment. Recorded follow-up for the business: set a target before this service becomes a hard dependency of a customer-facing journey. | PO: Marco | **Resolved** |

## Assumptions

Recorded so a reviewer can challenge them; reviewed and accepted at G1.
Each is a default chosen where the BRD was silent, not a requirement
derived from it.

- The greeting is a single piece of text per language; the BRD describes
  no structure, variants, or accompanying content beyond it.
- "Regional applications" are the only consumers; the BRD names no
  end-user-facing or third-party consumer of this service.
- Greeting text is not personal or sensitive data, which is what makes
  the AMB-006 ruling defensible.
- The supported-language set changes rarely and through business action,
  since translation content management is out of scope per §3.
- No existing greeting service is being replaced in place; §1 describes
  per-application greeting text, not a shared incumbent to migrate from.

## Traceability Summary

| BRD requirement | Covered by |
|---|---|
| BR-1 — greeting appropriate to language preference | GRT-001, GRT-002 |
| BR-2 — available to all regional applications | GRT-003, GRT-004 |
| BR-3 — handle unsupported language | GRT-005 |
| BR-4 — monitorable by operations | GRT-006 |

No BRD requirement is left uncovered, and no criterion exists without a
BRD requirement behind it.
