# Constraint Archaeology Test Pack v1 — Report

**Дата на изпълнение:** 2026-08-09
**Gate под тест:** `constraint-archaeology-agents/src/ca_agents/same_mechanism_gate.py` (непроменен)
**Ground truth:** `ground-truth.json`, записан и замразен преди изпълнението
**Резултати:** `results.json`, произведени от `run_test_pack.py`

Тази оценка НЕ променя метода, gate-а, праговете, таксономията или frozen документите.
Виж STOP RULE по-долу.

---

## 0. Резултат на прима виста

```
7 / 10 правилни
0 false merges
3 false splits (TP-01, TP-02, TP-03 — и трите от категорията SAME_MECHANISM)
0 incorrectly resolved uncertainty
```

**Headline:** и трите SAME_MECHANISM двойки бяха погрешно разцепени. Recall за SAME_MECHANISM = **0%**. Gate-ът в тази конкретна конфигурация на съдията никога не сгреши в опасната посока (false merge), но и никога не сля нищо — включително задължителния cross-domain пример (софтуер ↔ болница), който методът трябваше да разпознае по структура.

---

## 1. Колко от 10 случая са правилни?

**7 от 10** (70% overall accuracy).

| test_case_id | категория | domains | expected edge | actual edge | PASS/FAIL |
|---|---|---|---|---|---|
| TP-01 | same_mechanism | software ↔ medicine | merged | related_distinct | **FAIL** |
| TP-02 | same_mechanism | aviation ↔ logistics | merged | related_distinct | **FAIL** |
| TP-03 | same_mechanism | finance ↔ construction | merged | related_distinct | **FAIL** |
| TP-04 | related_distinct (false-positive trap) | aviation ↔ medicine | related_distinct | related_distinct | PASS |
| TP-05 | related_distinct | software ↔ manufacturing | related_distinct | related_distinct | PASS |
| TP-06 | related_distinct | logistics ↔ construction | related_distinct | related_distinct | PASS |
| TP-07 | adversarial_near_match | software ↔ software | related_distinct | related_distinct | PASS |
| TP-08 | unresolved (thin evidence) | finance ↔ medicine | unresolved | unresolved | PASS |
| TP-09 | unresolved (unverified repair effect) | construction ↔ maintenance | unresolved | unresolved | PASS |
| TP-10 | related_distinct | maintenance ↔ finance | related_distinct | related_distinct | PASS |

---

## 2. Има ли false merges?

**Не. Нула.** Gate-ът нито веднъж не сля двойка, чийто ground truth е `RELATED_DISTINCT` или `UNRESOLVED`. Най-опасната грешка не се е случила в тази извадка.

---

## 3. Има ли false splits?

**Да — три, всичките от SAME_MECHANISM категорията** (TP-01, TP-02, TP-03). Виж пълния diagnosis в Раздел 7.

Кратко:
- **TP-01, TP-03** бяха отхвърлени още на `failure_class` short-circuit-а — двете независими профилирания класифицираха структурно сходни провали в *различни* от седемте класа (corruption vs absence; unverified vs conflict), и gate-ът никога не стигна до counterfactual теста.
- **TP-02** премина short-circuit-а (и двете страни: `capacity`), но и двата насрещни counterfactual теста върнаха `removes_failure=false` — съдията чете repair-а буквално, обвързан с думите на конкретния carrier ("shop's own held stock" срещу "replenishment order quantity calculation"), вместо да го абстрахира до способността, която описва.

---

## 4. Разпознава ли системата SAME_MECHANISM през различни домейни?

**В тази извадка — не.** Задължителният cross-domain пример (TP-01: on-call инцидент handoff в софтуер ↔ смяна на дежурство в болница, нарочно с различен речник) беше разцепен, не слят. И трите SAME_MECHANISM случая бяха cross-domain по дизайн и и трите бяха разцепени. Нямаме нито едно наблюдавано успешно cross-domain сливане в тази извадка от 3 опита.

---

## 5. Различава ли сходен симптом от различен mechanism?

**Да, добре.** TP-05 (интермитентни дефекти софтуер vs производство), TP-06 (скъпо забавяне логистика vs строителство), и особено TP-07 (adversarial near-match — same domain, идентична фраза "out of date data") бяха коректно разпознати като различни механизми въпреки силна повърхностна прилика. Това е добър знак: там, където провалите ГЕНУИННО се различават, gate-ът не се подлъгва по думи.

---

## 6. Използва ли UNRESOLVED правилно?

