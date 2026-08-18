# Case/Claim Identity Kernel v0.1

Stage 1 of the autonomous multi-model knowledge system (Phase 0 reuse archaeology).
Adds exactly the one primitive that audit found missing everywhere in this repo: a
stable, deterministic identity that spans packages. Everything else the eventual
system needs (a second model provider, blind dispatch, Falsifier, Judge, a router,
outcome resolution, Trust Engine integration, Grok Scout, Headquarters changes) is
explicitly out of scope for this slice — see `CONTRACT.md`.

## What this is

Three objects (`src/case_claim_kernel/models.py`):

- **Case** — wraps one already-published source record (one Constraint Archaeology
  Anomaly, one Business Candidate Analyst Candidate) unchanged.
- **Claim** — one atomic assertion inside a Case, modelled directly on BCA's own
  `DimensionResult` shape.
- **ArtifactEnvelope** — the neutral wire format both are persisted through, modelled
  on `ca_agents.findings_ledger.Finding`'s envelope.

A Case is not a Claim. A Claim is not an analysis. No analysis, decision, or outcome
object exists in this package — Stage 1 does not build them.

## What this is not

- Not a second model provider, not a dispatcher, not a reviewer, not a resolver.
- Not a rewrite of any existing ledger. `constraint-archaeology-agents/data/*` and
  `business-candidate-analyst/data/*` are read-only inputs; this package never opens
  them in a writing mode.
- Not fuzzy or semantic identity. Every `case_id`/`claim_id` is a deterministic hash
  of an already-known source id — see `src/case_claim_kernel/identity.py`.

## Running it

```
python3 run_case_claim_kernel.py --anomaly-id ANOM-0001 --candidate-id BC-0001
```

Reads `constraint-archaeology-agents/data/anomalies.json` and
`business-candidate-analyst/data/candidates.json` read-only. Appends the resulting
Case/Claim envelopes to `data/artifacts.jsonl`. Re-running with the same ids is a
no-op (same `artifact_id`s, already known to the ledger).

## Tests

```
python3 -m unittest discover -s tests -v
```

`tests/test_wrap_real_data.py` is the acceptance test: it loads the real
`anomalies.json`/`candidates.json` already committed to this repo (not a fixture),
wraps a real anomaly and a real candidate, and asserts identity is stable across two
independent wrap calls. `tests/test_safety.py` statically checks that no module in
this package ever opens a file in a writing mode outside `ledger.py`, and that no
module imports `ca_agents` or `business_candidate_analyst`.
