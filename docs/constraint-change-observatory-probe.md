# Constraint Change Observatory — Real-World Probe

**Companion to:** `docs/constraint-change-observatory-design.md`.
**Purpose:** not to find businesses. To test whether the Constraint Change Record
schema (design doc §8) can be populated reliably, honestly, and with real citations
— specifically whether `current_constraint_state` can be assigned from evidence
rather than assumed from the existence of newer technology (design doc §12).
**Method:** four constraints, chosen to span technological / economic-infrastructure
/ regulatory-institutional / non-AI-structural, each reconstructed as
THEN → constraint → adaptation → structural change → NOW → replacement constraint,
then formalized against the schema. All four are zero-AI by construction (adversarial
case G). Sourcing followed design doc §11's evaluated classes: historical
price/performance datasets, government/regulatory-history essays, and recent
engineering-benchmark reports.
**Caveat, stated once and binding throughout:** every claim below is either a direct
citation (`OBSERVED`) or a stated inference across two citations (`INFERRED`).
Nothing here is asserted from general knowledge. Where the search results didn't
settle a number precisely, that's written down as `INSUFFICIENT_DATA`, not rounded
off.

---

## Probe 1 — DNA sequencing cost (technological)

### Narrative reconstruction

**THEN.** Sequencing a human genome via the methods available at the completion of
the Human Genome Project (2001) cost approximately **$95 million** [OBSERVED,
genome.gov/NHGRI cost data]. This was the binding constraint on essentially all
individual-level genomic medicine and research: at that price, whole-genome
sequencing was a national-project-scale undertaking, not a clinical tool.

**Constraint.** `cost` (family), and downstream `capital_requirements` for any
institution wanting to sequence more than a handful of genomes.

**Adaptation.** `INSUFFICIENT_DATA` — the pre-2001 field's adaptation (targeted
Sanger sequencing of specific genes rather than whole genomes, large centralized
sequencing centers pooling capital) is plausible but not independently confirmed by
a citation in this pass; flagged for a future research pass rather than asserted.

**Structural change.** The arrival of next-generation sequencing (NGS) platforms
from roughly 2007–2008 "compressing a decade of cost reduction into a single year"
[OBSERVED via search-summarized NHGRI trend description]. By mid-2015 the cost had
fallen to just above **$4,000**, then below **$1,500** by late 2015
[OBSERVED, genome.gov cost-data page, per search summary]. `change_driver.category =
technological_improvement`, specifically massively parallel sequencing replacing
Sanger capillary sequencing.

**NOW.** Current per-genome sequencing cost is commonly reported in the
**$500–600** range as of the most recent NHGRI data available to this search
[OBSERVED, genome.gov / Our World in Data grapher "cost-of-sequencing-a-full-human-genome",
exact 2021/2022 figure not independently re-verified in this pass — treat the
number as approximate, the >100,000× order-of-magnitude decline as solid].

But **the constraint on turning a sequenced genome into a clinical decision did not
fall at the same rate.** A 2021 clinical-genetics paper states directly: *"the
development of next-generation sequencing has displaced the bottleneck in genomics
from sequencing to variant interpretation and the identification of pathogenic
mutations"* [OBSERVED, "Challenges in genetic testing: clinician variant
interpretation processes and the impact on clinical care," *Genetics in Medicine*,
2021]. Genetic-counselor workforce training for variant interpretation is described
as historically ad hoc, with existing programs lacking capacity to reach the whole
workforce, motivating MOOC-based training efforts as of 2023 [OBSERVED, PMC
11170928, 2023].

**Replacement constraint.** `expertise_scarcity` (variant-interpretation capacity)
and, more weakly, `regulation`/`licensing` (clinical genetic-testing interpretation
is typically gated through certified laboratory and, for patient-facing counseling,
licensed-genetic-counselor workflows) — the licensing half is `INFERRED` from the
existence of a credentialed genetic-counselor profession and clinical-lab
certification regimes, not from a single source stating the rule directly in this
pass.

