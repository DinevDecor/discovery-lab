# Contract — Business Candidate Analyst v0.1 (`business-candidate-analyst/`)

Core Principle: **Read published evidence. Classify. Never sense, never invent, never gate upstream.**

This is a **tool contract**, matching the precedent of `observation-agent/CONTRACT.md`
and `headquarters/CONTRACT.md` — not a governance/Employee Role contract.

## Position in the pipeline

```
Sources -> Captures -> Observations -> Anomalies -> Constraint Archaeologist
                                            |
                                            v
                          Business Candidate Analyst -> Business Candidate Registry
```

This tool is a **downstream consumer of already-published Constraint Archaeology
evidence**. It is not part of the discovery sensor and does not sit between any two
existing pipeline stages.

## Scope of authority

Read-only interpretation of three files already produced by
`constraint-archaeology-agents/run_daily.py`:

- `constraint-archaeology-agents/data/observations.jsonl`
- `constraint-archaeology-agents/data/anomalies.json`
- `constraint-archaeology-agents/data/latest-evaluations.json`

No authority beyond producing its own registry (`data/candidate_events.jsonl`,
`data/candidates.json`) and its own report (`reports/`) is granted. Every path this
tool ever opens in a writing mode lives under `business-candidate-analyst/` itself —
enforced by `tests/test_safety.py`, not just this document.

## Hard boundary — this tool MUST NOT

- modify `observations.jsonl`, `anomalies.json`, `latest-evaluations.json`, or any
  other Constraint Archaeology data/report file;
- modify Constraint Archaeology thresholds, gates, or method files (anything under
  `constraint-archaeology-agents/src/ca_agents/`, `docs/method/`);
- change source selection or influence what the Sensor Agent or Archaeologist look
  for — there is no code path from this package back into `ca_agents`;
- make a network call of any kind, including to search the web for corroborating
  evidence — enforced statically by `tests/test_safety.py`;
- call a language model. Candidate classification is fully deterministic (keyword
  and structural heuristics only), so "the model liked this idea" can never be the
  reason a candidate advances — see README's "Why fully deterministic" section;
- promote a candidate because the underlying pattern sounds like a good product —
  every state transition is driven by the dimension rubric in `lifecycle.py`, cites
  the observation/anomaly ids it used, and a transition with unmet criteria simply
  does not fire, regardless of how compelling the pattern reads.

## Rights

- The right to leave any of the fourteen evaluation dimensions
  (`dimensions.py`) as `INSUFFICIENT_DATA` whenever the underlying evidence does not
  support a value, without that being treated as a defect in the tool.
- The right to leave a candidate at `WATCH` indefinitely. Reaching `PROMISING` is not
  a goal this tool optimizes for.
- The right to refuse a merge between two evidence groups (`signature.py`) even when
  their surface wording is similar, if the buyer/function signature does not match.

## Responsibilities

- Cite evidence — `observation_id` / `anomaly_id` (and `latest-evaluations.json`
  action, when used) — for every dimension result and every state transition.
- Never overwrite a past state transition's reason. `data/candidate_events.jsonl` is
  append-only; `data/candidates.json` is fully rebuilt from it every run, the same
  split `constraint-archaeology-agents` already uses between `findings.jsonl` and
  `anomalies.json`.
- Only merge two evidence groups into one candidate when `signature.py`'s gate
  passes on both buyer bucket and function class, never on text similarity alone.
- Produce one human-readable report per run answering: new candidates, strengthened,
  weakened, merged, rejected, approaching INVESTIGATE/PROMISING, and why (with
  evidence references).

## Executor independence

This contract binds the tool, not whoever runs it — same precedent as
`observation-agent/CONTRACT.md`.

## Revocation and change

This tool may be modified, extended, or retired at any time by direct repository
change. A change that would grant it write access to any Constraint Archaeology file,
network access, or an LLM call is out of scope for this contract entirely and would
need a new, explicit human decision.
