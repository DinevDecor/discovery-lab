# REAL-CASE-001 — Evidence Pack

**Candidate:** EU plastic pellet certification capacity / accreditation calendar opportunity
**Research date (as_of for every item below unless stated otherwise):** 2026-08-16
**Researcher note on access constraints:** This session's network egress policy blocks
direct `WebFetch` access to `eur-lex.europa.eu`, `consilium.europa.eu`,
`environment.ec.europa.eu`, and every other external domain tried (including
`en.wikipedia.org`, law-firm sites, and certification-body sites) — confirmed by
repeated `EGRESS_BLOCKED` errors, not worked around. Every fact below was obtained
through the `WebSearch` tool's own aggregation, which cites and quotes primary sources
(EUR-Lex, Council of the EU, European Commission) but could not be independently opened
and read in full by this session. This is a **material limitation** stated once here and
applied consistently below: facts corroborated by multiple independent secondary sources
that explicitly cite/quote the primary text are marked **OBSERVED** with this caveat
noted; single-source or paraphrased claims are marked **INFERRED**; anything not
found or not specific enough to support a number is **INSUFFICIENT_DATA** — never
filled in with a plausible-sounding guess.

Legend: **[O]** Observation (raw fact, cited) · **[E]** Evidence (supports a specific
model field) · **[I]** Inference (reasoning from [O]/[E], not itself sourced) · **[ID]**
INSUFFICIENT_DATA (explicitly not found / not specific enough).

---

## 1. Exact regulatory obligation and affected operators

**[O]** Regulation (EU) 2025/2365 of the European Parliament and of the Council, "on
preventing plastic pellet losses to reduce microplastic pollution," was published in
the Official Journal of the European Union; multiple independent sources (Council of
the EU press release summary, European Commission environment news page summary,
ChemRadar regulatory news, several law-firm client alerts) converge on **26 November
2025** as the Official Journal publication date. Source: WebSearch aggregation citing
`eur-lex.europa.eu/eli/reg/2025/2365/oj/eng`, `consilium.europa.eu`,
`environment.ec.europa.eu` (direct fetch blocked, see access-constraint note above).

**[O]** Scope: applies to economic operators in the EU handling **≥5 tonnes of plastic
pellets per year**, plus operators of facilities that clean plastic pellet containers
and tanks, plus carriers transporting pellets within the EU and by sea. Multiple
independent sources converge on this 5-tonne threshold.

**[E]** Feeds `CalendarAssessment.summary` / `category=accreditation_qualification`.
Does not by itself feed a numeric field.

**[ID]** Exact article numbers and full verbatim obligation text — not independently
verified against primary text this session (egress blocked). Everything above is
secondary-source paraphrase, not a direct quotation checked against EUR-Lex.

---

## 2. Exact deadline/shock date and shock_type

**[O]** Large and medium-sized operators handling ≥1,500 tonnes/year must hold a
compliance certificate by **17 December 2027**. Multiple independent sources
(Consilium summary, EC environment news summary, Hoganlovells, KHLaw, ChemRadar, an
EUR-Lex PDF search hit) converge on this date.

**[O]** A separate, earlier obligation — to avoid losses and implement containment
measures (not the certification obligation) — applies from **16 December 2025**. This
is a different obligation from the certification deadline and must not be conflated
with it.

**[E]** `shock_forecast.shock_type = DATED`, `date_bound.earliest = date_bound.latest =
"2027-12-17"`, `evidence_status = OBSERVED` (with the access-constraint caveat above).
This is a fixed date in an already-adopted, in-force Regulation, not a proposal —
methodologically the strongest kind of DATED shock this package's schema recognizes.

**[ID]** Whether "17 December 2027" is itself subject to a phase-in grace period, a
transitional derogation, or a national implementing measure that could shift it for
specific member states — not found.

---

## 3. Exemptions, alternative compliance routes, permits, EMAS or other mechanisms that suppress certification demand

**[O]** Operators registered under **EMAS** (Eco-Management and Audit Scheme) are
exempt from the third-party certification requirement **if** their EMAS verifier
verifies compliance with the pellet-loss-prevention requirements instead. Multiple
sources converge on this.

