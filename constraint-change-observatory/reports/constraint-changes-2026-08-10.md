# Constraint Change Observatory — 2026-08-10T11:36:32Z

Current records: **14** · Superseded: **0** · Newly added this run: **10**

This report states, per constraint, whether the evidence shows it weakened, still binds, shifted to a different bottleneck, or inverted. It does not assess what that means commercially - no field in this schema exists for such a judgment, and none is added here. See `CONTRACT.md`.

## Newly added constraint changes

- **ccov-0005** (labor_cost / maritime freight / port logistics) → `SHIFTED` — loading and unloading break-bulk cargo at a port
- **ccov-0006** (search_cost / urban taxi and ride-hailing transportation) → `SHIFTED` — matching a vacant taxi/vehicle to a waiting passenger in real time
- **ccov-0007** (capital_requirements / enterprise IT infrastructure) → `SHIFTED` — provisioning compute/server capacity for a business workload
- **ccov-0008** (cost / consumer and professional photography) → `SHIFTED` — capturing and processing a photographic image
- **ccov-0009** (regulation / retail/consumer banking) → `SHIFTED` — opening and servicing a consumer bank account or loan relationship
- **ccov-0010** (minimum_economic_scale / discrete parts manufacturing) → `STILL_BINDING` — producing a plastic part at production volume (thousands to tens of thousands of units)
- **ccov-0011** (energy / residential and commercial lighting) → `SHIFTED` — producing visible light from electrical energy
- **ccov-0012** (distribution_access / recorded music) → `SHIFTED` — manufacturing, distributing, and promoting a recorded music release to reach a paying audience
- **ccov-0013** (infrastructure_availability / electric grid operations) → `INVERTED` — integrating distributed, inverter-based generation (rooftop/distributed solar, batteries) into the electric grid without compromising stability
- **ccov-0014** (distribution_access / consumer retail) → `SHIFTED` — offering and selling a physical product to a consumer, bounded by store shelf space and geographic reach

## Constraint states

- **WEAKENED**: 0
- **SHIFTED**: 11 — ccov-0001, ccov-0003, ccov-0004, ccov-0005, ccov-0006, ccov-0007, ccov-0008, ccov-0009, ccov-0011, ccov-0012, ccov-0014
- **INVERTED**: 2 — ccov-0002, ccov-0013
- **STILL_BINDING**: 1 — ccov-0010
- **INSUFFICIENT_DATA**: 0

## Old bottleneck → new bottleneck transitions

