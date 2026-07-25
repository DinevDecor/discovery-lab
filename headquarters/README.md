# Ecosystem Headquarters v1.0

`EXEC-004`'s implementation: the ecosystem's strategic interpreter.
Headquarters reads what already exists — Observation Agent reports,
the Recommendation Ledger, project state files, ADR directories, the
project registry, the governance document, and `docs/proposals/` — and
turns it into one thing: **the single highest-value next action, with
its reasoning shown**. It is advisory only. It observes, understands,
prioritizes, explains, and recommends; it never executes, never
modifies a repository, and never self-approves anything. See
`CONTRACT.md`.

## Architecture

```
collector.py     -> reads existing artifacts (no repository scanning of its own)
drift.py         -> Strategic Drift Detector (6 mechanical checks)
opportunity.py   -> Opportunity Detector (3 DRAFT-only heuristics, generically discovered)
inconsistency.py -> classifies every Drift finding into one of 5 taxonomy categories
health.py        -> Ecosystem Health Engine (8 documented metrics)
portfolio.py     -> Portfolio Engine (one entry per configured repo)
prioritizer.py   -> Attention Engine (selects exactly one recommendation)
recommendation.py-> HQ-000N traceability + Recommendation Evaluation
history.py       -> run-over-run trend detection
brief.py         -> Executive Brief renderer
cli.py           -> orchestrates one full execution
```

Each module has one job and depends only on the ones above it in this
list — `drift.py` and `opportunity.py` never import `prioritizer.py`,
`prioritizer.py` never imports `brief.py`, and so on. `collector.py` is
the only module that touches a filesystem path outside this tool's own
`reports/` directory, and every path it opens is a specific,
pre-configured artifact — never an open-ended directory walk.

### Why this shape and not the ten suggested modules

EXEC-004 suggested a `Collector` / `Portfolio Engine` / `Health Engine`
/ `Drift Detector` / `Opportunity Detector` / `Prioritizer` /
`Recommendation Engine` / `Executive Brief Generator` / `History
Manager` split. This implementation follows that shape closely
(`Recommendation Engine` and the traceability half of Section 8 live
together in `recommendation.py`, since they share the same persistent
log) rather than inventing an alternative — the suggested split
already matches this tool's actual responsibilities well.

## How to run it

```
cd headquarters
python3 run_headquarters.py
```

No dependencies beyond the Python 3 standard library (same constraint
observation-agent works under — no PyYAML). Optional flags:

```
python3 run_headquarters.py --config path/to/config.json --reports-dir path/to/reports
```