### Constraint Change Record

```yaml
record_id: ccov-0001
protocol_version: ccov0.1
constraint_family: cost
domain: genomic diagnostics
constrained_activity: sequencing and clinically interpreting an individual human genome

historical_constraint:
  statement: "Whole-genome sequencing cost ~$95M per genome as of 2001, restricting it to large centralized projects."
  evidence_status: OBSERVED
historical_evidence:
  - citation: "NHGRI / genome.gov, DNA Sequencing Costs Data"
    value: 95000000
    unit: USD per genome
    as_of_date: 2001

historical_adaptation:
  statement: null
  evidence_status: INSUFFICIENT_DATA

change_driver:
  category: technological_improvement
  statement: "Next-generation (massively parallel) sequencing platforms replaced Sanger capillary sequencing starting ~2007-2008."
  evidence_status: OBSERVED
change_evidence:
  - citation: "genome.gov cost-data trend summary"
    value: 1500
    unit: USD per genome
    as_of_date: "2015 (late)"

current_constraint_state: SHIFTED
current_evidence:
  - citation: "genome.gov / Our World in Data, cost-of-sequencing-a-full-human-genome"
    value: "~500-600 (approximate, not independently re-verified)"
    unit: USD per genome
    as_of_date: "~2021-2022"
  - citation: "Genetics in Medicine (2021), 'Challenges in genetic testing: clinician variant interpretation processes and the impact on clinical care'"
    value: "bottleneck explicitly stated to have moved to variant interpretation"
    unit: n/a
    as_of_date: 2021

constraint_delta:
  cost:
    then_value: 95000000
    now_value: 550
    unit: USD per genome
    ratio: ~0.0000058
    magnitude_class: ORDER_OF_MAGNITUDE
    evidence_ids: [obs-0001, obs-0002]
  skill_requirement:
    then_value: null
    now_value: null
    unit: n/a
    ratio: null
    magnitude_class: DIRECTION_ONLY   # inferred to have INCREASED as interpretation load grew, not measured
    evidence_ids: [obs-0003]

replacement_constraint:
  family: expertise_scarcity
  statement: "Clinical variant interpretation capacity, not sequencing throughput, is the current binding constraint on turning a genome into a diagnosis."
  evidence_status: OBSERVED

first_seen: 2026-08-10
last_updated: 2026-08-10
provenance: [cap-0001, cap-0002, cap-0003]
unresolved_questions:
  - "What was the pre-2001 adaptation (centralized sequencing centers, targeted Sanger panels)? Not confirmed this pass."
  - "Exact current cost-per-genome figure for 2024-2026 not verified against a primary NHGRI release in this pass."
  - "Is clinical interpretation gated by explicit licensing statute, or informally by workforce/training capacity? Both may be true; only capacity is directly cited here."
analyst: "Claude (directed research pass), human review pending per design doc §18"
```

**Adversarial cases exercised:** C (licensed-human-shaped constraint persists after
the technology commoditizes — though here it's workforce/training capacity more than
statute, which is itself an honest finding, not a clean textbook match), G (zero AI).

---

## Probe 2 — Long-distance telephone call cost (economic / infrastructure)

### Narrative reconstruction

**THEN.** A three-minute Boston–London call cost about **$12 in 1950**
[OBSERVED, Click Americana]. Even domestically, long-distance calling was priced by
distance and duration under the regulated AT&T (Bell System) monopoly through the
1970s [OBSERVED, general search summary].

**Constraint.** `cost`, compounded by `geographic_distance` and a `regulation`-created
monopoly structure (Bell System) that kept prices administered rather than
competitive.

**Adaptation.** `INSUFFICIENT_DATA` for a specific organizational adaptation in this
pass — plausibly businesses centralized voice communication through operators/PBX
systems and used telex/mail for non-urgent long-distance communication to avoid
call costs, but not independently confirmed by a citation here.

