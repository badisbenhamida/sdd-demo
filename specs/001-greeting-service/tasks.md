# Tasks: Greeting Service

**Derived from:** specs/001-greeting-service/spec.md
**Status:** Approved (Gate G2 passed — Tech lead: Dana, 2026-07-31)
**Sync:** `scripts/gh_sync.py` reads this file. GitHub Issues are
derived from these tasks; edits happen here, never in GitHub.

---

## Story S1 — Serve localized greetings
Implements: GRT-001, GRT-002, GRT-004, GRT-006

- [ ] T1.1 Load locale templates from `config/locales.yml` at startup. (GRT-006) [P2]
- [ ] T1.2 Implement `GET /greet` with `locale` param and JSON response shape. (GRT-001, GRT-002) [P1]
- [ ] T1.3 Default-locale fallback when `locale` absent. (GRT-004) [P2]

## Story S2 — Reject unsupported locales explicitly
Implements: GRT-003

- [ ] T2.1 Return 400 + `UNSUPPORTED_LOCALE` + supported list. (GRT-003) [P1]

## Story S3 — Operational health
Implements: GRT-005

- [ ] T3.1 `GET /health` reflecting config load state (503 → 200). (GRT-005) [P2]