Each run writes exactly three files, all inside `reports/`:
`executive-brief-<timestamp>.md`, `recommendation-log.json` (persistent
`HQ-000N` traceability, overwritten with the latest state each run —
existing IDs are reused, not reassigned), and `history.json` (the last
90 runs' headline numbers, for trend detection).

## What it consumes

| Input | Source | Used for |
|---|---|---|
| State files | each configured repo's own state file (3 different real formats — see `parsing.py`) | Portfolio current state, trend, last progress |
| Observation Agent's latest report + execution log | `observation-agent/reports/` | Observation Cleanliness, Observation Coverage, Human Decisions Required |
| Recommendation Ledger | `docs/investigations/RECOMMENDATION-LEDGER.md` | Recommendation Backlog, Decision Backlog, Decision Currency, ledger-derived candidates |
| Project Registry | `project-memory/PROJECT_REGISTRY.md` | Registry-gap drift findings |
| ADR directories | each configured repo's own ADR directory listing | Duplicate-ID and staleness drift findings |
| `docs/proposals/` | discovery-lab | Possibly-abandoned-initiative drift findings |
| README purpose paragraph, CHANGELOG line count | each configured repo | Portfolio purpose field, changelog-size opportunity |

Headquarters never re-walks a repository the way observation-agent
does — every one of the paths above is a specific, named artifact
location, configured once in `config.json`, read directly.

## Inconsistency Classification

Per the Additional Execution Directive, Headquarters adapts to the
ecosystem — it does not reshape the ecosystem to satisfy itself.
Whenever a Drift check surfaces a real inconsistency, `inconsistency.py`
records and classifies it rather than silently fixing anything (nothing
in this tool has write access to any observed repository regardless).
Every classified inconsistency carries all four required fields —
affected artifact, observed evidence, operational impact, recommended
future action — plus the rationale for its category assignment, and
appears in the Executive Brief's own "Inconsistencies" section.

Five categories, one fixed mapping from each Drift check (made once,
documented, not re-derived per run):

| Category | Populated by |
|---|---|
| Governance Issue | duplicate ADR IDs, registry gaps, decision backlog |
| Documentation Issue | stale ADRs |
| Data Quality Issue | a configured state file that exists but doesn't parse into a meaningful shape |
| Unknown | possibly-abandoned proposals (genuinely ambiguous from the available signal) |
| Implementation Issue | *no v1.0 check maps here* — reserved for a future check comparing documented capability against actual implementation status; not fabricated to fill the category |

Opportunities are never classified as inconsistencies — they are
positive, optional suggestions, not problems (see `inconsistency.py`'s
`classify_all`, which only ever processes Drift findings).

If a run has no Ledger entry, Drift finding, or Opportunity to
recommend from, the Executive Brief's "Most Important Recommendation"
section says exactly **`INSUFFICIENT EVIDENCE`**, per the Design
Philosophy — Headquarters never invents an assumption to fill an
evidence gap.

## Extensibility (Robustness Requirement)

New repositories, agents, registries, and documents should be
discoverable with minimal changes to this tool:

- **New repository**: add one entry to `config.json`'s `repos` list.
  Every module (`portfolio.py`, `health.py`, all 6 `drift.py` checks)
  already iterates the configured repo list generically — no code
  change is needed for the new repo to appear in the Portfolio, Health
  metrics, or any Drift check.
- **New registry file, in a repo already configured**: nothing to do.
  `opportunity.py`'s `discover_registry_files` finds any `*.md` file
  whose name contains "registry" (case-insensitive) via a bounded,
  shallow, excluded-dir-aware walk — it no longer hard-codes a
  per-repo file list.
- **New tool with its own safety scanner**: nothing to do.
  `discover_safety_scanners` matches any `<tool>/tests/test_safety.py`
  found under a configured repo's top-level subdirectories, without
  naming `observation-agent` or `headquarters` specifically.
- **New artifact type entirely** (a new kind of registry, a new
  governance document shape): requires a code change — this tool
  cannot discover a *shape* of artifact it has never been told to look
  for, only new *instances* of shapes it already knows. That is a
  real, honest limit, not a gap this README papers over.

Both generic discovery functions are still bounded and narrow —
filename-pattern matching within a depth limit, never reading or
interpreting file content — which keeps them distinct from
Observation Agent's own deep content-scanning checks (broken links,
orphan files, etc.). Extensibility here means "less hard-coded
per-repo knowledge," not "Headquarters starts scanning repository
content the way Observation Agent does."

## The Attention Engine

Every run assembles a candidate pool from three sources: the
Recommendation Ledger's `PROPOSED` entries, this run's Drift findings,
and this run's Opportunities. Each candidate gets one score from a
fully transparent, documented rubric (see `prioritizer.py`'s
`score()`):

- `+3` if the evidence is `MISMATCH`-confidence (mechanically
  confirmed), `+1` if `INSUFFICIENT_EVIDENCE` (a real signal, not yet
  confirmed), `+0` for a DRAFT opportunity.
- `+2` if resolving it is small and mechanical (a pending decision, a
  duplicate-ID fix) — this is where the guiding principle is
  operationalized: *finishing* scores a real bonus.
- `+2` if it unblocks the Recommendation Ledger's own
  `acceptance_rate` metric.
- `+1` per distinct repository affected, capped at `+2`.
- `-1` if it is an opportunity — starting something new is actively
  deprioritized relative to finishing something already in flight.

The highest-scoring candidate is selected; ties break on the
candidate's own stable key, so a rerun over unchanged evidence always
picks the same one. Every other candidate is still listed in the brief
("Other Candidates Considered"), explicitly *not* as a second priority
list — EXEC-004's "never Top 10" rule is enforced by construction:
`brief.py` only ever renders one recommendation under "Most Important
Recommendation."

