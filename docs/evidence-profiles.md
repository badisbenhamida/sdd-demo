# Evidence profiles — one governance model, three enforcement forms

## The invariant

Every acceptance criterion (GRT-###) must have **linked, current
verification evidence** before it ships, and the check must be
**mechanical** — a query or a build, never someone's memory.

In custom development, evidence happens to be an annotated automated
test and the check happens to be CI failing a pull request. That is
one *profile* of the invariant, not the invariant itself. This
document defines the profiles for each delivery substrate so the same
governance model — same spec format, same criterion IDs, same gates
G1/G2/G3, same ambiguity log — runs across 100% of the portfolio, not
just the homegrown 20%.

What never changes across profiles:

- BRD → EARS spec with stable criterion IDs → ambiguity log → G1
- Plan → tasks (criterion-linked) → G2 → one-way sync to work items
- A named human owns every gate; evidence checks are mechanical
- The criterion corpus is versioned in git and accumulates as
  retrievable enterprise knowledge

What varies: what counts as *implementation*, what counts as
*evidence*, and where the *drift check* runs.

---

## Profile A — Git-native (custom development)

**Applies to:** homegrown apps, services, scripts, infra-as-code.

| Element | Form |
|---|---|
| Implementation | Source code in git |
| Evidence | Automated test annotated `Implements: GRT-###` |
| Drift check | `spec_drift.py` in CI; fails the PR |
| Enforcement point | Build Validation policy / required status check on `main` |
| Vendor drift | n/a (you own the whole stack) |

**Agent roles:** spec transformation, test-first implementation,
drift remediation.
**Reference:** this repository is the walking skeleton.

---

## Profile B — Metadata-as-code (Salesforce, ServiceNow, BTP-side SAP)

**Applies to:** SaaS platforms whose configuration is exportable as
versionable artifacts (SFDX metadata, ServiceNow update sets via CI/CD,
SAP BTP extensions via abapGit/gCTS).

| Element | Form |
|---|---|
| Implementation | Metadata + platform code (Apex, Flow, script includes) in git |
| Evidence | Platform tests annotated with criterion IDs (Apex tests; ATF tests in ServiceNow), plus metadata diff review against spec |
| Drift check | Same `spec_drift.py` pattern over the metadata repo's test tree; fails the PR |
| Enforcement point | Same branch policy / required check as Profile A |
| Vendor drift | Quarterly platform releases — see "Vendor-release regression" below |

**Delta from A:** nearly none — this is the strongest argument that
the model generalizes. Salesforce already *mandates* 75% Apex coverage;
this profile makes that coverage *mean something* by tying each test
to a business criterion.
**Agent roles:** everything in A, plus **fit/gap classification** —
see below.

---

## Profile C — Config-and-transport (SAP core, Oracle Fusion, Workday)

**Applies to:** platforms where implementation is configuration through
vendor UIs, moved by transports or setup migration, with little or no
git-visible surface.

| Element | Form |
|---|---|
| Implementation | Config changes, moved via transport / setup migration, annotated with criterion IDs in the transport description or change record |
| Evidence | Test cases in the test-management system (Xray, Zephyr, or equivalent), each carrying its criterion ID(s) in a designated field, with a current passing run |
| Drift check | A coverage **query**, not a build: "active criteria with no linked test case in state Passed for this release." Non-empty result blocks the release gate. |
| Enforcement point | Release/go-live checklist gate (change advisory step), executed as a saved query in the test-management system — mechanical, auditable, but human-actioned |
| Vendor drift | Quarterly vendor releases — primary risk surface; see below |

**Delta from A:** the check moves from per-PR to per-release, and from
CI-automatic to query-mechanical. That is a real weakening — name it
honestly — but it preserves the invariant: no criterion ships without
cited, current evidence, and the check is a query anyone can run, not
a person's recollection.
**Agent roles:** spec transformation and fit/gap as in B; plus
**generating test scripts from criteria** (the EARS form maps almost
1:1 to test-step language) and drafting release impact assessments.

---

## The fit/gap ruling (Profiles B and C)

SaaS delivery adds a decision custom dev doesn't have: for each
criterion, is fulfillment **native config**, **supported extension**,
or **customization**? This ruling drives most of the platform's
long-term cost and upgrade risk, and it is usually made implicitly by
whoever configures the screen.

Under this model it becomes explicit and governed:

- The agent drafts a fit/gap classification per criterion against the
  platform's documented capabilities, as an added column in the spec.
- Ambiguity-log entry type: "GRT-014 can be met natively at 90%
  (limitation: X) or fully via customization (upgrade risk: Y) —
  business ruling required."
- A human (platform architect + PO) rules at G1/G2. The ruling is
  recorded in the spec, permanently citable.

The classification column makes a portfolio-level question answerable
for the first time: "what fraction of our Salesforce criteria are
customizations, and which business requirements forced them?"

## Vendor-release regression (Profiles B and C)

In custom dev, drift means your spec and code diverged. In SaaS, the
vendor changes behavior *underneath unchanged configuration* every
quarter. The criterion corpus is the countermeasure:

- **The spec is the regression suite.** When a vendor release lands in
  sandbox, "what do we retest?" has a machine answer: the criteria
  list, filtered by the modules the release notes touch.
- The agent drafts the impact assessment: release notes × criterion
  corpus → candidate-impact list for human triage.
- Post-release, evidence must be *re-current*: Profile C's coverage
  query scopes to "passing run against release N+1," which mechanically
  forces the retest cycle.

This converts the corpus from a compliance artifact into an
operational asset with quarterly recurring value — often the fastest
path to buy-in from SaaS platform owners.

## Choosing a profile

Ask one question: **can the implementation live in git?**

- Fully → Profile A.
- As exportable metadata → Profile B.
- No (vendor UI + transports) → Profile C.

Hybrid programs (an SAP rollout with BTP extensions; Oracle with OIC
integrations) run two profiles side by side, one spec — the criterion
ID scheme is shared, so a single requirement fulfilled partly in
config and partly in an extension traces cleanly into both evidence
stores.

## Portfolio view

| | A: git-native | B: metadata-as-code | C: config-and-transport |
|---|---|---|---|
| Spec + gates G1–G3 | identical | identical | identical |
| Evidence | annotated tests | annotated platform tests | linked test cases (the test-management system (Xray, Zephyr, or equivalent)) |
| Drift check | CI fails PR | CI fails PR | query blocks release |
| Check cadence | per PR | per PR | per release |
| Fit/gap ruling | n/a | at G1/G2 | at G1/G2 |
| Vendor-release regression | n/a | quarterly, corpus-driven | quarterly, corpus-driven |

Rollout logic: pilot A (walking skeleton) and B (highest similarity,
mandatory test culture already in place) first; bring C onto the same
spec discipline immediately but let its evidence linkage mature through
the test-management system (Xray, Zephyr, or equivalent), which the organization already owns.
