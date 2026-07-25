# Dataset 1 Re-Audit — Personal Diary (PILOT-RUN-0002 / first walkthrough)

Applies this stress test's failure-search checklist to the **existing**
`PILOT-RUN-0002-recovery-report.md` and
`../AG-003-knowledge-curator-walkthrough/` material, actively hunting for
defects rather than re-confirming prior conclusions.

## Real defects found

### F-3 — No cycle detection/prevention for directional relationship types

Neither `RELATIONSHIP-ONTOLOGY.md` nor `CURATION-PROTOCOL.md` Stage 5
checks whether a new `supersedes` or `depends_on` proposal would close a
cycle in the relationship graph. This matters specifically for these two
types (not `supports`/`alternative_to`, which are coherent even when
mutual — `REL-0001`'s bidirectional `supports` is fine by design) because
`supersedes` and `depends_on` both encode a **directional authority
claim** — "B is now current, not A" / "B requires A to hold." A cycle
among either (`A supersedes B supersedes C supersedes A`, or the
`depends_on` equivalent) is not just messy, it is **logically
incoherent**: there is no well-defined "current" version, or no
well-defined dependency root. **No actual cycle exists in any of the
four stress-test datasets** — this is a structural gap found by
deliberately asking the question the task's failure list poses
("circular relationships"), not a defect that produced a wrong output
anywhere in this engagement so far. Recorded as a real, reproducible
architectural gap regardless: nothing currently stops one from being
created, and nothing would catch it if one were. See
`REALITY-STRESS-TEST-REPORT.md` finding **F-3** and the resulting
correction to `CURATION-PROTOCOL.md`.

### Two concrete missing relationships in the original walkthrough

The first walkthrough's own `ADVERSARIAL-REVIEW-0001.md` (finding 7)
already disclosed, in general terms, that only one Knowledge Object
(`KO-0001`) was built end-to-end and that its Gap Report's claims were
therefore not computed from a full graph. This re-audit makes that
general admission concrete with two specific, real, missed edges:

- **`RI-15` (Generation-Validation Separation) explicitly lists "KOD
  Kernel architecture itself" as one of five independent convergence
  domains** (`PILOT-RUN-0002-recovery-report.md`, `RI-15`) — a direct
  textual link to `RI-1`/`RI-2` (the Kernel's own gatekeeper/judging
  protocol). A `supports` relationship between a Knowledge Object built
  from `RI-15` and one built from `RI-1`/`RI-2` is directly evidenced in
  the source and was never proposed, because no Knowledge Object was
  ever built for either finding in the original walkthrough.
- **`RI-7` ("the whole doesn't control the parts") is explicitly a
  candidate principle produced by applying `RI-5`'s own methodology**
  (both `2026-06-25`, same entry) — the source's own framing (*"a
  candidate pending wider testing"*) reads as a direct output of `RI-5`'s
  "strip organism-specific traits to find a fundamental process" method,
  not an independent claim. A `derived_from` relationship between
  `RI-7`'s Knowledge Object and `KO-0001` (built from `RI-5`/`RT-3`) is
  directly evidenced and was never proposed, for the same reason as
  above.

Neither is a newly-discovered category of defect (the general gap was
already disclosed); both are now concrete, checkable evidence that the
gap is real and reproducible, not just a theoretical caveat. Recorded as
part of `REALITY-STRESS-TEST-REPORT.md` finding **F-4** (a scale/coverage
limitation, distinct from F-1–F-3's logic-level gaps).

## Checked and confirmed correct (no defect found)

- **"Same idea expressed differently"**: `KMP-0001`'s RI-8/RI-12
  judgment (declined to merge, correctly — re-verified against the
  source text in this re-audit, still holds) and `REL-0001`'s RI-11
  bidirectional-`supports` judgment both re-checked; both still stand.
- **"Duplicated provenance"**: checked whether citing the same diary
  quotation under both a Recovered Idea (`RI-N`) and a Repeated Theme
  (`RT-N`) constitutes duplicated provenance in a Knowledge Object. It
  does not — `RI-N` is the atomic citation; `RT-N` groups citations that
  independently also stand as their own findings. `KO-0001`'s own
  `provenance` list (5 entries) does not double-count `RI-5` and `RT-3`
  as separate citations for the same diary date — verified directly
  against `KO-0001-nature-as-library-of-architectures.md`.
- **"Contradictory terminology"**: `ROLE.md`'s Terminology note
  (KOD `Registry`/`Knowledge Graph`/`confidence` disambiguation) was
  re-tested against real, previously-unseen KOD content in dataset 3
  (`KNOWLEDGE_OBJECT_TEMPLATE.md`, an actual KOD Knowledge Object schema)
  and held up without modification — a genuine positive confirmation,
  not just an assertion re-read.
- **"Confidence inflation"**: `KO-0001`'s `confidence: 0.4` (post the
  first walkthrough's own adversarial-review correction) re-checked
  against the formula; still correct, still conservative (capped by
  `diversity_factor: 0.4` for a single source).
- **Missing contradiction detection**: `CONTRADICTION-CHECK-0001.md`'s
  restraint (declining to escalate the `NORM`/confidence tension past
  AG-002's own `INSUFFICIENT EVIDENCE` marking) re-verified against
  `PILOT-RUN-0002-recovery-report.md`'s Open Questions — still an
  accurate, non-manufactured restraint, not a missed real contradiction.

## Verdict for this dataset

**PASS**, with two real architectural gaps found (`F-3`, and `F-4`'s
concrete evidence) that apply across all four datasets, not specific to
this one. No dataset-1-specific defect was found that the first
walkthrough's own adversarial review had not already substantially
covered — this re-audit's value is in (a) finding `F-3`, a genuinely new
gap, and (b) converting an already-disclosed general limitation into two
concrete, checkable missed-relationship examples.
