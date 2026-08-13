# Feature Specification: Global Greeting Service

**Feature Directory**: `specs/001-greeting-service`

**Source BRD**: [BRD-2026-014](../../docs/brd/BRD-2026-014-greeting-service.md) — Global Greeting Service (approved by business 2026-07-28)

**Created**: 2026-08-12

**Status**: Draft — **PENDING G1** (spec approval). Per constitution Art. III.1, a human (PO/BA) must approve this spec *including resolution of every item in the Ambiguity Log* before planning begins.

**Input**: Transform BRD-2026-014 into a specification: EARS notation, stable `GRT-###` criterion IDs, a traceability column to BRD requirements, and an Ambiguity Log covering every gap. Invent nothing the BRD does not imply.

---

## Scope Boundary

Carried verbatim from BRD §3. The following are **out of scope** and no criterion below may assume them:

- Personalization (user names, time-of-day variants)
- Translation workflow / content management

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Regional application greets a user in their language (Priority: P1)

A customer-facing regional application needs to show a greeting to a user who has a known language preference. Instead of shipping its own greeting text, it asks the Greeting Service and displays what it gets back. Every regional application asking for the same language gets the same words.

**Why this priority**: This is the whole business case. BR-1 and BR-2 together are the reason the service exists — without this story there is no product, and the duplicated-translation cost named in BRD §1 is not addressed.

**Independent Test**: Ask the service for a greeting in a supported language and confirm the returned text is in that language; repeat from a second calling application and confirm the text is identical. Delivers the core value on its own.

**Acceptance Scenarios**:

1. **Given** the service supports the requested language, **When** a regional application requests a greeting for that language, **Then** the greeting returned is in that language.
2. **Given** two different regional applications, **When** both request a greeting for the same language, **Then** both receive the same greeting text.
3. **Given** a request that names no language preference, **When** the application requests a greeting, **Then** a greeting in the configured default language is returned. *(Contingent on AMB-002.)*

---

### User Story 2 - Calling application meets an unsupported language (Priority: P2)

A regional application requests a greeting for a language the service does not carry. Rather than breaking or returning something misleading, the service responds in a defined way the calling application can detect and act on programmatically.

**Why this priority**: BR-3 is a stated requirement, and unhandled unsupported languages would surface to end users as broken UI. It ranks below P1 because a service that only ever sees supported languages still delivers value.

**Independent Test**: Request a greeting for a language known not to be supported and confirm the response is the defined outcome, is distinguishable from a successful greeting without inspecting the text, and is not an unhandled failure.

**Acceptance Scenarios**:

1. **Given** a language the service does not support, **When** a regional application requests a greeting for it, **Then** the service returns its defined unsupported-language outcome rather than failing unhandled.
2. **Given** that outcome, **When** the calling application inspects it, **Then** it can determine programmatically that the language was unsupported. *(Shape contingent on AMB-001.)*

---

### User Story 3 - Operations verifies service health (Priority: P3)

An operations engineer, or an automated monitor acting for them, needs to confirm at any time whether the Greeting Service is able to do its job — without making a greeting request and guessing from the result.

**Why this priority**: BR-4 and BRD §4 both require it, and it gates production readiness. It ranks last because it delivers no end-user value on its own.

**Independent Test**: Query the health indicator while the service is able to serve greetings and confirm it reports healthy; put the service in a state where it cannot serve greetings and confirm it reports unhealthy.

**Acceptance Scenarios**:

1. **Given** a running service able to serve greetings, **When** operations queries the health indicator, **Then** it reports healthy.
2. **Given** a service that cannot serve greetings, **When** operations queries the health indicator, **Then** it reports unhealthy.

---

### Edge Cases

Listed because the BRD leaves them undefined. Each is carried into the Ambiguity Log rather than resolved here by assumption.

- A request naming a language the service does not support → AMB-001.
- A request naming no language at all → AMB-002.
- A language identifier in an unexpected form (`fr` vs `fr-FR`, differing case) → AMB-006.
- The service starts but its greeting content cannot be loaded — can it be simultaneously "running" and unable to greet? → AMB-004, GRT-008.
- A language that is configured but has no greeting text behind it → AMB-002.

