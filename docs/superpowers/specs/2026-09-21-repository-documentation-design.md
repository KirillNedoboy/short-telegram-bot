# Versioned Short Telegram Bot Documentation Design

**Status:** approved by operator
**Scope:** public repository documentation; no credentials, production databases, private endpoints, or autoexecution material.

## Goal

Make the repository understandable as a technical artifact and as an operational signal system while keeping historical GitHub code, the 14 September production release, and the 17 September Lane B release distinct.

## Source-of-truth model

The documentation uses three explicit layers:

1. **GitHub baseline** — commit `ce77d744d7a3da93b9b05c5fcafde57dfb36ca77`, 2026-09-08.
2. **Production A** — release `bf47d2b1d2b0b159da780dc337adefe3dcd2b6e71c13c2506721c4c816be92ea`, 2026-09-14.
3. **Lane B** — release `dfcdb9df3e6c6a3667fa914e3ea0189f7a6f8e35db43ac530ba8db51b69f7553`, 2026-09-17.

A claim is labelled `implemented in baseline`, `production-only`, `Lane-B-only`, `historical`, or `not verified` when the layers differ.

## Documentation set

- `README.md` — product explanation, safe quick start, documentation map, current limitations.
- `docs/SOURCE_OF_TRUTH.md` — versions, provenance, release matrix, and evidence boundaries.
- `docs/MATHEMATICS.md` — source-grounded feature and scoring formulas with units, windows, missing-data rules, and code links.
- `docs/STRATEGIES.md` — strategy contracts, gates, scoring, state machines, confirmation, invalidation, and delivery policy.
- `docs/SIGNAL_PIPELINE.md` — end-to-end flow from Bybit data to Telegram outbox.
- `docs/MARKET_DATA.md` — candle semantics, `as_of`, continuity, freshness, recovery, and data-quality states.
- `docs/DELIVERY.md` — signals, WATCH, EARLY DROP WARNING, persistence, idempotency, retries, and Telegram delivery.
- `docs/RELEASES.md` — dated release differences and rollback/provenance guidance.
- `docs/OPERATIONS.md` and `docs/DEPLOYMENT.md` — safe local/private operation, health checks, backups, and rollback.
- `docs/examples/` — sanitized signal, rejection, warning, lifecycle, and delivery examples.

## Content rules

- Every formula links to the implementation file and relevant test.
- No profitability, hit-rate, or trading-edge claim is inferred from score/grade.
- No secret, token, chat ID, database, private host, or production connection string is published.
- `AUTOEXECUTION=OFF` and manual-entry policy are explicit.
- Actionable short signals, WATCH candidates, shadow observations, and EARLY DROP WARNING remain separate throughout the docs.
- Historical claims are dated and labelled; current runtime claims require current evidence.

## Verification contract

Before publishing:

- validate Markdown links and code/config snippets;
- run the repository test, compile, lint, and configuration checks;
- run a formula/source cross-reference scan;
- scan for secret-like values and private paths;
- compare docs against the three source layers;
- verify the pushed default branch through GitHub raw/API readback.
