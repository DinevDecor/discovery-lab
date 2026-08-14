# TikTok Sensor Feasibility Spike

**Status:** research artifact only. Not integrated. Not a decision. No production code touched.
**Scope:** read-only experimental spike, per task instructions. No collector was built, no
thresholds/taxonomy/lifecycle logic was touched, nothing was added to the daily pipeline,
and no TikTok data was committed to any production corpus.
**Verdict:** `RESEARCH_ACCESS_FURTHER` — see §12.

---

## 0. How to read this document

This spike hit a hard environmental constraint partway through: **this sandboxed session's
network egress policy blocks direct outbound access to `tiktok.com` and, in fact, to every
domain outside a short allowlist** (confirmed below in §2). That is a property of *this
Claude Code environment*, not a finding about TikTok's own access controls. Per the task's
own instruction — "If a route requires credentials/access we do not have, record it as
BLOCKED rather than circumventing it" — this is recorded as BLOCKED, not worked around.

Practical effect: §§3–6 (the real public-content spike) could not be executed with live
fetches. No TikTok post, comment, creator, or quote in this document is a real, independently
verified observation. Where §§3–6 report numbers, they are honestly zero, and the reasoning
in those sections is desk research (official documentation, third-party reporting, and
`WebSearch` snippets of TikTok's own SEO pages — see §2C) rather than a verified sample. This
document says so at every point where it matters, in keeping with this repo's own rule that
model-generated content is never evidence and provenance is truthful or absent.

---

## 1. Current sensor system

Source: `constraint-archaeology-agents/config/sources.json`, `src/ca_agents/{collector,sensor,dedup,memory}.py`.

**Configured sources today:** Hacker News (Algolia newest), Lobsters, DEV.to (`discuss`,
`startup`, `entrepreneurship` tags), five subreddits (`startups`, `Entrepreneur`,
`smallbusiness`, `SaaS`, `SideProject`), Product Hunt (GraphQL, confidence-capped as a
solution/announcement signal, not a firsthand report), and five Discourse forums (Python,
Home Assistant, OpenAI Developer Community, Level1Techs, Fly.io).

### A. What current sources observe well

Every one of the above is **text, English-language, and populated by people who already
write on technical/startup forums.** The Sensor Agent's own extraction prompt
(`sensor.py`) asks for "concrete processes, handoffs, workarounds, repeated manual work,
expensive intermediaries, normalized failure, waiting, duplicated data entry, or
capability-price shifts" — and it gets them reliably when the reporter is a developer,
sysadmin, indie-hacker, or SaaS founder describing their own tooling, infrastructure, or
business-building friction. This is a **self-reported, text-native, technically fluent**
population. It is a good sensor for: developer tooling pain, infra/ops failure modes, SaaS
go-to-market friction, capability-price shifts in developer platforms.

### B. What is structurally under-observed

Nobody in `sources.json` runs a restaurant, salon, HVAC business, retail counter, clinic,
farm, or delivery route as their day job. The task's own list of target domains — trades,
hospitality, retail, beauty, healthcare operations, logistics, construction, repair,
agriculture, parenting, service businesses, repetitive manual work — maps almost exactly
onto **populations that don't post on Hacker News, Lobsters, DEV, or a Discourse forum
about Python or Home Assistant.** Even the Reddit subs (`smallbusiness`, `Entrepreneur`)
filter for people who frame their own situation *as a business problem in writing*,
which already selects for founders over front-line workers, and for people comfortable
narrating their operations in prose. A plumber describing "I still write every job on a
paper carbon pad because the app my boss bought doesn't work on site" is not a person who
shows up in any current source.

### C. What TikTok would add, structurally

Two things the current network has zero of, not partial coverage of:

1. **A visual/demonstrated evidence modality.** Every current `Capture` is prose someone
   chose to type. TikTok's native format is someone physically *showing* the workaround —
   the three open apps, the handwritten ledger, the whiteboard, the manual re-entry — which
   is a different and arguably higher-fidelity evidence type for the same
   FACT→CLAIM→EVIDENCE chain the Reality Observatory design (`docs/architecture/reality-observatory-v0.1.md`)
   describes. Note this is also an ingestion problem: `sensor.py`'s extraction step is
   built for `capture.text` — a video-native source needs a transcript/caption/ASR step to
   even produce text for the existing prompt to run on. That's a real structural gap, not
   a redesign proposal.
2. **A population that types nothing on any current source** — non-developer, physical-world,
   often lower-formal-education creators, whose only public expression of a business or
   operational constraint may be a video, not a forum post.

This section does not require live TikTok access to answer — it follows entirely from
reading `sources.json` and the extraction prompt. §§2–8 below are where live access would
have mattered, and where this spike was blocked.

---

## 2. TikTok access routes — desk research + what could be tested

### What "tested" actually means in this spike

`WebFetch` and direct `curl`/Bash networking were attempted against `tiktok.com`,
`developers.tiktok.com`, and, as a control, `example.com` and `en.wikipedia.org`. All four
were rejected identically:

```
$ curl https://www.tiktok.com/oembed?...   → CONNECT tunnel failed, response 403
$ curl https://example.com                  → CONNECT tunnel failed, response 403
WebFetch(tiktok.com)                        → EGRESS_BLOCKED
WebFetch(developers.tiktok.com)             → EGRESS_BLOCKED
WebFetch(en.wikipedia.org)                  → EGRESS_BLOCKED
WebFetch(github.com)                        → succeeded
```

The proxy status endpoint (`$HTTPS_PROXY/__agentproxy/status`) confirms this is a policy
allowlist, not a TikTok-specific block: `example.com` failed the exact same way TikTok did.
**Only `WebSearch` (Anthropic's own search backend, returning snippets rather than raw
fetched pages) was reachable in this session.** Everything below that isn't attributed to a
live test is desk research from `WebSearch` results (official docs, third-party reporting),
not a verified first-hand check.

### A. Official TikTok APIs

| Route | What it is | Access | Verdict |
|---|---|---|---|
| **Research API** | Structured read access to public profiles, videos, and **comments** | Restricted to accredited academic/non-profit researchers, in TikTok-approved regions, non-commercial only, ~4-week manual review, 1,000 requests/day, up to 100k records/day. PhD applicants need an advisor endorsement letter. | **BLOCKED (eligibility unverified).** Discovery Lab has not established academic/non-profit standing with TikTok. This is the *only* official route that returns comments, and it explicitly forbids commercial use — worth a real eligibility check before ruling it out, but not assumable. |
| **Display API** | Lets a third-party app show a **creator's own, self-authorized** videos | Requires the content owner to OAuth-authorize your app | **NOT SUITABLE.** This is the wrong tool for observing arbitrary third parties' public content — it only ever shows content the account holder has personally connected, the opposite of a discovery sensor. |
| **Content Posting API** | Publishing content to TikTok | OAuth, app review | **NOT APPLICABLE.** We want to read, not post. |
| **oEmbed** (`https://www.tiktok.com/oembed?url=...`) | Public, key-free, standard oEmbed response for a *known* video URL: title/caption text, `author_name`, `author_url`, thumbnail, embed HTML/dimensions | No auth. Documented at `developers.tiktok.com/doc/embed-videos`. | **Plausibly WORKS for enrichment, not discovery** — it needs a URL you already have, and by design returns no comments, no transcript, no engagement counts, no hashtags as a structured field, no search. **Could not be live-tested in this session** (egress blocked); the response shape above is from TikTok's own documentation and third-party oEmbed-provider listings, not a fetch I actually performed. |

### B. Public web pages (unauthenticated)

A public TikTok video page is viewable by anyone without logging in — but TikTok's Terms of
Service explicitly prohibit "scrap[ing], crawl[ing], export[ing], or otherwise extract[ing]
any data or content... using any automated system or software, including automated 'bots,'
except as approved in writing by TikTok," and the platform backs this with signed request
tokens (`X-Bogus`, `_signature`, `msToken`), canvas/WebGL/navigator fingerprinting, and
CAPTCHA challenges on automated-looking traffic. The task instructions explicitly forbid
defeating CAPTCHAs or access controls. **Verdict: what a human can view in a browser and
what can be legitimately automated diverge sharply here — this route is human-manual-only,
not automatable within this spike's constraints, and was additionally blocked at the
sandbox network layer regardless.**

### C. Search-engine discovery

This is the one sub-question actually testable from inside this session, since `WebSearch`
was reachable. Five queries were run, deliberately spanning different economic domains:

- `site:tiktok.com "day in the life" restaurant owner small business`
- `site:tiktok.com plumber electrician "we still do this manually" OR "takes hours"`
- `"tiktok.com/@" "hair salon" OR "nail salon" booking no-show workaround`
- `"tiktok.com/@" construction contractor "quote" "estimate" manual spreadsheet`

Result, consistently: search results surface TikTok's own SEO **`/discover/<topic-slug>`**
landing pages (e.g. `tiktok.com/discover/day-in-the-life-of-a-coffee-shop-owner`) and
unrelated third-party blogs almost exclusively. **Zero individual `tiktok.com/@handle/video/...`
permalinks were returned across five queries, including two that explicitly quoted the
`"tiktok.com/@"` URL pattern.** Separately, Google is reported to surface some individual
TikTok videos in a mobile search-results video carousel, but that surface is not a queryable
text index and isn't something this spike could drive systematically.

**Verdict: search-engine discovery is UNRELIABLE for systematically sampling individual
posts.** It's fine for finding *topics*, useless for finding *specific evidence*.

### D. Public creator/profile discovery

Same ToS/anti-bot posture as §B: a profile's recent-posts list is human-browsable but not
legitimately automatable at spike scale without either an approved API or crossing into the
scraping the ToS prohibits.

### E. Browser-based public access

Not testable in this session: TikTok was unreachable through this sandbox's egress policy
regardless of tool (Bash `curl`, `WebFetch`). Independent of that block, the anti-bot posture
described in §B means an automated/scripted browser session faces the same
fingerprinting/CAPTCHA wall a scraper does; a single human manually clicking through a real
browser session remains the only clearly-legitimate version of this route, and doesn't scale
to "20–50 posts across a dozen domains" as an automated or even semi-automated process.

### F. Third-party data providers (desk research only — nothing purchased or trialed)

| Provider (examples found) | Claimed coverage | Pricing (as published) | Notes |
|---|---|---|---|
| EnsembleData | Video metadata, some comments | $100–$1,400/month tiers | |
| TikHub | Metadata, comments | $0.001–$0.01/request pay-as-you-go | |
| Bright Data | Broad scraping-as-a-service | ~$1.50/1,000 records | General scraping infra, not TikTok-specific |
| Apify | TikTok scraper actors | From $15/1,000 results | Community + official actors |
| Data365 | Metadata | $0.60/1,000 records | Cheapest headline rate found |
| ScrapeCreators | Metadata | $47/25,000 credits | |
| Tikapi | TikTok-only API wrapper | $49/month | |
| SocialCrawl | Metadata | From £15/2,500 credits | |

All of these operate by reverse-engineering or scraping TikTok's private endpoints — i.e.,
exactly the automated collection TikTok's ToS prohibits on TikTok's side, whatever
compliance language the provider itself publishes to its own customers. This is legally
unsettled territory (the general shape of the dispute resembles *hiQ v. LinkedIn* /
*Meta v. Bright Data*), jurisdiction-dependent, and several of the source blog posts used
for this table (ScrapeBadger, Scrapfly) describe frequent breakage as TikTok updates its
anti-bot defenses — i.e., these are not presented by their own trade press as operationally
stable for unattended daily automation. **Per task instructions, none were trialed or
purchased.** Transcript availability is inconsistent across providers (some add ASR as a
paid extra; not verified here).

---

## 3–5. Real public-content spike, extraction capability, comments test

**PUBLIC POSTS TESTED (live-fetched, structured, real): 0.**

This is the section the sandbox network block hit hardest. §2C already shows that even the
one tool that *was* reachable (`WebSearch`) cannot return individual TikTok post records —
only topic pages. Without a working `WebFetch`/HTTP path to `tiktok.com`, there was no way
to retrieve an actual video page, oEmbed response, or comment thread inside this session.

**What was not done, stated plainly, so nobody mistakes silence for a negative result:**

- No video ID/URL, creator handle, post date, or engagement counts were captured from a real
  post.
- No caption, transcript, or comment text was extracted from a real post.
- No field-by-field RELIABLE/PARTIAL/UNRELIABLE/UNAVAILABLE table can be produced *from
  observed evidence*, because there is no observed evidence. Producing one anyway, from
  documentation alone, and labeling it as if it were measured, would be exactly the kind of
  fabricated provenance this repo's own rules forbid ("Provenance is truthful or absent...
  never fabricate provenance to satisfy a schema").

**What can be said, from documentation only, clearly labeled as unverified:**

| Field | Best documented route | Best-case classification (unverified) |
|---|---|---|
| Video ID / URL | oEmbed input (you must already have it) | N/A — not a discovery field |
| Creator handle | oEmbed `author_name`/`author_url` | Plausible RELIABLE, undemonstrated |
| Post caption/description | oEmbed `title` | Plausible RELIABLE, undemonstrated |
| Hashtags | Embedded in caption text only, no structured field in oEmbed | Plausible PARTIAL, undemonstrated |
| Post date | Not in oEmbed response at all | UNAVAILABLE via oEmbed; possibly present via Research API, unverified |
| Engagement counts | Not in oEmbed | UNAVAILABLE via oEmbed; Research API only, unverified |
| Captions (on-screen text) | Not in oEmbed | UNAVAILABLE via any tested route |
| Transcript / spoken content | Not in oEmbed; some third-party providers add ASR | UNAVAILABLE via oEmbed; PARTIAL at best elsewhere, unverified |
| Comments | Not in oEmbed | UNAVAILABLE via oEmbed; Research API (if eligible) or third-party providers only, unverified |
| Comment likes/replies | Not in oEmbed | Same as above |
| Media access (video file) | Not via oEmbed (only embeddable player) | UNAVAILABLE via oEmbed for this use case |
| Thumbnail | oEmbed `thumbnail_url` | Plausible RELIABLE, undemonstrated |

The honest summary: **the one ToS-compliant, no-eligibility-question route (oEmbed) is
metadata-poor and structurally incapable of discovery** (needs a URL you already have) —
it cannot supply comments, transcript, dates, or engagement data under any circumstance,
tested or not, because those fields simply are not part of the oEmbed response shape. Every
field that would matter for CA evidence (transcript, comments, engagement-as-corroboration)
sits behind either unverified Research API eligibility or the ToS/anti-bot-restricted paths
this spike was told not to cross.

**Comments test (§5): not performed.** The methodological point the task asks this section
to evaluate — that many comments under one video are one evidence cluster, not N independent
sources — is already structurally built into this codebase's own `dedup.py`
(`crosspost_group`/`story_group`) and `memory.py` (`independent_sources` counting, which
explicitly refuses to let a second capture from the same `crosspost_group` inflate
independence). Any future TikTok ingestion should reuse that exact mechanism rather than
invent a new one: a video and its comment thread would need to share a single
`crosspost_group`/conversation identifier, counted as one source in `independent_sources`
regardless of comment count. This is a design note carried into §11, not a tested result.

---

## 6. Constraint-Archaeology quality test

**USEFUL CA OBSERVATIONS EXTRACTED: 0. HIGH-VALUE: 0.**

No real post content was retrieved (§3–5), so there is nothing to extract a
DOMAIN/ACTOR/OBSERVED CONSTRAINT/... record from. `WebSearch` snippets did surface *topics*
that sound like the right territory — "day in the life of a coffee shop owner," "restaurant
owner taking in inventory shipment, double-checking the pallet," a "Contractor Command
Center" Excel workflow a construction creator built for estimates — but these are search
snippets about content, several steps removed from a verbatim quote, a real URL, or comment
corroboration. Recording any of them as a CA-style observation would misrepresent a topic
label as evidence. Per this repo's own findings-ledger discipline, that's exactly the
distinction `origin=generated` vs `origin=captured` exists to prevent, and the honest
classification for all of it is **NOISE (not because the topic lacks value, but because
nothing here clears the evidentiary bar)**.

---

## 7. Sensor value test

**NOVEL SENSOR VALUE: MEDIUM (structural argument, not empirically demonstrated).**

The structural case is real and doesn't depend on live access: §1 already shows the current
network has zero coverage of the physical/non-developer economy and zero non-text evidence.
If TikTok's well-known content mix (documented broadly, not verified in this spike) includes
real creators in trades, hospitality, beauty, retail, and construction — which the §2C
snippets ("coffee shop owner," "food truck owner," "contractor command center") suggest
without proving — then it is observing a population and a modality nothing else in
`sources.json` touches. That argues for HIGH.

What pulls it down to MEDIUM rather than HIGH: this spike could not verify how large the
constraint-revealing slice of that content actually is versus the platform's well-documented
dominant modes (entertainment, trend/dance/comedy content, aspirational small-business
"glow-up" narratives that are closer to marketing than to a firsthand pain report — the same
caution this codebase already applies to Product Hunt as a "solution signal" rather than a
firsthand report). Until a real sample is pulled, "genuinely novel evidence exists" and
"mostly reproduces problems already visible elsewhere, just with a camera pointed at them"
are both live possibilities.

**Physical/non-developer economy coverage — current network: effectively ZERO** (§1B).
**TikTok's plausible coverage: MEDIUM-HIGH, unverified.**

---

## 8. Algorithmic bias / sensor distortion

All of the following are analysis, not measurement — none of it required live access, and
none of it should be read as calibrated against a real sample:

- **Recommendation-algorithm bias**: TikTok's For You feed optimizes for watch-time/engagement,
  not representativeness. What a researcher *finds* depends heavily on what the algorithm
  chose to surface to search/discovery queries, not what's actually typical of a trade or
  domain.
- **Virality bias**: a post that shows a dramatic or funny workaround is far more likely to
  surface than a mundane, repeated one — the opposite of what a frequency signal needs.
- **Creator incentives**: business-account creators often post *to market themselves*, which
  can shade "here's my painful workaround" content toward "look how resourceful/relatable I
  am," i.e., closer to a Product-Hunt-style solution signal than a raw firsthand pain report.
- **Entertainment bias**: TikTok's dominant content modes are entertainment-first; operational
  content is a minority slice of a minority slice.
- **Demographic / geographic / language bias**: TikTok's user base skews younger and mobile-first
  relative to e.g. Discourse/HN's skew; language and regional availability (TikTok is banned
  or restricted in some jurisdictions) will shape which economies are visible at all.
