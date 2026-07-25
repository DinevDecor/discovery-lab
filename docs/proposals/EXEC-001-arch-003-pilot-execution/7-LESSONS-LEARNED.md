# Deliverable — Lessons Learned

Per `EXEC-001`. Observations from actually running (partially) a real
pilot, as distinct from specifying one — some of these could only be
learned by execution, not by analysis.

## 1. The independence requirement is harder to satisfy than it looks on paper

`ARCH-003` named this risk in the abstract (Risk 1). Actually trying to
satisfy it revealed a specific, previously-unstated distinction:
memory-independence (a fresh context, no recollection of authoring the
proposal) is achievable inside this session with existing tooling;
actor-independence (a reviewer outside the orchestrating session's own
control) is not. `REVIEW-PROTOCOL.md`'s text is satisfied by the
former; a stricter reading would require the latter. This distinction
was invisible until the pilot was actually run — `ARCH-003`'s
specification could name the risk but not observe which half of it a
real attempt would clear.

## 2. A clean Gate pass creates real pressure to treat it as sufficient

Once `KR-0001` came back with all six questions `SOUND` and a
recommendation of `ACCEPT`, there was a genuine pull toward reading
that as "the pilot basically worked, why not just finish it." This is
exactly the shortcut `EXEC-001`'s Critical Rule and `ARCH-003`'s Risk 2
exist to prevent, and resisting it required treating the Human
Decision Record as already-decided (written before the Gate result was
known) rather than revisiting it in light of a favorable Gate outcome.
The lesson generalizes: a well-designed gate sequence needs the human
step to be genuinely insulated from how convincing the AI-run steps
turn out to be, not just formally sequenced after them.

## 3. Real citation-checking surfaces things a specification review cannot

`KR-0001`'s Reviewer found three concerns no prior task in this session
had surfaced: an internal contradiction in `CURATION-0004.md`'s own
prose structure (a bullet heading says one thing, its body says
another), a legitimate timing question about when a governing spec
amendment was made relative to the proposal that depends on it, and an
explicit statement of its own verification scope limits. None of these
came from re-reading the architecture — they came from a reviewer
actually doing the citation-by-citation work the Gate specifies. This
is direct evidence that `AG-003`'s Knowledge Review mechanism does
real work when actually run, not just when described.

## 4. "Specify, then execute" as two separate tasks caught a real gap the specification alone did not

`ARCH-003` reasoned, correctly, that the write step had no ratified
component to perform it. Only in trying to execute did it become
concrete exactly *where* that gap sits in a real sequence (between a
passed Gate and an absent Human Decision) — the abstract gap and the
concrete blocking point turned out to be the same thing, but this was
not obvious in advance; the specification could have been wrong about
where execution would actually stall.

## 5. Filing the review at the ratified path, not a new one, mattered

`ARCH-003`'s specification named an exact path
(`AG-003-reality-stress-test/reviews/KR-0001-cpp-s3-01.md`) rather than
a path inside this task's own deliverable directory. Honoring that
distinction kept the real governance artifact inside `AG-003`'s own
review trail — where a future, real Knowledge Reviewer would look for
it — rather than burying it inside a one-off execution log where it
would be easy to miss on a later, unrelated pass through the
repository.

## 6. What this pilot did test, once the real decision arrived

A real human decision did arrive, the same day, and led cleanly into
the execution step exactly as `3-EXECUTION-SPECIFICATION.md`
specified: one field changed, every reference path recomputed
correctly for the new file location, no other file touched. The
gap identified in `ARCH-003/4-COMPONENT-MAPPING.md` (no ratified
component names who performs the physical write) did not turn out to
need one — the write was small and specific enough that "an Executor,
acting only after Human Final Authority" was sufficient in practice,
without inventing a Runtime or Dispatcher to fill it. Whether this
holds for a larger or more complex action (a merge, a relationship
proposal, a higher promotion threshold) is still untested — this run
tested exactly the one narrow case `ARCH-003` scoped it to, no more.

## 7. Writing the Human Decision Record before knowing the Gate's outcome, and updating rather than rewriting it afterward, was the right call

Because `3-HUMAN-DECISION-RECORD.md` was written and committed with
status `NOT OBTAINED` *before* the Gate's `ACCEPT` recommendation was
known, the later real decision could be checked against criteria set
in advance, not criteria adjusted to fit what arrived. When the real
decision came in, updating the same document (preserving the original
`NOT OBTAINED` record as history rather than deleting it) kept the
full sequence — blocked, then unblocked, with the block's reasoning
still visible — inspectable by anyone reading the file later. The same
discipline was applied to `6-FINAL-VERDICT.md`. This is a pattern
worth keeping for any future execution: record the block honestly
before knowing whether it will resolve, and when it resolves, append
rather than overwrite.
