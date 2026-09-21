# PHASE 1 RESULT

**PASS.** The implementation is isolated, read-only against source SQLite, and does not implement production cleanup.

## Source

- Branch: `architecture/phase1-research-archive`.
- HEAD: `a28ddf8` (`test: freeze trading behavior contracts`).
- Phase 0 presence: `docs/architecture/current-trading-contract.md`, `docs/evidence/architecture-phase0-behavior-freeze-20260827T053347Z.md`, and `tests/contracts/` are committed at HEAD.
- Phase 0 gate in this branch: **28 passed**.
- Production/strategy source was not changed.

## Current DB inventory

Inventory source: safe copy `.codex-staging/volume-climax-profile-audit-20260825T164748Z/production.sqlite`; this was not the configured active DB. The read-only inventory found 31 user tables. Snapshot facts: database size **1,588,756,480 bytes**, page count **387,880**, page size **4,096**, `journal_mode=wal`, WAL size **0**, `user_version=0`, `query_only=1`, and identical source SHA-256 before/after observation (`338d1e1fa821fa14caf668c9ca04466267ca9bb4aaec39bf6e10e8cc7b68b5b4`). Per-table `dbstat` sizes were unavailable in this SQLite build and are recorded as N/A rather than inferred.

Timestamp below is the deterministic archive-selection column; all other timestamp columns remain in the Parquet schema. No table has proven rebuildability, so `rebuildable=False` is the conservative inventory value.

| Table | Classification | Rows | Approx size | Selected timestamp | Live-critical | Research/audit |
|---|---|---:|---:|---|---|---|
| `__db_heartbeat` | OPERATIONAL_CRITICAL | 1 | N/A | none | YES | NO |
| `event_states` | OPERATIONAL_CRITICAL | 93 | N/A | `updated_at` | YES | NO |
| `signals` | OPERATIONAL_CRITICAL | 7 | N/A | `created_at` | YES | NO |
| `signal_provenance` | OPERATIONAL_CRITICAL | 7 | N/A | none | YES | NO |
| `signal_outcomes` | OPERATIONAL_CRITICAL | 7 | N/A | `updated_at` | YES | NO |
| `telegram_delivery_outbox` | OPERATIONAL_CRITICAL | 7 | N/A | `created_at` | YES | NO |
| `watch_candidates` | OPERATIONAL_CRITICAL | 349 | N/A | `created_at` | YES | NO |
| `climax_root_events` | OPERATIONAL_CRITICAL | 297 | N/A | `created_at` | YES | NO |
| `climax_entry_attempts` | OPERATIONAL_CRITICAL | 741 | N/A | none | YES | NO |
| `runtime_heartbeats` | OPERATIONAL_RECENT | 1 | N/A | `checked_at` | NO | NO |
| `runtime_heartbeat_history` | OPERATIONAL_RECENT | 56,324 | N/A | `created_at` | NO | NO |
| `climax_evaluations` | RESEARCH_APPEND_ONLY | 25,782 | N/A | `created_at` | NO | YES |
| `volume_climax_observations` | RESEARCH_APPEND_ONLY | 25,774 | N/A | `observed_at` | NO | YES |
| `strategy_observations` | RESEARCH_APPEND_ONLY | 51,564 | N/A | `observed_at` | NO | YES |
| `climax_entry_attempt_events` | RESEARCH_APPEND_ONLY | 10,595 | N/A | `observed_at` | NO | YES |
| `climax_monitor_events` | RESEARCH_APPEND_ONLY | 53,438 | N/A | `created_at` | NO | YES |
| `market_coverage_ledger` | RESEARCH_APPEND_ONLY | 1,896,986 | N/A | `observed_at` | NO | YES |
| `market_scan_cycles` | RESEARCH_APPEND_ONLY | 2,488 | N/A | `cycle_started_at` | NO | YES |
| `market_scan_rotations` | RESEARCH_APPEND_ONLY | 907 | N/A | `rotation_started_at` | NO | YES |
| `market_scan_symbol_results` | RESEARCH_APPEND_ONLY | 677,177 | N/A | `scheduled_at` | NO | YES |
| `reject_stats` | RESEARCH_APPEND_ONLY | 1,627 | N/A | `logged_at` | NO | YES |
| `root_detector_shadow_candidates` | RESEARCH_APPEND_ONLY | 1,021 | N/A | `first_seen_at` | NO | YES |
| `root_detector_shadow_episodes` | RESEARCH_APPEND_ONLY | 1,021 | N/A | `opened_at` | NO | YES |
| `root_detector_shadow_observations` | RESEARCH_APPEND_ONLY | 6,365 | N/A | `observed_at` | NO | YES |
| `root_detector_shadow_episode_outcomes` | RESEARCH_APPEND_ONLY | 1,021 | N/A | none | NO | YES |
| `root_detector_shadow_episode_root_links` | RESEARCH_APPEND_ONLY | 324 | N/A | none | NO | YES |
| `root_detector_shadow_legacy_mappings` | RESEARCH_APPEND_ONLY | 0 | N/A | none | NO | YES |
| `root_detector_shadow_v2_roots` | RESEARCH_APPEND_ONLY | 674 | N/A | `created_at` | NO | YES |
| `root_detector_shadow_v2_outcomes` | RESEARCH_APPEND_ONLY | 674 | N/A | none | NO | YES |
| `current_root_outcomes` | RESEARCH_APPEND_ONLY | 82 | N/A | `anchor_time` | NO | YES |
| `current_root_predicate_snapshots` | RESEARCH_APPEND_ONLY | 7,938 | N/A | `observed_at` | NO | YES |