**Structural change.** Two distinct drivers, both cited: (1) a new transatlantic
submarine cable dropped the Boston–London 3-minute price to about **$3 in the
1960s**, and further to **$1.70 by 1968** [OBSERVED, Click Americana /
KiowaCountyPress] — `infrastructure_deployment`. (2) The 1984 breakup of the AT&T
Bell System monopoly opened long-distance to competition (MCI, Sprint), producing
"a nearly 40% drop in the cost of making a long-distance call" [OBSERVED, search
summary citing the Bell System breakup] — `regulation_change`. Fiber-optic cable
capacity is cited as compounding this through the 1980s–90s [OBSERVED, general
search summary]. By 2006, the average long-distance call cost about **6 cents per
minute** [OBSERVED, search summary].

**NOW.** Marginal cost of a domestic or most international calls is effectively
bundled to zero in modern mobile/VoIP plans — `current_constraint_state` on the
original `cost`/`geographic_distance` constraint is **WEAKENED to the point of
near-elimination** for voice connectivity itself. But the same near-zero cost of
initiating a call is cited as the *cause* of a large-scale new problem: unwanted
scam/telemarketing call volume reached **29.6 billion calls in 2025**, a 15.6%
year-over-year increase and "the highest level in four years," with 31% of American
adults reporting at least one scam call per day [OBSERVED, PIRG "Ringing in Our
Fears 2025"]. The FCC took regulatory action against roughly 1,400 phone companies
in August 2025 for allowing illegal robocall traffic [OBSERVED, same source /
FCC-adjacent reporting].

**Replacement constraint.** `trust`/`identity` — caller verification and spam
filtering, not connection cost, is now the binding constraint on the value of an
inbound phone call.

### Constraint Change Record

```yaml
record_id: ccov-0002
protocol_version: ccov0.1
constraint_family: cost
domain: voice telecommunications
constrained_activity: placing a long-distance or international voice call

historical_constraint:
  statement: "A 3-minute transatlantic call cost ~$12 in 1950 under a regulated monopoly carrier structure."
  evidence_status: OBSERVED
historical_evidence:
  - citation: "Click Americana, 'International phone calls 1965'"
    value: 12
    unit: USD per 3-minute call (Boston-London, 1950)
    as_of_date: 1950

historical_adaptation:
  statement: null
  evidence_status: INSUFFICIENT_DATA

change_driver:
  category: infrastructure_deployment
  statement: "Transatlantic submarine cable deployment cut the same call to ~$3 in the 1960s, ~$1.70 by 1968; AT&T Bell System breakup (1984) opened long-distance to competition, cutting prices further; fiber-optic capacity compounded this through the 1980s-90s."
  evidence_status: OBSERVED
change_evidence:
  - citation: "KiowaCountyPress / Click Americana, historical long-distance pricing"
    value: 1.70
    unit: USD per 3-minute call
    as_of_date: 1968
  - citation: "Search-summarized reporting on 1984 AT&T breakup price effect"
    value: "~40% price drop"
    unit: n/a
    as_of_date: 1984

current_constraint_state: INVERTED
current_evidence:
  - citation: "PIRG, 'Ringing in Our Fears 2025'"
    value: 29600000000
    unit: unwanted calls per year (US)
    as_of_date: 2025
  - citation: "PIRG 2025 report, consumer-impact figures"
    value: "31% of US adults report >=1 scam call/day"
    unit: n/a
    as_of_date: 2025

constraint_delta:
  cost:
    then_value: 12
    now_value: "~0 (bundled/marginal)"
    unit: USD per call
    ratio: null
    magnitude_class: ORDER_OF_MAGNITUDE
    evidence_ids: [obs-0004, obs-0005]
  # trust/verification is the *replacement* dimension, not a delta on the original constraint -
  # deliberately not forced into constraint_delta; see replacement_constraint below

replacement_constraint:
  family: trust
  statement: "Near-zero call-initiation cost enabled scam/robocall volume at a scale that makes caller verification, not connection cost, the binding constraint on a call's value."
  evidence_status: OBSERVED

first_seen: 2026-08-10
last_updated: 2026-08-10
provenance: [cap-0004, cap-0005, cap-0006]
unresolved_questions:
  - "No citation found in this pass for the pre-cable-era organizational adaptation to expensive calling (telex/mail substitution, centralized switchboards) — plausible, not confirmed."
  - "Exact current marginal cost of a call under typical mobile bundles not pinned to a specific cited number, only characterized as near-zero."
analyst: "Claude (directed research pass), human review pending per design doc §18"
```

**Adversarial cases exercised:** A (early cable-driven price drops preceded and were
compounded by the 1984 deregulation — technology and regulation each did part of the
work, worth not attributing to one alone), F (VoIP's early-2000s cost advantage came
with real, citable-in-principle reliability/quality tradeoffs not fully explored in
this pass — flagged, not resolved), G (zero AI), and a genuine INVERTED example not
explicitly in the task's A–G list but predicted by the design's taxonomy (§6).

---

## Probe 3 — US interstate bank branching restriction (regulatory / institutional)

### Narrative reconstruction

**THEN.** The McFadden Act of 1927 confined national banks to branching only within
their own state, "to the same extent state banks could branch" [OBSERVED, Federal
Reserve History, "McFadden Act of 1927"]. This was compounded by the Douglas
Amendment to the Bank Holding Company Act of 1956, which extended the same
restriction to bank holding companies [OBSERVED, search summary citing the Douglas
Amendment].

**Constraint.** `regulation` / `licensing` — a legal, not technological or
economic, ceiling on where a bank could physically operate.

**Adaptation — the clean case-A example.** Long before the restriction was formally
lifted, banks and states worked around it. Starting in the early 1980s, states began
loosening their own laws to admit out-of-state bank holding companies under
**reciprocal agreements** (state A admits banks from state B only if state B admits
banks from state A) [OBSERVED, search summary of Balance/EBSCO/St. Louis Fed
sources]. By **1990, forty-six states** had adopted some form of this [OBSERVED,
same summary]. By 1993 the patchwork was extensive enough that Treasury Secretary
Lloyd Bentsen is quoted describing the country as *de facto* having an interstate
banking system already, "working under laws and regulations made for another time in
America" [OBSERVED, search-summarized reporting]. **This is adversarial case A
directly: the adaptation preceded the formal regulatory change by over a decade.**

**Structural change.** The Riegle-Neal Interstate Banking and Branching Efficiency
Act of 1994 federally removed the McFadden-Act-era restrictions, letting banks open
deposit-taking branches across state lines [OBSERVED, Federal Reserve History,
"Riegle-Neal Act of 1994"]. `change_driver.category = regulation_change`.

**NOW.** The geographic branching prohibition itself is gone — but Riegle-Neal did
not remove all limits, it replaced the *geographic* limit with a *concentration*
limit: a bank holding company may not control more than **10% of the nation's total
deposits, or 30% of any single state's deposits** [OBSERVED, Riegle-Neal Act text /
Federal Reserve History summary]. `current_constraint_state = SHIFTED` — the original
constraint (may a bank open a branch in another state at all) is resolved; a
different regulatory constraint (how much of the national/state deposit base one
institution may hold) now binds in its place for large banks specifically.

