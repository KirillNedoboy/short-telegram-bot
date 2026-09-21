# Legacy Rollback Rehearsal V2 — 2026-09-05

## Final classification

`SOURCE CLEANUP: PASS`

`LEGACY_ROLLBACK_REHEARSAL_PASS`

The exact historical runtime was exercised twice against a fresh SQLite Online
Backup API copy of the current production V1 database. All business-data
changes were explained, monotonic and idempotent. Production was never
restarted and its database was never opened writable.

## Source of truth

- `ACTUAL_MAIN_SHA`: `6d368210e8bc02b92e2bc7971c7fb24d00e88312`.
- Local `main` was clean before and after the rehearsal.
- Legacy source: `261646f7e7653957438dee54b38a23104f35c4ea`.
- Immutable release:
  `<PRIVATE_ADMIN_ROOT>/releases/261646f7e7653957438dee54b38a23104f35c4ea-legacy/`.
- Deterministic source archive SHA-256:
  `e8b11e88404717bee81bbc4a2c30ad4c01ade9acb3b7711e200c8cb8893304a9`.
- Release manifest SHA-256:
  `5135df724a4f33c567721ca5ab70164ca10190a8be01e3d4a44d40eb54205adf`.

## Fresh disposable copy

- Path:
  `<PRIVATE_ADMIN_ROOT>/work/legacy-rollback-rehearsal-v2-20260905T054100Z/bot.sqlite`.
- Size: `3,566,133,248` bytes.
- SHA-256:
  `729ce0004989770f58ac4207c098577dc9bd84b499d473d979661153004fb239`.
- Source production DB was opened with `mode=ro`; destination was created by
  SQLite Online Backup API.
- Before/after each run: `user_version=1`, `quick_check=ok`,
  `integrity_check=ok`.

## First startup write-set

Telegram, live scans, Bybit and execution were trapped; autoexecution remained
OFF. Historical config loading, DB open, schema ensure, heartbeat, state
restore and reconciliation were allowed.

- 8 `climax_entry_attempts` rows were reconciled:
  `APRUSDT:4h:1788464820:292900:r1:a1`,
  `BTWUSDT:4h:1788463560:513140:r1:a1`,
  `CAPUSDT:1h:1788491880:55540:r1:a1`,
  `MAGMAUSDT:15m:1788505560:280700:r1:a1`,
  `MAGMAUSDT:1h:1788488940:286700:r1:a1`,
  `MARSCOINUSDT:15m:1788470340:111600:r1:a1`,
  `SKRUSDT:1h:1788507780:21798:r1:a1`,
  `SKRUSDT:1h:1788507780:21798:r2:a1`.
- Every transition was identical in shape:
  `BREAKDOWN_PENDING -> EXPIRED`.
- Changed columns were exactly `attempt_state`, `attempt_closed_at`,
  `attempt_close_reason` and `last_observed_at`.
- Reason: `startup_reconciliation_ttl_expired`.
- Predicate: `confirmation_expires_at <= observed_at` and
  `attempt_closed_at IS NULL`.
- Source: `BotRepository.reconcile_shadow_lifecycle`.
- Classification for all 8: `A. EXPECTED_MONOTONIC_RECONCILIATION`.
- 16 corresponding `climax_entry_attempt_events` inserts were bounded
  reconciliation evidence; no deletes occurred.
- Heartbeat write was classified `B. EXPECTED_HEARTBEAT_OPERATIONAL_WRITE`.
- Four index ensures and heartbeat table ensure were classified
  `C. EXPECTED_IDEMPOTENT_SCHEMA_ENSURE`; all were `CREATE IF NOT EXISTS`.
- Outbox SQL claim statements affected no rows; outbox logical digest was
  unchanged.

## Second startup idempotency

- Exact same legacy startup ran again on the same disposable DB.
- Semantic changes to the already reconciled attempts: `0`.
- No oscillation and no repeated timestamp churn in historical evidence.
- Only idempotent schema ensures, heartbeat and zero-row outbox claim updates
  were observed.
- First/second captured write-set sizes: `25` / `8` statements.

## Protected data and forward validation

- Signals, provenance, outcomes, outbox, event states and root identities had
  no semantic mutation.
- Attempts changed only through the eight documented monotonic transitions;
  attempt-event additions matched those transitions.
- Current architecture release `2a88e7faa6bb32415636482b10e4652c1b529334`
  passed read-only `migrate_db.py --verify --include-shadow-v2`:
  version `1`, structure valid, no missing tables/columns/indexes.
- Forward validation return code: `0`.

## Rollback target and production invariants

- Before: `legacy-current -> <APP_ROOT>` (dirty checkout).
- After: `legacy-current -> .../261646f7e7653957438dee54b38a23104f35c4ea-legacy`.
- `LEGACY_CHECKOUT_NOT_ROLLBACK_SOURCE` marker is present.
- Production `current` remained:
  `.../releases/2a88e7faa6bb32415636482b10e4652c1b529334`.
- Service remained `active/running`, `MainPID=59867`, `NRestarts=0`;
  start timestamp and invocation ID were unchanged.
- Unit SHA-256:
  `6dada4137e82f713ff2f6e390e2e6cf35974b69cc967b9a3429c8d527257402e`.
- Production config SHA-256:
  `24bce4ca7dce59354cb8b22b581528daa9889cc66003a17c7500f727d3d515e6`.
- Production `.env` SHA-256:
  `a3d45490149154249795fc83fe6a08f3604b5b1a8ad3ada6e42408858996c51e`.
- `PRODUCTION_RESTARTED=NO`.
- `PRODUCTION_DB_MODIFIED_BY_REHEARSAL=NO`.
- Trading behavior changed: `NO`.
- Dirty checkout remains on disk but is not required for rollback.

## Result

`SOURCE_OF_TRUTH_AND_ROLLBACK_CLEANUP_COMPLETE`

`READY_FOR_PHASE_5_MARKETDATAHUB_WS_SHADOW`
