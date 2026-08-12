# Quickstart & Validation: Global Greeting Service

**Feature**: `specs/001-greeting-service` | **Date**: 2026-08-12
**Status**: 🔶 DRAFT — supports plan.md, pending G2

How to run the service and prove the eight approved criteria hold. Contract details are in
[contracts/greeting-api.md](./contracts/greeting-api.md); shapes in
[data-model.md](./data-model.md).

> Nothing below is runnable until implementation (`/speckit-tasks` → `/speckit-implement`).
> This is the validation guide the implementation must satisfy.

---

## Prerequisites

```bash
# From the repo root. Per CLAUDE.md, always use .venv/bin/python.
python3 -m venv .venv                      # only if .venv is absent
.venv/bin/pip install -r requirements.txt  # fastapi, pyyaml, pytest, httpx, uvicorn
```

All dependencies are already listed in `requirements.txt` — the feature adds none.

---

## Gate 1 — traceability

```bash
.venv/bin/python scripts/spec_drift.py
```

**Expected once implemented**: `Criteria: 8 active, 0 retired` / `Covered: 8/8`, exit 0.

Before implementation this reports `0/8` and exits 1. That is correct: the criteria exist,
the tests do not yet. Each test file must carry `# Implements: GRT-###` for the criteria it
covers, per the Criterion → Test Map in [plan.md](./plan.md).

## Gate 2 — acceptance tests

```bash
.venv/bin/python -m pytest tests/ -q
```

**Expected**: all pass. Both gates are required status checks on `main`
(`.github/workflows/spec-drift.yml`).

---

## Running the service

```bash
.venv/bin/python -m uvicorn src.greeting_service.app:app --reload --port 8000
```

Startup aborts if `config/locales.yml` is missing or invalid — a broken catalogue never
reaches traffic (research D3).

---

## Manual validation

Each check below maps to a criterion. Responses are illustrative; the contract is
authoritative.

**Supported language → greeting (GRT-001, GRT-002)**

```bash
curl "localhost:8000/greeting?language=fr"
# {"language":"fr","greeting":"Bonjour"}
```

Run it twice, and from two different clients — the text must be byte-identical (GRT-002).

**All five languages resolve (GRT-007)**

```bash
for l in en fr de es ja; do curl -s "localhost:8000/greeting?language=$l"; echo; done
```

Exactly these five succeed. Any sixth language must fail as unsupported.

**Unsupported language (GRT-004)**

```bash
curl -i "localhost:8000/greeting?language=xx"
# 404  {"code":"UNSUPPORTED_LANGUAGE", ...}
```

Confirm there is **no** `greeting` field. No fallback text may appear — that was the
AMB-002 decision.

**No language supplied (GRT-008)**

```bash
curl -i "localhost:8000/greeting"
# 400  {"code":"MISSING_LANGUAGE", ...}
```

⚠️ **The most important manual check in this document.** If this returns FastAPI's `422`
with a Pydantic validation body instead of `MISSING_LANGUAGE`, the implementation has
violated GRT-008 while looking superficially correct (research D1).

**Statelessness (GRT-006)**

```bash
curl "localhost:8000/greeting?language=fr&user_id=8842"
# identical to the plain fr request — the extra field is ignored
```

The service never identifies a user or looks anything up.

**Health (GRT-005)**

```bash
curl localhost:8000/health
# {"status":"healthy"}
```

Healthy only while a non-empty catalogue is loaded.

**Single interface (GRT-003)**

Everything above goes through one documented endpoint. No caller needs a private variant.

---

## Validation checklist

| Criterion | Check | Automated by |
|-----------|-------|--------------|
| GRT-001 | Supported language returns that language | `tests/test_greeting.py` |
| GRT-002 | Identical text across callers | `tests/test_greeting.py` |
| GRT-003 | One interface serves all callers | `tests/test_contract.py` |
| GRT-004 | `UNSUPPORTED_LANGUAGE`, no greeting body | `tests/test_errors.py` |
| GRT-005 | Health reflects ability to serve | `tests/test_health.py` |
| GRT-006 | Language from request only | `tests/test_greeting.py` |
| GRT-007 | Exactly en, fr, de, es, ja | `tests/test_locales.py` |
| GRT-008 | `MISSING_LANGUAGE`, distinct from GRT-004 | `tests/test_errors.py` |

Done when both gates are green and every row above passes.
