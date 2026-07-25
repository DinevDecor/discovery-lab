# Deliverable 3 — Shared Component Inventory

Per `EXEC-009` Phase 1, applying the Anti-Abstraction Rule literally:
**"Every shared component must have evidence from at least two
independent implementations."** Each of the task's own "Possible
candidates" is assessed against `2-COMPARATIVE-MATRIX.md`. Verdicts
are `PROMOTE` (extract, evidenced by 2+ independent implementations,
purpose genuinely shared), `PROMOTE AS PATTERN, NOT SCHEMA` (the
*shape* is shared, the *content* is not — extract the idiom, not a
rigid data structure), `OPTIONAL LAYER` (real, evidenced by exactly
one sensor, but plausibly needed by a whole future *family* of
sensors — held for the framework as an available, not mandatory,
piece), or `DO NOT PROMOTE` (fewer than two independent implementations,
or the two things that look similar actually differ in purpose).

## PROMOTE

### Safety enforcement

**Evidence: 3 independent implementations, already converging.**
`observation-agent/tests/test_safety.py` (original), `headquarters/
tests/test_safety.py` (adapted from it, added the network-forbidden
check), `reality-sensor/tests/test_safety.py` (adapted from both,
added the same network-forbidden check for a *different* reason —
enforcing the capture/process split rather than the advisory-only
boundary). This is the single strongest case in the whole review: the
same detector design has now been hand-copied and adapted three times
without anyone being asked to unify it. That is exactly what "proven
common, not invented" looks like.

**What to extract**: the forbidden-pattern scanner, the write-mode-
`open()`/`.write_text()` detector, the allow-list mechanism, and the
self-check pattern (`test_forbidden_patterns_actually_detect_violations`)
— parameterized per sensor by its own `_FORBIDDEN_ANYWHERE` additions
and `_ALLOWED_WRITE_MODULES` set. **Not** a single hardcoded rule set —
each sensor still declares what it forbids and what it's allowed to
write.

### Configuration loading pattern

**Evidence: 3 independent implementations**, all using the identical
idiom (`@dataclass` + `json.loads`, no third-party dependency, no
dynamic discovery, "add a source by editing this file"). The *shape*
of what's configured differs completely (`RepoConfig` vs `SourceEntry`
vs `HeadquartersConfig`'s five `ArtifactRef`s) — what's shared is the
*mechanism*, not a schema.

**What to extract**: a small `load_json_config(path, factory)`-style
helper plus the documented convention itself (JSON not YAML, fixed
list not dynamic discovery). Each sensor keeps its own dataclasses.

### CLI entry-point shape

**Evidence: 3 independent implementations**, identical structure:
`run_<tool>.py` (a 10-line `sys.path` shim) → `cli.main(argv)` →
`argparse` → an orchestration function kept separate from argument
parsing and I/O, printing a short human-readable summary.

**What to extract**: the shim script template and the
`main(argv) -> int` / separate-orchestration-function convention as a
documented pattern. Not a shared `main()` implementation — each
sensor's orchestration is genuinely different (Observation Agent walks
repos; Reality Sensor loads-and-clusters captures).

## PROMOTE AS PATTERN, NOT SCHEMA

### Evidence-plus-citation structure

**Evidence: 2 independent implementations**, same purpose (structurally
separate "what was found and where" from "what it means") and same
shape (a small dataclass pairing a quoted fact with its provenance,
exposing a `.citation()` method) — but genuinely different fields
(`repo/file_path/line_number` vs `source_name/source_url/source_trust`),
because internal provenance and external provenance are not the same
kind of thing.

**What to extract**: the *principle*, stated as a Required Design
Constraint (see `1-FRAMEWORK-SPECIFICATION.md`) — every Finding's
evidence must be a list of small, individually-citable,
provenance-tagged records, never a blob of prose. **Not** a single
shared `Evidence` dataclass — forcing one would either lose fields one
domain needs or add fields the other domain doesn't, which is exactly
the "artificial abstraction" this task forbids.

### Report rendering pattern

