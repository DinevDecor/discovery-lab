# Findings Ledger — Slice 01

## Какво е това

`constraint-archaeology-agents/data/findings.jsonl` е **append-only** поток от
изведени решения на pipeline-а.

- **Append-only.** Никога не се пренаписва. Няма изтриване и няма редакция на стар запис.
  По-нов резултат се записва като **нов** Finding, не като поправка.
- **В момента е dual-write.** Записва се успоредно със съществуващите файлове.
- **Файловете-снимки остават истината за изпълнението.** `observations.jsonl`,
  `anomalies.json`, `latest-evaluations.json` и дневният доклад не са променени.
- **Findings са изведени, не сурови.** Затова всеки запис носи `origin: "generated"`.
  Сурови доказателства не влизат тук.
- **Нито един читател още не консумира регистъра.** Той е история и одит.
- **Не е правен исторически backfill.**

## Защо няма backfill

Регистърът е активен **от момента на първия запис нататък**. Записан със задна
дата Finding не е равностоен на Finding, записан тогава — точно това разграничение
е причината регистърът изобщо да съществува. Ако някога се направи backfill, той
трябва да е отделна задача и записите да носят изричен маркер, че са
реконструирани.

## Envelope

```json
{
  "finding_id": "same_mechanism_decision:9f2c...",
  "kind": "same_mechanism_decision",
  "recorded_at": "2026-08-08T12:00:00Z",
  "derived_from": ["mechanism_profile:an-1", "mechanism_profile:an-2"],
  "analyst": "same_mechanism_gate",
  "analyst_version": "0.1.0",
  "method_version": null,
  "origin": "generated",
  "payload": { }
}
```

**Поддържани `kind` в този разрез — само това, което pipeline-ът произвежда днес:**
`anomaly` · `mechanism_profile` · `same_mechanism_decision` · `ca_evaluation`.

**`analyst_version` vs `method_version`.** За изходите на Constraint Archaeology
`method_version` е винаги `"0.5"`, а `analyst_version` е версията на **адаптера**.
Промяна в интеграцията мърда адаптера; замразеният метод не мърда. Записът показва
разликата.

**Провенанс.** `derived_from` сочи към записите, които наистина са били използвани.
Празен провенанс се отхвърля, освен ако извикващият изрично подаде
`allow_empty_provenance=True` **и** запише причината в `payload["provenance_note"]`.
Не се измисля провенанс, за да мине схемата.

**Всички изходи на gate-а се пазят** — `MERGED`, `RELATED_DISTINCT` и `UNRESOLVED`.
Отказаното сливане е историята, заради която този регистър съществува.

---

# Списък за интеграция (не е изпълнен — вж. бележката за достъпа)

Закачането изисква точките на запис в реалния код. За всяка от четирите:

| Kind | Къде се закача | Какво трябва да е налично на място |
|---|---|---|
| `anomaly` | там, където се създава или обновява аномалия | `anomaly_id` + списък `observation_id` |
| `mechanism_profile` | след профилирането на всяка аномалия поотделно | `subject_id` + id-тата, от които е изведен профилът |
| `same_mechanism_decision` | веднага след връщането на решението от gate-а, **за всичките три изхода** | `GateDecision` + `gate_version` |
| `ca_evaluation` | след оценката по v0.5 | `subject_id` + точните доказателства + версия на адаптера |

**Форма на закачането — една линия на точка на запис:**

```python
ledger.append(build_same_mechanism_decision(
    left_id=d.left_id, right_id=d.right_id,
    verdict=d.verdict.value, edge=d.edge.value,
    reasons=d.reasons,
    counterfactuals=[c.__dict__ for c in d.counterfactuals],
    short_circuited=d.short_circuited,
    gate_version=GATE_VERSION,
    derived_from=[...],            # реалните входове, не измислени
    analyst_version=PIPELINE_VERSION,
))
```

**Правила при закачането:**

1. Един `FindingsLedger` на изпълнение, създаден веднъж в началото.
2. Записът е **след** съществуващия запис в снимковите файлове, не вместо него.
3. Провал при запис в регистъра **не спира** pipeline-а в този разрез —
   ловете изключението и го логвайте. Регистърът още не е критичен път.
4. Незадължителен ред в доклада: `Findings appended: N` от `append_many`.
5. Нито един читател не се сменя.
