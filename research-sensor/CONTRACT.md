# Contract — Research Reality Sensor 001 (`research-sensor/`)

Version: **v0.1** (implements `EXEC-010`)
Core Principle: **Detect research opportunities. Cite evidence. Never
decide, never act, never generate an implementation plan.**

This is a **tool contract**, not an Employee Role contract — same
precedent as `reality-sensor/CONTRACT.md`, `headquarters/CONTRACT.md`,
and `observation-agent/CONTRACT.md`. `EXEC-010` did not ask for a new
Employee ID or the full `docs/ai-organization/employees/` document set,
so this deliberately does not instantiate one.

## Scope of authority

Read-only processing of a raw-captures file supplied by whoever invokes
this tool (a human, or an AI executor acting under explicit human task
authorization — see `ARCHITECTURE.md` for why capture and processing
are separate steps). No authority beyond producing a Research Signal
Registry and two human-readable briefs, all inside this package's own
`reports/` directory, is granted under any circumstance.

## Position in the ecosystem

`Scientific Reality -> Research Reality Sensor 001 -> Research Signal
Registry -> Headquarters -> Human Decision`. This sensor never bypasses
Headquarters — it produces one artifact and stops. It does not call
Headquarters, does not import any Headquarters module, and does not
know Headquarters exists at runtime.

## Rights

- The right to report `INSUFFICIENT_EVIDENCE` confidence, or to refuse
  to register a signal at all (`COMMUNITY_HINT`-only clusters), without
  this being treated as a defect.
- The right to report `WATCH` for `affected_projects` whenever no
  configured project plausibly benefits — `EXEC-010`'s own "do not
  force relevance" instruction.
- The right to report an empty `possible_experiments` list for any
  signal that is not high-value (per `docs/EXPERIMENT-EXTRACTION-POLICY.md`),
  rather than inventing a weak experiment to fill the field.
- The right to have any signal, trust classification, or confidence
  score disputed or corrected by a human without that requiring a
  change to this contract.

## Responsibilities

- Every registered `ResearchSignal` must carry all 14 fields
  `EXEC-010`'s Research Signal Model names — see
  `docs/RESEARCH-SCHEMA.md`.
- Every registered signal must cite at least one piece of evidence with
  a real `source_url` and `quoted_abstract` — never fabricated.
- Never register a signal from `COMMUNITY_HINT`-only evidence — see
  `docs/TRUST-POLICY.md`.
- Keep FACT/CLAIM/EVIDENCE (`problem_addressed`, `main_contribution`,
  `evidence`) structurally separate from INTERPRETATION/ACTION
  (`architectural_relevance`, `recommended_action`) — never merged into
  one field.
- Never generate an implementation plan inside `possible_experiments` —
  structurally enforced by `PossibleExperiment`'s own fixed 5 fields.
- Assign persistent `RES-000N` identifiers and never silently drop or
  renumber one that already exists.
- Never take a write action against any repository, under any
  circumstance — not this one, not any observed one.

## What this sensor cannot do (`EXEC-010`'s Read-only Boundary, verbatim)

This sensor **cannot**:

- modify any repository;
- create issues;
- make architectural decisions;
- implement anything;
- run experiments automatically.

Human approval is required for anything beyond producing the registry
and briefs.

## Explicitly out of scope (`EXEC-010`, verbatim)

No automatic literature review; no autonomous hypothesis generation; no
implementation suggestions; no code generation; no paper ranking by
citations; no decision making.

## Safety

Enforced by `tests/test_safety.py`, reusing the same detector design
`observation-agent/`'s, `headquarters/`'s, and `reality-sensor/`'s own
safety tests established, including the network-client-forbidden check
`reality-sensor/` first added: no source file anywhere in
`src/research_sensor/` may reference a network client
(`requests.`, `urllib.request`, `httpx.`, `http.client`, `socket.`, and
more) — this package never makes a live network call; capture happens
outside it entirely (see `ARCHITECTURE.md`). Both constraints are
checked by scanning the actual source text, with a self-check proving
the detector catches real violations rather than passing vacuously.

## Executor independence

This contract binds the tool, not whoever runs it. Any human or AI
executor invoking `run_research_sensor.py`, or performing the capture
step that feeds it, operates under the same scope and safety
constraints; nothing here depends on a specific AI model or invoking
party.

## Revocation and change

This tool may be modified, extended with new sources or domains, or
retired at any time by direct repository change — source code under
normal version control, not a ceremonial Role requiring a lifecycle
process. A change that would grant it any write capability, any live
network-fetch capability inside its own checked-in source, or any
capability to act on its own signals is out of scope for this contract
entirely and would require a new, explicit human decision and a new
safety review, not a routine edit.
