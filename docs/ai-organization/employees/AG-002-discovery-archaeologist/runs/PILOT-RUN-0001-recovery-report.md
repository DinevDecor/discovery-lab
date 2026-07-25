# Recovery Report

## Run Metadata

- **Run ID:** PILOT-RUN-0001
- **Timestamp:** 2026-07-24
- **Sources requested:** "the supplied diary archive" together with "the
  Project Memory archive."
- **Sources scanned:**
  - `project-memory/archive/architecture-design-document.md` (full)
  - `project-memory/archive/spike-protocol-potok-b.md` (full)
  - `project-memory/archive/AI-Collaboration-Architecture-v1_0.md`
    (full)
  - `project-memory/archive/AI-Collaboration-Architecture-v1_1.md`
    (full)
  - `project-memory/archive/project-memory-phase-1.zip` (listing only —
    confirmed, via prior session work, to contain a backup snapshot of
    `project-memory`'s own phase-1 files already present and read in
    their current form below; not separately extracted or re-mined for
    this run)
  - For "Idea Evolution" and "latest state" comparison only (current,
    not archival, but within the same `project-memory` repository):
    `project-memory/protocols/AI_COLLABORATION_PROTOCOL.md`,
    `project-memory/adr/ADR-0001-ai-collaboration-architecture.md`,
    `project-memory/PROJECT_REGISTRY.md`,
    `project-memory/notes/2026-07-19-dinev-decor-systems-location-check.md`
- **Sources inaccessible:** the "diary archive" named in the run
  request. A full filesystem search (`/home/user`, `/workspace`, and a
  broad `find / -xdev -iname "*diary*" -o -iname "*journal*"`) found no
  matching file anywhere accessible to this session — recorded as
  `INSUFFICIENT ACCESS`, not substituted with different material without
  saying so.

---

## Executive Summary

This run scanned the Project Memory archive only; the named diary
archive could not be located anywhere accessible and is not included.
Within the material actually scanned, this run recovered: one
completely designed but apparently never-executed business system
(an installer "Handover" architecture), one completely designed but
apparently never-run validation spike ("Поток B"), a documented
two-version evolution of this repository's own collaboration
architecture with several ideas that survived unchanged, several that
were explicitly revised, and at least one (a governance "Kernel" layer)
that reappears after being absent from the earliest version scanned. No
new ideas are proposed here — only what the sources themselves already
say, with citations.

---

## Recovered Ideas

1. **A complete installer "Handover" / Readiness architecture.** An
   18-section production-grade system design (executive summary,
   goals/non-goals, domain model, state machines, AI architecture,
   security, technology stack, ADR backlog, phased rollout plan).
   [Evidence 1]
2. **A complete "Поток B" validation spike protocol** for testing
   whether recorded installer-dispatcher phone calls can be reliably
   turned into structured data via STT + LLM extraction, with
   pre-registered, frozen success thresholds. [Evidence 2]
3. **A "Kernel" governance layer** — a formal gatekeeper role, separate
   from an Author/Reviewer/human arbiter, returning only PASS or
   BLOCKED. [Evidence 3]
4. **A "Control Plane" concept** — one repository (`project-memory`)
   holding shared protocol, contracts, templates, and a cross-project
   registry, which other project repositories reference rather than
   copy. [Evidence 4]
5. **A five-stage session lifecycle** — `OPEN → BRIEF → WORK → EXTRACT
   → CLOSE`. [Evidence 5]
6. **A "Fast-track" lighter path** for small changes, distinct from the
   full flow. [Evidence 6]
7. **A revised rule on old/stale chats** — from "never return to an old
   chat" to "an old chat is a legitimate raw source, but never a source
   of authority." [Evidence 7]

---

## Repeated Themes

- **"AI proposes; only a human decides."** Present, worded differently
  each time, in all three points in time scanned: "Само човекът пише
  истина" (v1.0); "Човешка крайна власт... само човекът: приема ADR,
  разрешава merge, разрешава drift" (v1.1); "Only the human accepts
  governance decisions and authorizes merge" (current protocol).
  [Evidence 8]
- **"The repository, not the chat, is authoritative."** v1.0's
  "Инвариант #1... Знание, което живее в чат, е мъртво знание"; v1.1's
  INV-1/INV-2; the current protocol's points 1–2, worded almost
  identically to v1.1. [Evidence 9]
