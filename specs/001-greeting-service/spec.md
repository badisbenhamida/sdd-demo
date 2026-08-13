# Feature Specification: Global Greeting Service

**Feature Directory**: `specs/001-greeting-service`

**Source BRD**: [BRD-2026-014](../../docs/brd/BRD-2026-014-greeting-service.md) — Global Greeting Service (approved by business 2026-07-28)

**Created**: 2026-08-12

**Status**: **Approved — Gate G1 passed** 2026-08-12 by **PO: Marco**. Every Ambiguity Log item is Resolved; nothing is pending. Planning may begin (constitution Art. III.1 satisfied; Art. III.2 / Gate G2 still ahead).

**Input**: Transform BRD-2026-014 into a specification: EARS notation, stable `GRT-###` criterion IDs, a traceability column to BRD requirements, and an Ambiguity Log covering every gap. Invent nothing the BRD does not imply.

---

## Gate G1 — Spec approval record

| Field | Value |
|---|---|
| Gate | G1 — Spec approval (constitution Art. III.1) |
| Outcome | **Approved** |
| Resolver | PO: Marco |
| Date | 2026-08-12 |
| Ambiguity Log | 8 of 8 items Resolved, 0 pending |
| Ruling basis | The PO accepted the agent's proposed resolution on all eight items, and ruled on the two points those proposals had deliberately left open to the business (AMB-002 launch language set, AMB-005 field naming). |
| Criteria added by this gate | GRT-009, GRT-010 — see "Criteria added at G1" below |

Criteria wording sharpened by these rulings: GRT-002, GRT-005, GRT-006, GRT-008. Per Art. I.2 the IDs are unchanged; sharpening a criterion never renumbers it.

---

## Scope Boundary

Carried verbatim from BRD §3. The following are **out of scope** and no criterion below may assume them:

- Personalization (user names, time-of-day variants)
- Translation workflow / content management

