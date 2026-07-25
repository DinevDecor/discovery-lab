# Source Registry (human-readable)

The authoritative, machine-readable copy is
`config/source-registry.json` — this document exists only so a human
can read the same list without parsing JSON. Add or remove a source by
editing the config file; this document is not itself consumed by any
code.

`search_budget: 40` — the fixed cap on fetch/search operations a
single capture pass may use. This task's own validation capture pass
used 14 real operations (10 `WebSearch` + 4 `WebFetch`; 3 `WebFetch`
attempts against `anthropic.com`, `openai.com`, and `arxiv.org` were
blocked with HTTP 403 and are not double-counted as separate budget
spend beyond the attempt itself) — see `docs/VALIDATION-REPORT.md`.

## A. Foundation Model Releases

| Source | Trust Level |
|---|---|
| OpenAI News | OFFICIAL |
| OpenAI Platform Changelog | PRIMARY |
| Anthropic News | OFFICIAL |
| Anthropic Release Notes | PRIMARY |
| Google DeepMind Blog | OFFICIAL |
| Meta AI Blog | OFFICIAL |
| xAI News | OFFICIAL |
| Mistral AI News | OFFICIAL |
| Qwen Blog | OFFICIAL |
| Cohere Blog | OFFICIAL |

## B. Agent Infrastructure

| Source | Trust Level |
|---|---|
| Model Context Protocol Specification | PRIMARY |
| Model Context Protocol Docs | PRIMARY |
| Claude Agent SDK Docs | PRIMARY |
| OpenAI Agents SDK Docs | PRIMARY |
| LangChain Blog | OFFICIAL |

## C. Developer Platforms

| Source | Trust Level |
|---|---|
| GitHub Blog | OFFICIAL |
| GitHub Changelog | PRIMARY |

## D. Research

| Source | Trust Level |
|---|---|
| arXiv cs.AI Recent | RESEARCH |
| arXiv cs.CL Recent | RESEARCH |
| OpenReview | RESEARCH |

## Sources actually used in this task's validation pass (not yet in the
## fixed Registry above, kept and flagged per the Source Validation rule)

These appeared as real, useful evidence during capture but are not
(yet) part of the fixed initial list — each was correctly flagged by
`cli.py`'s validation check rather than silently trusted:

| Source | Trust Level used | Why not in the fixed list |
|---|---|---|
| Claude Code Changelog (`code.claude.com/docs/en/changelog`) | PRIMARY | A genuinely first-party Anthropic artifact, arguably belongs in Domain B (Agent Infrastructure / Claude Code specifically) - a config addition, not a code change, for a future capture pass |
| Tech Press Roundup (Axios/9to5Mac/TechCrunch synthesis) | SECONDARY | Aggregated tech journalism, not a single fixed URL |
| TechCrunch (specific articles) | SECONDARY | Tech journalism, deliberately not promoted to the fixed Registry - `EXEC-008` names the vendors themselves as Domain A sources, not journalism about them |
| The Register | SECONDARY | Same reasoning |

Whether to formally add `code.claude.com/docs/en/changelog` (and
similarly, `openai.github.io/openai-agents-python/`-style SDK-specific
changelogs) to `config/source-registry.json` is a routine config edit
a human can make at any time - not attempted here to keep this task's
own scope narrow, per `EXEC-008`'s "Do not create parallel
architecture" instruction (extending the fixed list is exactly the
kind of decision left to a human, the same way Observation Agent's
own repo list is never expanded by the tool itself).
