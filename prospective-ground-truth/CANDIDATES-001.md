# Short-Horizon Candidate Search — 2026-08-18

Read-only search across `constraint-archaeology-agents/data/observations.jsonl`
(456 real observations, scraped by `ca_agents/collector.py`'s real HTTP calls to
Hacker News, Lobsters, dev.to, Reddit, Product Hunt, and five real Discourse
communities — not synthetic content) and `business-candidate-analyst/data/
candidates.json` (161 candidates), keyword-filtered for the task's preferred
short-horizon shapes (tender award, regulator approval, permit decision, announced
launch or delay, capacity allocation, official deadline outcome, certification
issuance, company action tied to a stated date) and manually read for fit against
criteria A-G.

**Finding, stated plainly:** the corpus is overwhelmingly individual/anonymous pain
points (a forum poster's own side project, a personal home-automation annoyance) with
no natural external resolution mechanism — this is expected for a pipeline built to
find business opportunities, not to track institutional decisions. Only observations
tied to a **named, real company or project with its own public changelog/release
process** produced genuinely suitable candidates. Two did; a few more are listed with
explicit reservations rather than omitted.

## Registered (see `data/cases.jsonl`)

### PGT-0001 — Fly.io flyctl CLI support for MPGv1→MPGv2 Postgres restore
- **Source:** 5 observations (`OBS-20260811-0044-6c7732` etc.), all citing
  `community.fly.io/t/you-can-now-restore-your-mpgv1-backups-as-a-v2-cluster/28466`,
  underlying BCA candidate `BC-0101` (`pain_severity: SEVERE`).
- **Proposition:** Will Fly.io ship flyctl CLI support for this restore path (UI-only
  as of 2026-08-11) by 2026-10-15?
- **Why suitable:** real, named, active company; a real primary source (Fly.io's own
  changelog, `flyctl` GitHub releases, or the cited thread itself, which Fly.io staff
  actively post in) will unambiguously answer this; short horizon (~8 weeks); directly
  gates an existing SEVERE-pain candidate, so it is genuinely decision-relevant, not a
  curiosity.
- **Registered as:** `pgt-case:f6aba5c46ea1754809cbddfc49f22b28` — see final report.

## Strong but not registered (one live case only, per task §12)

### Matplotlib binary-wheel availability for Python 3.15
- **Source:** `OBS-20260814-0051-0c1caf`, `discuss.python.org/t/trying-to-install-
  matplotlib/108559`. Quote: "Python 3.15 prerelease? Matplotlib doesn't provide
  binaries for that version yet. Try e.g. Python 3.14 instead."
- **Proposition:** Will Matplotlib publish a `cp315` wheel on PyPI before/around
  Python 3.15's final release?
- **Why suitable:** PyPI's package-file listing is an unambiguous, machine-checkable
  primary source (no human judgment call needed to resolve this one) — arguably an
  even cleaner resolution mechanism than PGT-0001's. Python's annual release cadence
  (final releases historically ship in early October) gives a natural, defensible
  resolution window.
- **Not registered:** task §12 asks for exactly one live acceptance case per this run;
  this is the strongest runner-up, ready to register in a follow-up pass with the same
  protocol.

## Weaker candidates found, listed with reservations (not registered)

### OpenAI Community: "notes in side panel" feature request
- `OBS-20260812-0042-c99516`, `community.openai.com/t/feature-request-notes-in-side-
  panel/1390133`. A real, named company forum, but this is a **user feature request**,
  not a company commitment — there is no natural expected-resolution horizon (feature
  requests can sit unaddressed indefinitely), which weakens criterion D/G
  (pre-statable resolution horizon). Would need OpenAI to have said *something* about
  intent before this is registerable with a defensible window.

### HIPAA Business-Associate-Agreement confirmation for a healthcare app launch
- Three near-duplicate observations (`OBS-20260810-0011`, `-0066`, `-0077-1ef5de`)
  about an anonymous developer awaiting written BAA-scope confirmation from their
  hosting provider before launching. Real institutional shape (a compliance sign-off
  gating a launch), but the poster and their hosting provider are both anonymous in
  the observation — there is no way to re-find and check on the *same* specific
  situation later, unlike PGT-0001's named company and public thread. Excluded on
  criterion C (T1 evidence cannot be reliably located later).

### Python 3.14 annotation-semantics migration cutoff (multiple observations, feeds
BC-0082)
- Real and dated, but the "cutoff" is an **already-fixed, already-public** fact about
  Python's own release schedule (not an open question whose answer is currently
  unknown) — there is no genuine uncertainty for a T1 resolution to add over what is
  already knowable at T0. Fails criterion A (not actually an open, falsifiable
  proposition; it's a scheduled, disclosed fact).

## What did not qualify at all

`discourse:home-assistant` and `discourse:level1techs` (123 observations combined)
produced zero keyword hits for pending-decision language on this pass — worth a
second, differently-worded search in a future round rather than a conclusion that
nothing suitable exists there. `product_hunt` (47 observations, new-product-launch
announcements) also produced zero hits on this keyword set, which is somewhat
surprising for a "launch" category and likely reflects the keyword list being tuned
too narrowly toward "pending/upcoming" phrasing rather than "just launched, will it
gain traction" phrasing — a different, also-legitimate short-horizon shape worth its
own search pass later.
