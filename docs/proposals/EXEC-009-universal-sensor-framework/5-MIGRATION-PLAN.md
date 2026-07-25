# Deliverable 5 — Migration Plan

Per `EXEC-009`'s Compatibility Requirement ("Observation Agent and
Reality Sensor 001 must remain operational. Do not redesign them
merely for elegance… support incremental migration") and its
Explicitly Out of Scope list ("Do not… rewrite existing sensors;
migrate code"). **Nothing in this plan is executed by this task.**
This is the path a future, separately-authorized task would follow,
stage by stage, if the framework proposed in Deliverable 1 is
accepted.

## Stage 1 — Current (today, unchanged by `EXEC-009`)

`observation-agent/` and `reality-sensor/` remain exactly as merged
(`428e18f`/`12f82fd` and `acf281f` respectively). Both continue
operating under their own `CONTRACT.md`s. No framework code exists
yet. This stage is the baseline every later stage is measured against
for regression.

## Stage 2 — Framework Introduction

A new top-level package (name not decided here — out of scope) is
built containing **only** the four `PROMOTE`d components from
Deliverable 3: Safety enforcement, the config-loading helper, the CLI
shim/orchestration template, and the Markdown report-rendering
helpers. It has:

- its own tests, its own `CONTRACT.md`, its own safety self-check;
- **zero** required changes to `observation-agent/` or
  `reality-sensor/` — introduction alone changes nothing operational;
- a documented example showing how a *hypothetical* third sensor
  would consume it, without that third sensor actually being built
  (`EXEC-009` also excludes "add new sensors").

**Exit criterion for this stage**: the framework package exists,
passes its own tests, and neither existing sensor's behavior, tests,
or output has changed in any way. Verifiable by rerunning both
sensors' existing test suites unmodified and diffing their outputs
against Stage 1's.

## Stage 3 — Partial Adoption

Each existing sensor **optionally** and **independently** adopts
individual framework pieces, one at a time, each as its own small,
narrow, separately-authorized, separately-validated change — following
exactly the same discipline every prior narrow merge in this
engagement already used (isolated branch, isolated test run, explicit
human approval before merge). Candidate order, safest first:

1. **Safety module** — lowest risk, since both sensors' existing
   `test_safety.py` files are already near-identical to what the
   framework would provide; adopting it should be closer to a
   no-op refactor than a behavior change. Verify by confirming the
   framework's detector still catches the same self-check violations
   each sensor's own file already proves it catches.
2. **Config-loading helper** — low risk, mechanical, no schema change
   (each sensor keeps its own dataclasses; only the JSON-reading
   boilerplate moves).
3. **CLI shim/orchestration template** — low risk, mechanical.
4. **Report-rendering helpers** — slightly higher risk, since each
   sensor's report layout is bespoke; adopt only the line-building
   utilities, not a shared template, to avoid the exact false-
   abstraction Deliverable 3 warned against.

**Neither sensor is required to adopt anything it doesn't need.**
Observation Agent has no reason to ever adopt Trust Classification,
Deduplication, or the Signal Registry pattern — its own ephemeral diff
model is not a legacy artifact to be migrated away from, it is a
correct design for its own domain (see `1-FRAMEWORK-SPECIFICATION.md`).
Partial adoption may mean "adopted the Safety module, nothing else,
forever" for Observation Agent, and that is a success state, not an
incomplete one.

**Exit criterion for this stage**: each sensor that adopts anything
does so via its own isolated, tested, human-approved change; sensors
that adopt nothing remain fully supported.

## Stage 4 — Full Adoption (per sensor, not ecosystem-wide)

"Full" means a *given* sensor uses every framework layer relevant to
its own family (per `1-FRAMEWORK-SPECIFICATION.md`'s two-family
split) — not that every sensor uses every layer. For Reality Sensor,
full adoption would mean formally extracting its own `trust.py`/
`dedup.py`/`registry.py` designs into the framework's optional-layer
modules and re-pointing its own imports at them, with its own
behavior, schema, and test suite otherwise unchanged (a refactor of
*location*, not of *design*, since the framework's optional layers are
templated directly from Reality Sensor's own code per Deliverable 4).
For Observation Agent, full adoption may permanently mean only Stage
3's mechanical pieces — there is no "Trust Classification, Deduplication,
Signal Registry" stage for it to eventually reach, because its domain
never needed those things. This is Stage 4 correctly completing, not
Stage 4 stalling.

**Exit criterion**: a sensor's own `CONTRACT.md` explicitly lists which
framework layers it uses and why; the framework's own documentation
lists which sensors currently use which layer, so the "is this
component actually shared" question Deliverable 3 asks stays
answerable indefinitely, not just at design time.

## What makes this non-disruptive by construction

Every stage above is additive or optional; no stage requires deleting,
renaming, or behaviorally changing existing code as a precondition for
the next stage to begin. A future team could stop after Stage 2
(framework exists, nothing adopted it yet) or after adopting only the
Safety module in Stage 3, and both are coherent, supportable end
states — not a partially-completed migration in need of finishing.
This follows directly from Deliverable 3's own discipline: because
nothing was promoted without two-implementation evidence, nothing in
the framework requires an existing sensor to change in order to keep
working.
