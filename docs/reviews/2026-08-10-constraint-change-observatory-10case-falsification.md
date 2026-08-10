# Constraint Change Observatory — 10-Case Falsification Study, run 2026-08-10

**Scope note:** this is a research/data addition only. No code in
`constraint-change-observatory/` was modified — `schema.py`, `validator.py`,
`ledger.py`, `report.py`, `intake.py`, and the CLI are exactly as merged in
PR #25. The 10 new records were built with the real `ConstraintChangeRecord`
dataclasses and passed through the real `validate()` function before being
appended via the existing `add` CLI. This document is the cross-case
analysis the task asked for; it is prose, not a new pipeline component.

**Corpus:** 14 records — the 4 probe records from PR #24
(`ccov-0001`..`ccov-0004`) plus 10 new records (`ccov-0005`..`ccov-0014`)
researched for this study, one per historical case listed in the task.
Full per-case reconstructions (THEN / OLD BOTTLENECK / ADAPTATION / CHANGE /
NOW / NEW BOTTLENECK / LEGACY ARCHITECTURE / falsification search /
sources / unresolved questions) live in the `current_evidence`,
`change_evidence`, `historical_evidence`, and `unresolved_questions` fields
of each record in `data/constraints.json`; this document summarizes and
cross-analyzes them rather than repeating them in full.

---

## 1. Corpus at a glance

| record_id | case | current_constraint_state | replacement_constraint evidence_status |
|---|---|---|---|
| ccov-0001 | DNA sequencing cost | SHIFTED | OBSERVED |
| ccov-0002 | long-distance telephony | INVERTED | OBSERVED |
| ccov-0003 | interstate bank branching (regulatory) | SHIFTED | OBSERVED |
| ccov-0004 | solar PV module cost | SHIFTED | OBSERVED |
| ccov-0005 | containerization | SHIFTED | OBSERVED |
| ccov-0006 | GPS/smartphones + taxi dispatch | SHIFTED | OBSERVED |
| ccov-0007 | cloud computing vs on-premise | SHIFTED | OBSERVED |
| ccov-0008 | digital photography vs film | SHIFTED (lower confidence) | OBSERVED |
| ccov-0009 | online/mobile banking vs branches | SHIFTED | OBSERVED |
| ccov-0010 | 3D printing vs tooling/batch size | **STILL_BINDING** | n/a (no replacement claimed) |
| ccov-0011 | LED lighting | SHIFTED | OBSERVED |
| ccov-0012 | music: physical → streaming | SHIFTED | OBSERVED |
| ccov-0013 | distributed solar/batteries/inverters (grid) | INVERTED | OBSERVED |
| ccov-0014 | e-commerce vs physical retail | SHIFTED | OBSERVED |

State counts: **SHIFTED 11/14 (79%)**, **INVERTED 2/14 (14%)**,
**STILL_BINDING 1/14 (7%)**, **WEAKENED 0/14**, **INSUFFICIENT_DATA 0/14**.

---

## 2. Answers to the 10 cross-case questions

**1. How often does a major reduction in Constraint A actually make
Constraint B dominant?**
13/14 (93%) show Constraint A weakening with a specifically-cited,
evidence-backed Constraint B named as newly binding. But "dominant" needs a
caveat: in several of those 13 (cloud computing, online banking, e-commerce,
digital photography) the replacement constraint is dominant only in a
growing or frontier segment of the domain, while the old constraint remains
materially present in the bulk of it — 37signals still finds owned hardware
cheaper for a stable workload; banking branches remain relevant for
customers 45+ and complex lending; 83–85% of US retail dollars still
transact in physical stores in 2025. A stricter reading that requires the
new constraint to dominate the *whole* domain, not just its growing edge,
would put clean full-domain migration closer to 8–9/14, with the rest
showing partial, segment-level migration.

**2. How often does the original constraint simply remain binding?**
Strictly STILL_BINDING: 1/14 (7%, 3D printing). A softer count that credits
the "shifted at the frontier, still binding in the bulk" pattern above adds
several partial cases (cloud, banking, e-commerce, photography) where
STILL_BINDING is a defensible alternate label for the domain as a whole —
this is noted explicitly in each of those records' `unresolved_questions`
rather than silently resolved one way.