No `DERIVED_REBUILDABLE` table was claimed. The repository has no retention purge function. `Database._ensure_sqlite_schema()` performs additive compatibility changes, but Phase 1 did not invoke it on the snapshot.

## Archive design

- Format: Apache Parquet via lazy PyArrow import.
- Compression: Zstandard (`zstd`).
- Partition: `dataset=<table>/year=<UTC year>/month=<UTC month>`.
- Default batch/file target: 50,000 rows; row groups use the batch size to avoid tiny files.
- Strict cutoff: selected timestamp `< --before`; exact boundary is excluded.
- Deterministic row ordering: primary key, or all columns when no primary key exists.
- Default archive set: only `RESEARCH_APPEND_ONLY` tables. Operational-critical/recent tables are refused when explicitly requested.
- Source connection: SQLite URI `mode=ro` plus `PRAGMA query_only=ON`.

## Manifest contract

Manifest path: `manifests/archive-run-<archive_run_id>.json`.

The run ID is derived from source SHA-256, selected table set, strict cutoff, and SQLite `user_version`. Each manifest records source identity/hash, code SHA, schema version, dataset epoch field, cutoff, format/compression/partition contract, table row counts, timestamp range, schema fingerprint, null counts, numeric count/min/max/sum, identity digest, archive file paths/sizes/SHA-256, warnings, errors, and verification status.

The complete manifest is atomically published only after staging verification. An incomplete staging attempt is represented separately with status `INCOMPLETE` and is not accepted by `--verify-only`. Repeating the same source snapshot/table/window returns the existing verified manifest and does not create duplicate logical rows.

## Verification contract

`verify_manifest` checks file existence, byte size, SHA-256, Parquet readability, archive row counts, schema fingerprint, NULL counts, numeric aggregates, timestamp range, and deterministic identity digest. With `--db`, it repeats the selected source query over a read-only connection and compares source metrics and source SHA-256. No source write, checkpoint, vacuum, or migration is performed.

## Sample export

- Source: safe snapshot copy `production.sqlite` from the staging audit directory.
- Source SHA-256: `338d1e1fa821fa14caf668c9ca04466267ca9bb4aaec39bf6e10e8cc7b68b5b4`.
- Source code SHA in manifest: `a28ddf8b0ba0da28f8e875fcb891a3a21437165d`.
- Cutoff: `2026-08-24T00:00:00Z`.
- Dataset: `climax_evaluations`.
- Rows archived: **20,768** of source **25,782**.
- Parquet files: **1**.
- Parquet size: **10,138,012 bytes**; manifest directory total including JSON manifests: **10,150,056 bytes**.
- Compression ratio: not claimed; SQLite `dbstat` could not attribute source bytes per table in this build. Whole-database-to-Parquet byte ratio would be misleading.
- Sample manifest: `evidence/phase1-sample-archive-20260827T053347Z/manifests/archive-run-2c0c0d779e01c15804dd74b069860cbb.json`.
- Verification: **PASS** (`--verify-only`, zero errors).

