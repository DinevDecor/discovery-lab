# Recommendation Ledger

Per `PROP-0001-discovery-lab-boundaries.md` §"Recommendation quality:
interface definition only (not implemented)". That section specified
this ledger's schema, fields, status discipline, and metrics in full,
and explicitly deferred creating it until a real recommendation existed
to seed it — *"This ledger has no home yet... and is not populated
until at least one recommendation exists to track — it should not
block the first run of Ecosystem Health Review v0.1."* `INV-0003` now
provides six. Created here, for the first time, as `STRATEGIC-001`'s
own chosen initiative — see `../proposals/STRATEGIC-001-close-
evidence-loop/DECISION-REPORT.md`.

**Status discipline, quoted from `PROP-0001`, binding on every entry
below**: *"`status` is set only from the destination repository's own
recorded decision — never inferred by Discovery Lab itself. In
particular, silence is never treated as `REJECTED`."* Every entry below
is filed `PROPOSED` because no destination repository has yet been
asked. None is `PENDING_NO_RESPONSE` — that status requires an ask to
have gone out and gone unanswered, which has not happened yet.

## Entries

```
recommendation_id: REC-0001
source_investigation: INV-0003-ecosystem-health-review-v0.1.md (project-memory, C1)
destination_repository: project-memory
date_proposed: 2026-07-25
status: PROPOSED
date_status_recorded: 2026-07-25
summary: PROJECT_STATE.md dated 2026-07-16 ("Phase 1 closed... Begin
  Phase 2") does not reflect real repository activity through
  2026-07-24 (archive/, notes/). Suggested action: update the state
  file's own current_step/updated_at fields, or confirm the phase is
  genuinely still closed and the state file is simply due for a
  routine refresh.
```

```
recommendation_id: REC-0002
source_investigation: INV-0003-ecosystem-health-review-v0.1.md (project-memory, C2)
destination_repository: project-memory
date_proposed: 2026-07-25
status: PROPOSED
date_status_recorded: 2026-07-25
summary: PROJECT_REGISTRY.md lists "Dinev Decor Systems" as
  "ACTIVE / DISCOVERY," contradicted by the separate project-memory
  repository's own notes/2026-07-19-dinev-decor-systems-location-
  check.md (not reachable by relative path from here; INSUFFICIENT
  ACCESS). Suggested action: reconcile the registry entry with the
  investigation's own conclusion, or record why the registry
  intentionally differs.
```

```
recommendation_id: REC-0003
source_investigation: INV-0003-ecosystem-health-review-v0.1.md (kod, C1/C2)
destination_repository: KOD
date_proposed: 2026-07-25
status: PROPOSED
date_status_recorded: 2026-07-25
summary: Core/Registry/PROJECT_STATE.md states "Corpus Status:
  NOT_STARTED" and does not reference SPRINT-024.md (state: APPROVED,
  priority: HIGH), despite real corresponding code existing
  (Infrastructure/python/kod/artifact.py and siblings). Suggested
  action: update PROJECT_STATE.md's Runtime/Current Sprint fields to
  reflect SPRINT-024's real status and output.
```

```
recommendation_id: REC-0004
source_investigation: INV-0003-ecosystem-health-review-v0.1.md (kod, C3)
destination_repository: KOD
date_proposed: 2026-07-25
status: PROPOSED
date_status_recorded: 2026-07-25
summary: DOMAIN_MODEL.md contains two different sections both titled
  "Domain Model v2," plus an unresolved "Open Question" about KOD's own
  fundamental entity (first found in this session's G2 task, reconfirmed
  unmodified in INV-0003). Suggested action: reconcile or explicitly
  supersede one of the two "v2" sections, and resolve or explicitly
  defer the Open Question with a stated owner.
```

```
recommendation_id: REC-0005
source_investigation: INV-0003-ecosystem-health-review-v0.1.md (kod, notes)
destination_repository: KOD
date_proposed: 2026-07-25
status: PROPOSED
date_status_recorded: 2026-07-25
summary: Two 0-byte files found (ROS_ARCHITECTURE.md,
  Infrastructure/python/kod/validator.py). Suggested action: either
  populate or remove, at KOD maintainers' own discretion — flagged as
  orphan content, not assumed to be a defect.
  CORRECTION (EXEC-003, 2026-07-25): a third file originally listed
  here, Infrastructure/python/registry.py, is not empty — it is 33
  bytes (a single import line), a non-empty stub rather than an
  orphan file, and is removed from this recommendation.
```

```
recommendation_id: REC-0006
source_investigation: INV-0003-ecosystem-health-review-v0.1.md (trust-engine, C2/C3)
destination_repository: trust-engine
date_proposed: 2026-07-25
status: PROPOSED
date_status_recorded: 2026-07-25
summary: No PROJECT_STATE.md- or registry-equivalent artifact exists
  anywhere in trust-engine, making C2/C3 uncheckable
  (INSUFFICIENT_EVIDENCE, not a confirmed defect). Suggested action:
  consider adopting a minimal self-status artifact, at trust-engine
  maintainers' own discretion — this is a suggestion for
  checkability, not a claim anything is currently wrong.
```

## Metrics (computed now that entries exist; interface `PROP-0001` itself specified)

```
total: 6
accepted: 0
rejected: 0
pending_no_response: 0
insufficient: 0
acceptance_rate: undefined (0 / 0 — no denominator yet; per PROP-0001's
  own rule, accepted + rejected must both be excluded-if-zero, not
  divided as 0/0)
```

**Naming caveat, quoted from `PROP-0001`, binding on this section**:
*"`acceptance_rate` measures whether a destination repository's own
governance agreed with a Discovery Lab proposal. It is not a measure of
objective correctness, and must never be called 'precision' without
this caveat attached."*

## What this ledger does not do

It does not deliver these six proposals to `project-memory`'s or `kod`'s
own maintainers — Discovery Lab has no authority to do that itself
(Principle 0; `PROP-0001`'s Transfer 1 spec: "the destination
repository's own human-only finalization rule"). That delivery is a
human-mediated act, per `kod/ADR-0009`'s own "Human Message Bus"
admission — not something this document performs. It does not infer,
guess, or pre-fill any `status` beyond `PROPOSED`. It does not compute
a single score across repositories or across the six entries — none is
computed, and the ledger's own `acceptance_rate` field is explicitly
left `undefined` above rather than shown as a misleading `0%` or `N/A`
without explanation.