- **Duplicate/reposted content**: cross-posting and "stitch"/"duet" repost culture on TikTok is
  at least as bad as the crosspost problem `dedup.py` already handles for HN/Reddit/DEV, likely
  worse given how central resharing is to the platform's mechanics.
- **Coordinated/promotional content**: sponsored or agency-produced "authentic day in the life"
  content exists and is not always disclosed clearly; a discovery pipeline would need a
  detection step for this that nothing in `sources.json`'s current sources needs today (HN/Reddit/
  Discourse threads are comparatively harder to astroturf believably at this content style).
- **Survivorship bias**: businesses that failed because of the constraint they'd have shown
  can't post about it — the same blind spot every after-the-fact source has, but sharper on a
  platform this dependent on an active, still-operating creator.

**What TikTok engagement metrics must not be interpreted as** (explicit, per task instruction):
`views != market size`. `likes != willingness to pay`. `comments != independent sources`
(the last one is already structurally enforced in this codebase's `crosspost_group` logic —
see §5 — and any TikTok ingestion must extend that same discipline rather than treat comment
count as source count).

**Proposed safeguards (proposal only, not implemented):** cap confidence for TikTok the same
way `sensor.py` already caps Product Hunt's `_SOLUTION_SIGNAL_CONFIDENCE_CAP`, since business-account
TikTok content has the same "self-marketing framing" risk; require independent
off-platform corroboration before any TikTok-sourced anomaly can reach MERGED status; never
let engagement counts enter `Observation.confidence` (mirroring the existing rule that
upvotes/comment counts are never even read into a `Capture` for Product Hunt today).

