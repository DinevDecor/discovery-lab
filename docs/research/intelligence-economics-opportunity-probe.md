# Rapid Opportunity Probe: Intelligence Economics / AI Resource Optimization

**Type:** Rapid opportunity probe (not a Constraint Archaeology finding, not a BCA candidate
promotion). This document is a one-time investigation artifact. It does not modify, gate, or
promote anything in the independent CA/BCA pipeline.

**Date:** 2026-08-17
**Branch:** `claude/intelligence-economics-probe-0qnxuz`
**Status:** Investigation complete. Awaiting human review. Not merged.
**Predecessor artifact:** `docs/research/ai-agent-cost-governance-opportunity-probe.md`
(branch `claude/ai-agent-cost-governance-probe-9axch5`, PR #37, decision `INVESTIGATE`). This probe
does not modify that document and does not assume its conclusion is wrong. Where the two overlap,
this document says so explicitly rather than re-deriving the point.

---

## Executive summary

PR #37 investigated **agent cost governance** — "how much may an agent spend, and can that be
enforced" — and found the enforcement layer (budgets, kill switches, orphan cleanup) forming fast
but structurally thin on one specific capability: nobody ties spend enforcement to whether the
spend was *worth it*. This probe was asked to test a broader, adjacent hypothesis: not "control
spend" but "optimize what is purchased" — choose the cheapest model/reasoning-effort/tool/attempt
strategy that clears a required quality bar, and ultimately weigh that cost against the task's
actual business value.

The central finding is that **this hypothesis splits cleanly into two very different-aged
problems, and the probe's job is to not blur them.** The narrower version — "route each task to
the cheapest model/effort setting that meets an accuracy bar" (this document's Layer C) — is not
an emerging category. It is a five-year-old academic research area (FrugalGPT, 2023) with mature
production tooling today: RouteLLM-style routers are cited at 85% cost reduction while retaining
~95% of top-model quality, OpenRouter/Portkey/LiteLLM/Not Diamond/Unify are all shipping products
priced as thin markup on the routed traffic, and — most importantly — **the two strongest
incumbents in the entire industry already built exactly this as flagship product**: Microsoft
Foundry ships a native cost/complexity-aware model router, and OpenAI made automatic model routing
the *core architecture* of GPT-5 itself. OpenAI's router shipped, drew immediate user backlash over
unpredictability, and was partially rolled back within a week to let users bypass it. That is not
evidence the problem is unsolved — it is evidence a top-three AI lab solved the *technical* routing
problem and hit a *trust* problem instead, which is a materially different and more informative
finding than "nobody has tried."

The broader version — "weigh cost against actual downstream business value and stop spending when
marginal cost exceeds marginal value" (this document's Layer D) — is genuinely different in kind,
not degree, from Layer C, and it is empirically almost empty. Real practitioner writing exists
describing agents running economically underwater after passing every quality eval (a documented
case: $4.20 business value per resolved ticket against $4.79 cost per successful outcome — a
59-cent loss on every success, invisible to any eval that only measures accuracy). Real academic
work exists on budget-aware and value-aware stopping (budget-aware value tree search, conformal
risk-controlled stopping rules). But no shipped product was found that takes an economic value
input and outputs a spend decision. The reason is not neglect — it is that Layer D requires an
input (a defensible dollar value for "this specific completed task") that most organizations do
not have and cannot cheaply generate, and that is a data-availability problem, not an engineering
gap a well-funded team can route around.

This reframes the pipeline's own two live, unmerged signals (`ANOM-0213` — routing every task to a
frontier model by default; `ANOM-0153` — small vs. medium local models producing different, harder-
to-diagnose error classes) correctly: they are real, and they are evidence the *pain* of "we don't
know what tier of model a task needs" exists among practitioners today. They are not evidence that
a product opportunity sits open at Layer C — the opposite: this probe's external research found
that exact pain already has a crowded, commoditizing answer. The opening, if there is one, is
narrower and harder than "build a router." It is at the Layer C/D boundary, specifically for
organizations whose "was this worth it" signal is objectively measurable (support ticket
resolution, ad conversion, sales-qualified-lead accuracy) rather than subjective — and even there,
this probe did not find anyone shipping it as a standalone product buyers can point to and buy.

**Decision: WATCH.** Not DROP — Layer D is real, economically evidenced, and genuinely
under-built. Not INVESTIGATE — unlike PR #37's wedge (which had a concrete, narrow, buildable MVP
scoped to orphan cleanup), this probe could not find a Layer-D wedge narrow enough to validate with
a discovery sprint without first solving the same generalized "define task value" problem that has
stalled every other entrant. The correct next step is not customer interviews; it is a scoped
technical/data feasibility check on whether *any* task class has a business-value signal cheap and
reliable enough to build a stopping rule on top of — see Section 20.

---

## 1. Observed evidence, previous research conclusions, and the new hypothesis

Per project rules, these three are kept in strictly separate buckets. Nothing below was generated
by re-reading old anomalies through the new hypothesis's lens; every OBSERVED EVIDENCE row is
quoted from the live pipeline files as they exist on `main` today, unmodified by this probe.

### OBSERVED EVIDENCE (verbatim from the pipeline, read from
`constraint-archaeology-agents/data/observations.jsonl` and `anomalies.json`)

| Anomaly | Status | Observation | Source | Pain (as recorded) | Quote |
|---|---|---|---|---|---|
| `ANOM-0213` | WATCH, single-observation | `OBS-20260811-0076-185bbe` | `discourse:level1techs` | Companies overspend on frontier AI API tokens by routing all requests to expensive models instead of using cheaper models for routine tasks | "stop sending every stupid little task to a frontier model... frontier inference becomes an exception rather than the default" |
| `ANOM-0153` | WATCH, single-observation | `OBS-20260810-0021-7e8921` | `discourse:level1techs` | Smaller (8b–27b) local models make predictable but different errors than medium models; a 12b model could not fix a conceptual error even when pointed directly at it; required 15k manually-run prompts to map the error pattern | "About 15k prompts, a dozen errors for the small, a couple for the middle... the 12b was unable to fix it" |
| `ANOM-0288` | WATCH, single-observation | `OBS-20260812-0075-528ae4` | `discourse:openai-devs` | Difficult to determine which of several conflicting AI-generated engineering recommendations to trust; model agreement does not indicate correctness | "Which evidence is actually relevant to my constraints? How should conflicting recommendations be handled?" |
| `ANOM-0387` | WATCH, single-observation | `OBS-20260816-0009-ff4399` | `discourse:openai-devs` | Prompt-based ("don't spend more than $X") spend limits fail under context crowding, retry loops, or orchestration bugs; billing alerts fire only after the money is gone | "don't spend more than \$X in the system prompt is not a limit. It's a suggestion the agent can talk itself out of" |
| `ANOM-0022` | WATCH → promoted to `BC-0004` (`WATCH`, `frequency: INSUFFICIENT_DATA`) | `OBS-20260808-0031-b9be3e` | `hacker_news` | Cannot predict or control inference cost before the bill arrives; no feedback loop between prompt design and token/cost impact | "developers managing AI inference costs lack real-time visibility into token consumption and costs during LLM API calls" |

