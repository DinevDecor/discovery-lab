# Deliverable 2 — Cross-Reference Matrix

Concept × source-document terminology. "—" means the concept is not
stated in that document's own text (within the scope defined in
`README.md`), not that it is contradicted.

| Concept | `project-memory` (PM) | `kod` (KOD) | `discovery-lab` (DL) |
|---|---|---|---|
| Repository/document as authoritative | `INV-2` "Чатът не е истина"; Authority/Truth Model | "The repository is the Single Source of Truth" | Assumed via versioned `STATUS.yaml`/`HISTORY.md` records; not restated |
| Roles as versioned contracts, not models | `INV-3` "Договори, не модели"; §7 contract format | "Roles are defined by versioned Agent Contracts... Prompts do not define roles" | Assumed via each `AG-00X`'s `CONTRACT.md` requirement; not restated in `GOVERNANCE.md` itself |
| Formal, criterion-bound gate | "Kernel" (§8) — `PASS`/`BLOCKED` + criterion, bound to a Review Contract | "Kernel Review" — `PASS`/`BLOCKED`, gates `Draft → Accepted` | "Adversarial Review" — one stage of seven, broader defect-hunt, not bound to an external contract |
| Gate never edits/decides/merges | Explicit list, §8 "Какво Kernel никога не прави" | Implicit via role separation (Kernel Review ≠ Headquarters) | Implicit — Adversarial Review produces "a stated verdict," a later, separate step (Freeze Recommendation → human `FROZEN`) decides |
| Reviewer/gate-author independence | "в идеалния случай" (ideally, not absolute) | "в идеалния случай" mirrored: "ideally, different from the artifact's author" (via `INV-5` cross-reference) | "preferred but... not required to proceed" — same-session review must disclose the limitation |
| Human Final Authority (accept/merge/protocol-change) | `INV-4`, explicit; Authority Matrix ("Само човек") | "Headquarters commits the status change" — **does not state Headquarters must be human** | "an explicit human decision... accepts the Freeze Recommendation"; "Discovery Lab does not freeze itself" |
| Drift / normative-operational mismatch, named state | `INV-6` + full procedure (§6) | — (Authority Matrix precedence order addresses a narrower, different question) | — (`NOT READY` verdict is a lifecycle rollback, not a named cross-layer drift state) |
| Structured Handoff, never itself evidence | §14, fixed template | "A Handoff is never evidence and never replaces repository state" | — (out of `GOVERNANCE.md`'s scope) |
| Human-mediated communication, explicitly acknowledged as current-state-only | Implicit in Handoff/session model | Explicit named section ("Human Message Bus (Current Implementation)"); future automation "without changing the collaboration model" | — |
| Staged lifecycle, gate before authority | Assumed (Authority Matrix; §16) | Two states: `Draft → Accepted`, one gate | Seven named stages, most granular of the three |
| Versioning tied to change scope | — (not elaborated in the Stable Core sections reconciled here) | — (not elaborated in `ADR-0009`) | Five-way taxonomy: bug fix / clarification / minor / major / deprecation, most granular of the three |
| Self-check against theater/complacency | `INV`-adjacent, §8 "Анти-театър клауза" (20 consecutive `PASS` is a red flag, not success) | — | — |
| No component/role is self-exempting | `INV-5` "Разделение на властите" (structural, absolute) | Role separation via Writer/Authority Matrices (structural, not stated as a named invariant) | Implicit via "no stage may be self-certified by the same act that produced the artifact under review" |

## Reading this matrix

Eleven rows show real convergence (same concept, different
vocabulary); two rows (Drift, Anti-theater) show a concept stated
fully in one source and absent from the other two's cited text; one
row (Human Final Authority) shows a real, specific gap — `KOD`'s
`ADR-0009` does not state the restriction `PM` and `DL` both state
explicitly. None of these gaps are filled by this matrix — see
`4-CONFLICT-RESOLUTION-LOG.md`.