---

## 9. Proposed Sensor Map entry (documentation/proposal only)

```
SENSOR:                       TikTok (public posts + comments)
POPULATION OBSERVED:          Non-developer, physical/service-economy creators and
                               consumers; largely absent from current sources
DOMAINS:                      Trades, hospitality, retail, beauty, healthcare ops,
                               logistics, construction, repair, agriculture, household/
                               consumer — unverified beyond topical plausibility (§2C, §7)
EVIDENCE TYPE:                Video (visual demonstration + spoken/on-screen text) +
                               threaded comments; structurally different modality from
                               every current text-only source
STRENGTHS (claimed, unverified): visual "show the workaround" evidence; large volume;
                               comment threads as vocabulary/corroboration source if
                               accessible
BLIND SPOTS:                  entertainment/virality-selected sample; business-account
                               self-marketing framing; survivorship bias; heavy duplicate/
                               repost culture
DISTORTIONS:                  recommendation-algorithm selection, creator incentives,
                               demographic/geographic/language skew (§8)
ECONOMIC SIGNAL QUALITY:      UNVERIFIED — views/likes/comments must never be read as
                               market size / willingness-to-pay / independent-source count
DISCOVERY VALUE:              UNVERIFIED in this spike; structurally plausible (§7)
VALIDATION VALUE:             LOW on its own — needs independent off-platform confirmation
                               before any TikTok-sourced Finding can support a merge,
                               consistent with how Product Hunt is already treated
INDEPENDENCE CHARACTERISTICS: One video + its comment thread = one evidence cluster,
                               never N independent sources (same discipline as this repo's
                               existing crosspost_group/story_group handling)
ACCESS RELIABILITY:           LOW-UNVERIFIED — no route tested end-to-end in this spike;
                               every documented route is either data-poor (oEmbed),
                               eligibility-gated (Research API), or ToS/anti-bot-restricted
                               (page scraping, most third-party providers)
AUTOMATION SUITABILITY:       LOW at present (§10, §12)
```

