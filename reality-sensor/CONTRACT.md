# Contract — Reality Intelligence Sensor 001 (`reality-sensor/`)

Version: **v0.1** (implements `EXEC-008`)
Core Principle: **Observe external reality. Report evidence. Never decide, never act.**

This is a **tool contract**, not an Employee Role contract — same
precedent as `observation-agent/CONTRACT.md` and
`headquarters/CONTRACT.md`. `EXEC-008` did not ask for a new Employee
ID or the full `docs/ai-organization/employees/` document set, so this
deliberately does not instantiate one.

## Scope of authority

Read-only processing of a raw-captures file supplied by whoever invokes
this tool (a human, or an AI executor acting under explicit human task
authorization — see `ARCHITECTURE.md` for why capture and processing
are separate steps). No authority beyond producing a Signal Registry
and two human-readable briefs, all inside this package's own `reports/`
directory, is granted under any circumstance.

## Position in the ecosystem

`External Reality -> Reality Sensor 001 -> Signal Registry ->
Observation Layer -> Headquarters -> Human Decision`. This sensor never
bypasses Headquarters — it produces one artifact and stops. It does
not call Headquarters, does not import any Headquarters module, and
does not know Headquarters exists at runtime.

## Rights

- The right to report `INSUFFICIENT_EVIDENCE` confidence whenever a
  signal has no supporting evidence, without this being treated as a
  defect.
- The right to report `WATCH` for `affected_projects` whenever no
  configured project plausibly benefits, per `EXEC-008`'s own explicit
  "Do not force relevance" instruction.
- The right to have any signal, trust classification, or confidence
  score disputed or corrected by a human without that requiring a
  change to this contract.

## Responsibilities

- Every Signal must carry all 13 fields `EXEC-008`'s Signal Model
  names — see `docs/SIGNAL-SCHEMA.md`.
- Every Signal must cite at least one piece of Evidence, or its
  confidence is forced to `INSUFFICIENT_EVIDENCE`.
- Never assign `HIGH` confidence from `COMMUNITY`-trust evidence alone
  — see `docs/TRUST-POLICY.md`.
- Keep FACT/CLAIM/EVIDENCE structurally separate from
  INTERPRETATION/ACTION — `Evidence.quoted_text` never contains this
  tool's own summary, practical-impact assessment, or recommended
  action.
- Assign persistent `RS-000N` identifiers and never silently drop or
  renumber one that already exists (mirrors
  `headquarters/src/headquarters/recommendation.py`'s `HQ-000N`
  pattern).
- Never take a write action against any repository, under any
  circumstance — not this one, not any observed one.

## What this sensor cannot do (`EXEC-008`'s Read-only Rules, verbatim)

This sensor **cannot**:

- modify any repository;
- merge anything;
- change any priority anywhere;
- create a task;
- recommend implementation (its `recommended_action` field is always
  advisory prose, never an instruction to build, merge, or deploy
  anything).

It only reports evidence.

## Explicitly out of scope (`EXEC-008`, verbatim)

No autonomous browsing; no automatic coding; no project creation; no
autonomous decisions; no repository modification; no Research
Intelligence; no Decision Intelligence; no Tender monitoring; no
Market monitoring; no Calendar integration.

## Safety

Enforced by `tests/test_safety.py`, reusing the same detector design
`observation-agent/`'s and `headquarters/`'s own safety tests
established, extended with one property unique to this tool: no source
file anywhere in `src/reality_sensor/` may reference a network client
(`requests.`, `urllib.request`, `httpx.`, `http.client`, `socket.`, and
more) — this package never makes a live network call; capture happens
outside it entirely (see `ARCHITECTURE.md`). Both constraints are
checked by scanning the actual source text, with a self-check proving
the detector catches real violations rather than passing vacuously.

## Executor independence

This contract binds the tool, not whoever runs it. Any human or AI
executor invoking `run_reality_sensor.py`, or performing the capture
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
