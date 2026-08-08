# Slice 01 — стартово съобщение за Claude Code

Копирай текста между линиите като първо съобщение в нова сесия.
Приема се, че `CLAUDE.md` и `docs/` вече са в хранилището и са комитнати.

---

```
Context: this repo runs a daily Constraint Archaeology pipeline:
public sources -> Sensor Agent -> observations.jsonl -> anomaly clustering
-> same-mechanism gate -> Constraint Archaeology v0.5 -> adversarial review
-> WATCH / INVESTIGATE / KILL.

Read CLAUDE.md and docs/method/README.md before anything else. The method is
frozen; this task does not touch it.

TASK — Slice 01: wire the append-only findings ledger into the pipeline.

constraint-archaeology-agents/findings_ledger.py already exists and its tests
pass (16/16 offline). It is NOT yet called from anywhere. Your job is only the
integration.

Dual-write only:
- every NEW derived decision is ALSO appended to
  constraint-archaeology-agents/data/findings.jsonl
- existing snapshot files stay authoritative and unchanged
- no existing reader is migrated
- no backfill of historical records

Kinds to wire, and nothing else:
  anomaly | mechanism_profile | same_mechanism_decision | ca_evaluation

Rules:
- derived_from must reference the records actually used. Do not fabricate
  provenance to satisfy the schema. If the current code does not expose enough
  provenance for a kind, say so and record the strongest truthful chain
  available.
- persist ALL three gate outcomes, not just merges
- ca_evaluation carries method_version="0.5"; analyst_version is the adapter
  version, not the method
- one FindingsLedger per run, created once at the start
- ledger writes are wrapped in try/except and must never break the daily run
- do not change same_mechanism_gate logic, any threshold, or any frozen file

FIRST STEP — do not edit anything yet:
1. print the tree (git ls-files)
2. show me the daily runner and the clustering/memory module
3. show me exactly where the gate is called and where CA evaluations are
   produced
4. list the precise write points you propose to hook, one per kind
5. flag any kind where truthful provenance is not currently available
Then stop and wait for my confirmation before writing any code.

Completion criteria: daily pipeline still runs; all existing tests pass; ledger
tests pass; findings.jsonl is append-only; retry is idempotent; all gate
outcomes persisted; no reader migrated; no frozen file changed.

Report at the end: files changed / integration points / provenance strategy /
tests run + results / what you deliberately did not implement / risks /
recommended next slice. Do not start the next slice.
```

---

## Защо е написано така

**„Stop and wait" преди редакциите.** Без този ред ще предположи имената на файловете и
ще познае част от тях грешно. Точките на запис са единственото, което не мога да
определя отдалеч.

**`try/except` около записа.** Регистърът още не е критичен път. Не бива да събаря
дневния run заради собствената си незрялост.

**„Do not fabricate provenance."** Схемата се удовлетворява лесно с измислени id-та.
Регистър с фалшив провенанс е по-лош от липсващ регистър — изглежда като доказателство.

## Следващ разрез — не се стартира сега

Едва след като Slice 01 работи няколко цикъла: `spec_fingerprint` върху ~20 артикула
за C3. Това е първото нещо, което започва да натрупва непопълваем актив.
