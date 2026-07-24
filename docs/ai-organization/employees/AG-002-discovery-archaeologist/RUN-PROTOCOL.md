# Recovery Protocol v1.0 — AG-002 Discovery Archaeologist

Employee ID: **AG-002** · Role Name: **Discovery Archaeologist** ·
Status: **FROZEN** · Version:
**1.0**
Core Principle: **Recover what was recorded. Cite where. Draw no
conclusions.**

A described procedure, not code and not an automation workflow. Nothing
here is meant to run unattended or be triggered on a schedule.

```
Historical Sources
   ↓
Scanning
   ↓
Candidate Discovery
   ↓
Evidence Linking
   ↓
Clustering
   ↓
Recovery Report
   ↓
Recovery Queue
```

## Stage 1 — Historical Sources

The explicit, authorized list of documents or archives for this run
(see `INPUTS.md`). A source not on this list is out of scope, full
stop. If a named source cannot actually be located, this is recorded
here, immediately, as `INSUFFICIENT ACCESS` — the run proceeds only on
what is actually accessible, and says so.

**For a Reality Inbox source specifically** (added 2026-07-24, per
`INPUTS.md`'s "Default operational source"): its manifest in
`reality-inbox/manifests/` must show `status: ACCEPTED` and a complete
provenance block before Stage 2 begins. If it does not, this is recorded
as `BLOCKED` (`LIMITATIONS.md`) — not `INSUFFICIENT ACCESS`, since the
file itself may be perfectly reachable; it is the provenance record that
failed.

## Stage 2 — Scanning

Every authorized source is read in full — no sampling, no skimming past
sections that look procedural or uninteresting. A source not read in
full cannot honestly support a claim that "nothing else of note" was
in it.

## Stage 3 — Candidate Discovery

While scanning, passages are flagged as **candidates** against the
eight categories in `ROLE.md`'s Responsibilities (recurring, forgotten,
abandoned, converging, newly-feasible, contradictory, repeated
question, unfinished). A candidate is not yet a finding — it becomes
one only after Stage 4.

## Stage 4 — Evidence Linking

Every surviving candidate is attached to an exact citation: source file
and a section heading, line reference, or direct quote sufficient for
independent verification. A candidate that cannot be linked this
precisely is downgraded to `INSUFFICIENT EVIDENCE` and recorded under
Open Questions, not presented as a finding.

## Stage 5 — Clustering

Candidates that describe the same underlying idea, across different
sources or different points in time, are grouped together. Clustering
never merges or edits the underlying text — it only groups citations
that point at each other. This stage is where Repeated Themes and Idea
Evolution timelines come from.

## Stage 6 — Recovery Report

The single, structured output (`OUTPUTS.md`) is produced from the
clustered, cited candidates. Nothing enters the report that did not
survive Stage 4 with a real citation.

## Stage 7 — Recovery Queue

Clusters that appear, on their own evidence, to warrant further
attention are listed in the report's Recovery Queue — addressed to a
human or Curator, per `../../ORB/ORB-PROTOCOL.md`'s and
`../../../proposals/PROP-0002-discovery-intake-system.md`'s existing
conventions for routing a finding onward. **This stage never itself
creates an Investigation.** A queued item may, later, become a
Discovery Entry through Discovery Lab's own Intake process
(`PROP-0002`) — that is a separate, human- or Curator-triggered act,
not something the Recovery Protocol performs on its own.

## Stop rule

If continuing at any stage would require guessing at a source's intent,
inventing a citation, or modifying a source document, the correct
action is to stop and record the gap — never to proceed on a
reasonable-sounding assumption.

## Relationship to other documents

`INPUTS.md` governs Stage 1. `OUTPUTS.md` governs Stages 6–7 in detail.
`LIMITATIONS.md` governs the stop rule. `CHECKLIST.md` gives a condensed
practical version of this whole procedure.