---

## 10. Access-path comparison

| Path | Data coverage | Comments | Transcript | Search | Volume | Cost | Reliability | Access/compliance risk | Automation suitability | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| oEmbed | Title/caption, author, thumbnail only | No | No | No (needs known URL) | Unlimited, no key | Free | Untested here; documented as stable | Low — documented, sanctioned use | High for enrichment, zero for discovery | **PARTIAL** |
| Research API | Profiles, videos, comments | Yes | Unverified | Yes (structured query) | 1,000 req/day, 100k records/day | Free | Unverified; official, presumably stable | Low if eligible — eligibility itself is the blocker | High, if eligible | **BLOCKED** (eligibility unverified) |
| Display API | Only the authorizing creator's own content | No | No | No | N/A | Free | N/A | N/A | Not applicable to this use case | **NOT SUITABLE** |
| Public page view (manual) | Everything visible to a logged-out viewer | Yes (visually) | No structured field | No | 1 human, 1 page at a time | Free | High for a human, N/A for automation | Low for a human; ToS-prohibited the moment it's automated | None (by design/instruction) | **PARTIAL** (human-only) |
| Public page scraping (automated) | Same as above, extracted programmatically | Yes | No | No | Scales, but adversarial | Free–low | Reported as unstable — breaks with anti-bot updates | High — explicit ToS violation, active anti-bot defenses, CAPTCHA | Would require defeating access controls — out of scope by task instruction | **BLOCKED** (by task instruction) |
| Search-engine discovery | Topic pages, not individual posts | No | No | Yes, but returns wrong granularity | N/A | Free | Low — tested in this spike, consistently returns discover pages | Low (no ToS issue) | Low — not a reliable discovery mechanism | **NOT SUITABLE** |
| Third-party commercial providers | Metadata, often comments, sometimes ASR transcript | Often | Sometimes | Often | Varies by tier | $0.001–$0.01/req or $15–$1,500+/mo | Reported as variable, breaks with platform changes | Medium-high — providers scrape TikTok's private endpoints; legal position unsettled | Medium, per provider's own claims (untested) | **NOT SUITABLE** (untrialed; needs legal/compliance review before it could even become PARTIAL) |