**[O]** **Micro-enterprises**, and small/medium/large enterprises handling **below**
1,500 tonnes/year, may use **self-declaration of conformity** instead of third-party
certification (a materially cheaper compliance route that removes them from
certification demand entirely).

**[I]** These are two independent, real demand-suppression mechanisms for third-party
CERTIFIER services specifically (as opposed to the underlying regulatory obligation,
which is not suppressed) — an operator using either route generates zero demand for a
new certification body's services, regardless of how the broader shock plays out.

**[ID]** What fraction of in-scope operators are already EMAS-registered, or fall
below the 1,500-tonne certification threshold — not found. This directly blocks a
defensible `demand_suppression_risk` numeric value (see section 8 below): the
mechanism is real and evidenced, its magnitude is not.

---

## 4. Exact accreditation/certifier requirements

**[O]** The industry-developed **OCS Europe** certification scheme (Operation Clean
Sweep Europe, developed by Plastics Europe and EuPC) is the explicit model the
Regulation's certification approach is built on. Under OCS Europe's own published
requirements, a certifying body must be "an independent Certification Body with
technical competence in the plastic sector," demonstrated through accreditation by an
**International Accreditation Forum (IAF) member accreditation body** for product
certification under **ISO/IEC 17065** and/or management-system certification under
**ISO/IEC 17021** "in the plastics sector."

**[O]** As of the most recent source found, "it is the intention to have the [OCS
Europe] scheme itself be accredited" — an application to **European Accreditation
(EA)** "will be made" "when appropriate." This is stated in the future/intentional
tense in the source, not as a completed fact.

**[I]** This means the *formal* accreditation of the OCS Europe scheme as the
regulation's official certification route was, as of the sources found, **not yet
confirmed complete** — a real, evidenced uncertainty about exactly when/whether the
existing voluntary scheme becomes the legally recognized one, and under what transition
terms.

