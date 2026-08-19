# Bulgarian display layer

The Mobile Machine Console is Bulgarian-first for human-facing case narrative, while canonical ledgers remain unchanged and authoritative.

- `site/translations-bg.json` is derived display data, never evidence.
- Every cache entry is bound to the exact SHA-256 of its source text.
- Missing or stale translations fall back to the original source text.
- `site/bg-ui.js` exposes a BG/EN toggle; the English/source form is always available.
- The browser has no model client, API key, or mutation endpoint.
- `.github/workflows/mobile-console-bg-translations.yml` refreshes the derived cache when relevant canonical records change. The model call is isolated to the translation job; Pages build/deploy jobs have no model/API secret.
- The translation workflow writes only `mobile-console/site/translations-bg.json`; it never writes to a canonical ledger.