Ruled out of scope at G1, recorded rather than dropped (per the PO's instruction that an out-of-scope ruling stays on the record):

- **Authentication and network exposure policy** — platform-layer concern, not this service's responsibility (AMB-003).
- **Metrics, log aggregation, and alerting** — deferred beyond this feature; the health indicator alone satisfies BR-4 for this release (AMB-004).
- **Contractual availability or latency targets** — none for this release; calling applications own their own timeout and degradation behaviour (AMB-008).
- **Inferring language preference from end-user context** (browser or device settings) — the calling application resolves preference and passes it explicitly (AMB-007).

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Regional application greets a user in their language (Priority: P1)

A customer-facing regional application needs to show a greeting to a user who has a known language preference. Instead of shipping its own greeting text, it asks the Greeting Service and displays what it gets back. Every regional application asking for the same language gets the same words.

**Why this priority**: This is the whole business case. BR-1 and BR-2 together are the reason the service exists — without this story there is no product, and the duplicated-translation cost named in BRD §1 is not addressed.

**Independent Test**: Ask the service for a greeting in a supported language and confirm the returned text is in that language; repeat from a second calling application and confirm the text is identical. Delivers the core value on its own.

**Acceptance Scenarios**:

1. **Given** the service supports the requested language, **When** a regional application requests a greeting for that language, **Then** the greeting returned is in that language.
2. **Given** two different regional applications, **When** both request a greeting for the same language, **Then** both receive the same greeting text.
3. **Given** a request that names no language preference, **When** the application requests a greeting, **Then** a greeting in the configured default language is returned.
4. **Given** a supported language identifier written in a different letter case, **When** a regional application requests a greeting for it, **Then** it is treated as that supported language.

---

### User Story 2 - Calling application meets an unsupported language (Priority: P2)

A regional application requests a greeting for a language the service does not carry. Per the G1 ruling on AMB-001, the end user still sees a greeting — the service substitutes the default language and marks the response so the calling application can detect that a substitution happened and log the gap.

**Why this priority**: BR-3 is a stated requirement, and unhandled unsupported languages would surface to end users as broken UI. It ranks below P1 because a service that only ever sees supported languages still delivers value.

**Independent Test**: Request a greeting for a language known not to be supported, confirm a default-language greeting is returned, and confirm the response is marked as a fallback in a way detectable without reading the greeting text.

**Acceptance Scenarios**:

1. **Given** a language the service does not support, **When** a regional application requests a greeting for it, **Then** a greeting in the configured default language is returned rather than an error or an unhandled failure.
2. **Given** that response, **When** the calling application inspects it, **Then** it can determine programmatically that a fallback occurred and which language was actually served, without parsing the greeting text.

---

### User Story 3 - Operations verifies service health (Priority: P3)

An operations engineer, or an automated monitor acting for them, needs to confirm at any time whether the Greeting Service is able to do its job — without making a greeting request and guessing from the result. Per the G1 ruling on AMB-004, health reflects whether greeting content actually loaded, not merely whether the process is running.

**Why this priority**: BR-4 and BRD §4 both require it, and it gates production readiness. It ranks last because it delivers no end-user value on its own.

**Independent Test**: Query the health indicator while greeting content is loaded and confirm it reports healthy; start the service with greeting content that cannot be loaded and confirm it reports unhealthy.

**Acceptance Scenarios**:

1. **Given** a running service whose greeting content has loaded, **When** operations queries the health indicator, **Then** it reports healthy.
2. **Given** a running service whose greeting content failed to load, **When** operations queries the health indicator, **Then** it reports unhealthy — a running process is not by itself healthy.

---

### Edge Cases

Each was undefined in the BRD and is now settled by the G1 ruling shown.

- A request naming a language the service does not support → default-language greeting, marked as a fallback (AMB-001, GRT-005, GRT-006).
- A request naming no language at all → configured default language (AMB-002, GRT-002).
- A language identifier differing only in letter case → matched case-insensitively (AMB-006, GRT-009).
- A language identifier in an unexpected form → language-and-region identifiers are the contract; anything not in the supported set is treated as unsupported and falls back (AMB-006, GRT-005).
- The service starts but greeting content cannot be loaded → the service is unhealthy; a running process is not sufficient (AMB-004, GRT-008).
- A language configured but with no greeting text behind it → it is not in the supported set; requests for it fall back (AMB-002, GRT-010).

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
| GRT-005 | If a calling application requests a greeting for a language the Greeting Service does not support, then the Greeting Service shall return a greeting in the configured default language rather than an error, and shall not fail unhandled. | BR-3 |
| GRT-006 | If the Greeting Service substitutes the default language for an unsupported one, then the response shall indicate in machine-readable form that a fallback occurred and which language was served, distinguishable without inspecting the greeting text. | BR-3 |
| GRT-007 | The Greeting Service shall expose a health indicator that operations can query to determine whether the service is able to serve greetings. | BR-4, §4 |
| GRT-008 | While the Greeting Service's greeting content is not loaded, the health indicator shall report unhealthy. | BR-4 |
| GRT-009 | When a calling application requests a greeting using a supported language identifier that differs only in letter case, the Greeting Service shall treat it as that supported language. | BR-1 |
| GRT-010 | The Greeting Service shall determine its supported language set and its default language from configuration, so that adding or changing a language requires no change to any calling application. | BR-1, BR-2, §1 |

**Criteria added at G1**: GRT-009 and GRT-010 did not exist in the draft. They are testable obligations created by the rulings on AMB-006 (case-insensitive matching) and AMB-002 (configuration as the single source of truth). Recording them as criteria rather than as prose keeps them inside the traceability gate — an obligation not in this table is an obligation `spec_drift.py` cannot enforce.

**Note on requirement IDs**: this spec deliberately does not carry the stock template's parallel `FR-###` list. Two competing requirement-ID systems in one spec would break the single-authority rule in CLAUDE.md ("when the two conflict, the criterion ID is authoritative"). `GRT-###` is the only requirement ID here.

### Key Entities

- **Greeting**: the text returned to a calling application, in one language. Sourced centrally so that all applications share tone (BRD §1). Carries no personalization (BRD §3).
- **Language**: the identifier a calling application uses to ask for a greeting, and the key by which greeting text is selected. Language-and-region form, matched case-insensitively, so regional variants are distinguishable (AMB-006).
- **Supported language set**: the languages for which the service holds greeting text. Determined by configuration, not by code (AMB-002, GRT-010). At launch: **en-US** (default), **fr-FR**, **de-DE**, **ja-JP**.
- **Health indicator**: the signal operations queries to learn whether the service can serve greetings. Reflects greeting-content load state, not process liveness alone (AMB-004, BR-4).

---

## Success Criteria *(mandatory)*

Derived from BRD §4 and the business context in §1. Technology-agnostic and verifiable without knowing the implementation.

- **SC-001**: A regional application can retrieve a greeting for a supported language through the standard interface without any application-specific integration work. *(BRD §4, BR-2)*
- **SC-002**: Operations can determine whether the service is able to serve greetings at any time, without issuing a greeting request and inferring health from it. *(BRD §4, BR-4)*
- **SC-003**: For any given language, every regional application receives identical greeting text — zero divergence in tone across applications. *(BRD §1, BR-2)*
- **SC-004**: A calling application can determine programmatically whether the greeting it received was in the language it asked for or was a default-language fallback, with no text parsing. *(BR-3 — restated at G1 under the AMB-001 ruling: the distinction is fallback-vs-exact, not error-vs-success.)*
- **SC-005**: Adding or changing a greeting for a language requires no change to any calling application. *(BRD §1 — eliminating duplicated translation cost)*

---

## Ambiguity Log

**All items are Resolved.** Every item below was a gap in BRD-2026-014, raised as a question for the business with a proposed resolution. At Gate G1 on 2026-08-12 the Product Owner ruled on all eight; the rulings below are **in force** and bind the plan and implementation stages. Nothing here is pending.

| ID | Gap in the BRD | Affected criteria | Status | Resolved by |
|---------|----------------|-------------------|--------|-------------|
| AMB-001 | Unsupported language: fail or fall back? | GRT-005, GRT-006 | **Resolved** | PO: Marco, 2026-08-12 |
| AMB-002 | Which languages at launch, and which is default? | GRT-002, GRT-010 | **Resolved** | PO: Marco, 2026-08-12 |
| AMB-003 | What is the "standard interface", and who may call it? | GRT-003 | **Resolved** | PO: Marco, 2026-08-12 |
| AMB-004 | What does "monitorable by operations" require? | GRT-007, GRT-008 | **Resolved** | PO: Marco, 2026-08-12 |
| AMB-005 | What is the response format and its fields? | GRT-001, GRT-006 | **Resolved** | PO: Marco, 2026-08-12 |
| AMB-006 | What form does a language identifier take? | GRT-005, GRT-009 | **Resolved** | PO: Marco, 2026-08-12 |
| AMB-007 | How does a caller convey the language preference? | GRT-001, GRT-002 | **Resolved** | PO: Marco, 2026-08-12 |
| AMB-008 | What availability or latency is the service held to? | (none — ruled no new criteria) | **Resolved** | PO: Marco, 2026-08-12 |

---

### AMB-001 — Unsupported language: fail or fall back?

**Question for the business**: BR-3 says the system "should handle" an unsupported language but does not say what handling means. When a regional app asks for a language we do not carry, should the service (a) return an error the caller must handle, or (b) return a greeting in the default language, marked so the caller knows a substitution happened?

**Why it matters**: This is the difference between a blank or error state in a regional UI and a user silently reading English in Osaka. It also decides whether every calling application must write error-handling code.

**Proposed resolution**: Option (b) — return the default-language greeting with an explicit indicator that a fallback occurred, so end users always see *something* while callers can still detect and log the gap.

**Ruling**: **Accepted as proposed — option (b).** An unsupported language is a successful response carrying a default-language greeting plus an explicit fallback indicator, not an error. No calling application is required to implement error handling in order to display a greeting. The substitution must never be silent: the response states that a fallback occurred and which language was served.

**Affected criteria**: GRT-005, GRT-006 — both sharpened to state fallback rather than a generic "defined outcome".

**Status**: **Resolved** — **Resolved by**: PO: Marco, 2026-08-12

---

### AMB-002 — Which languages at launch, and which is default?

**Question for the business**: The BRD names no languages. Which languages must be supported at launch, which is the default when none is requested, and where does that list live so it can change without a code release?

**Why it matters**: Determines launch readiness and translation commissioning; GRT-002 cannot be tested without a known default.

**Proposed resolution**: A configuration file is the single source of truth for the supported set and the default, so languages can be added without a code change (supporting SC-005). Launch membership is a business decision and is not proposed here.

**Ruling**: **Accepted as proposed, and the open half decided by the business.** Configuration is the single source of truth for both the supported set and the default — this becomes GRT-010. Launch membership, which the proposal correctly left to the business: **en-US, fr-FR, de-DE, ja-JP**, with **en-US as the default** when no preference is named. A language belongs to the supported set only if greeting text exists behind it; a configured entry with no text is not supported and falls back under AMB-001.

**Affected criteria**: GRT-002, GRT-010 (new)

**Status**: **Resolved** — **Resolved by**: PO: Marco, 2026-08-12

---

### AMB-003 — What is the "standard interface", and who may call it?

**Question for the business**: BRD §4 requires retrieval "via a standard interface" and BR-2 requires availability to "all regional applications". Which interface style is standard here, and is access restricted — authenticated callers only, internal network only, or open to any regional app?

**Why it matters**: GRT-003 is untestable until the interface is named, and an access ruling changes the security surface.

**Proposed resolution**: A synchronous request/response network interface over HTTP. Authentication and network exposure are platform-layer concerns handled outside this service; record that as an explicit ruling rather than silence.

**Ruling**: **Accepted as proposed.** The interface is a synchronous HTTP request/response API. Authentication and network exposure policy are **ruled out of scope** for this service — they are platform-layer concerns — and that out-of-scope ruling is recorded here and in the Scope Boundary rather than left as silence. This service does not implement authentication, and its criteria must not assume any.

**Affected criteria**: GRT-003

**Status**: **Resolved** — **Resolved by**: PO: Marco, 2026-08-12

---

### AMB-004 — What does "monitorable by operations" require?

**Question for the business**: BR-4 requires the service be "monitorable" without defining the obligation. Is a health signal sufficient for launch, or do operations also require metrics, structured logs, or alerting?

**Why it matters**: Sets the size of the observability workstream, and decides whether "unable to serve greetings" (GRT-008) means only "process down" or also "greeting content failed to load".

**Proposed resolution**: A queryable health indicator that reflects whether greeting content actually loaded — not merely whether the process is running. Metrics, log aggregation, and alerting are deferred beyond this feature unless operations states otherwise.

**Ruling**: **Accepted as proposed.** A queryable health indicator satisfies BR-4 for this release, and it must reflect greeting-content load state — a process that is up but cannot serve greetings reports unhealthy. Metrics, log aggregation, and alerting are **ruled out of scope** for this feature and recorded in the Scope Boundary; they are deferred, not rejected, and may return as a later BRD amendment.

**Affected criteria**: GRT-007, GRT-008 — GRT-008 sharpened from "unable to serve greetings" to the content-load state that makes it testable.

**Status**: **Resolved** — **Resolved by**: PO: Marco, 2026-08-12

---

### AMB-005 — What is the response format and its fields?

**Question for the business**: The BRD never describes what a caller receives. Is the response the greeting text alone, or a structured payload; and which fields must it carry?

**Why it matters**: This is the integration contract for every regional application; changing it after launch means changing all of them.

**Proposed resolution**: A structured payload carrying at minimum the greeting text and the language it was served in, so callers can confirm what they got. Exact field names are a design decision for the plan stage, not a business ruling.

**Ruling**: **Accepted as proposed.** The response is a structured JSON payload carrying at minimum the greeting text, the language actually served, and — under the AMB-001 ruling — the fallback indicator. The business ruling binds the *content* of the payload; **exact field naming is delegated to the plan stage (Gate G2)**, as the proposal asked. Field names are therefore not fixed by this spec and no criterion depends on them.

**Affected criteria**: GRT-001, GRT-006

**Status**: **Resolved** — **Resolved by**: PO: Marco, 2026-08-12

---

### AMB-006 — What form does a language identifier take?

**Question for the business**: Do callers identify a language by bare language code (`fr`), or by language-and-region (`fr-FR`, distinguishing `pt-BR` from `pt-PT`)? Are identifiers matched case-sensitively?

**Why it matters**: Regional variants are the difference between a correct and an insulting greeting in several markets, and the choice determines what counts as "unsupported" in GRT-005.

**Proposed resolution**: Language-and-region identifiers, matched case-insensitively, so regional variants can be distinguished when the business needs them.

**Ruling**: **Accepted as proposed.** Identifiers are language-and-region form and are matched case-insensitively, so a difference in letter case alone never causes a fallback. Case-insensitive matching becomes GRT-009. Any identifier not in the configured supported set — including a bare language code with no region — is unsupported and falls back under AMB-001.

**Affected criteria**: GRT-005, GRT-009 (new)

**Status**: **Resolved** — **Resolved by**: PO: Marco, 2026-08-12

---

### AMB-007 — How does a caller convey the language preference?

**Question for the business**: BR-1 refers to "the user's language preference" without saying how it reaches the service. Does the calling application pass it explicitly, or is the service expected to infer it from the end user's browser or device settings?

**Why it matters**: Inference would make the service responsible for interpreting end-user context it cannot see, and would change the meaning of "no preference given" in GRT-002.

**Proposed resolution**: The calling application resolves the user's preference and passes it explicitly. The service does not infer preference from end-user context.

**Ruling**: **Accepted as proposed.** The calling application resolves the end user's preference and passes it explicitly. Inferring preference from browser or device context is **ruled out of scope** and recorded in the Scope Boundary. "No preference given" therefore means the caller sent none, which is a well-defined, testable condition for GRT-002.

**Affected criteria**: GRT-001, GRT-002

**Status**: **Resolved** — **Resolved by**: PO: Marco, 2026-08-12

---

### AMB-008 — What availability or latency is the service held to?

**Question for the business**: The BRD sets no performance or availability target, yet this service would sit in the render path of every regional application's page load. Is there a target it must meet, and what should a calling application do when the service is unreachable?

**Why it matters**: A shared dependency with no stated target becomes a single point of failure by default. If a target exists, it adds criteria to this spec.

**Proposed resolution**: No contractual target for this release; calling applications remain responsible for their own timeout and degradation behaviour. If the business disagrees, new criteria are added here before G1 rather than assumed later.

**Ruling**: **Accepted as proposed — no contractual target for this release**, and therefore no criteria added. Calling applications own their own timeout and degradation behaviour. This is **ruled out of scope and recorded, not dropped**: the risk that a shared render-path dependency has no stated target was raised, considered, and accepted by the business. Revisiting it requires a BRD amendment, which would add criteria here.

**Affected criteria**: none — the ruling matches the proposal, so no criteria were added

**Status**: **Resolved** — **Resolved by**: PO: Marco, 2026-08-12

---

## Assumptions

Kept deliberately short. Where the BRD was silent on something material, the gap went to the Ambiguity Log for a human ruling rather than being assumed away here — and all eight are now ruled.

- The BRD is approved and stable; requirement changes arrive as BRD amendments, and reach this spec by PR (constitution Art. I.3).
- "Regional applications" are first-party applications within the organisation, not third parties. The BRD names no external consumer. *(Access ruled platform-layer in AMB-003.)*
- Greeting text is authored and translated outside this feature — translation workflow is out of scope per BRD §3. This service serves existing text; it does not produce it.
- No end-user personal data is involved: a greeting is selected by language alone, with personalization out of scope per BRD §3.

---

## Traceability Summary

Every BRD requirement is covered by at least one criterion, and every criterion traces back to a BRD requirement. No orphans in either direction.

| BRD requirement | Covered by |
|-----------------|------------|
| BR-1 — greeting appropriate to language preference | GRT-001, GRT-002, GRT-009, GRT-010 |
| BR-2 — available to all regional applications | GRT-003, GRT-004, GRT-010 |
| BR-3 — handle unsupported language | GRT-005, GRT-006 |
| BR-4 — monitorable by operations | GRT-007, GRT-008 |