**[ID]** The Regulation's own implementing/delegated acts (if any) defining the exact
legal accreditation criteria for a "certifier" under Regulation (EU) 2025/2365 itself
(as opposed to the voluntary OCS Europe scheme's own requirements) — not found; could
not verify from primary text this session.

---

## 5. Whether existing certification bodies can extend scope, and the approximate calendar process

**[O]** Multiple major, already-accredited global certification bodies are, as of this
research date, **already marketing and delivering "OCS Europe Certification" audits
today**: SGS, DQS, Bureau Veritas, BSI, and DNV all have live service pages describing
themselves as accredited providers of OCS Europe certification (found via WebSearch
snippets quoting each company's own site).

**[I]** This is the single most important adversarial finding in this evidence pack.
These are not de-novo entrants — they are existing, broadly-accredited global
certification houses (already holding ISO/IEC 17065 and/or 17021 accreditation across
many sectors) who, per the OCS Europe scheme's own stated requirement, only need to
demonstrate *sector-specific technical competence* — i.e., a **scope extension** of
existing accreditation — not a de-novo build of a certification body from zero. A
scope extension for an already-accredited, operating certification body is a
fundamentally different (and typically much faster) calendar process than a first-time
accreditation.

**[O]** General ISO/IEC 17011 accreditation-body practice (not specific to this
scheme): accreditation is not automatically transferred on ownership change; the
accreditation body reassesses/reviews when the certified body's structure or scope
changes materially. (Sources: certbetter.com, a-lign.com, schellman.com — ISO
certification consultancy commentary, not the primary ISO/IEC 17011 text, which is
paywalled and was not independently fetched this session.)

**[ID]** A specific, sourced calendar-time figure (days/months) for how long a
scope-extension audit takes for an already-accredited certification body to add
"plastics pellet / OCS Europe" scope — **not found**. General accreditation-industry
commentary suggests scope extensions are materially faster than first-time
accreditation, but no specific number for this exact scope was located.

---

## 6. Defensible L_irr for a de-novo entrant

**[ID]** **No specific, sourced calendar-time figure was found** for how long it would
take a genuinely new entity (holding no prior ISO/IEC 17065 or 17021 accreditation of
any kind) to become a first-time accredited certification body, then obtain OCS
Europe/pellet-loss scope specifically. A targeted search on Bulgarian Accreditation
Service (BAS) accreditation timelines explicitly returned no specific month-level
figure (BAS's own site describes its accreditation scope and process categories but
the search did not surface a stated turnaround time).

Per the explicit instruction not to invent a point estimate or a plausible-sounding
bound without a source: **`l_irr_denovo` is recorded as INSUFFICIENT_DATA**, not
approximated from general industry lore. This is a materially important gap, not a
minor one — see the validation report's "cheapest next evidence action."

---

## 7. Known existing or pending competitors

**[O]** Named, evidenced, currently-active competitors offering OCS Europe
certification today: **SGS, DQS, Bureau Veritas, BSI, DNV** (company service pages,
found via WebSearch). This list should be treated as a floor, not a ceiling — these
are simply the five that surfaced in the queries run; the real OCS Europe public
certified-company/certifier register (`opcleansweep.eu`) was identified but not
directly fetchable this session to get a complete, current list.

**[I]** `l_min_remaining_as_of` for a tracked "already active" competitor: qualitatively
defensible as at-or-near **zero** (they are marketing and delivering this exact
certification service today), but this is an **inference from marketing pages**, not a
confirmed accreditation-register entry naming a specific certifier as accredited under
the Regulation's own (as opposed to the voluntary scheme's) framework — recorded as
`evidence_status=INFERRED`, not `OBSERVED`, and `provenance=REPEATED`, not `MEASURED`.

**[ID]** `l_max_remaining_as_of` for any competitor — not found; not asserted.
**[ID]** `q_max` (capacity — e.g. audits/year, or tonnes of client throughput a given
certifier can cover) for any competitor — not found for any of the five named firms.
**[ID]** A complete competitor list (only five names surfaced from targeted search
queries; the full OCS Europe/EA-recognized certifier register was not accessed).

---

## 8. Defensible common real-world unit for D_shock / S_existing / S_ready

**[ID]** No source found gives a usable count of "in-scope operators requiring
third-party certification," an aggregate tonnage figure gated to the ≥1,500t/year
certification tier specifically, or a certifier-side throughput/capacity unit
(audits/year, certified-operators/year) that could serve as a common unit across
`D_shock`, `S_existing`, and `S_ready`. **No defensible common unit exists in this
evidence pack.** Per the task's own instruction and the package's methodology: **Rivalry
Index is INSUFFICIENT_DATA**, not approximated.

---

## 9. Evidence for/against transferability of accumulated accreditation/calendar progress

**[O]** General ISO/IEC 17011-adjacent accreditation-industry commentary (not
specific to this scheme; sources are ISO-consultancy blogs, not the primary ISO/IEC
17011 standard text, which was not independently fetched): accreditation/certification
is issued to a specific legal entity and scope; it does **not** automatically transfer
on ownership change, merger, or acquisition. A change of legal entity typically
requires notification to the accreditation body (commonly within a defined window,
e.g. ~30 days is cited as typical in general ISO-certification-management commentary)
and may require a certificate amendment, a full transfer review (per IAF MD 2-style
criteria: confirming accreditation/certification body scopes, transferring sites,
prior audit history), or in some cases a fresh assessment.

**[I]** This is **evidence against** easy transferability: accumulated accreditation
progress does not straightforwardly survive an acquisition/ownership-change structure
without accreditation-body review, which itself consumes calendar time not quantified
here.

**[ID]** Any pellet-loss/OCS-Europe-specific transfer rule (as opposed to general
ISO/IEC 17011 industry practice) — not found. A specific calendar-time cost for a
transfer review — not found.

---

## 10. The cheapest fatal falsification test

**[I]** Given finding #5 above (multiple major global certifiers already actively
marketing this exact certification service), the cheapest test that could kill this
candidate outright: **check the public OCS Europe certifier/certified-company register
at `opcleansweep.eu`** (identified, not fetched this session) for (a) how many
certification bodies are already listed as OCS Europe-accredited certifiers, and (b)
whether any of them already lists Bulgaria or the wider EU as covered territory. If the
register shows several already-accredited certifiers with EU-wide coverage, the
"calendar arbitrage" thesis (an exclusivity window a new entrant could exploit) is
falsified directly and cheaply — no de-novo accreditation research, no BAS inquiry, no
capital commitment required. This is a single free public-register check, cheaper than
any other item in this pack.

