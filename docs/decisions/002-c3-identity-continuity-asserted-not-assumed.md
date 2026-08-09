# 002 — C3 identity continuity is asserted, never assumed

**Status:** adopted, implemented in `capability-observatory/`.

## Decision

`capability-observatory/src/capability_observatory/fingerprint.py` computes a
deterministic `spec_fingerprint` from each panel item's declared identity
fields. `capability_observatory/identity.py` and `capture_intake.py` compare
a new fingerprint against the last one previously recorded for that panel
item, read fresh from the append-only Observation log every time (never a
cached "latest" value). If the two differ, an `IdentityBreak` record is
written with `status="UNRESOLVED"` — the two observations remain on record
under their own fingerprints, and nothing in this package ever writes a
resolved `SAME_ENTITY_AS` link or otherwise merges them into one continuous
series. Resolving that assertion is left entirely to a future, separate,
human/analyst step.

## Reason

A silently-continued series that actually crossed a real identity change
(a different manufacturer part number, a packaging change, a distributor
substitution) produces a false longitudinal trend that looks exactly like a
real capability-price-shift finding. Because the whole reason this sensor
exists is to accumulate trustworthy longitudinal evidence, a false
continuity is worse than a visibly broken one — a broken series can be
resolved later with real judgment; a silently merged one corrupts the
record with no visible seam to catch it at.

## Alternative rejected

Automatic merging when the fingerprint match rate is "high enough" (e.g.
same distributor SKU, same product title) was considered and rejected. Any
confidence threshold would eventually auto-merge a case like a distributor's
own out-of-stock substitution under the same URL, or a marketing rename with
a genuinely different manufacturer part underneath — exactly the adversarial
cases the design review identified. No threshold is safe enough to automate.

## Consequence

More manual/analyst review is required in the first months of operation
than a naive tracker would need — every fingerprint change becomes a
standing, visible `UNRESOLVED` record until someone actively resolves it.
This is the accepted cost: `capability-observatory/README.md`'s 30-day
stop rules explicitly tolerate up to 3 such open items across the 20-item
panel (`identity_backlog`) before treating it as a design defect requiring
rework, rather than normal operating noise.