## DuckDB verification

DuckDB successfully read the published partition through `read_parquet`. Example result for `COUNT(*) GROUP BY symbol ORDER BY count DESC LIMIT 5`:

```text
TUTUSDT 1657
BTWUSDT 1567
ACEUSDT 1412
CASHCATUSDT 1154
HEMIUSDT 1123
```

The automated parity test compares SQLite and DuckDB for symbol grouping, strategy grouping, and UTC time-range filtering.

## Query equivalence

**PASS** in `tests/archive/test_query.py`:

- grouped counts by symbol;
- grouped counts by strategy;
- inclusive/exclusive UTC time range;
- Parquet read through DuckDB `read_parquet`.

The test uses a disposable SQLite snapshot and never joins operational tables or changes live runtime behavior.

## Retention policy

Created: `docs/architecture/data-retention-policy.md`.

The policy is provisional and uses categorical targets rather than unsupported numeric days. Critical signal/provenance/outcome/outbox/event state tables remain KEEP. Research append-only tables become cleanup-eligible only after a COMPLETE verified archive and separate Phase 1B approval. No production delete command exists.

## Disk budget and WAL observation

Safe snapshot observation:

- Active DB: 1,588,756,480 bytes.
- WAL: 0 bytes.
- Journal mode: `wal`.
- Free disk: 85,232,619,520 bytes.
- Rough daily research rows: 278,302.5.
- Rough daily DB growth: 203,241,036.6 bytes.
- Conceptual status: `OK`; estimated days to warning free-space threshold: 366.5.
- Checkpoint performed: false.

These are rough snapshot-span estimates, not alert thresholds or production policy.

## Performance

Measured on the safe snapshot with one `climax_evaluations` export:

- 20,768 rows in 31.637 seconds;
- 656.4 rows/second;
- 0.31 MiB/second compressed output throughput;
- Python `tracemalloc` peak: approximately 374.93 MiB (PyArrow native allocations are not included).

No production DB benchmark was performed.

## Cleanup simulation

`simulate_cleanup_on_copy` was tested only against a disposable SQLite copy. It reports rows before/eligible/remaining and does not VACUUM. There is no production cleanup CLI mode. SQLite file compaction remains a future controlled operation; DELETE alone does not guarantee filesystem size reduction.

## Production impact

- Production DB modified: **NO**.
- Production service modified/restarted: **NO**.
- Production config modified: **NO**.
- Trading behavior changed: **NO**.
- Database schema changed: **NO**.
- Live runtime imports archive package: **NO**.

## Tests

- Phase 0 contract gate: **28 passed**.
- Archive/Phase 1 tests under 64-bit Python 3.12 with optional dependencies: **8 passed**.
- Full suite after Phase 1 files: **303 passed in 85.13 seconds**.
- Compile: `python -m compileall -q app tests scripts` → **PASS**.
- Lint: `ruff check app/research scripts/archive_research.py tests/archive` → **PASS**.

## Limitations

- The active production path `<APP_ROOT>` and systemd service were not reachable from this Windows workstation; all DB measurements used a safe local snapshot copy.
- The default interpreter is 32-bit Python 3.11 and cannot install the available PyArrow Windows wheel. Archive verification used installed 64-bit Python 3.12 with `requirements-research.txt`; live runtime requirements remain unchanged.
- No `dbstat` per-table byte attribution was available; per-table sizes are N/A.
- Dataset epoch is currently not a runtime field and remains `null` in manifests.
- No production cleanup, checkpoint, vacuum, migration, or retention rollout was attempted.

## Cleanup readiness

**READY_FOR_PHASE_1B_CONTROLLED_RETENTION_ROLLOUT: YES** for a separately approved controlled rollout. No cleanup was executed in Phase 1.