**BEST CURRENT PATH:** oEmbed — the only route that is simultaneously ToS-compliant,
key-free, and requires no unverified eligibility. It only enriches a URL you already have; it
cannot discover anything on its own.

**BEST FALLBACK PATH:** TikTok Research API, *contingent on confirming Discovery Lab (or a
named individual/institution behind it) actually qualifies as an eligible academic/non-profit
researcher* — this spike could not confirm that either way. If eligibility fails, there is no
fallback rated better than NOT SUITABLE in this table; that is itself the headline finding of
§10.

---

## 11. Minimum future sensor design (design only — not implemented)

Only sketched because §7 doesn't foreclose the possibility; nothing here is built.

```
DISCOVERY (Research API query, once eligibility confirmed — NOT search-engine discovery,
           per §2C/§10)
  → PUBLIC POST (video URL + Research API metadata)
  → METADATA / CONTENT (caption, transcript if available, on-screen text)
  → COMMENTS (fetched as one bundle per post, never as separate per-comment sources)
  → CA RELEVANCE FILTER (reuse existing sensor.py-style extraction prompt, adapted for
    video-derived text; carry the Product-Hunt-style confidence cap forward for any
    business-account/self-marketing-framed post)
  → OBSERVATION (source = "tiktok", crosspost_group = the post's own ID — the post AND
    every comment drawn from it share one crosspost_group, so memory.py's existing
    independent_sources logic cannot count a video plus its own comment section as more
    than one independent source, exactly as it already refuses to do for HN/Reddit crossposts)
  → independent confirmation elsewhere (a TikTok-sourced Observation should never alone
    reach MERGED in the same-mechanism gate — it needs an off-platform corroborating
    Observation, mirroring the treatment Product Hunt already gets)
  → BCA
```

