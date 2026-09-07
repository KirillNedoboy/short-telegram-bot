# Immutable Research Archive Contract

Status: Phase 1 foundation plus Phase 1C retention maturation. Offline/admin only. The live bot does not import `app.research` and no strategy/runtime behavior is changed.

## Boundary

`app/research/archive.py` opens SQLite with a URI `mode=ro` connection and immediately sets `PRAGMA query_only=ON`. The exporter never calls `Database.create_all`, never uses SQLAlchemy live repositories, and has no production cleanup mode. `scripts/archive_research.py` is the explicit offline entrypoint.

Research tables are selected by the authoritative `TABLE_CLASSIFICATION` map. The default set is only `RESEARCH_APPEND_ONLY`. Explicit requests for operational-critical or operational-recent tables are refused. Signals, provenance, outcomes, event state, outbox, watch candidates, root state, and current heartbeats are not automatically archived.

## Phase 1C retention dry-run

`app/research/retention_policy_v1.json` is the immutable policy artifact for
policy version `phase1c-v1`; `app/research/retention.py` evaluates lifecycle
state without publishing an archive. The extended CLI is:

```text
python -m scripts.archive_research --db <production-db> --output <admin-root> \
  --retention-dry-run [--policy <versioned-json>] [--as-of <UTC_TIMESTAMP>] \
  [--sample-limit N]
```

The dry-run opens the source read-only, enables `PRAGMA query_only=ON`, and
writes machine-readable JSON to stdout. It reports per-table total/KEEP/
ARCHIVE_ONLY/DELETE_ELIGIBLE/UNKNOWN counts, reason counts, dependency graph
hash and completeness, protected identity evidence, deterministic samples,
source hashes, and policy version. It never creates Parquet files, manifests,
backups, temporary output, or a deletion plan. Archive publication options and
destructive/cleanup options are rejected when combined with the retention
mode. `--as-of` is an observation boundary only; it does not invent a numeric
retention period. Missing hot-window input therefore cannot produce a delete
eligible result.

## Selection and partitioning

- `--before` is a strict UTC cutoff: rows with a selected timestamp `< cutoff` are exported; the exact boundary is excluded.
- Rows with a null/unparseable selected timestamp are retained in `year=unknown/month=unknown` with a manifest warning, avoiding silent evidence loss.
- Default partition path: `dataset=<table>/year=<UTC year>/month=<UTC month>/part-<archive_run_id>-<chunk>.parquet`.
- Default batch size is 50,000 rows. One or more row groups per file avoid per-row/tiny-file output; `batch_size` is configurable through the Python API for tests and future admin tuning.
- Source rows are ordered deterministically by primary key, or by all columns when a table has no primary key.

## Parquet fidelity

PyArrow is loaded lazily and is an offline/admin dependency (`requirements-research.txt`), not a live runtime dependency. SQLite declarations map to typed Arrow columns:

- INTEGER → signed 64-bit integer
- REAL/FLOAT/DOUBLE/NUMERIC/DECIMAL → 64-bit float
- BOOLEAN → boolean
- DATETIME/TIMESTAMP → UTC timestamp with microsecond resolution
- JSON/TEXT/VARCHAR → string containing the original SQLite serialized value
- BLOB → binary

JSON strings are not parsed, sorted, normalized, or rewritten. Floating point values remain IEEE-754 doubles in Parquet. Timestamp values are normalized to UTC as a typed timestamp; source and archive comparisons use the same microsecond instant.

## Manifest

Each run derives `archive_run_id` from source DB SHA-256, strict cutoff, selected table names, and SQLite `user_version`. The manifest records:

- run/source identifiers, source SHA-256, code SHA when available, schema version, dataset epoch, cutoff;
- format, compression, partition, and batch contract;
- per table: source/selected/archive row counts, timestamp min/max, primary key, schema and schema fingerprint, null counts, numeric count/min/max/sum, identity digest, file paths, file sizes, and SHA-256 hashes;
- verification status, errors, and warnings.

The complete manifest is written atomically only after all Parquet files are staged, read back, hashed, and verified. A crash leaves an `INCOMPLETE` manifest and staging files; incomplete manifests are not accepted by `verify-only`.

## Idempotency and publication

A repeated export against the same source bytes, table set, and cutoff resolves to the same run ID. If its complete manifest exists, the exporter verifies and returns it without creating files. New archive bytes are written under a unique staging attempt, then each file is atomically moved into the deterministic final path. Existing divergent files are never overwritten. Complete manifests are immutable; a mismatched existing archive fails closed.

## Verification

`verify_manifest` checks every file hash and size, reads every Parquet file, compares archived row totals, and recomputes schema, null, numeric, timestamp, and identity digests. With `--db`, it repeats the selected source query through a read-only connection and compares source and archive metrics plus source SHA-256. `--verify-only` accepts only a complete manifest.

## DuckDB compatibility

`app/research/query.py` provides read-only in-memory DuckDB helpers. Example:

```sql
SELECT symbol, COUNT(*)
FROM read_parquet('research_archive/dataset=strategy_observations/**/*.parquet')
GROUP BY symbol
ORDER BY symbol;
```

The CLI/query helper is not imported by live runtime. DuckDB is an offline/admin dependency only.

## Disk and WAL observation

`disk_budget_report` measures active DB size, `-wal` size, archive size, free disk, rough observed daily research rows, rough DB growth, and conceptual warning/critical free-space thresholds. It does not alert, checkpoint, vacuum, or mutate SQLite. `sqlite_observation` records journal mode, page count/size, `user_version`, query-only state, and whether the source hash stayed unchanged. Current code configures WAL and a 5-second busy timeout; Phase 1 performs no checkpoint.

## Cleanup boundary

No cleanup command is provided. `simulate_cleanup_on_copy` exists only as an explicitly named test/admin helper requiring a caller-supplied disposable copy; it reports eligible rows and does not vacuum. Production deletion, compaction, and retention rollout remain Phase 1B work requiring separate approval.