**Replacement constraint.** `regulation` (deposit-concentration caps) — notably the
*same family* as the original constraint, just a different rule within it. This is
useful evidence that `SHIFTED` does not require the replacement to come from a
different constraint family, only that it be a distinct, separately-binding rule.

### Constraint Change Record

```yaml
record_id: ccov-0003
protocol_version: ccov0.1
constraint_family: regulation
domain: retail/commercial banking
constrained_activity: opening a bank branch outside the bank's home state

historical_constraint:
  statement: "McFadden Act (1927), extended by the Douglas Amendment (1956), confined national banks and bank holding companies to branching within their home state."
  evidence_status: OBSERVED
historical_evidence:
  - citation: "Federal Reserve History, 'McFadden Act of 1927'"
    value: "branching confined to home state"
    unit: n/a
    as_of_date: 1927

historical_adaptation:
  statement: "States adopted reciprocal interstate agreements from the early 1980s (46 states by 1990), letting bank holding companies acquire out-of-state banks years before the federal restriction was lifted."
  evidence_status: OBSERVED

change_driver:
  category: regulation_change
  statement: "Riegle-Neal Interstate Banking and Branching Efficiency Act of 1994 removed the federal interstate branching restriction."
  evidence_status: OBSERVED
change_evidence:
  - citation: "Federal Reserve History, 'Riegle-Neal Interstate Banking and Branching Efficiency Act of 1994'"
    value: "federal restriction removed"
    unit: n/a
    as_of_date: 1994

current_constraint_state: SHIFTED
current_evidence:
  - citation: "Riegle-Neal Act text, deposit concentration provisions"
    value: "10% national / 30% state-level deposit concentration cap"
    unit: percent of total deposits
    as_of_date: 1994
    note: "The cap itself is the current binding rule, still in force as enacted; this pass did not verify subsequent amendment history."

constraint_delta:
  regulatory_burden:
    then_value: "branching prohibited outside home state (binary)"
    now_value: "branching permitted, subject to 10%/30% deposit concentration cap"
    unit: n/a
    ratio: null
    magnitude_class: DIRECTION_ONLY
    evidence_ids: [obs-0007, obs-0008]
  geographic_reach:
    then_value: "single state"
    now_value: "nationwide, subject to concentration cap"
    unit: n/a
    ratio: null
    magnitude_class: ORDER_OF_MAGNITUDE
    evidence_ids: [obs-0007]

replacement_constraint:
  family: regulation
  statement: "A deposit-concentration cap (10% national / 30% state) replaces the geographic branching prohibition as the binding regulatory limit on large-bank expansion."
  evidence_status: OBSERVED

first_seen: 2026-08-10
last_updated: 2026-08-10
provenance: [cap-0007, cap-0008, cap-0009]
unresolved_questions:
  - "Has the 10%/30% cap itself been amended or waived since 1994? Not checked in this pass."
  - "How binding is the concentration cap in practice today — has any institution approached it? Not checked."
analyst: "Claude (directed research pass), human review pending per design doc §18"
```

