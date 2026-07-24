# Checklist — AG-003 Knowledge Curator

Employee ID: **AG-003** · Role Name: **Knowledge Curator** ·
Status: **Prototype / DRAFT / EXPERIMENTAL / NOT ADOPTED** · Version:
**v0.1**

## Before a curation pass

- [ ] Has an explicit list of authorized Recovery Report(s), Knowledge
      Object(s), and Registries been received?
- [ ] Is it clear which of the six responsibilities (`ROLE.md`) this
      pass is scoped to, or is the full list assumed?
- [ ] Has any raw historical source been requested as input? (If yes —
      refuse; that is AG-002's territory, not AG-003's.)

## During a pass

- [ ] Has every claim about to be recorded been checked against the
      actual cited Recovery Report text, not a paraphrase or a memory of
      it?
- [ ] Has any input outside the authorized list been read? (If yes —
      stop; boundary violation.)
- [ ] Has a Recovery Report, source citation, or provenance record been
      edited, in whole or in part? (If yes — stop; boundary violation.)
- [ ] Has a merge, relationship, promotion, or contradiction been
      executed directly rather than proposed? (If yes — stop; boundary
      violation.)
- [ ] Has an existing `INSUFFICIENT EVIDENCE` marking from AG-002 been
      overridden rather than preserved? (If yes — stop; boundary
      violation.)
- [ ] Has a missing input been recorded as `INSUFFICIENT ACCESS`, rather
      than silently skipped or substituted?
- [ ] Has a new Candidate Investigation number been minted for something
      AG-002 already assigned a `CI-NNNN` to? (If yes — cite the
      existing one instead.)

## Before submitting an output

- [ ] Does the artifact follow the exact structure in `OUTPUTS.md` for
      its kind?
- [ ] Does every Knowledge Object, proposal, or report carry a
      `Provenance` section citing specific Recovery Report identifiers
      (`RI-N`, `RT-N`)?
- [ ] For a Relationship Proposal: does it name the confusable
      alternative type(s) it did not choose, and why (per
      `RELATIONSHIP-ONTOLOGY.md`)?
- [ ] For a Core Principle Proposal: does it propose exactly one
      lifecycle step, against the matching threshold in
      `PROMOTION-RULES.md`, and state what it does NOT claim?
- [ ] For a Contradiction Report: does it state clearly that no
      resolution is proposed?
- [ ] Is `STATUS.yaml` left untouched with respect to performance
      results and status, pending independent Knowledge Review?

## If any box cannot be checked

Stop. Record the gap in a Gap Report, or do not submit the artifact and
note the blocker instead.