## Safety guarantees

Headquarters is read-only, the same way observation-agent is: it does
not commit, push, merge, edit, rewrite, or delete anything in any
observed repository, does not touch the network (no GitHub API, no
HTTP), and only ever writes the three files above, inside its own
`reports/` directory.

Enforced, not just documented: `tests/test_safety.py` statically scans
every source file for the same forbidden-pattern list
observation-agent's own safety test uses (`subprocess.`, `os.remove(`,
`.commit(`, `.push(`, `.merge(`, etc., plus a Headquarters-specific
check that no source file references an HTTP client library), and
restricts writing-mode file opens to the three modules that legitimately
write this tool's own output (`cli.py`, `recommendation.py`,
`history.py`).

## Limitations

- **Dependencies** are always reported `INSUFFICIENT_EVIDENCE` in the
  Portfolio — v1.0 does not parse a cross-repository dependency graph.
  A future version could derive this from ADR content or explicit
  config, but nothing here fabricates a relationship.
- **Drift Detection** implements 5 of the 10 categories EXEC-004 names
  (duplicate ADR IDs, stale ADRs, registry gaps, decision backlog,
  possibly-abandoned proposals), plus a sixth check
  (`unparseable_state_files`) added to give the Inconsistency
  taxonomy's Data Quality Issue category real coverage. Overlapping
  projects, execution-without-specification,
  specification-without-execution, and architectural contradictions
  are not attempted — each would require semantic judgment across
  free-text documents this tool has no honest way to automate yet.
- **Health metrics are simple, stated formulas**, not a validated
  model. `Overall Health`'s 71% (as of this task's own real run) means
  exactly what its formula says and nothing more — it is not a
  claim about the ecosystem's real health beyond what four
  mechanically-computed sub-scores capture.
- **Self-review problem**, same as every tool in this session: built
  and evaluated by the same kind of agent it reports on. Disclosed,
  not solved.
- **Recommendation Evaluation** (EXEC-004 §8) can only report real
  numbers once a human has actually recorded decisions in
  `reports/recommendation-decisions.json` — until then it honestly
  reports `INSUFFICIENT_EVIDENCE`, not a fabricated score.
- **Opportunity Detector** ships 3 heuristics, not an open-ended list —
  each was chosen because it is mechanically verifiable (a bounded
  filename-pattern discovery finding 2+ matches, a line count), not
  because it is the most valuable opportunity the ecosystem might
  have.
- **Generic discovery is filename-pattern matching only.** A registry
  or safety scanner that doesn't follow the naming conventions
  `discover_registry_files`/`discover_safety_scanners` look for (a
  `.md` file with "registry" in its name; a `tests/test_safety.py`
  path) will not be found. This is a real, stated boundary of the
  Robustness Requirement's implementation, not a claim of unlimited
  discovery.

## Future evolution

- A dependency-graph parser (from ADR content or explicit
  configuration) to fill in the Portfolio's `Dependencies` field
  honestly.
- The remaining five Drift categories, once a defensible mechanical
  (or explicitly-scoped semi-manual) check exists for each.
- `reports/recommendation-decisions.json` accumulating real decisions
  over multiple runs, so Recommendation Evaluation can start reporting
  a real accepted/implemented/useful/obsolete/incorrect breakdown
  instead of `INSUFFICIENT_EVIDENCE`.
- The shared-safety-scanner opportunity this run's own Opportunity
  Detector found (`observation-agent/tests/test_safety.py` and
  `headquarters/tests/test_safety.py` duplicate the same detector) is
  a legitimate, self-referential candidate for a future run to surface
  again until someone acts on it.

## Provenance

Implements `EXEC-004 — Ecosystem Headquarters v1.0`, consuming
`observation-agent`'s output (`EXEC-002`/`EXEC-003`) directly rather
than duplicating its repository scanning, plus EXEC-004's Additional
Execution Directive (Inconsistency Classification, the Robustness
Requirement's extensibility approach, and the explicit
`INSUFFICIENT EVIDENCE` reporting discipline). See `CONTRACT.md` for
the tool's operating contract.