---

## Requirements *(mandatory)*

### Acceptance Criteria (EARS)

Every criterion is written in EARS notation and carries a stable ID. Per constitution Art. I.2, IDs are never reused; per Art. II.1, each must be covered by a test declaring `Implements: GRT-###`. The **Traces to** column maps each criterion to the BRD requirement that justifies it — no criterion exists without one.

| ID | Acceptance criterion (EARS) | Traces to |
|---------|-----------------------------|-----------|
| GRT-001 | When a calling application requests a greeting for a supported language, the Greeting Service shall return a greeting in that language. | BR-1 |
| GRT-002 | When a calling application requests a greeting without naming a language preference, the Greeting Service shall return a greeting in the configured default language. | BR-1 |
| GRT-003 | The Greeting Service shall expose one interface through which any regional application can retrieve a greeting. | BR-2, §4 |
| GRT-004 | When two calling applications request a greeting for the same language, the Greeting Service shall return identical greeting text to both. | BR-2, §1 |
| GRT-005 | If a calling application requests a greeting for a language the Greeting Service does not support, then the Greeting Service shall return its defined unsupported-language outcome and shall not fail unhandled. | BR-3 |
| GRT-006 | If the Greeting Service returns its unsupported-language outcome, then that outcome shall identify the unsupported-language condition in a machine-readable form, distinguishable from a successful greeting without inspecting the greeting text. | BR-3 |
| GRT-007 | The Greeting Service shall expose a health indicator that operations can query to determine whether the service is able to serve greetings. | BR-4, §4 |
| GRT-008 | While the Greeting Service is unable to serve greetings, the health indicator shall report unhealthy. | BR-4 |

**Note on requirement IDs**: this spec deliberately does not carry the stock template's parallel `FR-###` list. Two competing requirement-ID systems in one spec would break the single-authority rule in CLAUDE.md ("when the two conflict, the criterion ID is authoritative"). `GRT-###` is the only requirement ID here.

**Contingent criteria**: GRT-002, GRT-005, and GRT-006 are stated at the level of precision the BRD actually supports. Their concrete shape depends on Ambiguity Log rulings (AMB-001, AMB-002) and the wording above may be sharpened — not replaced — at G1. The IDs are stable regardless.

### Key Entities

- **Greeting**: the text returned to a calling application, in one language. Sourced centrally so that all applications share tone (BRD §1). Carries no personalization (BRD §3).
- **Language**: the identifier a calling application uses to ask for a greeting, and the key by which greeting text is selected. Its exact form is open — AMB-006.
- **Supported language set**: the languages for which the service holds greeting text. Its membership at launch and its source of truth are open — AMB-002.
- **Health indicator**: the signal operations queries to learn whether the service can serve greetings (BR-4).

---

## Success Criteria *(mandatory)*

Derived from BRD §4 and the business context in §1. Technology-agnostic and verifiable without knowing the implementation.

- **SC-001**: A regional application can retrieve a greeting for a supported language through the standard interface without any application-specific integration work. *(BRD §4, BR-2)*
- **SC-002**: Operations can determine whether the service is able to serve greetings at any time, without issuing a greeting request and inferring health from it. *(BRD §4, BR-4)*
- **SC-003**: For any given language, every regional application receives identical greeting text — zero divergence in tone across applications. *(BRD §1, BR-2)*
- **SC-004**: A calling application can distinguish an unsupported-language response from a successful greeting programmatically, with no text parsing. *(BR-3)*
- **SC-005**: Adding or changing a greeting for a language requires no change to any calling application. *(BRD §1 — eliminating duplicated translation cost)*

---

## Ambiguity Log

**Every item below is a gap in BRD-2026-014, not a design preference.** Each carries a question for the business and a proposed resolution the agent believes defensible. **No proposed resolution is in force.** Per constitution Art. III.1, a human (PO/BA) rules on every item before planning; per Art. IV.2 these proposals are drafts.

