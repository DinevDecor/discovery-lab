# Constraint Change Observatory — 2026-08-10T05:56:00Z

Current records: **4** · Superseded: **0** · Newly added this run: **0**

This report states, per constraint, whether the evidence shows it weakened, still binds, shifted to a different bottleneck, or inverted. It does not assess what that means commercially - no field in this schema exists for such a judgment, and none is added here. See `CONTRACT.md`.

## Newly added constraint changes

_None this run._


## Constraint states

- **WEAKENED**: 0
- **SHIFTED**: 3 — ccov-0001, ccov-0003, ccov-0004
- **INVERTED**: 1 — ccov-0002
- **STILL_BINDING**: 0
- **INSUFFICIENT_DATA**: 0

## Old bottleneck → new bottleneck transitions

- **ccov-0001** [SHIFTED]: `cost` (Whole-genome sequencing cost ~$95M per genome as of 2001, restricting it to large centralized projects.) → `expertise_scarcity` (Clinical variant interpretation capacity, not sequencing throughput, is the current binding constraint on turning a genome into a diagnosis.) [OBSERVED]
- **ccov-0002** [INVERTED]: `cost` (A 3-minute transatlantic call cost ~$12 in 1950 under a regulated monopoly carrier structure.) → `trust` (Near-zero call-initiation cost enabled scam/robocall volume at a scale that makes caller verification, not connection cost, the binding constraint on a call's value.) [OBSERVED]
- **ccov-0003** [SHIFTED]: `regulation` (McFadden Act (1927), extended by the Douglas Amendment (1956), confined national banks and bank holding companies to branching within their home state.) → `regulation` (A deposit-concentration cap (10% national / 30% state) replaces the geographic branching prohibition as the binding regulatory limit on large-bank expansion.) [OBSERVED]
- **ccov-0004** [SHIFTED]: `cost` (Solar PV modules cost ~$106/watt (inflation-adjusted) in 1976, restricting deployment to niche non-grid applications.) → `labor_cost` (Installation, permitting, and customer-acquisition ('soft') costs now account for 45-60% of total residential system cost and are cited by NREL as the largest, most persistent contributor to solar pricing -- the module cost constraint weakened while the labor/coordination constraint around deploying it did not fall at a comparable rate.) [OBSERVED]

## Strongest quantitative changes

- **ccov-0001**.`cost` [ORDER_OF_MAGNITUDE]: 95000000 → 550 USD per genome, ratio=5.789e-06
- **ccov-0002**.`cost` [ORDER_OF_MAGNITUDE]: 12 → ~0 (bundled/marginal) USD per call
- **ccov-0003**.`geographic_reach` [ORDER_OF_MAGNITUDE]: single state → nationwide, subject to concentration cap n/a
- **ccov-0004**.`cost` [ORDER_OF_MAGNITUDE]: 106 → 0.38 USD per watt (module only), ratio=0.003585
- **ccov-0004**.`scale` [ORDER_OF_MAGNITUDE]: niche/off-grid only → grid-competitive, mass residential/utility deployment n/a

## Still-binding constraints

_None this run._


## INSUFFICIENT_DATA

_None this run._


Records with a populated state but an `INSUFFICIENT_DATA` sub-claim (not a defect - see CONTRACT.md):
- **ccov-0001**: `historical_adaptation` is INSUFFICIENT_DATA
- **ccov-0002**: `historical_adaptation` is INSUFFICIENT_DATA
- **ccov-0004**: `historical_adaptation` is INSUFFICIENT_DATA

## Unresolved questions

- **ccov-0001**:
  - What was the pre-2001 adaptation (centralized sequencing centers, targeted Sanger panels)? Not confirmed this pass.
  - Exact current cost-per-genome figure for 2024-2026 not verified against a primary NHGRI release in this pass.
  - Is clinical interpretation gated by explicit licensing statute, or informally by workforce/training capacity? Both may be true; only capacity is directly cited here.
- **ccov-0002**:
  - No citation found in this pass for the pre-cable-era organizational adaptation to expensive calling (telex/mail substitution, centralized switchboards) - plausible, not confirmed.
  - Exact current marginal cost of a call under typical mobile bundles not pinned to a specific cited number, only characterized as near-zero.
- **ccov-0003**:
  - Has the 10%/30% cap itself been amended or waived since 1994? Not checked in this pass.
  - How binding is the concentration cap in practice today - has any institution approached it? Not checked.
- **ccov-0004**:
  - No citation found in this pass for a specific pre-1976 organizational adaptation to high module cost beyond the general observation that deployment concentrated in cost-insensitive niches.
  - Soft-cost figures come from a search-summarized description of the NREL 2024 report, not a direct read of the primary PDF -- a build-phase record should re-verify against docs.nrel.gov directly.

## Possible conflicts (0)

Current records that share the same (constraint_family, domain, constrained_activity) but disagree on current_constraint_state. Neither is overwritten; both are listed here for a human to reconcile.

_None this run._


