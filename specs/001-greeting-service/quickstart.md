# Phase 1 — Quickstart: validating the Global Greeting Service

**Feature**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)
**Contract**: [contracts/greeting-api.yaml](./contracts/greeting-api.yaml)
**Date**: 2026-08-12

How to prove the six approved criteria hold, once implementation exists.
This is a validation guide, not implementation: no source, no test
bodies. Those belong to `tasks.md` and the implementation phase.

**Nothing here runs yet.** `src/`, `tests/`, and `config/locales.yml` are
all created during implementation, which is blocked on G2.

---

## Prerequisites

```bash
# From the repository root. Per CLAUDE.md, always use .venv — never system Python.
python3 -m venv .venv                       # only if .venv is absent
.venv/bin/pip install -r requirements.txt
```

`requirements.txt` already carries fastapi, pyyaml, uvicorn, httpx and
pytest. This feature adds no dependency.

---

## The mechanical gate (what CI actually checks)

Two commands, in the order `.github/workflows/spec-drift.yml` runs them.
Both must pass before the feature can merge.

```bash
# Gate 1 — every criterion has a test declaring `Implements: GRT-###`
.venv/bin/python scripts/spec_drift.py

# Gate 2 — those tests pass
.venv/bin/python -m pytest tests/ -q
```

**Expected before implementation** (today): Gate 1 exits 1 with
`Criteria: 6 active, 0 retired / Covered: 0/6`. That is the gate working,
not a defect — it is asserting that no criterion has shipped without
evidence.

**Expected when the feature is done**: `Covered: 6/6`, `PASS: spec and
tests agree`, and pytest green. Anything less is unfinished work, not a
tuning problem.

---

## Running the service by hand

```bash
.venv/bin/uvicorn src.main:app --reload
```

Then exercise the three greeting paths and the health path. Expected
responses are defined in the contract; the table below is the short form.

| # | Command | Expect | Criterion |
|---|---|---|---|
| 1 | `curl -s 'localhost:8000/greeting?lang=fr'` | 200, text in `fr`, `fallback: false` | GRT-001 |
| 2 | `curl -s 'localhost:8000/greeting'` | 200, English text, `language: "en"`, `requested_language: null` | GRT-002 |
| 3 | `curl -s 'localhost:8000/greeting?lang=xx'` | 200, English text, `requested_language: "xx"`, `fallback: true` | GRT-005 |
| 4 | `curl -s 'localhost:8000/health'` | 200, `{"status": "ok"}` | GRT-006 |

Substitute a language that is actually configured for step 1 — the
supported set is business-owned configuration (AMB-001), not fixed here.

**Step 3 is the one to look at closely.** It returns **200**, not 400. A
fallback is a successful request that happens to note a gap, per the G1
ruling on AMB-003. If you get a 4xx there, the implementation has
diverged from the approved spec — see the divergence note in plan.md
before "fixing" the test.

---

## Validating the criteria that curl cannot show you

Two criteria are claims about the system as a whole, not about a single
response.

**GRT-004 — identical text for every caller.** No single request proves
this. Call the same language repeatedly, and from different clients, and
compare bytes:

```bash
for i in 1 2 3; do curl -s 'localhost:8000/greeting?lang=fr' | shasum; done
# expect three identical digests
```

Structurally this holds because the model carries no caller identity at
all and the locale table is immutable for the process lifetime
(data-model.md, research R-4). The check above confirms the property; the
design is what guarantees it.

**GRT-003 — a single interface.** This is a negative claim: that no
second, per-region interface exists. The served route set should contain
exactly `/greeting` and `/health`:

```bash
curl -s localhost:8000/openapi.json | .venv/bin/python -m json.tool | grep -E '^\s+"/' 
```

A test can assert today's route set, but only a reviewer stops a second
interface being added later. Stated plainly in plan.md's Test Strategy.

---

## Validating the failure path

The one case operations actually cares about, and the easiest to skip:

```bash
mv config/locales.yml config/locales.yml.bak
.venv/bin/uvicorn src.main:app          # restart
curl -s -o /dev/null -w '%{http_code}\n' localhost:8000/health    # expect 503
curl -s -o /dev/null -w '%{http_code}\n' localhost:8000/greeting  # expect 503
mv config/locales.yml.bak config/locales.yml                      # restore
```

The service must **not** serve a greeting here. There is no in-code
default text by design (research R-6) — if you see "Hello" come back with
the config file moved aside, greeting text has leaked into source and
both the exclusive-config constraint and GRT-004 are broken.

---

## Definition of done for this feature

Straight from CLAUDE.md, plus this feature's gates:

- [ ] `.venv/bin/python -m pytest tests/ -q` passes
- [ ] `.venv/bin/python scripts/spec_drift.py` reports 6/6 covered
- [ ] Every commit cites its criterion ID
- [ ] Working tree clean; nothing left uncommitted
- [x] G2 — tech lead approved this plan (Art. III.2) — Dana, 2026-08-12
- [ ] G3 — human review under branch protection; the agent does not merge (Art. III.3)