The demo runbook's G1 script rules *against* the AMB-001 proposal below. That is expected — the proposal is the agent's honest recommendation, and the gate exists precisely so a human can overrule it.

| ID | Gap in the BRD | Affected criteria | Status |
|---------|----------------|-------------------|--------|
| AMB-001 | Unsupported language: fail or fall back? | GRT-005, GRT-006 | PENDING HUMAN APPROVAL |
| AMB-002 | Which languages at launch, and which is default? | GRT-001, GRT-002 | PENDING HUMAN APPROVAL |
| AMB-003 | What is the "standard interface", and who may call it? | GRT-003 | PENDING HUMAN APPROVAL |
| AMB-004 | What does "monitorable by operations" require? | GRT-007, GRT-008 | PENDING HUMAN APPROVAL |
| AMB-005 | What is the response format and its fields? | GRT-001, GRT-006 | PENDING HUMAN APPROVAL |
| AMB-006 | What form does a language identifier take? | GRT-001, GRT-005 | PENDING HUMAN APPROVAL |
| AMB-007 | How does a caller convey the language preference? | GRT-001, GRT-002 | PENDING HUMAN APPROVAL |
| AMB-008 | What availability or latency is the service held to? | (none — would add criteria) | PENDING HUMAN APPROVAL |

---

### AMB-001 — Unsupported language: fail or fall back?

**Question for the business**: BR-3 says the system "should handle" an unsupported language but does not say what handling means. When a regional app asks for a language we do not carry, should the service (a) return an error the caller must handle, or (b) return a greeting in the default language, marked so the caller knows a substitution happened?

**Why it matters**: This is the difference between a blank or error state in a regional UI and a user silently reading English in Osaka. It also decides whether every calling application must write error-handling code.

**Proposed resolution**: Option (b) — return the default-language greeting with an explicit indicator that a fallback occurred, so end users always see *something* while callers can still detect and log the gap.

**Affected criteria**: GRT-005, GRT-006

**Status**: PENDING HUMAN APPROVAL — **Resolved by**: _(unassigned)_

---

### AMB-002 — Which languages at launch, and which is default?

**Question for the business**: The BRD names no languages. Which languages must be supported at launch, which is the default when none is requested, and where does that list live so it can change without a code release?

**Why it matters**: Determines launch readiness and translation commissioning; GRT-002 cannot be tested without a known default.

**Proposed resolution**: A configuration file is the single source of truth for the supported set and the default, so languages can be added without a code change (supporting SC-005). Launch membership is a business decision and is not proposed here.

**Affected criteria**: GRT-001, GRT-002

**Status**: PENDING HUMAN APPROVAL — **Resolved by**: _(unassigned)_

---

### AMB-003 — What is the "standard interface", and who may call it?

**Question for the business**: BRD §4 requires retrieval "via a standard interface" and BR-2 requires availability to "all regional applications". Which interface style is standard here, and is access restricted — authenticated callers only, internal network only, or open to any regional app?

**Why it matters**: GRT-003 is untestable until the interface is named, and an access ruling changes the security surface.

**Proposed resolution**: A synchronous request/response network interface over HTTP. Authentication and network exposure are platform-layer concerns handled outside this service; record that as an explicit ruling rather than silence.

**Affected criteria**: GRT-003

**Status**: PENDING HUMAN APPROVAL — **Resolved by**: _(unassigned)_

---

### AMB-004 — What does "monitorable by operations" require?

**Question for the business**: BR-4 requires the service be "monitorable" without defining the obligation. Is a health signal sufficient for launch, or do operations also require metrics, structured logs, or alerting?

**Why it matters**: Sets the size of the observability workstream, and decides whether "unable to serve greetings" (GRT-008) means only "process down" or also "greeting content failed to load".

**Proposed resolution**: A queryable health indicator that reflects whether greeting content actually loaded — not merely whether the process is running. Metrics, log aggregation, and alerting are deferred beyond this feature unless operations states otherwise.