**Evidence: 2 independent implementations**, same idiom (build a list
of Markdown lines, join with `\n`, section-by-section, timestamped
filename, written only inside the tool's own `reports/`) but
genuinely different section sets driven by genuinely different
schemas.

**What to extract**: small line-building helpers (a section header, a
bulleted evidence-citation block, an empty-section fallback like
`"None."`) as an optional utility module. Not a shared report
template — Deliverable 6 names the risk of trying to force one.

## OPTIONAL LAYER (evidenced by one sensor, needed by a whole future family)

### Trust Classification

**Evidence: 1 of 2 current implementations** (Reality Sensor only).
Does not currently meet the two-implementation bar on its own. **But**:
of `EXEC-009`'s own named future sensors — Research, Business, Public
Procurement, Regulations, Markets — every one of them observes
*external* evidence of variable reliability, exactly Reality Sensor's
situation, not Observation Agent's. Only the future Calendar/Personal
Operations sensor looks more like Observation Agent (internal,
deterministic, no "was this COMMUNITY-sourced" question). This is
strong *directional* evidence even though it isn't yet two independent
sensor implementations.

**Recommendation**: make Trust Classification an available, documented,
**optional** framework module — built once, from Reality Sensor's own
`trust.py`, offered to every future sensor, required by none. Do not
retrofit it onto Observation Agent, which has no use for it (see
`5-MIGRATION-PLAN.md`).

### Duplicate Detection

**Evidence: 1 of 2 current implementations** (Reality Sensor only),
for the same underlying reason: only a sensor whose capture step can
produce multiple raw units describing one real event needs clustering
at all. Observation Agent's checks are, by construction, incapable of
producing that situation.

**Recommendation**: same treatment as Trust Classification — an
optional module, offered not mandated, built from `reality-sensor/src/
reality_sensor/dedup.py`'s own clustering algorithm (category +
keyword-overlap, transitive), generalized only to the extent of
letting a sensor supply its own "do these two raw units describe the
same event" predicate.

### Persistent, ID-based Signal Registry

**Evidence: 1 of 2 sensor implementations** (Reality Sensor), though
the *pattern itself* is evidenced by a second, non-sensor system:
`headquarters/src/headquarters/recommendation.py`'s `HQ-000N` design,
which Reality Sensor's `RS-000N` design deliberately mirrors. This is
genuinely different from the other two "optional layer" items above —
it isn't evidenced by only one implementation, it's evidenced by two
*convergent, independently-arrived-at* implementations that simply
happen to be a sensor and its own executive-layer consumer rather than
two sensors. That is meaningfully stronger evidence than a single
implementation, even though it does not meet a strict "two sensors"
reading of the rule.

**Recommendation**: **promote conditionally.** Extract the pattern (a
content-derived `key`, ID reuse by key match, `times_seen`/`first_seen`/
`last_seen` bookkeeping, monotonic confidence, evidence-never-shrinks)
as an available module for any sensor that needs durable cross-run
identity — most future external/evidentiary sensors will. Do **not**
present this as replacing Observation Agent's own ephemeral diff
model, which solves a different problem (what changed since the last
run of *this* tool) and works correctly for its own domain. The two
are not the same component wearing different names — see
`2-COMPARATIVE-MATRIX.md`'s "cross-run identity" row.

## DO NOT PROMOTE

### A single unified Signal/Finding schema

**Evidence: 2 implementations, but purpose-divergent beyond a small
common core.** `Observation` (8 fields, no persistent identity) and
`Signal` (13 fields, persistent identity, trust, urgency, relevance)
share a recognizable core — an event/capability description, an
evidence list, a confidence value, a recommended action — but Signal's
remaining fields exist *because* Reality Sensor's domain needs them,
not because Observation Agent was arbitrarily built smaller. Forcing
one 13-field schema onto Observation Agent would add meaningless
fields (`source_trust`, `affected_projects`, `urgency`) to a tool whose
domain has no use for them — the literal definition of "artificial
abstraction" this task forbids.

**What to do instead**: document the small common core (see
`1-FRAMEWORK-SPECIFICATION.md`'s "Core Finding" section) as a
convention every sensor's own richer schema should be a superset of —
not a shared dataclass either sensor imports.

### Relevance gating

**Evidence: 1 of 2 implementations**, and unlike Trust Classification/
Deduplication, there is no clear future-family argument yet — some
future sensors (Business, Markets) will plausibly need something like
it; others (Regulations, a hypothetical internal Calendar sensor)
plausibly won't, and it's not yet clear the *shape* of relevance
gating (keyword-to-project matching) generalizes rather than needing
to be reinvented per domain (a Markets sensor's "relevance" question
looks nothing like a keyword match). Held back from even the optional-
layer tier pending a second real implementation.

### Capture itself

**Evidence: 2 implementations, but they are opposites by design**,
not two variations on a theme. Observation Agent's capture is
internal, synchronous, checked-in, and deterministic. Reality Sensor's
capture is external, asynchronous, deliberately *not* checked-in, and
non-deterministic. The one thing genuinely shared is the *boundary* —
a capture step exists, produces some enumerable set of raw evidentiary
units, and hands them to processing — which is exactly what the
Adapter Model already names as domain-specific, per `EXEC-009`'s own
text: "Every future sensor should implement only: domain-specific
capture..." Nothing here contradicts that; this entry exists so the
inventory states explicitly *why* capture is adapter-owned rather than
silently omitting it.