**3. How often is the constraint genuinely WEAKENED without an obvious
replacement?**
**0/14.** This is a real finding, not an oversight: across all 14 cases in
this corpus, no record qualified for a clean WEAKENED verdict — every case
where the original constraint eased also turned up a specifically-cited
replacement constraint (or, in one case, didn't ease at all). Either (a)
the case list, chosen for canonical "technology disrupted X" narratives,
is intrinsically biased toward migration stories, or (b) once a constraint
eases enough to matter economically, some other constraint reliably
becomes newly binding. The corpus as constructed cannot distinguish these
two explanations — see §4 and the verdict in §6.

**4. How often does abundance create an inverse problem (INVERTED)?**
2/14 (14%): long-distance telephony (near-zero call cost enabled robocall
volume large enough that caller trust, not connection cost, now binds) and
distributed solar/grid (cheap, abundant distributed generation produced
record curtailment, a 2,300 GW interconnection queue, and NERC-documented
inverter-reliability incidents). Both share a shape: the constraint didn't
just weaken, it collapsed toward zero/abundance, and a *previously
negligible* problem — spam at scale, or grid instability from generation
volume the system was never sized for — became the new binding constraint
specifically *because* of that abundance.

**5. Is bottleneck migration a meaningful recurring phenomenon, or are we
imposing a narrative on unrelated histories?**
Directionally real, but this corpus cannot yet settle it cleanly. In favor
of "real": 13/14 replacement-constraint claims rest on named, checkable
sources (NERC, LBNL, FDIC, Census, RIAA, Sift, Protolabs, FERC, AMA), not
vibes, and one case (3D printing) failed to show migration despite the
same research protocol actively looking for it — the protocol is not
incapable of returning a negative result. Against "real" (or at least
against treating this corpus as proof): every case was pre-selected
because it is a well-known disruption story; a corpus assembled from
canonical "technology changed everything" examples cannot establish a base
rate for constraint migration in general. See §5 for the strongest
narrative-risk concern (evidence-status conflation).

**6. In how many cases is NEW BOTTLENECK directly OBSERVED versus merely
INFERRED?**
**13/13** replacement_constraint records that exist in this corpus are
marked `evidence_status = OBSERVED`; **0 are INFERRED.** This is flagged
here as a corpus-level caution rather than a strength. Several of these
OBSERVED claims rest on notably weaker source tiers than others — digital
photography's "curation overload" and "authenticity" replacement
candidates are sourced to a vendor consumer survey and a vendor consortium,
and the case record itself says so — yet they were still coded OBSERVED
because a citation existed, using the same evidence-status value as
regulator-grade sources like NERC or FDIC. The schema's OBSERVED/INFERRED
distinction is being used here as "a citation exists" rather than "the
causal claim is well-established," and a 13-for-13 OBSERVED split across
sources of visibly uneven strength is itself evidence that distinction
wasn't applied with enough discrimination in this batch.

**7. In how many cases is there evidence the industry/business architecture
still reflects the old bottleneck?**
**10/14 (71%)** carry a specific, named, still-existing legacy structure
with direct citation: the ILA container-royalty system and 2024 automation
fight (containerization); medallion caps and London's "Knowledge" test
(taxi/GPS); regulated-industry on-premise mandates (cloud); Nikon's
F-mount and "full-frame" terminology (photography); the CRA's 2023 rule
rewrite and persistent, growing banking deserts (banking); the Protolabs
survey's own 67%/21% prototyping-vs-end-use split (3D printing — the
current-state evidence *is* the legacy-architecture evidence here); the
Edison screw base (LED lighting); F.B.T. v. Aftermath Records litigation
and album-equivalent-unit accounting (music); FERC Order 2006's "ten
screens" and California's forced NEM 3.0 tariff rewrite (solar/grid); and
slotting fees plus Target's 97%-fulfilled-via-stores figure (e-commerce).
The remaining 4/14 are the original probe records, which predate this
task's explicit LEGACY ARCHITECTURE reconstruction step and were simply
not probed for it — their gap is INSUFFICIENT_DATA, not a negative result.

**8. Are there identifiable conditions under which bottleneck migration is
especially likely?**
One pattern is visible across this small corpus: migration (SHIFTED or
INVERTED) shows up specifically when the eased constraint was a
market/priced, regulatory, or informational constraint (cost, geography,
matching friction, distribution access) — something with a discoverable
price or policy signal. The one STILL_BINDING case, 3D printing, is
different in kind: it hit a hard *materials-physics and process-throughput*
limit (documented anisotropic strength loss, fixed non-scaling per-part
cycle time) rather than a cost or access barrier. On this single
falsifying data point, migration looks more likely for
market/regulatory/informational constraints than for constraints rooted in
materials physics or fixed process throughput — a hypothesis this corpus
is far too small to confirm, but concrete enough to test with a
deliberately chosen next batch of physics-bound cases (e.g. battery energy
density, desalination thermodynamics, semiconductor lithography limits).

