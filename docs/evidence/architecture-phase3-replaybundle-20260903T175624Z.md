# PHASE 3 RESULT

## Source

- Branch: `architecture/phase3-replaybundle`
- Base SHA: `ccab365eb606303ab97092d5ba03c684cf5d17ba`
- Final implementation SHA: `d141e46` (foundation plus artifact-contract and offline replay hardening)
- Final branch HEAD is resolved by `git rev-parse HEAD` after this evidence commit; it is intentionally not self-embedded.

## ReplayBundle version

ReplayBundle v1. `COMPLETE` is a sealed lifecycle state; `CANONICAL` and `NON_CANONICAL` are separate provenance values.

## Artifact structure

The builder publishes `manifest.json`, `hashes.json`, `COMPLETE`, sanitized config/contract JSON/YAML, typed `market_data/candles_1m.parquet`, input, decision, outcome and provenance Parquet files, plus JSON/Markdown reports. It stages in a sibling directory, verifies before atomic publication, refuses existing run IDs and preserves failed staging diagnostics.

## Strategy input inventory

| Strategy | Current input boundary | Decision code | Replay gap |
|---|---|---|---|
| BASELINE_PULLBACK | `EventState`, `SymbolFeatures`, `ShortZone`, fixed decision time, `AppConfig` | `SignalEngine.analyze` | canonical serializer/record envelope |
| VOLUME_CLIMAX_UNWIND | `EventState`, `SymbolFeatures`, ordered 1m frame, `AppConfig` | `evaluate_climax_bundle` | portable frame reference |
| LOW_VOLUME_EXTENSION_FAILURE | same climax bundle boundary | `evaluate_climax_bundle` | portable frame reference |

All three adapters are pure; no live client, repository, Telegram or SQLite access is used by replay.

## Live/replay decision boundary

Replay deserializes inputs and calls the same production evaluators. It does not duplicate gates, scores, admission, lifecycle or side effects. `ROOT_DETECTOR_SHADOW_V2` remains research-only and is absent from the strategy contract.

## Canonicalization

Canonical bytes are UTF-8 JSON with sorted mapping keys, compact separators, preserved list order, UTC `Z` timestamps, finite floats formatted with `.15g`, and SHA-256 fingerprints. Config sanitization uses an explicit decision-only allowlist; credentials, tokens, chat IDs and DB URLs are not serialized.

## Clock/time semantics

Evaluator decision time is carried by each input. Builder wall-clock use is limited to metadata (`created_at_utc` and default run ID). Current source candle semantics are preserved: a 1m row becomes available at its interval close.

## Market-data availability semantics

Only `BYBIT / LINEAR / USDT / 1m` rows are accepted. Every row has stable ID, open/close/availability UTC timestamps, OHLCV and source. Rows after `dataset_cutoff_utc` are rejected; climax replay filters rows by availability before the recorded decision time.

## Deterministic ordering

Provenance ordering uses `(availability_time_utc, sequence, symbol, event_type, stable_event_id)` and rejects duplicate full keys. Parquet artifact metadata records physical SHA-256, logical SHA-256, schema digest and row count.

## Fixture bundles

The checked-in replay fixture builds a deterministic sealed baseline bundle; contract fixtures characterize actionable and non-actionable behavior for all three strategy families using existing Phase 0 factories. No historical market download is included.

## Replay parity

- BASELINE: PASS — replay adapter equals `SignalEngine.analyze`.
- VOLUME: PASS — climax adapter dispatches to `evaluate_climax_bundle`.
- LOW_VOLUME: PASS — climax adapter dispatches to `evaluate_climax_bundle`.

## Future leakage test

Input validation rejects features newer than decision time. Climax frame construction excludes rows whose availability exceeds decision time.

## Tamper verification

Changing a report byte or any payload invalidates verification through physical or logical artifact hashes and the COMPLETE seal.

## Network-independent replay

Replay imports only local contract/evaluator and research Parquet code; it does not construct Bybit clients or repositories. The full test suite passes with the offline replay path.

## Determinism

Canonical input and decision fingerprints are persisted in decision rows and recomputed by verification. Identical code/config/input content produces equal semantic hashes; run metadata may differ.

## Regression

- `py -3.12 -m pytest -q`: **353 passed, 3 skipped**.
- `python -m pytest -q`: **342 passed, 7 skipped** (PyArrow tests skipped by the 32-bit interpreter).
- `py -3.12 -m pytest tests/replay -q`: **9 passed**.
- `py -3.12 -m compileall -q app scripts`: PASS.
- changed-scope Ruff: PASS.
- `git diff --check`: PASS.

## Trading behavior

CHANGED = NO. Strategy source gates, thresholds, scores, grades, admission, dedupe, lifecycle, root logic and outcomes semantics were not rewritten.

## Production

MODIFIED = NO. No production checkout, database, systemd unit, Telegram or deployment command was used.

## Remaining limitations

SOURCE_FAITHFUL_BASELINE_REPLAY_NOT_IMPLEMENTED. Phase 4 must reconstruct the historical BASELINE state machine from raw market data; Phase 3 only carries evaluation-ready inputs.

## Classification

REPLAYBUNDLE_FOUNDATION_PASS

## Next

READY_FOR_PHASE_4_BASELINE_SOURCE_FAITHFUL_REPLAY