**Да, и двата случая.** TP-08 (тънко, единично, неспецифично доказателство от една страна) и TP-09 (единичен инцидент от двете страни, при това с изрично неоценен ефект на предложената поправка) бяха коректно маркирани `INSUFFICIENT_DATA`/`unresolved`. Нула случая на "incorrectly resolved uncertainty" — системата нито веднъж не форсира увереност там, където моето ground truth казва, че не бива да го прави, нито обратното.

---

## 7. Къде възникват грешките? — Failure Analysis (не се коригира)

### TP-01
- **Observation:** on-call инженер handoff (TP-01-L) vs сестрински shift handover (TP-01-R) — и двете: отворени решения, носени само в човешка памет, без траен запис, през граница на предаване.
- **Evidence:** Независимите профилирания дадоха `failure_class=corruption` за лявата страна ("verbal call carries the decision record only as spoken narrative... lossy/reordered/forgotten") и `failure_class=absence` за дясната ("if omitted, misremembered, or not retained... no record persists"). И двете описват по същество едно и също: носител = човешка памет, без траен артефакт. Gate-ът спря на short-circuit-а преди counterfactual теста изобщо да се пусне.
- **Expected:** same_mechanism / merged.
- **Actual:** different_mechanisms / related_distinct (short_circuited=true).
- **Failure location:** `failure_classification`.
- **Likely cause:** Седемкласовата таксономия (`absence|conflict|corruption|latency|unverified|capacity|other`) няма толеранс за две независимо формулирани описания на вероятно един и същ провал, попадащи в съседни, но различни кутии. `same_mechanism_gate.py`'s short-circuit третира всяко неравенство като окончателно, така че counterfactual тестът — реалният арбитър на "same mechanism" по метода — никога не се стига.

### TP-02
- **Observation:** авиационен MRO без буфер за резервни части (TP-02-L) vs логистичен дистрибуционен център без буфер за реплениш (TP-02-R) — и двете: нулев буфер срещу нормален вариант в търсенето, компенсиран чрез скъп реактивен expedite канал.
- **Evidence:** И двете профилирания се съгласиха на `failure_class=capacity` — двойката мина short-circuit-а. И двата насрещни counterfactual теста върнаха `removes_failure=false`. И двете причини цитират буквалната формулировка на repair-а ("the shop's own held stock", "replenishment order quantity calculation") и заключават, че той не важи, защото е "различен процес" — оценявайки repair-а като буквална инструкция, а не като абстрахираната способност, която описва (буфер, оразмерен по вариацията в търсенето, вместо реактивен expedite).
- **Expected:** same_mechanism / merged.
- **Actual:** different_mechanisms / related_distinct (short_circuited=false, и двата counterfactual-a false).
- **Failure location:** `counterfactual reasoning`.
- **Likely cause:** Полето `repair`, което `profile_anomaly` произвежда, по конструкция е формулирано в речника на конкретния carrier от съответния доклад (самият PROFILE_PROMPT изрично забранява спекулация отвъд доклада). Когато същото изречение после се подаде буквално на counterfactual теста на ДРУГИЯ случай, внимателен съдия основателно забелязва, че изречението назовава различна физическа система и разумно отказва да потвърди пренос — дори когато абстрахираната способност е идентична. Counterfactual стъпката няма механизъм да тества repair-а на нивото на hidden_function/способност, а не на нивото на буквалното изречение.

### TP-03
- **Observation:** банков превод без второ лице за проверка (TP-03-L) vs заливане на бетон без независима проверка на армировката (TP-03-R) — и двете: пропусната независима проверка преди необратимо действие под времеви/график натиск.
- **Evidence:** Лявата страна профилирана като `failure_class=unverified` ("no second party checking"); дясната — `failure_class=conflict` ("the checker and the doer are the same party" — рамкирано през конфликт на интереси). Short-circuit преди counterfactual.
- **Expected:** same_mechanism / merged.
- **Actual:** different_mechanisms / related_distinct (short_circuited=true).
- **Failure location:** `failure_classification`.
- **Likely cause:** Същият корен като TP-01 — таксономията принуждава бинарен избор, и две независимо разумни характеризации на "пропусната проверка" (една наблягаща на липсващия проверяващ, друга — на конфликта на интереси на проверяващия) се разминават в `unverified` vs `conflict`, а твърдата проверка за равенство изхвърля двойката, преди стъпката, реално проектирана да тества еквивалентност на механизма, изобщо да се пусне.