**9. What is the strongest counterexample to our hypothesis?**
**3D printing / additive manufacturing vs. tooling and minimum economic
batch size (ccov-0010), STILL_BINDING.** It is the strongest counterexample
for three reasons: (a) it rests on a direct, present-day, head-to-head cost
comparison at a real production volume — injection molding remains
roughly 7x cheaper per part than 3D printing at 10,000 units — not an
indirect inference; (b) it has direct current-state survey evidence (a
2024 Protolabs survey of 700+ manufacturing professionals) showing the
disruptive technology is used by two-thirds of respondents for
*prototyping*, not production, meaning it created an adjacent capability
without displacing the dominant economics of volume manufacturing; and (c)
it comes with two independently-cited technical reasons *why* migration
hasn't happened (material anisotropy, fixed per-part throughput), not
merely an absence of evidence for migration.

**10. Final verdict: KEEP / MODIFY / WEAKEN / REJECT?**
**MODIFY.** See §6 for the full reasoning; summary: the core pattern
recurs too often, and with too much independently-checkable evidence, to
WEAKEN or REJECT outright, and a real falsifying case was found rather
than failing to look for one. But the hypothesis as stated is cleaner than
what the evidence actually shows, and should be revised before further
use — not simply kept as-is.

---

## 3. The separate test: constraint migration vs. business-architecture lag

The task asked these to be tested as distinct phenomena, not assumed
identical. Results from this corpus:

- **Migration without any found legacy-architecture lag:** none clearly
  identified. Every SHIFTED/INVERTED case that was explicitly probed for
  legacy structure (all 10 new cases) turned up at least one still-existing
  structure built for the old constraint. The 3 SHIFTED/INVERTED cases from
  the original probe batch (ccov-0001, ccov-0002, ccov-0004) were not
  probed for this dimension and are INSUFFICIENT_DATA on it, not evidence
  of a clean, lag-free transition.
- **Migration with legacy-architecture lag persisting (the intersection the
  task flags as most important):** found, with direct citation, in **9 of
  the 10 new SHIFTED/INVERTED cases** (all except LED lighting, where the
  only legacy evidence found — the Edison screw base — is a comparatively
  minor, non-economic form-factor legacy rather than a load-bearing
  business structure).
- **No migration at all (architecture-lag concept does not apply):** 3D
  printing. Since the underlying constraint never weakened, describing the
  continued dominance of tooling-based manufacturing as "lag" would be
  wrong — per the Protolabs/cost-comparison evidence, it is still the
  economically correct choice, not inertia.

Read plainly, "constraint migrated while legacy architecture persists" is
not the rare intersection the task's framing anticipated — in this corpus
it is closer to the *default* outcome whenever migration happens at all
(9/10). That itself deserves skepticism rather than uncritical acceptance:
it may mean either (a) legacy structures are simply ubiquitous in any
sufficiently large, regulated, or capital-intensive industry regardless of
whether they were specifically built for the constraint in question — a
much weaker and more general claim than "this structure was built for the
old constraint and never re-examined" — or (b) the research protocol's
explicit instruction to search for legacy architecture in every case
produced a demand effect, since researchers who are told to find something
and are graded (implicitly) on finding it tend to find it. This corpus
cannot rule out (b), and it is flagged here rather than smoothed over.

---

## 4. Strongest supporting case

**Distributed solar + batteries + smart inverters (ccov-0013), INVERTED.**
This is the strongest positive case, not e-commerce or cloud computing,
because it shows the *cleanest, most mechanistically specific* version of
the pattern: the same abundance (41 GW of distributed PV, 13+ GW of CAISO
batteries) that eased the original scarcity is *directly, mechanistically*
what created both new binding constraints — the interconnection-queue
backlog (LBNL: ~2,300 GW queued nationally) exists because so much
generation now wants to connect, and the inverter-based-resource
reliability problem (NERC's documented 2022 Odessa and 2023 Western
Interconnection events) exists because so much of that connected capacity
is inverter-based rather than synchronous. This is not two loosely
associated facts; the replacement constraint is a direct causal
consequence of the same volume increase that eased the original one — the
strongest form the hypothesis can take. It is also honestly reported: the
record explicitly notes that smart inverters *did* work in at least one
documented local case (Hawaiian Electric/Enphase), so the case doesn't
overstate its own strength.

---

## 5. Strongest counterexample and false-positive / narrative-risk analysis

The strongest counterexample is 3D printing (§2, Q9); it is not repeated
here. The broader false-positive risk in this corpus has three parts,
stated plainly:

1. **Case-selection bias.** All 14 cases (the original 4 and the 10 added
   here) were chosen because they are well-known "technology changed
   everything" stories. A hypothesis about bottleneck migration tested
   only against pre-selected migration-flavored examples cannot establish
   how often migration happens in general — only how often it happens in
   stories already famous for exhibiting it. The one genuine null result
   (3D printing) shows the protocol *can* return a negative finding, which
   is reassuring but not sufficient: a fair test needs a batch of cases
   chosen for some property *other than* "known disruption narrative."

