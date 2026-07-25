# Deliverable 4 — Adapter Contract

Per `EXEC-009`'s Adapter Model: "Every future sensor should implement
only: domain-specific capture, domain-specific parsing, domain-specific
relevance rules. Everything else should reuse the framework." Deliverable
3 found that of these three, only the first two are evidenced as
universal; relevance rules are Reality-Sensor-specific and not yet
promoted even to optional-layer status. This contract reflects that
finding rather than restating the task's own draft unchanged.

## What every sensor MUST implement itself

### 1. Capture

A domain-specific procedure — not necessarily Python code inside the
sensor's own package, per the precedent both existing sensors already
set differently (Observation Agent: `scanner.py`, checked-in;
Reality Sensor: executor-mediated `WebFetch`/`WebSearch`, deliberately
outside the package) — that produces an enumerable list of **Raw
Units**, each carrying at minimum:

- a source identifier (what produced this unit — a file path, a URL,
  an API response, whatever the domain's own concept of "source" is);
- a timestamp (when this was captured, not necessarily when the
  underlying event happened);
- enough raw content that Normalization (below) can build evidence
  from it without re-contacting the source.

The framework does not specify a single `RawUnit` dataclass — it
specifies this minimum shape as a contract every sensor's own capture
step must satisfy, the same way `reality-sensor/docs/SIGNAL-SCHEMA.md`
documents `RawCapture`'s shape today without that shape being imported
anywhere outside `reality-sensor/`.

### 2. Normalization (domain parsing)

A domain-specific transform from Raw Units to the sensor's own Finding
schema. This is where a sensor's actual "understanding" of its domain
lives: Observation Agent's five `check_*` functions; Reality Sensor's
`registry.build_signal`. The framework does not and cannot provide
this — it is the reason the sensor exists.

**Contract**: whatever the sensor's own Finding schema looks like, it
must be a superset of the Core Finding fields (see below), and every
Finding's supporting evidence must satisfy the Evidence Provenance
constraint from `1-FRAMEWORK-SPECIFICATION.md`.

### Core Finding — the minimum every sensor's own schema must extend

Drawn from the genuine overlap `3-SHARED-COMPONENT-INVENTORY.md` found
between `Observation` and `Signal`, not invented:

| Field | Present in Observation Agent as | Present in Reality Sensor as |
|---|---|---|
| A description of what was found | `event` | `affected_capability` + `summary` |
| Supporting evidence (list of provenance-tagged records) | `evidence` | `evidence` |
| A confidence value (vocabulary is domain-owned — see below) | `confidence` | `confidence` |
| A recommended action (always advisory) | `recommended_action` | `recommended_action` |
| Whether a human needs to look at this | `human_needed` (bool) | implied by every Signal being human-reviewed; not a literal field today — a documented gap, not a contradiction |

**Confidence vocabulary is explicitly NOT unified.** Observation
Agent's `MATCH`/`MISMATCH`/`INSUFFICIENT_EVIDENCE` answers "did the
file's own claim match reality?"; Reality Sensor's `HIGH`/`MEDIUM`/
`LOW`/`INSUFFICIENT_EVIDENCE` answers "how much should this be
believed?" These are different questions. A sensor picks whichever
vocabulary fits the question its domain actually asks, or defines a
third one, as long as it includes some explicit "not enough evidence"
value — the one convention worth mandating, since every existing
sensor and Headquarters itself already converge on exactly that
discipline independently.

## What every sensor MAY implement itself (optional layers)

Per `1-FRAMEWORK-SPECIFICATION.md`'s two-family split, a sensor
declares in its own `CONTRACT.md` which of these it uses:

- **Trust Classification** — if the domain has evidence of varying
  reliability. Reuse `reality-sensor/src/reality_sensor/trust.py`'s
  design (a closed trust-level vocabulary + a pure function from
  evidence trust levels to confidence) as the template; the actual
  trust levels and the confidence-capping rule are domain decisions.
- **Deduplication** — if capture can plausibly yield more than one raw
  unit describing the same real event. Reuse `reality-sensor/src/
  reality_sensor/dedup.py`'s clustering algorithm (a same-event
  predicate + transitive union-find) as the template; the predicate
  itself is domain-owned.
- **Signal Registry** — if the domain benefits from persistent,
  cross-run identity for a recurring finding. Reuse the `RS-000N`/
  `HQ-000N` pattern (content-derived key, ID reuse by key match,
  `times_seen`/`first_seen`/`last_seen`, evidence that only grows,
  confidence that never silently downgrades) as the template.
  Observation Agent's own ephemeral per-run diff is an equally valid
  alternative for a sensor whose domain doesn't need durable identity
  — not a fallback to be migrated away from.
- **Relevance gating** — held back even from "reusable template"
  status pending a second real implementation (see Deliverable 3);
  a future sensor needing something like it should treat Reality
  Sensor's `relevance.py` as prior art to consult, not a module to
  import.

## What every sensor gets from the framework without writing it

Per Deliverable 3's `PROMOTE` list: the Safety enforcement module
(configured per-sensor with its own forbidden-pattern additions and
write-allow-list), the JSON-config-loading helper, the CLI shim/
orchestration-separation template, and small Markdown report-rendering
helpers. None of these encode domain knowledge; all three were
independently reinvented at least twice before this task named them,
which is the entire evidentiary basis for offering them centrally now.

## What no sensor may ever do, framework or not

Restated because it is not negotiable and does not vary by adapter:
no sensor writes outside its own `reports/` directory; no sensor
invokes `subprocess`, deletes, commits, pushes, or merges anything; no
sensor's `recommended_action` (or equivalent) is ever executed by
anything downstream automatically; no sensor bypasses Headquarters.
