# Phase 0 — Research: Global Greeting Service

**Feature**: [spec.md](./spec.md) (Approved — Gate G1) | **Plan**: [plan.md](./plan.md)
**Date**: 2026-08-12

The stack was given: Python 3.12, FastAPI, pytest, no database, locale
templates exclusively from `config/locales.yml`. So there are no
NEEDS CLARIFICATION items on technology choice. What remains genuinely
open are the design questions G1 explicitly deferred to G2 — chiefly
AMB-005 (how a caller expresses a language preference) — plus the
consequences of the exclusive-config constraint.

Each decision below cites the criterion it serves. None of them changes
a requirement; where a design option would have, it is rejected and the
reason is recorded.

---

## R-1 — How does a caller express its language preference?

**Decision**: An explicit query parameter, `GET /greeting?lang=fr`.
Absent parameter means "no preference" and triggers the GRT-002 default.

**Serves**: GRT-001, GRT-003. Implements the AMB-005 ruling.

**Rationale**: The G1 ruling says the preference is "passed explicitly by
the caller". A query parameter is exactly that: present or absent, one
value, visible in logs and in a curl command. It is also the cheapest
thing to test — no header plumbing in the test client.

**Alternatives considered**:

- **`Accept-Language` header with content negotiation.** The HTTP-native
  answer, and the one most reviewers will ask about. Rejected because
  negotiation is *implicit*: browsers inject the header without the
  calling application choosing it, quality weights (`fr;q=0.9, en;q=0.8`)
  make "what did the caller ask for?" a ranking rather than a value, and
  GRT-005 needs to echo a single `requested_language` back. It also sits
  awkwardly with AMB-005's word "explicitly".
- **Path segment, `/greeting/fr`.** Reads well, but makes "no preference"
  a separate route rather than an absent value, which splits GRT-002 and
  GRT-001 across two paths for no gain.
- **Both header and parameter, parameter wins.** Rejected as unneeded
  surface: two ways to say the same thing, with a precedence rule to
  document and test. Can be added later without breaking D-1 if a real
  caller needs it.

---

## R-2 — What shape is the response?

**Decision**: JSON on every path, with a fixed schema:

| Field | Type | Meaning |
|---|---|---|
| `message` | string | The greeting text to display |
| `language` | string | The language the text is actually in |
| `requested_language` | string or null | What the caller asked for; null when no preference was supplied |
| `fallback` | boolean | True when the requested language was unavailable and the default was used |

**Serves**: GRT-001, GRT-002, GRT-005.

**Rationale**: GRT-005 requires the service to "indicate in its response
that a fallback occurred". A dedicated boolean makes that indication
machine-readable and independent of the status code, so a caller detects
the gap with one field check rather than by comparing what it asked for
against what it got. Keeping all four fields present on every path means
callers parse one schema, not three.

**Alternatives considered**:

- **Bare string body.** Smallest possible response, but there is nowhere
  to signal fallback, so GRT-005 becomes unimplementable without abusing
  the status code. Rejected.
- **Omit `requested_language` and `fallback` on the happy path.** Saves
  bytes; costs every caller a null-check and makes the contract two
  shapes. Rejected — the schema is the interface (GRT-003).
- **A `warnings[]` array instead of a boolean.** More extensible, but
  nothing else currently warns. Speculative generality. Rejected.

---

## R-3 — Fallback or refusal for an unsupported language?

**Decision**: Fall back to the default language and return **HTTP 200**
with `fallback: true`.

**Serves**: GRT-005.

**Rationale**: This is not an open design question — it was ruled at G1.
AMB-003: "Fall back to the default language **and** state in the response
that a fallback occurred… Refusing outright was rejected because it
surfaces as broken UI." The plan implements the ruling.

An error status (4xx) would contradict the approved criterion: a status
in the 4xx range tells the caller the request failed, when in fact a
usable greeting was returned. Callers that treat non-2xx as an exception
would discard a valid greeting and render nothing — precisely the broken
UI the PO ruled against.

**Alternatives considered**:

- **HTTP 400 with an `UNSUPPORTED_LOCALE` code and no fallback.** This is
  what `docs/DEMO-RUNBOOK.md:120` sketches, and it is a defensible design
  in the abstract — it is louder, and it forces callers to handle the
  gap. It is rejected here for one reason only: **it contradicts an
  approved criterion.** Adopting it is a spec change requiring the PO at
  G1, not a plan decision. Flagged in plan.md as a divergence so the tech
  lead sees it at G2 rather than discovering it in review.