2. **Evidence-status conflation (§2, Q6).** Every replacement_constraint
   claim in this corpus is marked OBSERVED, including ones the underlying
   case record itself flags as resting on weaker source tiers (digital
   photography's curation-overload and authenticity claims). A taxonomy
   that never uses one of its own two "confidence" values across 13
   instances of varying real strength is not discriminating the way it is
   meant to. This is a process finding about how this batch was analyzed,
   not a change proposed to `validator.py` or `schema.py` — no code was
   touched, per this task's boundary — but it should inform how the next
   batch's analyst applies OBSERVED vs. INFERRED.

3. **Frontier-vs-whole-domain conflation (§2, Q1–Q2).** Several SHIFTED
   verdicts (cloud, banking, e-commerce, photography) describe a
   constraint that is genuinely easing at the growing edge of a domain
   while remaining materially binding across most of that domain's actual
   volume today. Coding these as a flat SHIFTED, rather than something like
   "SHIFTED at the frontier, STILL_BINDING in aggregate," compresses a
   real, important nuance into a binary the schema doesn't currently
   distinguish. Each affected record documents this honestly in its own
   `unresolved_questions`, but the cross-case counts in §1–2 would look
   different under a stricter standard, and a reader should not take the
   79% SHIFTED figure as if it meant "fully and uniformly shifted" in 11
   of 14 domains.

None of these three risks were found to actually overturn any individual
record's verdict on re-examination — they are corpus-level cautions about
how confidently the aggregate percentages in §1–2 should be read, not
retractions of specific findings.

---

## 6. Verdict and recommendation

**Verdict: MODIFY.**

The evidence across 14 cases is too consistent, and too often backed by
independently-checkable regulator/agency/peer-reviewed sources, to WEAKEN
or REJECT the hypothesis. A genuine falsifying case (3D printing) was
found by actively looking for one, which is itself evidence the research
protocol is not simply confirming whatever it's pointed at. But KEEP
(unchanged) would overstate how clean the result is: the hypothesis as
originally stated doesn't distinguish frontier-segment migration from
whole-domain migration, doesn't anticipate that legacy-architecture
persistence would turn out to be close to the *default* companion of
migration rather than a rare intersection, and the case list itself was
not sampled in a way that can establish a base rate. Recommended
modifications for the hypothesis's next iteration:

- Explicitly allow "migrated at the frontier, still binding in aggregate"
  as a named, first-class intermediate outcome rather than forcing every
  case into a domain-wide binary.
- Treat "legacy architecture persists after migration" as the expected
  default finding to be reported, not a rare, notable intersection to be
  specially flagged — and correspondingly raise the bar for what counts as
  a *meaningful* instance of it (e.g., a structure demonstrably built
  *for* the old constraint and *never revisited*, vs. any structure that
  merely still exists in a regulated or capital-intensive industry).
- Any future case batch intended to test the hypothesis's general validity
  (rather than illustrate it) should include cases *not* pre-selected as
  famous disruption stories, and ideally cases chosen for a shared
  property orthogonal to "did the constraint migrate."

**Is there enough evidence to begin connecting Constraint Change
Observatory to Business Candidate Analyst Mode B? No, not yet.**

Three concrete gaps stand between this corpus and that connection: (1) the
case-selection bias in §5.1 means we do not yet know Constraint Change
Observatory's true positive-prediction rate outside of pre-selected
disruption narratives — wiring it into a business-candidate generator
would inherit that bias directly into candidate generation; (2) the
evidence-status conflation in §5.2 means "OBSERVED replacement_constraint"
currently cannot be trusted, on its own, to distinguish a
regulator-grade finding from a vendor-survey-grade one — a Mode B
consumer would need that distinction to weight candidates sensibly; and
(3) no independent adversarial review (in the style of
`docs/reviews/2026-08-08-cross-source-candidate.md`) has yet been run
against a sample of this batch's SHIFTED/INVERTED calls — 13-for-13
agreement from the same research-and-transcription pipeline that
generated the hypothesis is a weaker form of confirmation than an
independently adversarial second pass. Recommend: (a) run a second,
differently-sampled case batch specifically to estimate a base rate; (b)
tighten evidence-status discipline in the next analyst pass, even without
changing the schema; (c) commission at least one adversarial review of a
sample of this batch's records before any Mode B integration work begins.
This document is that recommendation; it does not itself constitute the
review.

---

*Analyst: Claude (directed research + cross-case analysis pass), human
review pending per design doc §18. No `constraint-change-observatory`
source files were modified in the course of this study.*