---

## Summary table — evidence status by model field

| Field | Value | evidence_status | provenance | Why |
|---|---|---|---|---|
| `shock_forecast.date_bound` | 2027-12-17 (DATED) | OBSERVED (with access-constraint caveat) | REPEATED | Multi-source convergence on an adopted Regulation's own date; not independently re-read from primary text this session |
| `demand.demand_obligation_certainty` | high (0.9) | OBSERVED | REPEATED | Adopted, in-force Regulation (not a proposal); multi-source convergence |
| `demand.shock_date_stability` | — | INSUFFICIENT_DATA | — | No amendment/delay-risk evidence found either way |
| `demand.deadline_relief_risk` | — | INSUFFICIENT_DATA | — | No evidence found |
| `demand.demand_suppression_risk` | — | INSUFFICIENT_DATA | — | Mechanism (EMAS, small-operator self-declaration) evidenced; magnitude not |
| `readiness.l_remaining_days` | — | INSUFFICIENT_DATA | — | No real operating entity exists behind this research candidate |
| `defensive.g_d_novo` inputs (`l_irr_denovo`) | — | INSUFFICIENT_DATA | — | No sourced de-novo accreditation timeline found |
| `defensive.tracked_competitor.l_min_remaining_as_of` | ~0 days | INFERRED | REPEATED | Inferred from marketing pages of 5 named incumbents, not a register confirmation |
| `defensive.tracked_competitor.q` | — | INSUFFICIENT_DATA | — | No capacity figure found for any competitor |
| `rivalry.d_shock` / `.s_existing` / `.s_ready` / unit | — | INSUFFICIENT_DATA | — | No defensible common unit found |
| `clock_open_date` | 2023-10-16 (Commission proposal COM(2023) 645) | OBSERVED | REPEATED | Multi-source convergence including a direct PDF hit with the Commission's own header date |
| `latest_safe_date_as_of` | — | INSUFFICIENT_DATA | — | Depends on `l_irr_denovo`, which is INSUFFICIENT_DATA |

---

## Sources consulted (via WebSearch aggregation; direct WebFetch blocked this session)

- eur-lex.europa.eu/eli/reg/2025/2365/oj/eng (Regulation (EU) 2025/2365, primary text — not directly opened)
- eur-lex.europa.eu — COM(2023) 645 final proposal text (not directly opened)
- consilium.europa.eu — Council press release, 22 Sept 2025 (not directly opened)
- environment.ec.europa.eu — Commission news page, "New law reducing microplastic pollution enters into force" (not directly opened)
- europarl.europa.eu — Legislative Train Schedule entry on microplastics (not directly opened)
- chemradar.com — regulatory news summary
- hoganlovells.com, khlaw.com, natlawreview.com — law-firm client alerts (not directly opened)
- packlab.gr, packagingeurope.com, ssw.solutions, epy.it, rigk.de — trade-press summaries
- dqsglobal.com, sgs.com, bsigroup.com, bureauveritas.dk, dnv.com — certification-body service pages (not directly opened)
- opcleansweep.eu / ocscertification.eu — OCS Europe scheme's own site (identified, not opened)
- certbetter.com, a-lign.com, schellman.com — general ISO/IEC 17011 accreditation-transfer commentary
- iafcertsearch.org, nab-bas.bg, managementsystems.world — Bulgarian Accreditation Service identification (no timeline data surfaced)

All of the above were reached only through `WebSearch` tool result summaries; none was
independently opened and read via `WebFetch` in this session (blocked by network
egress policy — confirmed, not bypassed). Anyone reviewing this evidence pack should
treat "OBSERVED" here as "corroborated by the search layer's own citations of primary
sources," not as "personally read the primary text," and re-verify directly before any
material decision.