**Adversarial cases exercised:** A (adaptation demonstrably preceded the formal
change by over a decade — the clean, well-documented version of this case), B (the
underlying economics/technology of running a multi-state institution had matured
well before 1994; the *regulatory* text was the actually-binding constraint until it
changed), G (zero AI).

---

## Probe 4 — Solar photovoltaic module cost (non-AI structural / manufacturing)

### Narrative reconstruction

**THEN.** In 1976, a solar photovoltaic module cost approximately **$106 per watt**
(inflation-adjusted) [OBSERVED, Our World in Data / Voronoi, citing Nemet (2009)].
At that price, PV was viable only for niche applications (spacecraft, remote
installations) — the `cost` constraint made grid-competitive solar structurally
impossible regardless of the technology's physical viability.

**Constraint.** `cost`, rooted in `manufacturing capability` (crystalline-silicon
purification and cell manufacturing were artisanal-scale, not mass-industrial).

**Adaptation.** `INSUFFICIENT_DATA` in this pass — early solar deployment
concentrated in exactly the applications where cost was not the binding constraint
(space programs, off-grid remote power) is a plausible read of "adaptation" but not
independently cited here as a deliberate organizational response.

**Structural change.** A well-documented experience/learning curve: for every
doubling of cumulative installed capacity, module price fell by roughly **20%**
[OBSERVED, learning-rate literature (Nemet 2009; Farmer & Lafond 2016) as
summarized via Our World in Data]. This compounded through exponential capacity
growth (`change_driver.category = economies_of_scale` / `manufacturing_improvements`)
plus large-scale deployment programs (notably in Germany and China) that provided the
volume the learning curve needed [OBSERVED, general search summary]. By 2019, module
price had fallen to **$0.38 per watt** [OBSERVED, Our World in Data], a decline of
**over 99%** from 1976 [OBSERVED, Voronoi / OWID summary].