- **200 with the requested language echoed in `language`.** Would lie
  about what the text is. Rejected.

---

## R-4 — When and how are locales loaded?

**Decision**: Read and validate `config/locales.yml` once at application
startup into an immutable in-memory mapping. No file access on the
request path. No reload endpoint, no file watching.

**Serves**: GRT-004, and GRT-006 by way of R-5.

**Rationale**: GRT-004 requires every calling application to receive the
same text for a given language. If the file were re-read per request, two
callers straddling a config edit would legitimately receive different
text and GRT-004 would hold only between deployments. Loading once makes
the guarantee structural for the process lifetime. It also keeps the
request path allocation-only — no I/O, no parse — which matters for a
service every regional app depends on, even though AMB-007 sets no target.

**Alternatives considered**:

- **Read per request.** Simplest to reason about for config edits; breaks
  the GRT-004 guarantee mid-flight and puts a YAML parse on every call.
  Rejected.
- **Cached read with TTL.** Same GRT-004 hazard as per-request, just
  rarer and harder to reproduce. Rejected.
- **Hot-reload endpoint.** Operationally attractive, but it is new
  surface area no criterion asks for, and it reintroduces the mid-flight
  inconsistency. Out of scope — a config change ships as a restart.

---

## R-5 — What does "available" mean for the health indication?

**Decision**: `GET /health` returns 200 when the locale table loaded
successfully and 503 when it did not. Nothing else is reported.

**Serves**: GRT-006.

**Rationale**: GRT-006 asks whether "the service is available". A process
that is accepting connections but holds no locale table cannot serve any
greeting, so reporting it healthy would make the indication misleading
exactly when operations most needs it. Config-load state is therefore not
extra observability — it *is* availability for this service.

This deliberately stops short of anything else. AMB-004 was ruled at G1
as availability-only, with "metrics, per-language demand reporting, and
structured logging… deferred to a separate BRD". So: no request counters,
no per-language hit counts, no uptime figure, no locale list in the
payload. Each of those would be a small, tempting, unapproved expansion.

**Alternatives considered**:

- **Always 200 if the process is up.** A pure liveness check. Rejected as
  actively misleading under the D-8 failure mode — the one case where the
  answer matters.
- **Report the loaded locale count or list.** Genuinely useful to
  operations, and out of scope under the AMB-004 ruling. If operations
  wants it, that is a new BRD, not a quiet addition here.

---

## R-6 — Consequence of "exclusively from config/locales.yml"

**Decision**: No greeting text appears anywhere in source code, including
as a last-resort default. If the file is missing, unparseable, or lacks
the default language, the service does not serve invented text — it
reports unhealthy via R-5 and `GET /greeting` fails loudly.

**Serves**: GRT-004, GRT-006. Implements the stated constraint.

**Rationale**: This is the constraint's real consequence and it is worth
stating plainly, because the instinct when writing the config loader is
to add `except: return {"en": "Hello"}`. That single line would violate
the exclusivity constraint and quietly break GRT-004: some deployments
would serve config text and others code text, with nothing to reveal
which. The design has no in-code greeting to fall back to, by intent.

**Startup behaviour on bad config — ruled at G2**: whether a bad config
should abort startup outright or start the process in an unhealthy state.
Starting unhealthy was recommended — operations can then query `/health`
and get a definite answer rather than facing a crash-looping container
with the reason buried in logs. Either satisfies GRT-006.

**Ruling (Tech Lead: Dana, 2026-08-12)**: the recommendation is adopted.
The service starts in an unhealthy state and reports it via `/health`;
it does not abort startup.

---

## Summary of unresolved items

| Item | Status |
|---|---|
| Technology choices | Given in the plan request; nothing to research |
| AMB-005 mechanism (deferred to G2) | Resolved by R-1 |
| Response shape | Resolved by R-2 |
| Fallback semantics | Fixed by the G1 ruling; R-3 implements it |
| Config load timing | Resolved by R-4 |
| Health semantics | Resolved by R-5 |
| Startup behaviour on bad config | **Ruled at G2** — start unhealthy, do not abort (R-6) |

No NEEDS CLARIFICATION remains, and nothing is left awaiting an approver:
the last open item (R-6) was ruled at G2 on 2026-08-12.
