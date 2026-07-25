# Deliverable 5 — Evidence Collection Plan

Per `ARCH-003` Phase 5.

## Evidence to collect, by artifact

1. **The Knowledge Review file** (`KR-0001-cpp-s3-01.md`) — collect in
   full, not summarized. It is the direct record of whether the Formal
   Gate actually ran (all six questions answered, each with a verdict
   and a citation-backed explanation) or was shortcut.
2. **The Human Decision record** — collect the exact text, the named
   deciding human, and the timestamp. This is the only artifact that
   can prove Human Final Authority was real and not simulated.
3. **`memory/knowledge-objects/KO-S3-01.md`** (if created) — collect
   the full file, plus a mechanical diff against the object as it
   appears in `CURATION-0004.md`.
4. **Commit history** for whatever commit(s) this pilot produces —
   collect the diff directly, not a description of it.

## What would show the model works

- The Knowledge Review names a Reviewer genuinely distinct from
  `AG-003`'s original curator-executor for `CPP-S3-01`, and that
  independence is explicitly recorded, not assumed.
- All six mandatory questions are answered with an explicit verdict
  and a citation, none skipped, none merged into a single blanket
  answer.
- The Human Decision record exists, is attributable to a real named
  human, and precedes any file write in the commit history (i.e., the
  timestamp/commit order shows approval-then-write, not write-then-approval).
- The diff between `CURATION-0004.md`'s embedded `KO-S3-01` and the
  newly filed `memory/knowledge-objects/KO-S3-01.md` shows **exactly
  one field changed** (`status`) and nothing else — no invented dates,
  no rewritten provenance, no silently "improved" wording.
- No file other than the three named in `3-EXECUTION-SPECIFICATION.md`
  is created or modified.

## What would show the model does not work

- The pilot cannot proceed without inventing a new component (a
  Runtime, a Dispatcher, a new Role) to perform the write — per the
  Critical Rules, this is grounds to halt and report exactly which gap
  blocked it, not to improvise past it.
- The "independent" Reviewer turns out to be the same Executor that
  produced `CPP-S3-01` in the first place, and the pilot proceeds
  anyway — this would be direct, first-hand evidence of the
  self-review problem `ARCH-001`/`ARCH-002` already flagged in the
  abstract (`R4`/self-review limitation), now observed concretely
  rather than inferred.
- The Human Decision record is missing, backdated, or written by the
  same actor that ran the Knowledge Review — evidence that Human Final
  Authority is decorative rather than load-bearing in practice.
- The filed object differs from the reviewed proposal in any field
  beyond `status` — evidence that "execution" quietly became a second,
  ungated curatorial act.
- Any file besides the three named artifacts is touched — evidence of
  scope creep beyond what the Formal Gate actually authorized.

## What this evidence cannot show

A single pilot, on a single object, cannot show that the model
generalizes to merges, relationships, higher promotion thresholds, or
any action outside `discovery-lab`. This plan collects evidence for
exactly the claim `2-SELECTED-EXECUTION-PILOT.md` scoped this pilot
to — not a broader one.