A keyword screen for model-selection, routing, budget, context-size, and quality-tradeoff language
against the full 456-record observation set returned 24 matches; the five rows above are the ones
that speak directly to *choosing a resource allocation strategy under a quality requirement* — this
probe's named subject — as opposed to raw cost visibility (already covered by PR #37) or unrelated
infrastructure pain (Zigbee discovery, SSL termination, keyboard-over-RDP, etc., which matched only
on the word "routing" in its networking sense and are excluded here).

**A provenance caution, stated plainly per the frozen "provenance is truthful or absent" rule:**
`ANOM-0153` and `ANOM-0288` were each independently promoted by the BCA pipeline into a business
candidate (`BC-0093` and `BC-0126` respectively). Both candidates are typed `OLD_BUSINESS_REARCHITECTURE`
and, on inspection, their derivation trail (`history[0].derived_from`) cites a *different*
observation ID than the one grounding the anomaly itself — `BC-0093` derives from `OBS-20260810-0026-63ae1f`
(content-tracking-ledger rearchitecture), not `OBS-20260810-0021-7e8921` (the small-vs-medium-model
error-pattern observation this probe cares about); `BC-0126` derives from `OBS-20260813-0006-54f39a`
(AI-content-publishing rearchitecture), not `OBS-20260812-0075-528ae4` (the conflicting-model-
recommendation observation). This looks like ordinary anomaly-renumbering/multi-observation-cluster
bookkeeping in the live snapshot, not a same-mechanism merge decision — but the load-bearing point
for this probe is: **the pipeline's own downstream candidate analysis did not interpret `ANOM-0153`
or `ANOM-0288` as instances of an "intelligence economics" mechanism.** It interpreted the clusters
they belong to as something else entirely. Citing `BC-0093`/`BC-0126` as supporting evidence for
this probe's hypothesis would be exactly the retroactive reinterpretation the task instructions and
CLAUDE.md prohibit, so this document does not do that — the anomalies are cited, the candidates are
not.

### PREVIOUS RESEARCH CONCLUSIONS (PR #37, unmodified, not re-litigated)