The one new labeling rule this would require, stated precisely for whoever eventually
implements it: **a TikTok post and every comment fetched from underneath it share a single
`crosspost_group`/story identifier.** Fifty corroborating comments strengthen frequency/vocabulary
signal (useful, per §5) but must never increment `independent_sources` more than once per
post, exactly mirroring how `dedup.assign_story_groups()` already treats the same story
reposted across HN/Lobsters/Reddit today.

---

## 12. Stop rule

Per task instructions:

> `PROCEED_TO_PROTOTYPE` requires BOTH: (1) TikTok provides materially novel CA evidence;
> (2) at least one technically and operationally viable access path exists.

**Neither condition was demonstrated in this spike** — not because the answer is negative,
but because this session could not reach `tiktok.com` at all (§0, §2), so §§3–6 produced zero
real evidence and §10 could not confirm a single access path as fully WORKS-grade (oEmbed
works but is data-poor by design; Research API is the only comments-capable official route
and its eligibility is unconfirmed). The structural argument in §1 and §7 is genuinely
suggestive — the population and evidence-modality gap is real on paper — but "suggestive on
paper" is exactly the kind of thing this repo's own rules say not to treat as a Finding.

**VERDICT: `RESEARCH_ACCESS_FURTHER`.**

Concrete next step, in order: (1) confirm whether Discovery Lab or an affiliated individual
can actually qualify for Research API access — that single fact determines whether the best
fallback in §10 is real or not; (2) re-run §§3–6 of this exact spike from an environment with
real network egress to `tiktok.com`, so the field-reliability table in §4 and the CA-quality
test in §6 can be built from actual fetched posts instead of documentation; (3) only after
both of those produce real data, revisit §7's MEDIUM back up to HIGH or down to LOW.

