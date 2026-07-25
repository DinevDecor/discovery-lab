# Reality Inbox — Index

Status: DRAFT / EXPERIMENTAL v1
Agent-maintained current inventory. Updated whenever a manifest's status
changes. Not a second source of truth — see `PROCESSING-PROTOCOL.md`,
"No claim of verified truth."

## Current inventory

| intake_id | original_filename | status | intended_agent | outputs |
|---|---|---|---|---|
| [RI-0001](manifests/RI-0001.md) | `SYNTHETIC-TEST-note-0001.md` | `ACCEPTED` | AG-002 | [observation](../memory/observations/REALITY-VERIFY-0001-observation-0001.md), [run report](../docs/ai-organization/employees/AG-002-discovery-archaeologist/runs/REALITY-VERIFY-0001-recovery-report.md) |
| [RI-0002](manifests/RI-0002.md) | `oneDay 6.zip` (77 entries) | `COMPLETED` (real — all 77 entries read; 19 organizational entries extracted, 47 personal entries screened, correctly yielding no knowledge) | AG-002 | [run report](../docs/ai-organization/employees/AG-002-discovery-archaeologist/runs/PILOT-RUN-0002-recovery-report.md) |
| [RI-0003](manifests/RI-0003.md) | 4 files: this repository's own `docs/adr/ADR-0001`-`ADR-0004` | `COMPLETED` (real — AG-003 Reality Stress Test, dataset 2) | AG-002, curated by AG-003 | [run report](../docs/ai-organization/employees/AG-002-discovery-archaeologist/runs/STRESS-RUN-0003-recovery-report.md), [curation](../docs/proposals/AG-003-reality-stress-test/CURATION-0003.md) |
| [RI-0004](manifests/RI-0004.md) | 7 files: `kod` repository research artifacts | `COMPLETED` (real — AG-003 Reality Stress Test, dataset 3) | AG-002, curated by AG-003 | [run report](../docs/ai-organization/employees/AG-002-discovery-archaeologist/runs/STRESS-RUN-0004-recovery-report.md), [curation](../docs/proposals/AG-003-reality-stress-test/CURATION-0004.md) |
| [RI-0005](manifests/RI-0005.md) | 3 files: `trust-engine` repository operational reports | `COMPLETED` (real — AG-003 Reality Stress Test, dataset 4) | AG-002, curated by AG-003 | [run report](../docs/ai-organization/employees/AG-002-discovery-archaeologist/runs/STRESS-RUN-0005-recovery-report.md), [curation](../docs/proposals/AG-003-reality-stress-test/CURATION-0005.md) |

## Reading this index

- **Current total: 5 intakes. 1 `ACCEPTED` (synthetic test fixture,
  `RI-0001`). 4 `COMPLETED` (`RI-0002` real production diary data;
  `RI-0003`/`RI-0004`/`RI-0005` real cross-repository stress-test
  datasets — `RI-0003`/`RI-0004`/`RI-0005` use `intake_mode:
  SESSION-LOCAL-REPO-COPY`, a fourth real intake mode, added alongside
  `local-drive-sync`/`repo-tracked-fallback`/`GITHUB_UPLOAD` in
  `PROCESSING-PROTOCOL.md`, for a file copied from another repository
  already accessible in the same session's workspace rather than
  dropped by a human).**
- `RI-0002` was completed under the "AG-002 Personal Diary Processing
  Policy" decision (2026-07-24): AG-002 is authorized to read personal
  content, but personal content only becomes recorded knowledge when it
  directly supports a recovered principle or finding — see the run
  report's "Personal entries — screened, no knowledge extracted"
  section for the full, honest accounting.