**Affected criteria**: GRT-007, GRT-008

**Status**: PENDING HUMAN APPROVAL — **Resolved by**: _(unassigned)_

---

### AMB-005 — What is the response format and its fields?

**Question for the business**: The BRD never describes what a caller receives. Is the response the greeting text alone, or a structured payload; and which fields must it carry?

**Why it matters**: This is the integration contract for every regional application; changing it after launch means changing all of them.

**Proposed resolution**: A structured payload carrying at minimum the greeting text and the language it was served in, so callers can confirm what they got. Exact field names are a design decision for the plan stage, not a business ruling.

**Affected criteria**: GRT-001, GRT-006

**Status**: PENDING HUMAN APPROVAL — **Resolved by**: _(unassigned)_

---

### AMB-006 — What form does a language identifier take?

**Question for the business**: Do callers identify a language by bare language code (`fr`), or by language-and-region (`fr-FR`, distinguishing `pt-BR` from `pt-PT`)? Are identifiers matched case-sensitively?

**Why it matters**: Regional variants are the difference between a correct and an insulting greeting in several markets, and the choice determines what counts as "unsupported" in GRT-005.

**Proposed resolution**: Language-and-region identifiers, matched case-insensitively, so regional variants can be distinguished when the business needs them.

**Affected criteria**: GRT-001, GRT-005

**Status**: PENDING HUMAN APPROVAL — **Resolved by**: _(unassigned)_

---

### AMB-007 — How does a caller convey the language preference?

**Question for the business**: BR-1 refers to "the user's language preference" without saying how it reaches the service. Does the calling application pass it explicitly, or is the service expected to infer it from the end user's browser or device settings?

**Why it matters**: Inference would make the service responsible for interpreting end-user context it cannot see, and would change the meaning of "no preference given" in GRT-002.

**Proposed resolution**: The calling application resolves the user's preference and passes it explicitly. The service does not infer preference from end-user context.

**Affected criteria**: GRT-001, GRT-002

**Status**: PENDING HUMAN APPROVAL — **Resolved by**: _(unassigned)_

---

### AMB-008 — What availability or latency is the service held to?

**Question for the business**: The BRD sets no performance or availability target, yet this service would sit in the render path of every regional application's page load. Is there a target it must meet, and what should a calling application do when the service is unreachable?

**Why it matters**: A shared dependency with no stated target becomes a single point of failure by default. If a target exists, it adds criteria to this spec.

**Proposed resolution**: No contractual target for this release; calling applications remain responsible for their own timeout and degradation behaviour. If the business disagrees, new criteria are added here before G1 rather than assumed later.

**Affected criteria**: none currently — a ruling other than the proposal adds criteria

**Status**: PENDING HUMAN APPROVAL — **Resolved by**: _(unassigned)_

---

## Assumptions

Kept deliberately short. Where the BRD was silent on something material, the gap went to the Ambiguity Log for a human ruling rather than being assumed away here.

- The BRD is approved and stable; requirement changes arrive as BRD amendments, and reach this spec by PR (constitution Art. I.3).
- "Regional applications" are first-party applications within the organisation, not third parties. The BRD names no external consumer. *(Access is ruled on in AMB-003.)*
- Greeting text is authored and translated outside this feature — translation workflow is out of scope per BRD §3. This service serves existing text; it does not produce it.
- No end-user personal data is involved: a greeting is selected by language alone, with personalization out of scope per BRD §3.

---

## Traceability Summary

Every BRD requirement is covered by at least one criterion, and every criterion traces back to a BRD requirement. No orphans in either direction.

| BRD requirement | Covered by |
|-----------------|------------|
| BR-1 — greeting appropriate to language preference | GRT-001, GRT-002 |
| BR-2 — available to all regional applications | GRT-003, GRT-004 |
| BR-3 — handle unsupported language | GRT-005, GRT-006 |
| BR-4 — monitorable by operations | GRT-007, GRT-008 |
