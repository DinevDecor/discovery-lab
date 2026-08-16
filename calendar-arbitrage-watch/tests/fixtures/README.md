# Test fixtures

Every fixture in this directory is **synthetic** - hand-authored purely to
exercise this package's validation and math, not derived from or
transcribed from the Calendar Moat Analysis / Calendar Arbitrage Screener
v0.1 / Calendar Arbitrage Multi-Agent Watch v0.1 research documents.

Those research documents are not checked into `discovery-lab` or into
`DinevDecor/project-memory/archive`. As of the 2026-08-15-3 correction
pass they ARE reachable via Drive and have been read for provenance/
formula verification - see
`docs/method/calendar-arbitrage-screener-v0.1.1-delta.md`'s provenance
note. A minimal immutable fixture derived from the real Drive-hosted
baseline scan (with citation to the specific source file) is still
deferred, as a deliberate scope decision for this correction pass, not
because the source is unreachable - see "what was intentionally not
implemented" in the implementation report. Fabricating one from memory
instead of citing the real source would misrepresent it as real
evidence, which this repo's own provenance discipline (CLAUDE.md:
"Provenance is truthful or absent") forbids.

`synthetic_submission_dated.json` and `synthetic_submission_rolling.json`
are plain, minimal, made-up examples - a DATED regulatory-clock case and
a ROLLING infrastructure-queue case - used only to prove the intake ->
ledger -> gate -> lifecycle -> report pipeline wires together correctly.