- **"Roles are contracts, not models."** v1.0 P4; v1.1 INV-3; current
  protocol point 4 — same idea, three points in time, increasingly
  terse each time. [Evidence 10]
- **`OPEN → BRIEF → WORK → EXTRACT → CLOSE`** — appears with the
  identical five words, in the identical order, in v1.0, v1.1, and the
  current protocol. Of everything scanned in this run, this is the
  single most stable idea found — unchanged across every version
  available. [Evidence 5, restated]

---

## Idea Evolution (Discovery Timeline)

### Idea: Session/chat lifecycle discipline

- **First appearance:** v1.0 — "Инвариант", "Един чат = една задача."
  [Evidence 11]
- **Reappearance:** v1.1 explicitly revises this: "Промени спрямо v1.0:
  ... „един чат = една задача" заменено с „една сесия = една ограничена
  цел"." [Evidence 12]
- **Latest state:** current protocol's "Session rule" — "One working
  session has one bounded goal," matching v1.1's revised wording, not
  v1.0's original. [Evidence 13]
- **Recommendation (procedural only, not a judgment):** stable since
  v1.1; no contradiction found between v1.1 and current practice within
  the sources scanned. No further action queued.

### Idea: Kernel governance layer

- **First appearance in sources scanned:** absent from v1.0 entirely —
  confirmed by a full section-header scan of that document; no
  "Kernel" section exists in it.
- **Reappearance:** v1.1 §8, "Kernel Governance Layer" — and v1.1's own
  changelog line says the concept was "върнат" (**brought back**),
  implying an even earlier version not present in the sources scanned
  for this run. [Evidence 14]
