# Architecture — Research Reality Sensor 001

`EXEC-010`'s implementation. Second member of the **External
Evidentiary Sensor** family `EXEC-009` established. Read this before
the source — it explains what is reused, how, and why nothing here
imports from `reality-sensor/`.

## Position in the ecosystem

```
Scientific Reality
      │
      ▼
Research Reality Sensor 001     (this package)
      │
      ▼
Research Signal Registry         research-sensor/reports/research-registry.json
      │
      ▼
Headquarters                      reads the registry as one more named
      │                           artifact, exactly like Observation
      │                           Agent's reports/ and Reality Sensor's
      │                           signal-registry.json - see
      │                           "Headquarters compatibility" below
      ▼
Human Decision
```

Same discipline as `reality-sensor/`: this sensor produces one durable
artifact plus two human-readable briefs, and stops. It never calls
Headquarters, never decides, never acts.

## What is reused, and how — per `EXEC-009`'s binding decision

Per Petko's "Human Acceptance — EXEC-009": *"The following shall be
treated as shared architectural patterns, not yet shared runtime
modules: safety enforcement; configuration loading; CLI/orchestration
shape; evidence and citation discipline; reporting conventions."* and
*"No universal sensor framework code shall be implemented at this
stage."*

Concretely, that means this package's `tests/test_safety.py`,
`src/research_sensor/config.py`, `src/research_sensor/cli.py`, the
evidence/citation shape, and `src/research_sensor/brief.py` are
**independently reimplemented here**, following the same idioms
`observation-agent/` and `reality-sensor/` already established — not
imported from either. This is a deliberate, visible act of following
`EXEC-009`'s own ruling, not an oversight: a fourth convergent
implementation of the same patterns is itself further evidence for
(or against) eventual extraction, exactly the kind of evidence
`EXEC-009`'s own Migration Plan named as one of its two triggers for
reconsidering code extraction.

## The capture/process split, restated for this domain

Same reasoning `reality-sensor/ARCHITECTURE.md` gives in full: this
sensor's checked-in source makes **zero** network calls (enforced by
`tests/test_safety.py`'s network-forbidden check, identical in kind to
`reality-sensor/`'s own). Capture — fetching real papers from arXiv,
OpenReview, Nature, Science, ACL, NeurIPS, ICML, ICLR, and official
research blogs — is a separate, executor-mediated step (performed here
via `WebSearch`/`WebFetch`, against the fixed Source Registry and a
fixed processing budget) that produces a raw-captures JSON file.
Processing that file is 100% deterministic, which is what makes "3
identical repeated executions" achievable at all.

## What's different from Reality Sensor 001 (domain-specific, not
## architectural)

- **Schema**: `ResearchSignal` (14 fields `EXEC-010` names explicitly,
  plus a `evidence` citation list for provenance and bookkeeping) is
  not `Signal` — different domain, different questions. See
  `docs/RESEARCH-SCHEMA.md`.
- **The central question is different, on purpose.** `EXEC-010`
  states it as the Most Important Rule: *"Why should Discovery Lab
  care?"*, not *"What does the paper say?"* — every accepted signal
  must name a concrete possible impact (`architectural_relevance` +
  `possible_experiments`), or the paper is `WATCH`. Reality Sensor 001
  has no equivalent "so what" requirement this strict; it reports
  capability changes, not opportunity judgments.
- **Experiment Extraction** (`experiments.py`) has no analogue in
  Reality Sensor 001 at all — for every accepted, non-`WATCH` signal,
  at least one possible experiment must be structurally present, each
  with expected benefit, uncertainty, prerequisites, and a validation
  idea. `EXEC-010` is explicit that this is a **research opportunity**,
  never an implementation plan — `experiments.py` structurally cannot
  produce anything resembling a task list or code plan; see
  `docs/EXPERIMENT-EXTRACTION-POLICY.md`.