- Token/cost observability (Layer A here) — **commoditized**.
- AI application observability (Layer B here) — **commoditizing fast**.
- Agent resource/identity observability — **consolidating before maturing** (Cisco/Astrix).
- Agent cost *governance* — pre-approval + kill switch (Layer B in this probe's task framing) —
  **forming, heating up fast**, ~10–12 funded/hyperscaler entrants in the last 12 months.
- Agent *economic* governance — was spend justified by outcome — **structurally open**, no
  dedicated product found.
- Decision: **INVESTIGATE**. Weakest dimensions: buyer clarity (2/5) and defensibility (2/5).
  Recommended next action: a 10-customer discovery sprint on the orphan-cleanup-tied-to-live-spend
  wedge. Not run yet.

### NEW HYPOTHESIS (this probe's subject, stated precisely, not yet evaluated)

That a distinct infrastructure layer exists, or is about to exist, that does not merely observe or
cap AI spend but **actively chooses the cheapest resource-allocation strategy (model, reasoning
effort, context, attempts, tools, subagents) expected to clear a required quality bar for a given
task**, and — in its strongest form — **weighs that cost against the task's actual expected business
value and declines to spend further once marginal cost exceeds marginal value.**

---

## 2. The four layers, redefined by what this probe actually found

| Layer | Question | Finding |
|---|---|---|
| **A. Cost observability** | "What did AI cost?" | Commoditized (per PR #37, unchanged). |
| **B. Cost control** | "How much may it spend?" | Forming/heating up (per PR #37, unchanged). |
| **C. Cost optimization** | "What is the cheapest execution strategy likely to achieve the required result?" | **Mature research area, commoditizing product layer.** Five-plus years of academic literature (FrugalGPT 2023 onward), a crowded 2026 product market (Section 3), and — the decisive data point — the two strongest incumbents (OpenAI, Microsoft) have already shipped native, automatic versions of this as core product, not an add-on. |
| **D. Intelligence economics** | "How much machine intelligence is it economically rational to buy given the task's expected business value?" | **Structurally open, but for a specific, hard reason** (Section 7), not because nobody has thought of it. Real but thin academic work; zero shipped standalone products found. |

C and D are **genuinely different categories, not degrees of the same feature**, and the boundary
is sharp: **Layer C needs only a quality signal** (did the output clear a bar — often checkable
against a rubric, a test suite, a reference answer). **Layer D needs a *value* signal** (what is
this specific completed task worth in dollars, and does that number exist anywhere in the
organization before, during, or shortly after the task runs). Every product found in this research
pass that claims to do "cost-quality optimization" operates on the Layer C signal. None was found
operating on a genuine Layer D value signal — the closest evidence is practitioner writing
*describing* the problem (Section 5), not a system solving it.

---

## 3–4. Market map and the central-claim test

**Central claim under test:** given a task and a required quality level, can an existing system
empirically choose the cheapest execution strategy that clears the bar?

**Answer: yes, convincingly, for narrow, checkable-quality tasks, and this is not new.**

### Layer C — cost/quality-aware routing and cascading (mature, commoditizing)

| Product / project | Category | Optimization target | Model selection | Token/reasoning-effort opt. | Historical learning | Quality measurement | Pricing | Traction / evidence | Source |
|---|---|---|---|---|---|---|---|---|---|
| **FrugalGPT** (academic, 2023, still the reference architecture) | Cascading framework | Cost subject to quality floor | Yes — router + cascade | No | Learned quality estimator (DistilBERT) trained offline | Proxy (learned estimator), not ground truth | N/A (research) | Up to 98% cost reduction cited in follow-on work | [arxiv 2306](https://arxiv.org/abs/2305.05176)-lineage, cited via [Cluster/Route/Escalate survey](https://arxiv.org/pdf/2603.04445) |
| **RouteLLM** (academic, widely cited baseline) | Learned router | Cost subject to quality floor | Yes — matrix-factorization / causal-LLM classifier trained on Chatbot Arena preference data | No | Trained once on preference data, not per-deployment | Proxy (human-preference proxy) | N/A (research, OSS weights) | ~85% cost reduction at ~95% GPT-4-equivalent quality, widely reproduced | [arxiv 2406.18665](https://arxiv.org/html/2406.18665v4) |
| **OpenRouter** | LLM gateway/marketplace | Cheapest/fastest available provider per model | Manual + auto-fallback across providers | No | No | None (pass-through) | 5.5% credit fee, 300–600+ models behind one key | Large user base, de facto default gateway | [Requesty comparison 2026](https://www.requesty.ai/blog/best-llm-routing-platforms-compared-2026-requesty-portkey-litellm-openrouter) |
| **Portkey** | LLM gateway | Cost via semantic cache + routing | Yes, rules-based | Semantic caching (40–60% hit rate claimed, up to 40% cost cut) | No | None built-in (integrates with eval tools) | Enterprise pricing | Positioned for production observability/compliance | [ToolHalla 2026 comparison](https://toolhalla.ai/blog/openrouter-vs-litellm-vs-portkey-2026) |
| **LiteLLM** | OSS gateway | Cost via budgets/routing | Yes, rules-based + fallback | No semantic cache (Redis exact-match only) | No | None built-in | Free/OSS, zero markup | Widely adopted, cited already in PR #37 for Layer B | Same as PR #37 |
| **Not Diamond** | Managed router | Quality-preserving cost reduction | Yes — trained router model | No | Router retrained centrally, not per-customer | Proxy (internal benchmark suite) | Fixed per-million-token fee below cheapest routed model | Early Access (free) + Enterprise | [Not Diamond pricing via search synthesis](https://github.com/Not-Diamond/awesome-ai-model-routing) |
| **Unify** | Managed router | Balances quality/speed/cost by stated preference | Yes — neural quality-scoring function predicts quality ahead of time | No | Centrally trained | Proxy (predicted score) | Usage-based | Positioned as preference-weighted routing | [Zylos Research 2026](https://zylos.ai/research/2026-01-29-llm-routing-intelligent-model-selection/) |
| **ClawRouters** | Router aggregator | Cost optimization, BYOK | Yes | No | No | None | Free BYOK model | Claims tested against 11 routers | [ClawRouters 2026](https://www.clawrouters.com/blog/best-llm-routers-2026) |
| **Azure/Microsoft Foundry Model Router** | Hyperscaler-native router | Cost/complexity-aware selection across OpenAI/OSS/Anthropic pool | Yes, native | Unclear (not detailed in public docs found) | Unclear | Unclear | Bundled into Azure billing | Shipped, in Microsoft Foundry docs | [Microsoft Learn](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/model-router) |
| **OpenAI GPT-5 router** | Flagship-product-embedded router | Reduce cost/latency by routing easy queries to a fast model, hard ones to a reasoning model | Yes, native, trained on real usage signals (switch rate, preference rate, measured correctness) | Yes — routes into a distinct "thinking" model for harder queries | Continuously retrained on live traffic | Live user behavior + correctness signal | Included in ChatGPT | **Shipped as core architecture, drew backlash over unpredictability, partially rolled back within a week to add manual Auto/Fast/Thinking controls and restore legacy model access** | [OpenAI GPT-5 launch](https://openai.com/index/introducing-gpt-5/), [the-decoder rollback coverage](https://the-decoder.com/openais-gpt-5-router-rollback-shows-why-ai-requires-unlearning-old-habits/), [Fortune](https://fortune.com/2025/08/12/openai-gpt-5-model-router-backlash-ai-future) |
| **Cursor "Auto" mode** | IDE-embedded router | Best model per coding task, free of usage credits | Yes, automatic | Unclear | Unclear | Implicit (developer accepts/rejects diff) | Free within subscription | Shipped, default in a major coding tool | [CodeAnt 2026 comparison](https://codeant.ai/blogs/best-ai-code-editor-cursor-vs-windsurf-vs-copilot) |
| **GitHub Copilot "Auto" mode** | IDE-embedded router | Best model per task across GPT/Claude/Gemini | Yes, automatic | Unclear | Unclear | Implicit | Included in subscription | Shipped | Same source |

**Verdict on the central claim:** for the narrow form of the question — task X, quality floor Z,
pick the cheapest strategy expected to clear Z — **this is not an open research question and not an
empty product category.** It is mature enough that the two companies with the deepest access to
model internals and cost structure (OpenAI, and Microsoft via its Azure/OpenAI partnership) have
already built native, automatic, production versions of it, at the largest possible scale (all of
ChatGPT). The interesting finding is not that it's unsolved — it's *how* it broke:

**The OpenAI GPT-5 case is the single most informative data point in this entire probe.** OpenAI
did not fail to build cost/complexity-aware auto-routing — they built it, shipped it as the
flagship architecture, and had full access to every signal a hypothetical third-party "AI resource
optimizer" would want (real usage data, real correctness measurement, control over model internals,
zero integration burden). It still drew immediate, sharp user backlash — not because the routing
was technically wrong on average, but because **users could not predict or verify, on any given
query, which model had answered them, and lost trust in the system making that decision on their
behalf without visibility or override.** OpenAI's fix was not "route better" — it was to expose
manual override (Auto/Fast/Thinking) and un-deprecate the legacy picker. This is direct evidence
against a strong form of the hypothesis: even with perfect internal access, automatic resource
allocation has a **trust/predictability ceiling that is not a data or modeling problem** — it is a
product-and-governance problem, and it recurs regardless of who builds the router.

---

## 5. The stronger claim: cost against business value

**Claim under test:** can a system reason about expected task value, expected cost, expected
quality, marginal quality improvement, marginal cost, and apply a stopping rule derived from that
comparison — not a generic cost dashboard, but an actual allocation decision?

**Answer: the problem is real and documented in practitioner writing; no shipped system was found
that does this.**

The strongest evidence found is a documented case (via *Towards Data Science*, "Your AI Agent
Passed Every Eval. Finance Still Killed It.") of an agent whose business value per resolved ticket
was **$4.20**, against a cost per successful outcome of **$4.79** — a 59-cent loss on every
successful resolution, invisible to any evaluation harness that measures only task success and not
task economics. The same piece notes agent unit costs frequently do not fall with scale, because
each unit of work is its own inference run — meaning a pilot that is marginally underwater does not
get rescued by scaling it, the way software unit economics usually do. This is a genuinely
different failure mode from anything Layer A/B/C observability catches: **the agent can pass every
accuracy eval and still destroy value**, because nothing in the eval pipeline knows what the task
was worth.

Academic work exists that is directionally aimed at this: "Spend Less, Reason Better: Budget-Aware
Value Tree Search for LLM Agents" ([arxiv 2603.12634](https://arxiv.org/html/2603.12634)) frames
agent planning as search under an explicit compute budget with a value function; "Conformal
Thinking: Risk Control for Reasoning on a Compute Budget"
([arxiv 2602.03814](https://arxiv.org/html/2602.03814)) gives instance-level stopping rules
calibrated to a risk target under budget. Both are compute-budget-aware, not *business*-value-aware
— they optimize against a task-completion or correctness signal, not a dollar figure derived from
what the organization is actually willing to pay for this outcome. That distinction matters: **no
paper or product found takes "this task's outcome is worth at most $N" as an input and derives a
spend ceiling from it.** The $ input is precisely the thing missing everywhere this probe looked.

No dedicated product for this exact loop (expected value → expected cost → marginal
comparison → stop/continue decision, wired to a real dollar figure) was found in either research
pass. Generic "AI ROI framework" content is abundant (CFO-oriented cost-per-outcome frameworks,
agent ROI calculators) but these are retrospective reporting tools, not runtime allocation
decisions — they tell you after the fact that a pilot was underwater, the way the $4.20/$4.79 case
above was *discovered*, not prevented.

---

## 6. The marginal intelligence test

**Question:** could a system learn that spending past ~30k tokens on a task buys negligible
additional quality (using the task's illustrative curve: 72% → 87% → 93% → 94% → 94.2% at
10k/20k/30k/40k/50k tokens) and stop there?

**Answer: the signal exists and is actively being researched and partially productized, but only
for the "quality" half of the equation — the "value" half is still absent.**

- Reasoning-effort parameters are already shipped, real, and documented to produce exactly this
  shaped tradeoff: OpenAI's o-series exposes low/medium/high reasoning effort; Anthropic's Claude
  models expose an explicit thinking-token budget. Measured data shows reasoning tokens scale
  sharply with effort level (e.g., one benchmark reported 70 tokens at low effort vs. 181 at high
  effort for a smaller model), and Anthropic's own guidance explicitly frames the effort dial as
  "the primary cost lever," recommending teams sweep low/medium/high on their own eval set before
  assuming high is needed — i.e., **the vendor is already telling customers to do exactly the
  diminishing-returns search this task describes, manually, per task.**
- "Reasoning on a Budget: A Survey of Adaptive and Controllable Test-Time Compute in LLMs"
  ([arxiv 2507.02076](https://arxiv.org/abs/2507.02076)) formalizes this as a taxonomy of
  fixed-budget ("L1-controllability") vs. dynamically-adaptive ("L2-adaptiveness") methods, and
  notes the core motivating fact: dataset-level accuracy does rise with token budget, then
  saturates, which is the exact curve shape the task describes.
- Pass@k / multiple-attempt data shows the same diminishing-returns shape independently: one
  measured example goes from 31.4% (best@1) to 51.2% (best@2) to 58.1% (best@3) to only 66.3%
  (best@5) — the first retry captures most of the gain (+19.8pp), later retries add only 2–3pp
  each. Practitioner guidance already recommends k=2 for cost-sensitive deployments and notes k=3
  captures 88% of the achievable ceiling. **This confirms the "stop around 30k because more tokens
  buy insufficient improvement" concept is technically meaningful and already measured across
  multiple resource dimensions (reasoning tokens, retry count), not merely a plausible-sounding
  analogy.**
- What is *not* solved: every curve above is fit against a **task-completion or benchmark-accuracy
  metric**, decided in advance by whoever built the benchmark. None of this literature or tooling
  answers "is 94% vs. 93% worth the extra 10k tokens *for this specific business*" — that requires
  the value signal from Section 5, which remains absent. The scaling-curve machinery is real and
  usable; the economic translation layer on top of it is the empty part.

---

## 7. The quality problem

Quality measurability was investigated per task class. This is very likely this hypothesis's most
consequential finding, because Layer C's maturity (Section 3–4) depends entirely on quality being
checkable, and that is true for a narrower set of task classes than "AI tasks" in general.

| Task class | Quality measurement type | Basis |
|---|---|---|
| **A. Classification** | **Objective** (when labels exist) | Accuracy/F1 against ground truth; this is exactly the task class every routing benchmark (RouterBench: MMLU, GSM8K, HellaSwag, ARC, Winogrande, MBPP, MT-Bench) is built on — no coincidence Layer C matured fastest here. |
| **B. Extraction** | **Objective-to-proxy** | Checkable against a schema/reference when one exists; degrades to proxy when "correct extraction" is itself judgment-dependent (e.g., which clause is "material"). |
| **C. Coding** | **Objective-to-proxy** | pass@k against tests is objective when tests are trustworthy and cover the real requirement (frequently they don't — "passed every eval, finance still killed it" generalizes beyond agents doing support work). |
| **D. Research** | **Proxy-to-subjective** | No ground truth for "found the right sources and synthesized them well" at generation time; typically judged by a human or an LLM judge after the fact. |
| **E. Writing** | **Subjective** | Long-form quality has no reference answer; this is precisely the task class where the RAND-cited research below applies most directly. |
| **F. Planning** | **Delayed** | Quality of a plan is only knowable once it has been executed, often much later, and confounded by execution quality. |
| **G. Autonomous business tasks** | **Delayed-to-unobservable** | The $4.20/$4.79 case is exactly this: the "was it worth it" signal arrived from Finance, after the fact, outside any eval harness the team controlled. |

**LLM-as-judge, the default proxy for classes D/E/F/G, is not reliable enough to close this gap
generally.** RAND Corporation research cited in this pass found no LLM judge uniformly reliable
across benchmarks, with frontier models exceeding 50% error rates on advanced bias tests
(verbosity bias, position bias, self-enhancement bias), and consistency breaking down on
formatting changes and paraphrasing alone. This is a **structural, not incidental, blocker** for
building a general-purpose Layer C/D optimizer on top of judge-based quality scoring for anything
outside class A/B/C.

**Answer to the task's question:** optimization does not work broadly. It works well where quality
is objectively measurable against a reference (A, and B/C when a trustworthy reference exists), it
works as a noisy proxy where an LLM judge or benchmark stands in (D/E, with real, documented
reliability problems), and it does not work at all today where the signal is delayed or genuinely
unobservable at decision time (F, G) — which is exactly the task class ("autonomous business
tasks") where Layer D's value would be largest if it could be built.

---

## 8. Historical learning / data moat

**Question:** after a large number of runs, does execution history become proprietary, defensible
data — and does it generalize across organizations, or does every organization need its own?

Evidence points toward **weak-to-medium, and non-generalizing across customers** — the opposite of
a strong data network effect.

- RouterBench-style cross-dataset evaluation shows **all tested routing approaches degrade under
  distribution shift** when trained on one domain and evaluated on another; simple k-NN routing
  generalizes better (smallest degradation, ~2.6 points) than more complex learned routers, which
  is itself informative — the sophistication that would make a data moat valuable (a complex
  learned model that improves with scale) is the part that generalizes *worst* out-of-domain.
  ([arxiv 2505.12601](https://arxiv.org/pdf/2505.12601))
- This mirrors a pattern familiar from the analogies in Section 9: ad-bidding and recommender
  systems get real data network effects because user/query distributions are shared across
  advertisers on the same platform; a code-review task at Company A and a customer-support
  classification task at Company B do not obviously share a distribution an execution-history
  dataset could transfer between.
- **What likely does generalize:** coarse-grained facts (e.g., "for straightforward classification,
  small models are usually sufficient"; the shape of the diminishing-returns curve itself). **What
  likely does not generalize:** the specific mapping from a given organization's task fingerprints
  to the model/strategy that clears *their* quality bar for *their* task distribution, because
  their quality bar is defined by their own downstream business process (Section 7, class G).

**DATA NETWORK EFFECT: WEAK.** The generalizable part (rough heuristics) is not defensible — it's
publishable as a blog post, and several already have been (this section's own citations). The
defensible part (per-customer fine-grained routing) does not generalize to a second customer, which
means each new customer effectively restarts the data-collection cost, undermining the classic
"more customers → better product for everyone" moat story.

---

## 9. Analogy test

| Analog | What is analogous | What breaks the analogy |
|---|---|---|
| **Database query optimizer** | Chooses an execution plan (join order, index use) to minimize cost subject to correctness — the closest structural match to Layer C | A query optimizer's "correctness" is guaranteed by SQL semantics; an LLM router's "correctness" is a *probabilistic estimate* of quality, not a proof. The optimizer never has to guess whether the answer was right. |
| **Cloud autoscaler / Kubernetes scheduler** | Predictively right-sizes compute to avoid both waste and starvation, minimizing cost for a resource-constrained workload — search results this pass explicitly draw this comparison for LLM inference cost tooling | Autoscalers optimize a homogeneous resource (CPU/memory) against a deterministic SLA (latency, uptime). LLM quality is not a deterministic, directly-measurable resource the way CPU utilization is — see Section 7. |
| **Compiler optimizer** | Picks among equivalent-output strategies to minimize resource use, holding correctness fixed | Compiler optimizations are provably semantics-preserving; "route to a cheaper model" is not provably quality-preserving, only statistically likely to be, per a proxy estimator. |
| **Ad bidding system** | Real-time value/cost tradeoff decision (bid = expected value of an impression) made per-request, at massive scale, with strong network effects across advertisers sharing a platform | Ad platforms have a direct, immediate, machine-readable value signal (click, conversion, revenue) that arrives in seconds. AI task "value" (Section 7, classes D–G) frequently does not exist as a number anywhere, ever — this is the single sharpest break in the whole analogy set. |
| **Electricity load management** | Balances supply/demand to minimize cost while meeting a service constraint | Electricity's "service constraint" (voltage/frequency) is physical and objectively measurable in real time; task quality is not. |
| **FinOps** | Cost visibility/allocation/optimization discipline for cloud spend, the direct predecessor category (per PR #37) | Classical FinOps optimizes provisioned, relatively stable infrastructure; it does not have to reason about a *quality* dimension at all — a bigger EC2 instance is not "smarter," only faster. This is the crispest way to state why Layer C/D is not merely "FinOps for AI": FinOps has no analog to the quality axis. |
| **Credit-limit / payment-risk engine** | Makes a per-transaction economic decision (approve/decline) balancing expected value against expected risk/cost, using a learned model, in real time | Risk engines have decades of labeled outcome data (did the loan default, yes/no) — an objective, delayed-but-eventually-observed value signal. Task "quality" for autonomous business tasks is frequently *never* observed at all (Section 7), which is a strictly harder data problem than "observed, but delayed." |

**Structural takeaway:** every analogy that holds up structurally (query optimizer, compiler,
autoscaler) is one where correctness or the service constraint is objectively, immediately
measurable — i.e., these are all really analogies for **Layer C, not Layer D.** Every analogy that
naturally includes a value/cost tradeoff (ad bidding, credit risk) breaks specifically on the
availability of a value signal — the exact gap this probe keeps finding at Layer D. The
analogy set itself is further evidence that C and D are different in kind, not degree.

---

## 10. Customer pain search (outside vendor marketing)

| Actor | Context | Problem | Consequence | Source |
|---|---|---|---|---|
| Enterprise agent operator (case study) | Support-ticket resolution agent | Agent passed every accuracy eval; cost per successful outcome ($4.79) exceeded business value per resolution ($4.20) | 59-cent loss per success, discovered by Finance after deployment, not by the eval suite | [Towards Data Science](https://towardsdatascience.com/your-ai-agent-passed-every-eval-finance-still-killed-it/) |
| ChatGPT/GPT-5 users (mass, public) | OpenAI's automatic model router | Could not tell or control which model answered a given query; router judged unpredictable | Public backlash forced OpenAI to restore manual model picker and un-deprecate legacy models within roughly a week of GPT-5 launch | [the-decoder](https://the-decoder.com/openais-gpt-5-router-rollback-shows-why-ai-requires-unlearning-old-habits/), [Fortune](https://fortune.com/2025/08/12/openai-gpt-5-model-router-backlash-ai-future) |
| Developer (level1techs discourse, this pipeline's own data) | Enterprise default routing | "stop sending every stupid little task to a frontier model" — every request routed to frontier models by default, no telemetry to justify the spend to management | `ANOM-0213`, WATCH, single observation, unmerged | This repo's `constraint-archaeology-agents/data/observations.jsonl` |
| Developer (level1techs discourse, this pipeline's own data) | Local model deployment (8b–27b) | Smaller models fail differently than medium ones; required manually running ~15k prompts to characterize the error pattern before trusting the smaller model for the task | `ANOM-0153`, WATCH, single observation, unmerged | Same |
| Developer (openai-devs discourse, this pipeline's own data) | Multiple AI models giving conflicting engineering recommendations | Model agreement doesn't indicate correctness; no principled way to decide which recommendation to trust | `ANOM-0288`, WATCH, single observation, unmerged | Same |
| Developer (openai-devs discourse, this pipeline's own data) | Prompt-level spend limits | "don't spend more than $X in the system prompt is not a limit. It's a suggestion the agent can talk itself out of" | `ANOM-0387`, WATCH, single observation, unmerged (already surfaced in PR #37 as Layer-B evidence; repeated here because it is also evidence that *soft* resource-allocation policies are known to fail, motivating harder allocation mechanisms) | Same |
| Anthropic (vendor guidance, not marketing copy) | Reasoning-effort tuning | Explicit guidance to sweep low/medium/high effort settings on your own eval set before assuming the highest tier is needed | Implicitly confirms customers are doing this tuning manually today, per task, with no automated tool cited | Search synthesis of Anthropic effort-tuning guidance, this pass |
| HN commenters (general, this pass) | MCP tool definitions loaded into context | Restricting models to relevant tools still results in models going on tangents and wasting large amounts of tokens without materially better output | Consistent with, and independent corroboration of, PR #37's "Hidden MCP Tax" citation | [HN discussion, this pass](https://news.ycombinator.com/item?id=45954572) |

**Read on this evidence:** the pattern is the same shape PR #37 found for cost governance — real,
recurring across independent sources, but each individual report is a single incident, not proof of
recurring frequency within one organization. The new information this pass adds is that the
*complaint* ("which model/effort level do I actually need") is well evidenced, but the *fix people
report reaching for* is almost always either (a) a Layer C product that already exists (routers,
gateways, "Auto" modes), or (b) manual, ad hoc experimentation (Anthropic's own guidance to
"sweep" settings). Nobody in this pass was found complaining about the absence of a Layer D
business-value optimizer specifically — because Layer D pain doesn't surface as a complaint about a
missing tool, it surfaces as a surprise line item Finance flags after the fact (the $4.20/$4.79
case), which is a much harder signal to sensor for and a plausible reason PR #37's and this probe's
pipeline-native evidence for Layer D specifically is thin to nonexistent.

---

## 11. Economic scale

Assumptions are stated explicitly; no market-size figure is asserted beyond arithmetic on the
inputs given.

**Base case (as given in the task):** 10M AI tasks/month, $0.02/task average cost → $2.4M/year.

| Optimizer savings | Annual value |
|---|---|
| 10% | $240,000/year |
| 20% | $480,000/year |
| 40% | $960,000/year |

**Scenario modeling**, using transparent, labeled assumptions (not sourced market-size claims):

| Scenario | Assumed monthly tasks | Assumed $/task | Annual spend | 20% savings value | Note |
|---|---|---|---|---|---|
| Small AI startup | 500,000 | $0.03 | $180,000 | $36,000 | Below almost any dedicated infra-vendor's minimum deal size; McKinsey's cited 20–30% consumption-design savings (Section 12) would likely be captured by switching to a $0-cost OSS gateway (Section 13), not by buying a platform |
| Mid-size AI product | 20,000,000 | $0.02 | $4.8M | $960,000 | Crosses into "could justify a dedicated headcount or tool budget," per this probe's buyer analysis in Section 12 |
| Large enterprise | 500,000,000 | $0.015 | $90M | $18M | Real budget-line territory; matches the scale at which FinOps Foundation's 98%-of-practitioners-manage-AI-spend statistic (PR #37) becomes operationally unavoidable |
| Massive agent platform (e.g., a coding-agent or support-agent vendor serving many downstream customers) | 5,000,000,000 | $0.01 | $600M | $120M | This is the scale at which the $4.20/$4.79 unit-economics failure mode (Section 5) stops being a rounding error and starts being existential — margin compression at this volume is a company-level risk, not a line-item |

**Reading these numbers against Section 8's data-moat finding:** the scenario where the economic
prize is largest (massive agent platforms) is also the scenario where the buyer is most likely to
build this in-house rather than buy it — they have by far the largest incentive and the largest
proprietary task-distribution dataset (Section 8's non-generalization finding means an outside
vendor's cross-customer data would help them the *least*, precisely because they're the biggest).
This is a real tension for any go-to-market plan built on the economic-scale numbers above.

---

## 12. Who pays

| Role | Would plausibly buy Layer C tooling? | Would plausibly buy Layer D tooling? | Rationale |
|---|---|---|---|
| AI Platform Engineering | Yes, already does (gateway/router adoption is real and growing) | Only if bundled | Owns the technical integration; Layer D needs a business input they don't own |
| FinOps | Partially — already extending into token/GPU cost, per PR #37 | Only as a downstream report consumer | Cost is their domain; task *value* generally is not |
| CTO | Approves Layer C spend above a threshold | Could sponsor a pilot | Layer D's payoff (avoiding another $4.20/$4.79 embarrassment) is exactly the kind of story that gets executive attention post-incident, not pre-emptively |
| CFO | Rarely direct buyer of dev tooling | **Most plausible sponsor for Layer D specifically** | The $4.20/$4.79 case was literally discovered by Finance; CFO is the role that already owns "was this worth it" as a question, for every other line item in the business |
| ML Infrastructure / Engineering | Yes, primary technical buyer for Layer C | Implements, doesn't sponsor | Same as PR #37's finding for the adjacent governance layer |
| AI Product Teams | Yes, cares about margin per feature | Yes — closest to owning the value definition (Section 7, class G) | The product team is usually the only group that both knows what the task is *for* and can see the cost; this makes them the most plausible **source of the value signal**, even if Finance is the buyer |

**On the standalone-vs-feature question:** for Layer C specifically, the evidence in Section 3–4 is
close to conclusive — OpenAI, Microsoft, and every major gateway already ship this as a *feature*,
not a product buyers seek out separately, and OpenAI's own experience shows the differentiator that
matters (trust/predictability) is closer to a UX design problem than a modeling problem an
independent vendor could out-execute a model vendor on. **For Layer D, there is currently no
product to categorize** — the honest answer is that no market has formed to reveal whether it would
be bought standalone or expected as a CFO-facing add-on to an existing FinOps/observability tool.
The most likely outcome, based on the buyer map above, is the latter: Layer D bolts onto an
existing FinOps or agent-observability relationship (CloudZero, Vantage, Datadog, or a support/CS
platform that already has the outcome data) rather than launching as a category of its own.

---

## 13. Build-nothing test

**Layer C: fails the build-nothing test in the vendor's favor, not the buyer's — i.e., a
competent team should not build this themselves, because free/cheap alternatives that are already
mature exist to *buy* instead.** LiteLLM (free, OSS) plus an eval harness plus a Slack webhook
composes most of "route cheap, escalate on failure" in well under a week, exactly as PR #37 found
for the adjacent budget-cap problem. Where a team does need to reach for a paid product, that
product (OpenRouter, Portkey) is thin markup on already-commoditized infrastructure, not a
defensible platform — this is consistent with, and reinforces, PR #37's Section 12 finding for the
neighboring governance layer.

**Layer D fails the build-nothing test in the opposite direction: it is not obviously buildable
in a week, but not because the mechanism is hard — because the *input data* does not exist yet.**
The stopping-rule mechanism itself (compare marginal cost to marginal value, stop when cost
exceeds value) is a few dozen lines of code once you have both numbers. **The entire difficulty is
manufacturing a trustworthy dollar figure for "this task's outcome was worth $N" per task, which is
an organizational and data-plumbing problem specific to each business's existing systems (a CRM,
a support platform, a sales pipeline) — not a problem a vendor's engineering team can solve once
and sell many times, because each integration is bespoke.** This directly explains Section 8's weak
data-network-effect finding and Section 12's "bolt-on" prediction: **Layer D is operationally hard
at scale in a way that specifically resists productization**, which is the sharpest possible
distinction from "technically possible but a week of engineering."

---

## 14. Incumbent attack test

| Proposed moat | Can OpenAI copy? | Can Anthropic copy? | Can cloud providers copy? | Can LLM gateways copy? | Verdict |
|---|---|---|---|---|---|
| Cost/quality-aware routing (Layer C) | **Already did — GPT-5's router is this, at the largest possible scale** | Has the reasoning-effort dial and the internal signals to build the same | Microsoft already did (Foundry Model Router) | Already do (every product in Section 3–4's table) | **No moat exists; this is already commoditized/copied by the strongest possible incumbents** |
| Cross-provider neutrality | No (single-provider bias) | No (single-provider bias) | Partially (multi-model but house-favoring) | **Yes — this is the gateways' actual structural advantage**, echoing PR #37's Section 11 finding | Real, but modest, and contested among many gateways, not exclusive to a "resource optimizer" specifically |
| Business-value-aware stopping (Layer D) | Could build if they chose to prioritize it — has the usage data | Same | Same, plus has the customer's cloud billing relationship already | No — gateways don't have access to the customer's downstream business outcome data | **This is the one place a neutral third party has a real structural argument** — not because incumbents can't build the mechanism, but because the *value signal* has to come from the customer's own business systems (CRM, support platform, sales data), which none of OpenAI/Anthropic/AWS/gateways have access to by default. A vendor whose entire product is integrating with those systems (closer to a specialized analytics/observability company than a router company) has a genuine, if narrow, position. |

**The layer with structural third-party advantage is Layer D, and specifically only the
value-signal-integration half of it — not the stopping-rule mechanism, which any of the above could
copy trivially once the input exists.** This is a meaningfully narrower moat than "build an AI
resource optimizer" — it is closer to "build the plumbing that gets a business-outcome number next
to a cost number, per task, reliably, for one specific class of measurable business process" —
which is a systems-integration and data-partnership problem, not a routing/ML problem.

---

## 15. Product boundary evaluation

The proposed abstraction (task/quality/value/latency/risk in → model/budget/tools/stopping-policy
out, updated by observed cost/quality/outcome) is tested against the findings above, not built.

- **As a Layer C product:** this is a **FEATURE**, and one that has already been built, shipped,
  and partially rejected by end users at the largest incumbent in the industry. A new entrant
  building only this is entering a market where the two strongest possible competitors already
  compete, with structural advantages (model internals access, zero integration burden, existing
  distribution) a startup cannot match, chasing a capability whose main differentiator (trust,
  predictability) both incumbents are actively still tuning.
- **As a Layer D product, as specified in the task (full input schema: quality requirement,
  economic value, latency, risk):** this is a **RESEARCH PROBLEM wearing a product-shaped
  abstraction.** The output schema (model/budget/tools/stopping-policy) is a solved-enough
  engineering problem (Section 6). The input schema's "economic value" field is the entire
  unsolved part, and it is unsolved for a data-availability reason (Sections 5, 7, 13), not an
  algorithm-design reason — no architecture diagram fixes a missing number.
- **A narrower cut — Layer D restricted only to task classes where quality and value are both
  objectively measurable at low latency (Section 7 classes A/B, paired with a business system that
  already emits an outcome value, e.g., a support platform with resolution-value already tagged)**
  — is the one sub-slice of this abstraction that is **COHERENT as a product**, though this probe
  found no one building even that narrow slice yet. It is coherent specifically because it avoids
  both of this probe's fatal objections: it doesn't compete with OpenAI/Microsoft's already-shipped
  Layer C routers (different buyer, different question — "was this worth it," not "which model"),
  and it doesn't require solving general business-value measurement (Section 7's unobservable
  classes), only integrating with businesses that already have the number.

---

## 16. Category name

| Candidate | Fit |
|---|---|
| AI Resource Optimization | Too broad — covers Layer C, which is not open |
| AI FinOps | Already claimed (PR #37), and already means Layer A/B, not C/D |
| Agent Economics | Vague; used loosely in venture commentary this pass ("agentic economics" in a 2026 investment-landscape piece) without a settled technical meaning |
| Intelligence Economics | Closest to the task's own framing, but this pass found "Inference Economics" already in use by at least one named research firm (Zylos Research, describing AI *agent compute markets* broadly — GPU/inference-provider economics, not per-task quality-cost-value optimization specifically) |
| Inference Economics | **Already taken, and taken for something adjacent but different** (compute-market economics, not task-level value-aware allocation) — using it here would create real confusion with existing usage |
| AI Economic Control Plane | Overstates what exists; "control plane" implies enforcement infrastructure (Layer B, already named and covered by PR #37) |

**Most accurate name for the layer this probe actually found to be open: "Task-Value-Aware
Inference Governance"** — deliberately narrower and less marketable than any option on the task's
list, because the honest finding is that only the value-awareness slice (Layer D) is open, and
calling the whole space by a broad name would misrepresent Section 3–4's finding that the
resource-optimization slice (Layer C) is not open. If a broader, more marketable name is wanted for
external communication, **"Intelligence Economics"** is defensible as long as it is scoped
explicitly to the value-aware layer and not used to imply the (already-solved) routing layer is
part of the same open opportunity.

---

## 17. Opportunity score

Scored for the genuinely open layer (Layer D, task-value-aware inference governance) — scoring the
task's full combined hypothesis (C+D) would conflate an open problem with a solved one and produce
a misleading number.

| Dimension | Score (0–5) | Basis |
|---|---|---|
| Problem severity | 3 | Real (the $4.20/$4.79 case is a genuine value-destroying failure), but only one strong documented instance found in this pass, versus PR #37's several |
| Problem frequency | 1 | This probe's own pipeline surfaced zero Layer-D-specific observations — every relevant anomaly found (`ANOM-0213`, `ANOM-0153`, `ANOM-0288`) is Layer C pain, not Layer D pain; external evidence for Layer D specifically is one case study, not a pattern |
| Economic value | 3 | Real at scale (Section 11's massive-platform scenario), but the scenario where it matters most is also the scenario least likely to buy rather than build (Section 11, Section 8) |
| Market growth | 2 | No market exists yet to measure growth of; Layer C (the adjacent, already-growing market) is not evidence of Layer D growth |
| Technical feasibility | 2 | The stopping-rule mechanism is easy (Section 6); the value-signal acquisition is hard for structural, not technical, reasons (Section 7, Section 13) |
| Quality measurability | 1 | Section 7's finding directly: quality is only objectively measurable for the narrowest task classes, and Layer D matters most exactly where measurability is worst (class G) |
| Buyer clarity | 2 | CFO is the most plausible sponsor, but this is inference from one case study and a buyer-role analogy (Section 12), not evidence of an existing budget line |
| Competitive white space | 4 | Genuinely open — no product found, and Section 14's incumbent-attack test found a real (if narrow) structural reason incumbents haven't filled it |
| Defensibility | 2 | The one real moat candidate (business-system integration) is narrow, bespoke per customer, and does not compound across customers (Section 8) |
| Timing | 2 | No trigger event found comparable to PR #37's (AWS/Cloudflare/OpenAI all shipping governance features in the same year); nothing here is visibly heating up |

**Total: 22/50.**

**Weakest dimension: Quality measurability (1/5), tied with Frequency (1/5).** Quality
measurability is the more foundational problem of the two: even if a buyer with clear budget
authority and urgent pain appeared tomorrow, Layer D cannot be built for their highest-value use
cases (autonomous business tasks, Section 7 class G) until quality and value are both observable at
decision time, and this probe found that gap to be structural, not a matter of better tooling. This
score is markedly lower than PR #37's 32/50 for agent cost governance — appropriately, since this
probe's central finding is that the more ambitious half of the new hypothesis (Layer D) is earlier
and thinner than the layer PR #37 already scored as merely INVESTIGATE, not FAST-TRACK.

---

## 18. Falsification conditions

| # | Condition | Result |
|---|---|---|
| 1 | Existing routers already solve most cost/quality optimization | **CONFIRMED**, for Layer C specifically. Section 3–4: mature academic base (FrugalGPT, RouteLLM), a crowded product market, and both OpenAI and Microsoft shipping native versions at flagship scale. This falsifies the hypothesis's Layer C claim outright. |
| 2 | Quality cannot be measured reliably enough | **PARTIALLY FALSIFIED / PARTIALLY CONFIRMED, split by task class.** Falsified for objectively-scorable classes (A/B/C, Section 7) — quality measurement is exactly why Layer C works there. Confirmed for subjective/delayed/unobservable classes (E/F/G) — LLM-judge reliability research (50%+ error rates on bias tests) shows no current fix, and this is precisely where Layer D's biggest prize sits. |
| 3 | Provider-native optimization has overwhelming structural advantage | **CONFIRMED for Layer C** (Section 14 — OpenAI and Microsoft already built it). **NOT FALSIFIED for Layer D** — Section 14 also found a genuine, if narrow, structural argument for a neutral third party specifically on business-value-signal integration, which incumbents do not have default access to. |
| 4 | Savings are too small to justify another infrastructure layer | **NOT FALSIFIED, but also not confirmed — INSUFFICIENT DATA.** Section 11's scenarios show real dollar values at scale for Layer C-style savings, but Layer C savings are already captured by existing free/cheap tooling (Section 13), so the *marginal* value of a new Layer C entrant is close to zero regardless of the gross savings number. For Layer D, no product exists to measure realized savings against, so this cannot be evaluated yet. |
| 5 | Cross-customer learning does not generalize | **CONFIRMED.** Section 8: cross-dataset generalization degrades under distribution shift in the routing literature itself; the plausible generalizable insights (rough heuristics) are not defensible, and the defensible insights (fine-grained per-task routing) do not transfer between organizations. |
| 6 | Companies can build adequate internal solutions trivially | **CONFIRMED for Layer C** (Section 13 — LiteLLM + eval harness + Slack webhook composes most of it in under a week, same finding as PR #37 for the adjacent layer). **FALSIFIED for Layer D** — Section 13's inverse finding: the blocker is not engineering effort but bespoke, per-organization data plumbing that does not reduce to a week of internal work regardless of team competence. |

---

## 19. Decision

**WATCH.**

Not DROP: Layer D (task-value-aware inference governance) is real, has at least one sharply
documented failure case ($4.20 value vs. $4.79 cost), has a genuine structural argument for
third-party defensibility (Section 14), and the pipeline's own unmerged anomalies (`ANOM-0213`,
`ANOM-0153`, `ANOM-0288`) confirm the underlying *pain of not knowing the right resource allocation*
is real among practitioners today, even though — as documented in Section 1 — that pain is
currently Layer C pain, not yet Layer D pain, in this pipeline's own evidence.

Not INVESTIGATE: PR #37 earned INVESTIGATE because it had a narrow, concrete, immediately
buildable wedge (orphan cleanup tied to spend enforcement) that a 10-customer discovery sprint
could directly validate. This probe could not identify an equivalently narrow Layer D wedge — every
candidate wedge this probe considered collapses back into the same blocker (no reliable, cheap
business-value signal exists for the task classes where Layer D would matter most), and a discovery
sprint aimed at customers would mostly re-discover that same blocker rather than resolve it, because
it is a data-availability fact about the world, not a question only customers can answer.

Not FAST-TRACK: nothing in this probe found a trigger event, competitive pressure, or narrowing
window comparable to what justified urgency in adjacent layers (PR #37's AWS/Cloudflare/OpenAI
governance-feature wave). The strongest incumbent evidence found (OpenAI's GPT-5 router) argues the
opposite of urgency for Layer C — that ground is already contested by the biggest possible players
— and no comparable incumbent movement was found at Layer D.

The right posture is to wait for a cheaper, more specific signal than a general discovery sprint
would produce — see Section 20.

---

## 20. Next action

**Run a scoped technical feasibility check, not a customer discovery sprint: for one objectively-
measurable task class already in this pipeline's own sourcing footprint (e.g., a coding task, where
pass/fail against tests is available, per Section 7 class C), attempt to locate or construct a real,
non-vendor-marketing example where an organization has BOTH a per-task cost figure AND a per-task
downstream business-value figure recorded close enough in time to compute a stopping-rule decision
retroactively.**

This is chosen over a discovery sprint because it directly targets this probe's two weakest
dimensions (Quality measurability, 1/5, and Frequency, 1/5) with a test that produces a binary,
falsifiable result fast: if even one clean example can be found or reconstructed, it upgrades
"structural blocker" to "hard but occasionally available," which is the minimum evidence needed
before any customer-facing validation would be worth running. If no such example can be found after
a genuinely diligent search, that is itself the strongest possible confirmation of Section 7's
finding and grounds to move this probe's status from WATCH toward DROP rather than spending
discovery-sprint effort asking customers a question this probe's own research already suggests the
data does not exist to answer. It is not performed as part of this probe.

---

*This document does not modify, gate, promote, or backfill any record in
`business-candidate-analyst/data/`, `constraint-archaeology-agents/data/`, or any frozen artifact
under `docs/method/`. `ANOM-0213`, `ANOM-0153`, `ANOM-0288`, and `ANOM-0387` remain at `WATCH` in
the live pipeline, unchanged by this probe. `BC-0093` and `BC-0126` are cited only to document a
provenance discrepancy (Section 1) and are not used as supporting evidence for this probe's
hypothesis. This document does not modify or supersede
`docs/research/ai-agent-cost-governance-opportunity-probe.md`.*
