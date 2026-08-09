# Как да сложиш това в хранилището

Пакетът е подреден точно както трябва да легне в `discovery-lab`.

## 1. Разархивирай в корена на хранилището

```bash
cd /path/to/discovery-lab
tar -xzf discovery-lab-bundle.tar.gz --strip-components=1
```

## 2. Провери какво презаписваш

| Файл | Ако вече съществува |
|---|---|
| `CLAUDE.md` | **слей ръчно.** Разделите „Frozen artifacts" и „Project rules" се добавят към твоя, не го заместват |
| `constraint-archaeology-agents/same_mechanism_gate.py` | **запази твоя.** Ако вече е интегриран и адаптиран, версията тук е по-стара по контекст |
| `tests/test_same_mechanism_gate.py` | **запази твоите фикстури.** Те са част от замразената база |
| всичко останало | ново, няма конфликт |

```bash
git status              # преди commit
git diff --stat
```

## 3. Пусни тестовете

```bash
python tests/test_findings_ledger.py        # очаква се 16/16
python tests/test_same_mechanism_gate.py    # очаква се 7/7
```

И двата файла работят и без pytest, и с pytest.

**Забележка за пътищата:** тестовете импортират `findings_ledger` и
`same_mechanism_gate` директно. Ако `constraint-archaeology-agents/` не е в
`sys.path`, добави `conftest.py` в корена или `PYTHONPATH=constraint-archaeology-agents`.
Това е единствената настройка, която може да потрябва.

## 4. Комитни преди да пуснеш Claude Code

```bash
git add -A
git commit -m "docs: freeze method v0.5, protocols, controls; add findings ledger (unwired)"
```

Важно е да е комитнато **преди** първата сесия: така Claude Code вижда замразените
документи като част от хранилището, а не като контекст, който трябва да му пействаш.

## 5. Отвори нова сесия и подай `KICKOFF-slice-01.md`

Текстът за копиране е между линиите в този файл.

---

## Какво съдържа пакетът

```
CLAUDE.md                              правила и замразени артефакти
KICKOFF-slice-01.md                    стартовото съобщение
INSTALL.md                             този файл

docs/method/README.md                  ред на четене и старшинство
docs/method/*.md                        спецификация v0.4 + кръпка v0.5, протокол, ход 1
docs/method/controls/*.md              валидационната история, 7 документа
docs/architecture/*.md                 Reality Observatory v0.1, разширения
docs/decisions/README.md               5 кандидата за ADR, нито един написан
docs/reviews/*.md                      противникови прегледи

constraint-archaeology-agents/
  findings_ledger.py                   append-only писач, незакачен
  same_mechanism_gate.py               gate, ако вече не е при теб
  FINDINGS_LEDGER.md                   документация + списък за интеграция

tests/
  test_findings_ledger.py              16 теста, офлайн
  test_same_mechanism_gate.py          7 теста, офлайн
```

## Какво НЕ е направено

- Регистърът **не е закачен** за нито една точка на запис. Това е Slice 01.
- Няма backfill и не бива да има без отделно решение.
- Няма ADR-и.
- Ход 2 от проспективния тест — прагове и предсказание до 28.02.2027 — не е направен
  и **не е работа за Claude Code.** Той остава в разговора за метода.