**NOW.** Module (hardware) cost is no longer the dominant constraint on solar
deployment cost. NREL's most recent residential benchmark puts **soft costs at
$1.64/W of a $3.25/W median installed cost — 50% of the total** [OBSERVED, NREL 2024
benchmark, search-summarized]. Panels themselves are reported at roughly **13%** of
total project cost heading into 2026, with inverters/balance-of-system equipment at
about **33%**, and *office work* (customer acquisition, permitting, design,
administration) alone at **26%** — larger than field installation labor's **7%**
[OBSERVED, NREL-derived industry summary]. NREL itself identifies soft costs as "the
largest and most persistent contributor to residential solar pricing," at
**45–60% of total project costs** [OBSERVED, same source]. In 2010, hardware still
made up roughly two-thirds of total cost; by the most recent data it is closer to
45% [OBSERVED, same summary] — the crossover from hardware-dominated to
soft-cost-dominated pricing is itself dated and citable.

**Replacement constraint.** Not a single family — the schema's multidimensional
delta is the honest representation here, not a replacement label: `labor_cost`
(installation, permitting, inspection) and `transaction_cost`/`coordination_cost`
(customer acquisition, administrative overhead, interconnection approval) together
now dominate, while the original `manufacturing capability`/`cost` constraint on the
panel itself is genuinely, substantially weakened.

### Constraint Change Record

```yaml
record_id: ccov-0004
protocol_version: ccov0.1
constraint_family: cost
domain: residential/utility solar energy
constrained_activity: manufacturing and deploying a photovoltaic power system

historical_constraint:
  statement: "Solar PV modules cost ~$106/watt (inflation-adjusted) in 1976, restricting deployment to niche non-grid applications."
  evidence_status: OBSERVED
historical_evidence:
  - citation: "Our World in Data / Voronoi, citing Nemet (2009)"
    value: 106
    unit: USD per watt
    as_of_date: 1976

historical_adaptation:
  statement: null
  evidence_status: INSUFFICIENT_DATA

change_driver:
  category: economies_of_scale
  statement: "~20% module price decline per doubling of cumulative installed capacity (learning curve), driven by manufacturing scale-up and large deployment programs."
  evidence_status: OBSERVED
change_evidence:
  - citation: "Our World in Data, solar-pv-prices-vs-cumulative-capacity, citing Nemet (2009) and Farmer & Lafond (2016)"
    value: "~20.2% price reduction per capacity doubling"
    unit: percent
    as_of_date: "1976-2019 series"

current_constraint_state: SHIFTED
current_evidence:
  - citation: "Our World in Data, solar-pv-prices"
    value: 0.38
    unit: USD per watt (module)
    as_of_date: 2019
  - citation: "NREL 2024 residential solar benchmark (search-summarized)"
    value: "soft costs = 50% of $3.25/W median installed cost ($1.64/W); panels ~13%, BOS/inverters ~33%, office work alone ~26%"
    unit: n/a
    as_of_date: 2024

constraint_delta:
  cost:
    then_value: 106
    now_value: 0.38
    unit: USD per watt (module only)
    ratio: 0.0036
    magnitude_class: ORDER_OF_MAGNITUDE
    evidence_ids: [obs-0010, obs-0011]
  scale:
    then_value: "niche/off-grid only"
    now_value: "grid-competitive, mass residential/utility deployment"
    unit: n/a
    ratio: null
    magnitude_class: ORDER_OF_MAGNITUDE
    evidence_ids: [obs-0010]
  # labor_cost / regulatory_burden (soft costs) shown separately below as the near-flat dimension

replacement_constraint:
  family: labor_cost
  statement: "Installation, permitting, and customer-acquisition ('soft') costs now account for 45-60% of total residential system cost and are cited by NREL as the largest, most persistent contributor to solar pricing -- the module cost constraint weakened while the labor/coordination constraint around deploying it did not fall at a comparable rate."
  evidence_status: OBSERVED

first_seen: 2026-08-10
last_updated: 2026-08-10
provenance: [cap-0010, cap-0011, cap-0012]
unresolved_questions:
  - "No citation found in this pass for a specific pre-1976 organizational adaptation to high module cost beyond the general observation that deployment concentrated in cost-insensitive niches."
  - "Soft-cost figures come from a search-summarized description of the NREL 2024 report, not a direct read of the primary PDF -- a build-phase record should re-verify against docs.nrel.gov directly."
analyst: "Claude (directed research pass), human review pending per design doc §18"
```

