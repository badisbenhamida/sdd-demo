# Phase 1 — Quickstart & Validation: Global Greeting Service

**Feature**: `specs/001-greeting-service` | **Date**: 2026-08-12 | **Plan**: [plan.md](./plan.md)

**Status**: Draft — supports a plan PENDING G2. **Nothing below runs yet**: `src/`, `tests/`, and `config/locales.yml` are created during implementation. This is the acceptance script the implementation must satisfy, written before the code exists (CLAUDE.md: test first).

---

## Prerequisites

Per CLAUDE.md, always use the repo's virtualenv — never the system Python.

```bash
# from the repository root
.venv/bin/python --version          # expect Python 3.12.x
```

If `.venv` is missing:

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
```

No new dependency is needed: FastAPI, PyYAML, uvicorn, httpx, and pytest are already pinned in `requirements.txt`.

---

## Run the service

```bash
.venv/bin/python -m uvicorn src.main:app --reload --port 8000
```

Interactive contract browsing (FastAPI serves this from the app itself): <http://127.0.0.1:8000/docs>. It should agree with [contracts/greeting-api.yaml](./contracts/greeting-api.yaml); a divergence means the code and the contract have drifted.

---

## Validation scenarios

Each scenario maps to criteria and mirrors an acceptance scenario in [spec.md](./spec.md). Field names come from the G2 decision recorded in [plan.md](./plan.md); shapes are defined in [data-model.md](./data-model.md).

### V-1 — Supported locale returns that language *(GRT-001, GRT-003)*

```bash
curl -s "localhost:8000/greeting?locale=fr-FR"
```

Expect HTTP 200, `locale` `"fr-FR"`, `fallback` `false`, and `message` the French text from `config/locales.yml`.

### V-2 — Same locale, same text for every caller *(GRT-004)*

```bash
curl -s "localhost:8000/greeting?locale=de-DE" > /tmp/a.json
curl -s "localhost:8000/greeting?locale=de-DE" > /tmp/b.json
diff /tmp/a.json /tmp/b.json && echo "identical"
```

Expect `identical`. Nothing in the request distinguishes one calling application from another, so this holds by construction — the test guards against a future change that introduces caller-specific behaviour.

### V-3 — No preference returns the default, and is not a fallback *(GRT-002)*

```bash
curl -s "localhost:8000/greeting"
```

Expect 200, `locale` `"en-US"`, `requested_locale` `"en-US"`, and **`fallback` `false`**. Reporting a fallback here would be wrong: the caller expressed no preference, so nothing was substituted against their wishes.

### V-4 — Case difference alone never causes a fallback *(GRT-009)*

```bash
curl -s "localhost:8000/greeting?locale=FR-fr"
```

Expect 200, `fallback` `false`, `locale` `"fr-FR"` (the configured spelling, not the caller's casing), `requested_locale` `"FR-fr"`.

### V-5 — Unsupported locale falls back, flagged *(GRT-005, GRT-006)*

```bash
curl -s -o /tmp/fb.json -w "%{http_code}\n" "localhost:8000/greeting?locale=pt-BR"
```

Expect **200**, not 4xx — the G1 ruling on AMB-001 makes an unsupported language a successful response. Body: `fallback` `true`, `locale` `"en-US"`, `requested_locale` `"pt-BR"`, `message` the default-language greeting. A caller must be able to detect the substitution from `fallback` alone, without reading `message`.

### V-6 — Health reflects loaded configuration *(GRT-007)*

```bash
curl -s -o /tmp/h.json -w "%{http_code}\n" localhost:8000/health
```

Expect **200**, `status` `"healthy"`, `locales_loaded` `4` (en-US, fr-FR, de-DE, ja-JP per the G1 ruling on AMB-002).

### V-7 — A running service with unloadable config is unhealthy *(GRT-008)*

The point of this scenario is that the process stays up and *says* it is unhealthy — a crash would make GRT-008 unobservable (see [research.md](./research.md) R-2).

```bash
mv config/locales.yml config/locales.yml.bak
.venv/bin/python -m uvicorn src.main:app --port 8001 &
sleep 2
curl -s -o /tmp/h2.json -w "%{http_code}\n" localhost:8001/health   # expect 503
curl -s -o /dev/null -w "%{http_code}\n" "localhost:8001/greeting"  # expect 503, NOT a greeting
kill %1
mv config/locales.yml.bak config/locales.yml
```

Expect 503 from both, `status` `"unhealthy"`, and a `detail` naming the cause. A greeting returned here would mean a hardcoded literal survived in `src/`, violating the config-exclusivity constraint (research.md R-4).

### V-8 — Adding a language needs no code change *(GRT-010, SC-005)*

Add one entry to `locales:` in `config/locales.yml`, restart, then request it. Expect 200 with the new text, `fallback` `false`, and `locales_loaded` incremented — with no file under `src/` modified.

---

## Gates

The three gates CI runs, in the order `.github/workflows/spec-drift.yml` runs them:

```bash
.venv/bin/python scripts/constitution_check.py      # Gate 0 — mirror matches memory/
.venv/bin/python scripts/spec_drift.py              # Gate 1 — criterion ⇄ test traceability
.venv/bin/python -m pytest tests/ -q                # Gate 2 — acceptance tests
```

**Expected today, pre-implementation**: Gate 0 passes. Gate 1 fails at 0/10 covered. Gate 2 collects nothing. That is the burndown baseline, not a defect.

**Expected when the feature is done**: all three pass, with Gate 1 reporting 10/10.

Per-criterion check during incremental work — a full Gate 1 run stays red while *other* criteria are uncovered, so judge a single task by:

```bash
.venv/bin/python scripts/spec_drift.py --criterion GRT-005
```

---

## Definition of done for this feature

Per CLAUDE.md, an implementation task is done when: pytest passes; `spec_drift.py --criterion GRT-###` exits 0 for each of the task's criteria; and the work is committed with the criterion ID in the message, leaving the tree clean. The feature is done when the **full** `spec_drift.py` run exits 0 — every one of GRT-001…GRT-010 covered by a test declaring `Implements: GRT-###`.
