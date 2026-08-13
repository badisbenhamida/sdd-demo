# Phase 0 — Research: Global Greeting Service

**Feature**: `specs/001-greeting-service` | **Date**: 2026-08-12 | **Plan**: [plan.md](./plan.md)

**Status**: Approved — supports a plan that passed Gate G2 on 2026-08-12 (Tech Lead: Dana). Decisions R-1…R-6 are binding on implementation.

Scope note: the technology choice itself was not researched. Python 3.12, FastAPI, and pytest were given as inputs, and all three are already pinned in `requirements.txt` and exercised by `.github/workflows/spec-drift.yml`. What needed resolving was *how* to use them against the G1 rulings. Each item below closes one unknown the Technical Context would otherwise have carried as `NEEDS CLARIFICATION`.

---

## R-1 — What HTTP status does a fallback return?

**Decision**: HTTP **200** with `fallback: true` in the body.

**Rationale**: GRT-005 requires the service return a default-language greeting "rather than an error", per the AMB-001 ruling. A 4xx would make every calling application implement error handling in order to display a greeting, which is precisely what the PO ruled against. The request succeeded — a greeting was produced — so 200 is also the honest status.

**Alternatives considered**:
- *4xx with a machine-readable code* — matches a stricter reading of BR-3 and was the alternative the PO explicitly rejected at G1. Rejected here on that ruling, not on merit.
- *200 with a warning header* — keeps the body clean, but headers are easy for a caller to drop through a proxy or client library, and GRT-006 wants the indicator in the payload.
- *203 Non-Authoritative Information* — semantically cute, but non-obvious to callers and likely to be treated as an error by defensive client code.

---

## R-2 — How is `config/locales.yml` loaded, and when?

**Decision**: Load **once at application startup** via a FastAPI lifespan handler, into an immutable in-memory structure. Failure to load is captured, not raised — the app still starts, and reports unhealthy.

**Rationale**: GRT-008 requires the health indicator report unhealthy *while* content is not loaded. If a load failure crashed the process at import time, there would be no service left to answer `/health`, and GRT-008 would be untestable — the failure mode would be an unreachable port, indistinguishable from a network problem. Starting degraded and reporting it is what makes "running but unable to greet" an observable state, which is the whole point of the AMB-004 ruling.

**Alternatives considered**:
- *Read the file per request* — would let operators edit locales without a restart, but adds filesystem I/O to the render path of every page load, and the BRD asks for none of it. Rejected as unrequested scope.
- *Fail fast at import* — simpler, and the usual default for config errors. Rejected because it makes GRT-008 unobservable, as above.
- *Reload on file change (watcher)* — no requirement. Rejected as unrequested scope.

---

## R-3 — How is case-insensitive matching implemented (GRT-009)?

**Decision**: Normalise locale keys to **lowercase once at load time**; lowercase the incoming query value at lookup. The response echoes the **configured** spelling, not the caller's.

**Rationale**: Normalising in one place makes case-insensitivity a property of the loaded data, so a future call site cannot reintroduce case sensitivity by forgetting to fold. Echoing the configured spelling keeps `locale` canonical in the payload — a caller asking for `FR-fr` gets `"locale": "fr-FR"` back, which is more useful than a mirror of their own typo.

**Alternatives considered**:
- *Fold at each comparison* — same behaviour today, but the invariant lives in every call site instead of one, and drifts the moment a second lookup path appears.
- *Full BCP-47 canonicalisation via a library (e.g. `langcodes`)* — correct in the general case, and would handle `fr_FR` or `fra`. Rejected: it adds a dependency the pinned set does not carry, and the G1 ruling on AMB-006 defined the contract as membership of the configured set, not general tag parsing. Anything outside the set falls back, which is defined behaviour rather than an error.

---

## R-4 — How is "templates load exclusively from `config/locales.yml`" enforced?

**Decision**: All file reads live in `src/config.py`; no greeting literal appears anywhere in `src/`, **including no built-in default greeting**. A missing or unparseable file yields the empty-config state (→ unhealthy), never a hardcoded fallback string.

**Rationale**: "Exclusively" is a constraint that decays silently. The tempting failure is a safety-net literal — `return "Hello!"` when config is missing — which would satisfy every greeting test while quietly violating the constraint and masking the unhealthy state GRT-008 exists to expose. Confining I/O to one module makes the constraint auditable by reading one file, and the no-literal rule is stated here so it can be checked at review rather than assumed.

**Alternatives considered**:
- *Embedded default greeting as a safety net* — improves apparent availability, directly violates the constraint, and hides exactly the condition GRT-008 must surface. Rejected.
- *An automated lint forbidding string literals in `src/`* — enforceable but noisy against ordinary code, and unrequested. Left to human review at G3.

---

## R-5 — Health endpoint semantics (GRT-007, GRT-008)

**Decision**: `GET /health` → **200** with a body naming the load state when locales are loaded; **503** when they are not.

**Rationale**: The AMB-004 ruling requires health reflect content load state rather than process liveness. 503 Service Unavailable is the standard way to say "running, cannot serve" and is what orchestrators and load balancers already act on, so the signal is usable by operations without bespoke monitoring. A body carrying the loaded-locale count makes a green check informative rather than merely green.

**Alternatives considered**:
- *Always 200 with `{"status": "unhealthy"}`* — forces every monitor to parse the body; a default HTTP check would report healthy while the service could not greet.
- *Separate liveness and readiness endpoints* — the standard Kubernetes split, and defensible. Rejected as unrequested: BR-4 asks for monitorability, the G1 ruling scoped it to one health indicator, and a second endpoint would need a criterion that does not exist.

---

## R-6 — Does anything here need persistence?

**Decision**: No database, no cache, no session state. Confirmed against the spec, not merely accepted as an input constraint.

**Rationale**: Every criterion is a pure function of the request and the loaded configuration. Personalization is out of scope (BRD §3), so nothing is per-user; translation workflow is out of scope, so nothing is written back. There is no criterion whose behaviour depends on a prior request. The "no database" input constraint and the spec agree.

**Alternatives considered**: none required — no criterion motivates storage.

---

## Resolved Unknowns Summary

| Unknown from Technical Context | Resolved by | Outcome |
|---|---|---|
| Status code for an unsupported locale | R-1 | 200 + `fallback: true` |
| Config load timing and failure behaviour | R-2 | Startup lifespan; degrade, do not crash |
| Case-insensitive matching mechanism | R-3 | Fold at load; echo configured spelling |
| Enforcing config exclusivity | R-4 | I/O in one module; no greeting literals in `src/` |
| Health signal semantics | R-5 | 200 / 503 on load state |
| Persistence need | R-6 | None |

No `NEEDS CLARIFICATION` markers remain in the plan's Technical Context.