**Adversarial cases exercised:** D (component became radically cheaper;
installation/service did not — the cleanest, most explicit match to case D of all
four probes, with the crossover from hardware-dominated to soft-cost-dominated
pricing itself dated), G (zero AI). This is also the direct real-world analogue of
the battery-storage reference failure mode named in the task: it would have been
invalid to read "module cost collapsed" as "solar deployment constraint gone" without
checking soft costs specifically — the same mistake the task warns against for
battery-cost claims.

---

## Cross-probe synthesis

| # | Constraint | Family | THEN evidence effort | NOW evidence effort | State reached | Adversarial cases hit |
|---|---|---|---|---|---|---|
| 1 | DNA sequencing cost | cost → expertise_scarcity | Low (one canonical dataset) | **Higher** — required a second, different-domain source (clinical genetics literature) not adjacent to the cost dataset | SHIFTED | C, G |
| 2 | Long-distance calling cost | cost → trust | Low (well-archived historical pricing) | **Higher** — required consumer-protection/FCC-adjacent reporting, a third source domain | INVERTED | A, F(partial), G |
| 3 | Interstate bank branching | regulation → regulation | Low (Federal Reserve History is authoritative and direct) | **Low** — the current rule text is itself the NOW evidence, same source family as THEN | SHIFTED | A, B, G |
| 4 | Solar PV module cost | cost → labor_cost/regulatory_burden | Low (OWID/IRENA canonical series) | **Higher** — required a distinct engineering-benchmark source (NREL) not part of the pricing dataset | SHIFTED | D, G |

**What this confirms about design doc §11's central claim:** in three of four
probes, establishing NOW required a *different source class* than the one that
established THEN/CHANGE — a second, independent search, often in a different
institutional domain entirely (clinical literature for genomics, consumer-protection
reporting for telephony, an engineering benchmark lab for solar). The one exception
(banking) is the one case where THEN and NOW evidence both come from the *same*
institution's own authoritative record of its own rules — which is exactly why §11
rates regulatory/standards-body sources as the strongest NOW class: the institution
that sets the rule is also the institution that states its current form, with no
inference gap in between.

**What this confirms about the taxonomy (§6):** zero of the four probes landed on a
clean `WEAKENED`. Two reached `SHIFTED`, one `INVERTED`, and the genomics case is
`SHIFTED` in substance even though its replacement constraint is workforce capacity
rather than a hard technological ceiling. A four-example sample is far too small to
generalize a base rate from, but it is at least evidence against the taxonomy
degenerating into "everything is WEAKENED" — the opposite failure mode this whole
design exists to prevent (design doc §12).
