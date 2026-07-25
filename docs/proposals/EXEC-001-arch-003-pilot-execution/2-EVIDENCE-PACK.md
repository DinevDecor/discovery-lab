# Deliverable — Evidence Pack

Per `EXEC-001` Requirement 5 ("Запиши всички доказателства" — record
all evidence). Every artifact this execution touched or produced,
collected in one place with its disposition.

## Artifacts consulted (read-only, unmodified)

| Artifact | Role in this execution | Confirmed unmodified |
|---|---|---|
| `docs/proposals/AG-003-reality-stress-test/CURATION-0004.md` | Source of `CPP-S3-01` and `KO-S3-01` | Yes — `git diff --stat` shows zero change |
| `docs/ai-organization/employees/AG-003-knowledge-curator/REVIEW-PROTOCOL.md` | Formal Gate procedure followed | Yes |
| `docs/ai-organization/employees/AG-003-knowledge-curator/KNOWLEDGE-OBJECT-SPEC.md` | Standard consulted by the Reviewer | Yes |
| `docs/ai-organization/employees/AG-003-knowledge-curator/PROMOTION-RULES.md` | Standard consulted by the Reviewer | Yes |
| `docs/ai-organization/employees/AG-002-discovery-archaeologist/runs/STRESS-RUN-0004-recovery-report.md` | Cross-checked citation-by-citation by the Reviewer | Yes |

## Artifacts produced by this execution

| Artifact | Status |
|---|---|
| `docs/proposals/AG-003-reality-stress-test/reviews/KR-0001-cpp-s3-01.md` | **Created** — the Knowledge Review itself, filed at the exact path `ARCH-003/3-EXECUTION-SPECIFICATION.md` specified |
| `memory/knowledge-objects/` (directory) | **Created** — first real instantiation, following `Accept`; did not exist before |
| `memory/knowledge-objects/KO-S3-01.md` | **Created** — the executed write, following the real Human Decision (`3-HUMAN-DECISION-RECORD.md`'s "Update" section) |
| `docs/proposals/EXEC-001-arch-003-pilot-execution/*` (this deliverable set) | **Created** — the execution record |

## Minimal-diff verification for `KO-S3-01.md`

Direct field-by-field comparison against the `CURATION-0004.md` source
object: every field identical except `status`
(`Draft → Candidate Principle`, the one specified change) and
`provenance[].report` path prefixes, mechanically recomputed to remain
correct references from the new file's location — same three target
files in every entry, not new or different sources. All seven paths
the new file references (five governing/source documents plus the two
new deliverables it cites) were checked with `realpath -m` + `test -e`
before commit; all seven resolved correctly.

## Direct confirmations performed

- `ls memory/knowledge-objects/` → "No such file or directory," checked
  both before Step 1 and again after the Gate ran (confirming the
  `BLOCKED` state was real, not assumed) — the directory was created
  only after the real Human Decision arrived, in Step 11.
- `git diff --stat docs/proposals/AG-003-reality-stress-test/
  CURATION-0004.md` → empty, checked at both the blocked point and
  after execution — the source proposal and object were never edited,
  at any point.
- `git status --short`, checked throughout — only new files appear at
  every check (the Knowledge Review, the deliverable set, and finally
  the two `memory/knowledge-objects/` artifacts); no existing tracked
  file was ever modified.

## Chain of custody for the Gate's evidence

`CPP-S3-01`/`KO-S3-01` (`CURATION-0004.md`) → read by an independently
invoked Reviewer → cross-checked against
`STRESS-RUN-0004-recovery-report.md` (read in full, not excerpted) →
six verdicts recorded, all `SOUND`, with citations for each → filed as
`KR-0001-cpp-s3-01.md` → summarized in `4-GATE-DECISIONS.md` — every
link in this chain is a real, inspectable file, not a paraphrase.