- **Trust Policy is publication-tier-based, not source-name-based.**
  `evidence_level` (peer-reviewed venue, notable-lab preprint, general
  preprint, community hint) drives confidence — "Confidence depends
  on... publication quality, peer review status, independent
  replication, evidence strength. Never on popularity." Community
  sources are explicitly *"only as discovery hints"* — a raw capture
  whose only evidence is `COMMUNITY` can never, by itself, produce an
  accepted signal (stricter than Reality Sensor 001's "never `HIGH`
  from `COMMUNITY` alone" — here it's "never accepted at all from
  `COMMUNITY` alone", forced to `WATCH`). See `docs/TRUST-POLICY.md`.
- **Duplicate Policy is idea-based, not event-based.** `EXEC-010`:
  "One research idea -> One research signal. Multiple papers
  supporting the same idea become supporting evidence." Clustering
  here groups papers making the *same underlying claim or proposing
  the same kind of method*, not papers reporting the *same event* (a
  release). The clustering predicate differs from Reality Sensor 001's
  accordingly — see `dedup.py`.

## Package layout

```
config/source-registry.json    -> PRIMARY (arXiv, OpenReview, Nature,
                                   Science, ACL, NeurIPS, ICML, ICLR),
                                   SECONDARY (official research blogs,
                                   lab publications), COMMUNITY
                                   (discovery-hint only) sources
config/relevance-gate.json     -> keyword -> project mapping, tailored
                                   to research domains A-E
src/research_sensor/
  models.py       -> ResearchSignal, Citation, PossibleExperiment,
                      RawPaperCapture; EvidenceLevel/Domain/Confidence/
                      Project closed vocabularies
  config.py       -> loads source-registry.json + relevance-gate.json
                      (independently reimplemented pattern)
  trust.py        -> evidence_level -> confidence policy; enforces
                      "never accepted from COMMUNITY alone"
  relevance.py    -> gates against the 5 named projects, or WATCH
  dedup.py         -> clusters papers proposing the same research idea
  experiments.py   -> validates/builds the possible_experiments
                       structure for accepted (non-WATCH) signals
  registry.py      -> idempotent RES-000N persistent IDs (same
                       reuse-by-key pattern as RS-000N/HQ-000N,
                       independently reimplemented)
  brief.py         -> Daily Research Brief + Weekly Research
                       Intelligence Report
  cli.py           -> orchestrates one execution (independently
                       reimplemented pattern)
run_research_sensor.py          -> convenience entry point
tests/                           -> see docs/VALIDATION-REPORT.md
docs/
  RESEARCH-SCHEMA.md
  TRUST-POLICY.md
  EXPERIMENT-EXTRACTION-POLICY.md
  SOURCE-REGISTRY.md
  VALIDATION-REPORT.md
  KNOWN-LIMITATIONS.md
validation-dataset/              -> fixed, committed raw-captures file,
                                     last 30 days
reports/                         -> this tool's own output only,
                                     enforced by tests/test_safety.py
```

## Headquarters compatibility

`research-registry.json` is a flat JSON list, same tolerant-read
contract Reality Sensor 001's `signal-registry.json` already
satisfies for `headquarters/src/headquarters/collector.py`'s reading
style. `EXEC-010` additionally names that "Headquarters may surface:
Top Research Opportunity. No automatic prioritization." — read
literally, that means Headquarters, if and when it is separately
extended to consume this registry, may *display* whichever entry a
human or Headquarters' own existing Attention Engine rubric already
ranks highest; this sensor never pre-selects one "top" signal itself
the way Reality Sensor 001's `WATCH`/non-`WATCH` split does not imply
ranking either. Not wired into `collector.py` in this task — same
"structurally proven, not integrated" boundary `EXEC-008` drew, and
`EXEC-009` did not ask to change.

## What this is not

Per `EXEC-010`'s own Explicitly Out of Scope: no automatic literature
review; no autonomous hypothesis generation; no implementation
suggestions; no code generation; no paper ranking by citations; no
decision making. This sensor identifies *that* a research opportunity
might exist and cites *why*, evidenced — nothing more.