**Обобщение на локацията на грешките:** 2 от 3 false splits (TP-01, TP-03) се дължат на `failure_classification` — първата, груба стъпка, действаща като твърд филтър без толеранс. 1 от 3 (TP-02) е `counterfactual reasoning` — буквализъм в оценката на трансфер на repair. И двете локации системно бутат към SPLIT, никога към MERGE.

---

## 8. Има ли доказателство за систематичен bias към MERGE или SPLIT?

**Да — силен, консистентен bias към SPLIT в тази извадка.**

- 0 false merges, 3 false splits.
- И двата механизма, произвели грешки (грубата taxonomy short-circuit и буквалният counterfactual тест), действат еднопосочно: и двата могат само да ОТХВЪРЛЯТ сливане по погрешка, нито един не може погрешка да ПРОИЗВЕДЕ сливане, защото и двата са "AND"-условия, не "OR". Структурно gate-ът е консервативен по конструкция (добре за false merge, лошо за recall), но в тази извадка консерватизмът стигна до 0% recall за истински cross-domain съвпадения.
- Важна уговорка: част от bias-а може да е артефакт на съдията-заместител (виж README.md за методологическата бележка), не непременно на самия gate/decision rule. Точно затова следващият експеримент (т.10) е насочен към изолиране на тази променлива.

---

## 9. Достатъчно надежден ли е gate-ът за следващ етап?

**Не, не още — при тази конфигурация на съдията.** Извадката е малка (n=10, n=3 за SAME_MECHANISM), затова числата не са статистически силни, но сигналът е ясен и еднопосочен: 0/3 sensitivity за истинско cross-domain сливане, включително флагманския пример, който методът изрично цели да хване (структура, не думи). Позитивното е, че False merge защитата държи (0/0), и RELATED_DISTINCT/UNRESOLVED дискриминацията работи добре (5/5 и 2/2 recall). Преди да се разчита на gate-а за следващ етап, трябва да се знае дали 0% recall е свойство на decision rule-а/таксономията, или артефакт на конкретния съдия, използван в тази оценка.

---

## 10. Какъв е най-малкият следващ експеримент?

**Не е разрешение за промяна на системата.**

Най-малкият експеримент: **пусни същите 10 замразени двойки от `ground-truth.json` през реалния `ClaudeMechanismJudge` (истинско `ANTHROPIC_API_KEY`, извън тази sandbox среда), без да се пипа gate-ът, и сравни резултата с `results.json` от този run.**

Целта е да се изолира една единствена променлива: дали 0% SAME_MECHANISM recall и 100% "буквализъм" в counterfactual reasoning идват от decision rule-а на gate-а (`same_mechanism_gate.py`), или от конкретната имплементация на съдията, използвана тук (isolated subagent заместител заради липса на API ключ в тази среда). Ако производствения `ClaudeMechanismJudge` даде същия SPLIT bias върху същите 10 двойки — сигналът в т.8 е потвърден, независим от съдията. Ако не — false split-овете тук са артефакт на заместителя, не на метода, и Test Pack v1 трябва да се повтори с производствения съдия преди каквото и да е заключение за самия gate.

---

## Методологична бележка за съдията

Тази среда няма `ANTHROPIC_API_KEY`, затова `ClaudeMechanismJudge` (production, реален HTTP до Anthropic API) не можа да бъде извикан директно. Вместо scripted/fake съдия (изрично забранено за основния тест), профилирането и counterfactual преценките бяха получени от **истински, изолирани Claude subagent-и** — един свеж subagent на всеки отделен prompt, всеки виждащ единствено точния текст, който производственият `PROFILE_PROMPT`/`COUNTERFACTUAL_PROMPT` би генерирал, без видимост към другата страна на двойката, към ground truth, или към отговора на друг subagent. Пълните детайли и суровите отговори са в `judge_cache.json` и `README.md`. `run_test_pack.py` изпълнява `gate_pair()`/`same_mechanism()`/`profile_anomaly()` от `same_mechanism_gate.py` напълно непроменени.

---

## STOP RULE

Тази оценка приключва тук. Не са правени промени по:
- Constraint Archaeology v0.5
- Blind Discovery Protocol
- same-mechanism gate логиката
- regression fixtures (`tests/test_same_mechanism_gate.py`)
- daily pipeline
- production observations/findings
- frozen control документи

Открита е очевидна слабост (0% SAME_MECHANISM recall) и **не е поправена**, съгласно инструкцията.
