# Versioned Repository Documentation Plan

> **For Hermes:** Execute this plan in the repository at `<WORKTREE>`; preserve the source-of-truth boundaries in the approved design.

**Goal:** Turn the public repository into a complete, source-grounded technical and operational reference for the Short Telegram Bot.

**Architecture:** Keep public GitHub baseline, production A, and Lane B as separate documentation layers. Describe formulas and behavior from code/tests, add diagrams and sanitized examples, then validate links, tests, security, and public readback.

**Tech Stack:** Markdown, Mermaid, Python source cross-reference scripts, pytest, compileall, ruff, GitHub Actions.

---

## Task 1: Record approved design and provenance

**Files:**
- Create: `docs/superpowers/specs/2026-09-21-repository-documentation-design.md`
- Create: `docs/plans/2026-09-21-versioned-repository-documentation.md`

Verify the documents contain the three source layers, scope lock, security rules, and verification contract.

## Task 2: Audit formulas and strategy contracts

**Files:**
- Read: `app/features/*.py`
- Read: `app/signals/*.py`
- Read: `app/baseline/lifecycle.py`
- Read: `docs/STRATEGIES.md`
- Read: relevant tests under `tests/contracts/` and `tests/test_*`

Extract only formulas and gates present in code. For each item record implementation path, test path, units, lookback, missing-data behavior, and whether it is baseline, production-only, or Lane-B-only.

## Task 3: Write source-of-truth and release matrix

**Files:**
- Create: `docs/SOURCE_OF_TRUTH.md`
- Create: `docs/RELEASES.md`

Document commit/release identifiers, dates, lane roles, config differences, strategy/delivery differences, and evidence boundaries. Never imply that a production-only release is present in the public baseline.

## Task 4: Write mathematics reference

**Files:**
- Create: `docs/MATHEMATICS.md`

Cover returns, EMA, ATR, RSI, VWAP, volume statistics, rejection/pullback distances, OI/funding, liquidity, freshness, score normalization, and grade mapping. Link every formula to source and tests; mark formulas absent from a layer as not implemented there.

## Task 5: Rewrite strategy contracts

**Files:**
- Modify: `docs/STRATEGIES.md`
- Create: `docs/examples/strategy-decision-example.md`

For every strategy document event detection, state transitions, hard gates, scoring, confirmation, invalidation, persistence, and delivery. Keep WATCH, shadow, EARLY DROP WARNING, and actionable signals separate.

## Task 6: Document pipeline, market data, and delivery

**Files:**
- Create: `docs/SIGNAL_PIPELINE.md`
- Create: `docs/MARKET_DATA.md`
- Create: `docs/DELIVERY.md`
- Create: `docs/examples/early-drop-warning.md`
- Create: `docs/examples/signal-lifecycle.md`

Include Mermaid sequence diagrams, freshness states, continuity/recovery behavior, outbox idempotency, retry/dead-letter behavior, and sanitized examples.

## Task 7: Make operations and deployment reproducible

**Files:**
- Modify: `docs/OPERATIONS.md`
- Modify: `docs/DEPLOYMENT.md`
- Create: `docs/examples/health-audit.md`

Document local setup, private production boundaries, read-only audits, backups, rollback, systemd verification, AUTOEXECUTION=OFF, and the exact evidence needed to claim healthy coverage or Telegram delivery.

## Task 8: Improve README and repository metadata

**Files:**
- Modify: `README.md`
- Review: `SECURITY.md`, `CONTRIBUTING.md`, `config.example.yaml`, `.env.example`
- Add only if needed: `LICENSE` after an explicit license decision

Make the first screen explain the product, route readers to the technical docs, and clearly distinguish public baseline from production documentation.

## Task 9: Add documentation validation

**Files:**
- Create: `scripts/validate_docs.py`
- Create: `tests/test_documentation_contract.py`

Validate required headings, local links, forbidden secret/private-path patterns, formula source links, release identifiers, and explicit AUTOEXECUTION/manual-entry statements.

## Task 10: Verify, commit, push, and read back

Run:

```bash
.venv/bin/pytest -q
.venv/bin/python -m compileall -q app scripts tests
.venv/bin/ruff check app scripts tests
.venv/bin/python scripts/validate_docs.py
```

Then inspect `git diff`, commit in logical documentation commits, push to the configured remote, and verify the public default branch via `git ls-remote` and GitHub raw/API reads. Report local and remote verification separately.

## Scope lock

Do not:

- publish credentials, chat IDs, private hostnames, production DBs, `.env`, WAL/SHM, or connection strings;
- change trading strategies, thresholds, scoring, lifecycle, or runtime code as part of documentation work;
- claim profitability, expectancy, or production readiness without evidence;
- enable autoexecution or add order-placement code;
- merge production-only code into the public baseline without explicit release provenance.
