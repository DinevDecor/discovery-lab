# Test fixtures

Every fixture in this directory is **synthetic** - hand-authored purely to
exercise this package's validation and math, not derived from or
transcribed from the Calendar Moat Analysis / Calendar Arbitrage Screener
v0.1 / Calendar Arbitrage Multi-Agent Watch v0.1 research documents.

Those research documents were not located in `discovery-lab` or in
`DinevDecor/project-memory/archive` as of this implementation (see the
implementation report). A minimal immutable fixture derived from the real
research baseline, with provenance to its archive location, is deferred
until that document is found or supplied - see "what was intentionally
not implemented" in the implementation report. Fabricating one from
memory would misrepresent it as real evidence, which this repo's own
provenance discipline (CLAUDE.md: "Provenance is truthful or absent")
forbids.

`synthetic_submission_dated.json` and `synthetic_submission_rolling.json`
are plain, minimal, made-up examples - a DATED regulatory-clock case and
a ROLLING infrastructure-queue case - used only to prove the intake ->
ledger -> gate -> lifecycle -> report pipeline wires together correctly.