---

## 13. Final report

CURRENT SENSOR BLIND SPOT: Physical/non-developer economy (trades, hospitality, retail,
beauty, healthcare ops, logistics, construction, repair, agriculture) and any non-text
evidence modality — both are at essentially zero coverage in `sources.json` today.

PUBLIC POSTS TESTED: 0 (live fetch blocked by this session's network egress policy — see §0/§2)

USEFUL CA OBSERVATIONS: 0

HIGH-VALUE: 0

COMMENT EVIDENCE VALUE: INSUFFICIENT DATA (not tested; see §5)

NOVEL SENSOR VALUE: MEDIUM (structural argument only, unverified — see §7)

PHYSICAL/NON-DEVELOPER ECONOMY COVERAGE: current network HIGH-confidence ZERO; TikTok's own
coverage plausible MEDIUM-HIGH but unverified here

BEST ACCESS PATH: oEmbed (metadata enrichment only — no discovery, no comments, no transcript)

BEST FALLBACK: TikTok Research API, contingent on unconfirmed academic/non-profit eligibility

COMMENTS ACCESS: UNAVAILABLE (in this spike); PARTIAL at best via Research API or third-party
providers, per documentation only

TRANSCRIPT ACCESS: UNAVAILABLE (in this spike); PARTIAL at best elsewhere, per documentation only

AUTOMATION FEASIBILITY: LOW — ToS explicitly prohibits scraping, anti-bot defenses are heavy,
Display API is the wrong tool, oEmbed can't discover, and Research API eligibility is unconfirmed

MAIN ACCESS RISK: The only ToS-compliant, no-eligibility-question path (oEmbed) cannot supply
comments, transcript, or discovery under any circumstance, while every path that could is
either eligibility-gated or crosses into scraping this task was explicitly told not to do.

MAIN SENSOR DISTORTION: Recommendation-algorithm and creator-incentive selection for
entertainment/virality means engagement metrics cannot be read as market size, willingness-to-pay,
or independent corroboration — and this spike could not measure how large the genuinely
constraint-revealing slice of TikTok content actually is.

STOP-RULE VERDICT: RESEARCH_ACCESS_FURTHER

FILES CHANGED: `docs/research/tiktok-sensor-feasibility.md` (new)

BRANCH: `claude/tiktok-sensor-feasibility-q1j8op`

COMMIT SHA: _(filled in after commit)_

DRAFT PR: _(filled in after push)_