- **ccov-0001** [SHIFTED]: `cost` (Whole-genome sequencing cost ~$95M per genome as of 2001, restricting it to large centralized projects.) → `expertise_scarcity` (Clinical variant interpretation capacity, not sequencing throughput, is the current binding constraint on turning a genome into a diagnosis.) [OBSERVED]
- **ccov-0002** [INVERTED]: `cost` (A 3-minute transatlantic call cost ~$12 in 1950 under a regulated monopoly carrier structure.) → `trust` (Near-zero call-initiation cost enabled scam/robocall volume at a scale that makes caller verification, not connection cost, the binding constraint on a call's value.) [OBSERVED]
- **ccov-0003** [SHIFTED]: `regulation` (McFadden Act (1927), extended by the Douglas Amendment (1956), confined national banks and bank holding companies to branching within their home state.) → `regulation` (A deposit-concentration cap (10% national / 30% state) replaces the geographic branching prohibition as the binding regulatory limit on large-bank expansion.) [OBSERVED]
- **ccov-0004** [SHIFTED]: `cost` (Solar PV modules cost ~$106/watt (inflation-adjusted) in 1976, restricting deployment to niche non-grid applications.) → `labor_cost` (Installation, permitting, and customer-acquisition ('soft') costs now account for 45-60% of total residential system cost and are cited by NREL as the largest, most persistent contributor to solar pricing -- the module cost constraint weakened while the labor/coordination constraint around deploying it did not fall at a comparable rate.) [OBSERVED]
- **ccov-0005** [SHIFTED]: `labor_cost` (Break-bulk cargo required manual loading/unloading by longshore gangs, costing about $5.83 per ton in 1956, with ships spending roughly as much time in port as at sea.) → `infrastructure_availability` (Landside drayage trucking capacity and chassis availability, not dockside handling labor, is now cited as the binding constraint on container flow through major US gateways, with chassis shortages reported to push container dwell times past 20 days at ports like LA-Long Beach and Memphis (trade-press sourcing, moderate confidence).) [OBSERVED]
- **ccov-0006** [SHIFTED]: `search_cost` (Taxi dispatch relied on drivers cruising and passengers street-hailing with no shared location information; Buchholz (2022) estimates roughly 53,000 NYC riders/day failed to find a cab due to this search friction, and London's 'The Knowledge' (required since 1865) required drivers to memorize ~25,000 streets as a substitute for navigation technology.) → `labor_cost` (Regulatory utilization-rate rules and algorithmic wage-setting on the driver/labor side (NYC TLC's 2024 minimum-pay rule and its 53% utilization threshold; documented algorithmic lockouts) are now the actively contested constraint, replacing rider-side search friction as the industry's binding problem.) [OBSERVED]
- **ccov-0007** [SHIFTED]: `capital_requirements` (Running a workload required buying/building servers, racks, power, and cooling ahead of demand, with provisioning taking IBM-benchmarked 'weeks' per resource and typical enterprise data-center utilization around 20%, driving chronic overprovisioning for peak loads.) → `cost` (FinOps-quantified cloud waste (~$44.5B projected 2025 enterprise waste), hyperscaler egress-fee lock-in serious enough to trigger a formal UK CMA investigation (opened Oct 2023), and GPU/data-center power scarcity for AI workloads are now cited as the binding constraints, replacing capex/provisioning-lead-time as the dominant problem.) [OBSERVED]
- **ccov-0008** [SHIFTED]: `cost` (A 36-exposure roll of film plus 1-hour processing cost about $12.99 in 1994 (~$28 today), with no in-field feedback until the film was developed; Kodak controlled roughly 90% of the US film market and 85% of camera sales at its peak.) → `consumer_behavior` (Curation/attention overload (Popsa's 8,000-consumer survey found the large majority of smartphone photos never revisited) and image authenticity/verification concerns (AI-generated/deepfake incidents up roughly 900% 2023-2025, prompting the C2PA provenance-standard effort) are cited as replacement constraints, though both rest on weaker source tiers (a vendor consumer-report and a vendor consortium) than the cloud or banking cases in this corpus.) [OBSERVED]
- **ccov-0009** [SHIFTED]: `regulation` (Banking required in-person branch visits for identity verification, cash handling, and complex-transaction advice, and this was reinforced by regulation: the McFadden Act (1927) and state-level branching restrictions confined most banks to intrastate branching into the 1970s-1990s.) → `trust` (Account-takeover/fraud risk that scales with digital-only access (Sift's Q3 2025 index found a 2.5% attack rate, up year-over-year, with $2.9B in losses and financial services the top-targeted sector) is now cited as the binding constraint, alongside a persistent, still-growing legacy problem: 3,629 'banking deserts' affecting 12.3 million Americans as of mid-2024, up from 2019, with majority-Black areas losing branches at nearly double the national closure rate.) [OBSERVED]
- **ccov-0011** [SHIFTED]: `energy` (Incandescent bulbs converted less than 5% of consumed energy into visible light (13-18 lumens/watt) and lasted only about 1,000 hours, requiring frequent replacement and generating significant waste heat that constrained fixture and HVAC design.) → `light_pollution` (Rising light pollution (9.6%/year global sky-brightness growth per peer-reviewed citizen-science data) and circadian/health effects from blue-rich LED spectra (AMA 2016) are now cited as the binding externality, replacing per-lumen energy/labor cost as the constraint industry and regulators are actively responding to.) [OBSERVED]
- **ccov-0012** [SHIFTED]: `distribution_access` (Physical-format manufacturing, distribution, and radio-airplay gatekeeping bundled the constraint on getting music to listeners; CD manufacturing cost roughly $1-4.50 per disc against $15.99-18.99 retail prices in the 1990s, with radio airplay functioning as the primary discovery gatekeeper for new artists.) → `algorithmic_curation_control` (Algorithmic/platform gatekeeping (peer-reviewed literature documents Spotify's hybrid editorial-algorithmic curation acting as a discovery gatekeeper) and per-stream royalty economics ($0.003-$0.005/stream, per Spotify's own published rates) are now cited as the binding constraint on whether music-making is economically viable, replacing physical manufacturing/distribution access.) [OBSERVED]
- **ccov-0013** [INVERTED]: `infrastructure_availability` (The electric grid was engineered for one-way power flow from centralized, dispatchable generators to passive loads, with IEEE 1547-2003 written for a low-penetration scenario where distributed generation was insignificant enough to simply disconnect if it threatened stability.) → `infrastructure_availability` (Interconnection-queue/hosting-capacity backlog (LBNL: ~2,300 GW queued nationally, 55-month median wait) and inverter-based-resource fault-ride-through reliability (NERC-documented 2022 Odessa and 2023 Western Interconnection disturbance events) are the new binding constraints created by the abundance of distributed, inverter-connected generation the grid was never engineered for.) [OBSERVED]
- **ccov-0014** [SHIFTED]: `distribution_access` (Finite shelf/floor space per store bounded how large a catalog a retailer could stock, and geographic reach was limited to a store's drive-time catchment area; slotting fees (averaging ~$1,500 per store per SKU, originating in the 1980s) are a direct market response to this scarcity, significant enough to draw a formal 2003 FTC industry study.) → `logistics_speed_cost` (Last-mile delivery cost (50-53% of total e-commerce shipping cost, per Dropoff/Radial industry data) and 'digital shelf space' - Amazon's paid-placement advertising generated over $46 billion in 2023, with an independent study finding roughly half of the first 25 Amazon search results were paid placements - are now cited as the binding replacement constraints, direct successors to physical slotting fees.) [OBSERVED]

## Strongest quantitative changes

- **ccov-0001**.`cost` [ORDER_OF_MAGNITUDE]: 95000000 → 550 USD per genome, ratio=5.789e-06
- **ccov-0002**.`cost` [ORDER_OF_MAGNITUDE]: 12 → ~0 (bundled/marginal) USD per call
- **ccov-0003**.`geographic_reach` [ORDER_OF_MAGNITUDE]: single state → nationwide, subject to concentration cap n/a
- **ccov-0004**.`cost` [ORDER_OF_MAGNITUDE]: 106 → 0.38 USD per watt (module only), ratio=0.003585
- **ccov-0004**.`scale` [ORDER_OF_MAGNITUDE]: niche/off-grid only → grid-competitive, mass residential/utility deployment n/a
- **ccov-0008**.`film_roll_sales` [ORDER_OF_MAGNITUDE]: 800000000 → 20000000 rolls per year, ratio=0.025
- **ccov-0012**.`streaming_share_of_us_revenue` [ORDER_OF_MAGNITUDE]: 0 → 84 percent of US recorded-music revenue
- **ccov-0013**.`distributed_pv_capacity` [ORDER_OF_MAGNITUDE]: 0 → 41 GW (US distributed PV)
- **ccov-0014**.`ecommerce_share_of_us_retail` [ORDER_OF_MAGNITUDE]: 0.9 → 16.4 percent of total US retail sales, ratio=18.22
- **ccov-0005**.`labor_productivity` [MULTIPLE_X]: 0.837 → 4.234 tons per man-hour, ratio=5.059
- **ccov-0006**.`weekday_pickups_within_10min` [MULTIPLE_X]: 40 → 90 percent of pickups within 10 minutes, ratio=2.25
- **ccov-0007**.`infra_spend_37signals_case` [MULTIPLE_X]: 3200000 → 1300000 USD per year, ratio=0.4062
- **ccov-0011**.`luminous_efficacy` [MULTIPLE_X]: 15 → 107 lumens per watt, ratio=7.133

## Still-binding constraints

- **ccov-0010**: `minimum_economic_scale` on producing a plastic part at production volume (thousands to tens of thousands of units) — current evidence: Protolabs, '3D Printing Trend Report 2024' (700+ engineers/designers/manufacturers surveyed) (2024); Formlabs / hlhrapid.com cost-comparison synthesis (2024-2025)

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
- **ccov-0005**:
  - Several core THEN/NOW figures ($5.83/$0.16 per ton, 0.837/4.234 tons/man-hour, port:sea time ratio) came through secondary aggregators rather than Levinson's book or PMA/ILWU primary data directly; a follow-up pass should verify against primary sources.
  - No government/FMC/BTS source was found for the current landside drayage/chassis bottleneck claim; it rests on trade-press reporting only.
  - No current-decade $/ton labor-cost figure was found for container handling to directly compare against the 1956 baseline.
- **ccov-0006**:
  - Buchholz's 53,000/day figure could not be directly re-measured in the same units post-app-saturation; the 'NOW' comparison bridges a different methodology (Cramer-Krueger utilization study, a separate wait-time study), not an apples-to-apples remeasurement.
  - Cramer & Krueger and Frechette/Lizzeri/Salz both attribute Uber's efficiency edge to multiple simultaneous factors (matching technology, platform scale, deregulated entry, surge pricing), so GPS/matching technology alone cannot be cleanly isolated as the sole cause of the improvement.
  - Research is US/UK-centric (NYC, London); non-Anglophone taxi/dispatch markets were not examined.
- **ccov-0007**:
  - Capex/lead-time was never the sole historical constraint: AWS's own origin narrative foregrounds scarce engineering/operational expertise as much as capital, and utilization/waste was a distinct co-occurring problem even before cloud existed.
  - No independent, non-vendor TCO comparison across workload types was found; the 37signals case is a single, well-documented data point, not a representative sample.
  - Whether GPU/power scarcity is a temporary supply-chain condition or a structural new bottleneck was not resolved.
- **ccov-0008**:
  - The then/now film-sales comparison mixes a US-only 1999 baseline (800M rolls/year) with a global 2023 figure (20M rolls/year); a true apples-to-apples US-only or global-only series was not found.
  - The actual mass-market camera collapse (94% shipment decline 2010-2023) was driven by smartphones displacing dedicated digital cameras - a second, later, distinct disruption from the original film-to-digital transition; this case may really be two separate constraint migrations compressed into one.
  - The 'new bottleneck' sourcing (curation overload, authenticity/deepfakes) is weaker-tier (vendor survey, vendor consortium) than other cases in this corpus and deserves independent replication.
  - Kodak's decline is attributed by retrospectives to a mix of factors (cannibalization fear, R&D mismanagement, pension burden), not the film constraint alone - the popular 'Kodak was blind to digital' story is oversimplified.
- **ccov-0009**:
  - The two branch-count series used here (73,649 industry-wide for 2025 vs. 68,632 FDIC-insured-commercial-only for 2024) disagree in absolute level, likely due to differing institutional scope; a primary FDIC BankFind/Summary of Deposits pull would resolve this.
  - No pre-2020 baseline for account-takeover fraud rate was found, so the 'how much did fraud risk grow relative to the branch era' comparison is qualitative, not quantitative.
  - The unbanked-household rate (4.2% in 2023) is attributed mainly to insufficient funds, not digital-access barriers, complicating a clean 'digital replaced physical access' narrative for that specific sub-population.
- **ccov-0010**:
  - Break-even volume between 3D printing and injection molding varies roughly 50x across sources (250 to 13,050 parts) depending on assumed part complexity and tooling cost; a single controlled study, not aggregated industry-blog claims, is needed for a precise figure.
  - Two AM-specific technical limitations were found that likely explain persistence of the tooling constraint rather than replace it: material anisotropy (printed parts show 3-4x lower compressive strength than cast/molded parts in some materials-science literature) and fixed, non-scaling throughput per part - these keep AM out of high-volume production regardless of price, but are not modeled here as a replacement_constraint since the original tooling/MOQ constraint has not itself been displaced.
  - Metal AM (distinct from polymer/FFF) was not researched separately and may show a different trajectory - aerospace's reported 74% AM adoption in 2024 hints at this.
  - No time series was found showing how the AM-vs-injection-molding break-even point has moved over time (e.g., 2015 vs. 2020 vs. 2025); only cross-sectional snapshots exist.
- **ccov-0011**:
  - A precise, authoritative year-by-year LED retail price curve was not obtained (a specific OSTI/CLASP dataset exists but could not be fetched in this pass).
  - No clean decomposition was found for how much 2012-2020 LED adoption is attributable to the EISA 2007 mandate versus organic market/cost dynamics - the two ran concurrently.
  - Lighting still accounts for roughly 17% (2018 CBECS-based EIA estimate) to 30-40% (other industry estimates) of commercial building electricity use; a rebound effect (Fouquet & Pearson 2006 found ~40,000x growth in lighting consumption 1800-2000 as price fell) means aggregate lighting energy use has not fallen proportionally even as per-lumen cost collapsed.
  - Incandescent's historical dominance was itself not purely efficiency-driven - gas-lighting infrastructure competition and low manufacturing cost were at least co-equal factors, per DOE and industry-history sourcing.
- **ccov-0012**:
  - Whether piracy (Napster) actually caused the 1999-2015 revenue collapse is a live, unresolved academic dispute: Oberholzer-Gee & Strumpf (2007, Journal of Political Economy) found file-sharing's effect on album sales statistically indistinguishable from zero, but a published rebuttal (Econ Journal Watch) argues their methodology is flawed - the 'Napster killed the industry' story cannot be taken as settled.
  - Physical distribution has not fully disappeared: US vinyl revenue reached ~$1.4B in 2024, its 18th consecutive year of growth and the highest since 1984, and Asia (particularly Japan) retains a much larger physical-format share than the US/UK-centric narrative implies.
  - Manufacturing cost was a minor share (roughly 5-25%) of 1990s CD retail price, suggesting distribution/marketing/radio-gatekeeping access - not raw manufacturing cost - was the more dominant historical constraint; the 'CD manufacturing was expensive' framing may itself be an oversimplification.
  - No single authoritative RIAA historical revenue-by-format time series was directly retrieved (riaa.com fetch blocked); figures here are search-synthesized from secondary reporting.
- **ccov-0013**:
  - No precise pre-2010 baseline for interconnection-queue wait times was found, so the exact scale of the 55-month current median wait relative to history is not established.
  - Whether 'grid stability' was ever the sole dominant historical constraint is questionable: institutional/regulatory conservatism (AEI/Knowledge Problem commentary on utility incentives) appears to be a co-cause alongside genuine inverter-based-generation physics, not physics alone.
  - Smart inverters demonstrably relieved the constraint in at least one documented local case (Hawaiian Electric cleared over 2,500 Oahu interconnection applications using Enphase smart microinverters), showing the technology can work - the aggregate curtailment/reliability picture is nonetheless still getting worse, not better, as of the most recent (2024) data.
  - No source was found directly comparing the cost of achieving grid stability at high DER penetration today versus under the old centralized-dispatch model.
- **ccov-0014**:
  - At the whole-economy level, 83-85% of US retail dollars still transact in physical stores as of 2025, and even a leading e-commerce-forward retailer (Target) fulfills the overwhelming majority of its 'online' orders through its physical store network; STILL_BINDING is a defensible alternate read of this case at the aggregate-economy level rather than SHIFTED.
  - Intermediate-year e-commerce-share figures are inconsistent across sources (e.g. one aggregator's '15.5% for 2019' vs. '19.1% for 2021'); this was not reconciled against a raw Census MRTS historical series, which could not be fetched directly in this research pass.
  - No category-by-category longitudinal (2000-2025) dataset was found, only recent-year snapshots; category-level online penetration varies enormously (electronics ~54-56% vs. grocery ~26% or less).
  - Last-mile delivery cost, return-rate/reverse-logistics cost, and digital-ad-driven visibility scarcity are all simultaneously cited as new frictions in the sources found, so clean single-factor attribution for 'the' new bottleneck is not really possible.
  - Whether slotting-fee dollar amounts have risen, fallen, or stayed flat in real terms since the 1980s baseline was not found - only that the practice persists essentially unchanged.

## Possible conflicts (0)

Current records that share the same (constraint_family, domain, constrained_activity) but disagree on current_constraint_state. Neither is overwritten; both are listed here for a human to reconcile.

_None this run._