- **Latest state:** the current, accepted protocol names Kernel as one
  of four minimal pilot roles ("applies an explicit Review Contract and
  returns only PASS or BLOCKED") — but the accepting ADR explicitly
  states Pilot 0 "does not validate... Kernel value." [Evidence 15]
- **Recommendation (procedural only):** queued — see Recovery Queue.
  Whether Kernel has been exercised anywhere since acceptance is outside
  this run's authorized scope to check.

### Idea: Control Plane (central cross-project governance hub)

- **First appearance:** absent from v1.0 — that document describes each
  project repository independently, with no central hub.
- **Reappearance:** v1.1 §4, "Control Plane Architecture," proposing
  `project-memory` as the hub. [Evidence 4, restated]
- **Latest state:** `ADR-0001` accepts this exactly: "Project Memory is
  established as the collaboration control plane." `PROJECT_REGISTRY.md`
  exists and lists five projects. [Evidence 16]
- **Recommendation (procedural only):** the core idea is fully present
  in current practice. One specific mechanism v1.1 proposed alongside
  it — a per-project `PROTOCOL_BINDING.md` file — was checked in one
  place (KOD, already cloned in this session from unrelated prior work)
  and not found there. Whether this was implemented anywhere is
  otherwise outside this run's authorized scope. Queued as an open
  question, not asserted as abandoned.

### Idea: Number of formal roles/contracts

- **First appearance:** v1.0's table of contents lists "Шестте договора
  накратко" (six contracts). [Evidence 17]
- **Reappearance:** v1.1 §7, "Минимално ядро: 4 роли," explicitly
  demoting two of the six ("Planner and Librarian remain modes until
  repeated work... justify separate contracts," in the current
  protocol's own English restatement). [Evidence 18]
- **Latest state:** current protocol's "Minimal pilot roles" lists
  exactly four — Architect/Researcher, Reviewer/Breaker, Implementer,
  Kernel — with the same Planner/Librarian deferral language as v1.1.
  [Evidence 19]
- **Recommendation (procedural only):** stable since v1.1; no further
  narrowing evidenced in the sources scanned.

### Idea: How old/stale chats should be treated

- **First appearance:** v1.0 — "CLOSE: Чатът се изоставя. Не се
  връщаш в него." (an explicit "never return" rule). [Evidence 20]
- **Reappearance:** v1.1 explicitly reverses this — "НЕ: 'Никога не се
  връщай в стар чат.' ДА: '...стар чат [е] легитимен суров източник'"
  — old chats become a legitimate raw source (for research trail,
  missed observations, decision history), while remaining
  non-authoritative. [Evidence 7, restated]
- **Latest state:** the current, shorter protocol document does not
  restate this nuance either way.
- **Recommendation (procedural only):** queued — whether v1.1's
  correction is still active practice, or was simply dropped when the
  protocol was condensed, could not be determined from the sources
  scanned.

---

## Forgotten Ideas

1. **The Handover / Readiness architecture appears to have no
   recorded follow-up anywhere in the sources scanned.** The document
   itself is complete and ready to build (18 sections, an 8-week
   implementation sequence, an ADR backlog). `PROJECT_REGISTRY.md`'s
   "Dinev Decor Systems" row — the only registry entry plausibly
   matching this system's subject matter — currently reads "Repository
   or operational system to be established... Not yet bound."
   [Evidence 1, 21]
2. **The Поток B spike protocol appears to have no recorded execution
   anywhere in the sources scanned.** An independent, earlier
   investigation already reached the same conclusion by a different
   method: "Artifacts found: a complete, fixed-threshold validation
   protocol. No audio, no transcripts, no extraction outputs, no
   results," after a dedicated filesystem search for audio/transcript
   patterns found nothing. [Evidence 2, 22]

---

## Candidate Investigations

Proposed only. **No Investigation file is created by this report.**

1. Whether the Handover / Dinev Decor Systems architecture should be
   formally bound to a repository, or explicitly retired, and why
   eight months (by document dates) have passed without either.
2. Whether Поток B was ever run, partially run, in progress elsewhere,
   or superseded by a different approach.
3. Whether Kernel's practical value — explicitly left unvalidated by
   Pilot 0's own stated boundary — has since been tested anywhere.
4. Whether the v1.1 "old chats are a legitimate raw source" correction
   remains current practice.

---

## Contradictions

- **Documented revision, not a live contradiction:** v1.0's "never
  return to an old chat" versus v1.1's explicit reversal. v1.1 names
  itself as replacing v1.0 and states the change outright — this is
  the sources correcting themselves in the open, not two live,
  competing claims. Recorded here for completeness, not as an unresolved
  disagreement. [Evidence 7, 20]
- **A gap between principle and observed outcome, not a logical
  contradiction:** every version of the collaboration architecture
  scanned states that decisions should be deliberate and explicit
  (never silent, never assumed). Yet the Handover architecture — a
  complete, deliberate design — sits with no recorded decision, in
  either direction, anywhere in the sources scanned. This is not two
  texts disagreeing; it is a designed system with no recorded outcome
  at all. Reported as a gap, not adjudicated.

---

## Open Questions

- Where the "supplied diary archive" actually is, if it exists.
- Whether `PROTOCOL_BINDING.md` (or an equivalent) exists in any
  project repository other than KOD, which was the only one checked in
  this run.
- Whether Kernel has been exercised in any real session since
  `ADR-0001`'s acceptance.
- Whether the Handover architecture is still an active intention.
- Whether Поток B was ever executed anywhere outside this run's
  scanned sources.
- Whether the v1.1 "old chats" correction is still active guidance.

---

## Recovery Queue

Listed for a human or Curator to act on. **Nothing below is
auto-escalated to an Investigation.**

1. Handover / Dinev Decor Systems architecture — status check
   recommended.
2. Поток B spike — status check recommended (a second, independent
   check now agrees with the 2026-07-19 note's own conclusion).
3. Kernel value validation — currently outside any pilot's declared
   boundary.
4. "Old chats as raw source" — whether this guidance is still active.

---

## Evidence

1. `project-memory/archive/architecture-design-document.md`, full
   document, e.g. Executive Summary (lines 7–11), Evolution to Product
   (lines 305–313), ADR Backlog (lines 336–352).
2. `project-memory/archive/spike-protocol-potok-b.md`, full document,
   e.g. header (lines 1–5), decision format (lines 218–232).
3. `AI-Collaboration-Architecture-v1_1.md`, line 279, "## 8. Kernel
   Governance Layer."
4. `AI-Collaboration-Architecture-v1_1.md`, lines 76–115, "## 4. Control
   Plane Architecture."
5. `AI-Collaboration-Architecture-v1_0.md`, lines 177–183 (diagram);
   `AI-Collaboration-Architecture-v1_1.md`, lines 354–356 (identical
   diagram); `protocols/AI_COLLABORATION_PROTOCOL.md`, lines 62–66
   ("Every session follows: OPEN → BRIEF → WORK → EXTRACT → CLOSE").
6. `AI-Collaboration-Architecture-v1_1.md`, line 493, "## 13.
   Implementation Flow + Fast-track"; `adr/
   ADR-0001-ai-collaboration-architecture.md`, line 61, "KOD Sprint 23
   will be used as Fast-track Pilot 0."
7. `AI-Collaboration-Architecture-v1_1.md`, lines 363–369, "Старите
   чатове — коригирано правило."
8. `AI-Collaboration-Architecture-v1_0.md`, line 40, "P3 ... Само
   човекът пише истина"; `AI-Collaboration-Architecture-v1_1.md`, line
   42, "INV-4 Човешка крайна власт"; `protocols/
   AI_COLLABORATION_PROTOCOL.md`, line 19, "Only the human accepts
   governance decisions and authorizes merge."
9. `AI-Collaboration-Architecture-v1_0.md`, lines 11–28, "Инвариант #1";
   `AI-Collaboration-Architecture-v1_1.md`, lines 30–37, "INV-1, INV-2";
   `protocols/AI_COLLABORATION_PROTOCOL.md`, lines 15–16.
10. `AI-Collaboration-Architecture-v1_0.md`, line 41, "P4 ... Ролите
    са договори, не модели"; `AI-Collaboration-Architecture-v1_1.md`,
    lines 38–40, "INV-3"; `protocols/AI_COLLABORATION_PROTOCOL.md`,
    line 18.
11. `AI-Collaboration-Architecture-v1_0.md`, line 42, "P5 ... Един чат
    = една задача."
12. `AI-Collaboration-Architecture-v1_1.md`, line 21, "Промени спрямо
    v1.0: ... „един чат = една задача" заменено с „една сесия = една
    ограничена цел"."
13. `protocols/AI_COLLABORATION_PROTOCOL.md`, line 60, "One working
    session has one bounded goal."
14. `AI-Collaboration-Architecture-v1_1.md`, line 21, "Kernel върнат
    като governance слой"; line 279 (§8 header); full-repository scan
    of `AI-Collaboration-Architecture-v1_0.md`'s section headers found
    no "Kernel" entry.
15. `protocols/AI_COLLABORATION_PROTOCOL.md`, lines 20, 23, 54;
    `adr/ADR-0001-ai-collaboration-architecture.md`, line 89, "Kernel
    value" listed under what Pilot 0 "does not validate."
16. `adr/ADR-0001-ai-collaboration-architecture.md`, line 59, "Project
    Memory is established as the collaboration control plane";
    `PROJECT_REGISTRY.md`, lines 5–11 (five-row table).
17. `AI-Collaboration-Architecture-v1_0.md`, line 270, "### Шестте
    договора накратко."
18. `AI-Collaboration-Architecture-v1_1.md`, lines 225–244, "###
    Минимално ядро: 4 роли."
19. `protocols/AI_COLLABORATION_PROTOCOL.md`, lines 49–56, "Minimal
    pilot roles."
20. `AI-Collaboration-Architecture-v1_0.md`, line 200, "CLOSE: Чатът
    се изоставя. Не се връщаш в него."
21. `PROJECT_REGISTRY.md`, line 11, "Dinev Decor Systems | Repository
    or operational system to be established | ACTIVE / DISCOVERY |
    Operational memory and workflow systems | Project-specific path to
    be confirmed | Not yet bound."
22. `notes/2026-07-19-dinev-decor-systems-location-check.md`, lines
    40–41 (Поток B artifacts found, no audio/transcripts/results) and
    line 14 ("No loose audio, transcript, or benchmark files exist
    anywhere on the accessible local filesystem").

---

## Archaeologist Boundary Statement

No source document was modified, reordered, or annotated in place by
this run. No source, quote, date, or finding was invented — every claim
above traces to a specific line or section in a document that was
actually read in full during this run, or (for the diary archive) to
an actual, reproducible filesystem search that found nothing. No
recovered idea is asserted as true, good, or worth pursuing — this
report states only that a source says something, and where. No
duplicate was removed. No Investigation was created; the Recovery Queue
above is a proposal list only.
