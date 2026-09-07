# Production capacity recovery — 2026-09-05

## Result

`PRODUCTION CAPACITY RECOVERY: PASS`

`READY_FOR_PHASE_6_REST_WS_PARITY`

Capacity was recovered outside the active database. Production was not restarted, no release was deployed, and no strategy, retention, schema, configuration, journal, backup, or research-archive content was changed.

## Locked production state

- Active release: `d7d54fa8af070241711d5072cffbf8208f482b5d`.
- Legacy rollback: `261646f7e7653957438dee54b38a23104f35c4ea-legacy`.
- Additional retained rollback releases: `2a88e7faa6bb32415636482b10e4652c1b529334` and `eff29afac127511d02c0b1479744ec7b02fc6074`.
- Required rollback backup retained: `pre_architecture_rollout_20260903T200737Z.sqlite`.
- Service remained `active/running`, MainPID `108366`, `NRestarts=0`, start time `2026-09-05T08:19:39Z`.
- Strategy fingerprint before and after: `d35e71128fcae2a02746fa46d7ada459c708eee83642c6304b393d4f089d661c`.
- Active config SHA-256: `044481e302ea16676e32a09d90f1fecf97371ba7302cfa4bfd71e43c90d63a86`.
- Retention policy SHA-256: `cb6b22e14738204dd4144e9876039ec6f6afde8aa6d2fdf0caa97e709e7dd867`.
- AUTOEXECUTION remained `OFF`.

## Before

Deployed P0 snapshot at `2026-09-05T13:14:30Z`:

- free bytes: `3,504,156,672`;
- free percent: `5.5349`;
- free inodes: `3,142,735`;
- DB bytes: `3,651,665,920`;
- WAL bytes: `27,068,432`;
- dynamic reserve: `4,792,516,608`;
- state: `LOW_SPACE`.

The filesystem was `/dev/vda2`, 63,310,585,856 bytes total. Journal usage was 590 MiB and was not modified.

## Consumer classification

| Consumer | Classification | Action |
|---|---|---|
| Production DB/WAL/SHM and `/opt/short-telegram-bot-lite` | `ACTIVE_PRODUCTION_REQUIRED` | Retained |
| Active `d7d54fa…` release | `CURRENT_RELEASE_REQUIRED` | Retained |
| `261646f7…-legacy`, `2a88e7…`, `eff29af…` | `IMMUTABLE_ROLLBACK_REQUIRED` | Retained |
| `pre_architecture_rollout_20260903T200737Z.sqlite` | `CURRENT_ROLLBACK_BACKUP_REQUIRED` | Retained |
| Canonical research archive | `RESEARCH_ARCHIVE_REQUIRED` | Retained |
| `retention_20260902T133815Z.sqlite` | `RESEARCH_SNAPSHOT_OPTIONAL_OFFHOST` | Retained on host |
| Journal and `/var/log` | `LOG_ROTATABLE` | No rotation or deletion |
| Phase2C deployment work, phase1c1 work, phase2a backup, external backups, and releases without locally preserved commits | `UNKNOWN_DO_NOT_TOUCH` | Retained |

## Cleanup actions

Every target passed the same immediate preflight: exact `realpath`, real top-level directory, zero `lsof +D` handles, zero regular production SQLite files, no active/legacy/systemd reference, and preserved source/evidence. Targets were removed individually with a literal path; symlinks were not followed.

| Exact deleted path | Classification | Observed apparent bytes | Filesystem bytes recovered |
|---|---|---:|---:|
| `/opt/short-telegram-bot-lite-admin/work/phase5-shadow-validation-1bb1097` | `TEMPORARY_REHEARSAL_SAFE_TO_REMOVE` | 237,912,194 | 267,177,984 |
| `/opt/short-telegram-bot-lite-admin/work/phase5-shadow-validation-3f8d28a` | `TEMPORARY_REHEARSAL_SAFE_TO_REMOVE` | 471,872,350 | 531,034,112 |
| `/opt/short-telegram-bot-lite-admin/releases/ab4fd795e6d91885aee07e9538fea45d28c396d2` | `OLD_RELEASE_SAFE_TO_REMOVE` | 455,952,025 | 487,600,128 |
| `/opt/short-telegram-bot-lite-admin/releases/dd761486bc6ca566e3ce524321dd56db8bde23b7` | `OLD_RELEASE_SAFE_TO_REMOVE` | 456,058,991 | 487,641,088 |
| `/opt/short-telegram-bot-lite-admin/releases/d03d8fbdbfa838323d02eebd96e23b28b34c53c3` | `OLD_RELEASE_SAFE_TO_REMOVE` | 456,071,499 | 487,702,528 |
| `/opt/short-telegram-bot-lite-admin/releases/6f74fafce5ee7f0fc40389786e102d7f15bd8182` | `OLD_RELEASE_SAFE_TO_REMOVE` | 4,484,399 | 5,738,496 |
| `/opt/short-telegram-bot-lite-admin/releases/c8b8409cbea0a279c7bd80f7ef86fda45fb22ba` | `OLD_RELEASE_SAFE_TO_REMOVE` | 260,420,595 | 290,242,560 |
| `/opt/short-telegram-bot-lite-admin/releases/56dbc03e4cca40b36b8c1c34a27d752ebe74ab31` | `OLD_RELEASE_SAFE_TO_REMOVE` | 260,579,500 | 290,410,496 |

Total filesystem recovery measured by `df -B1`: `2,847,547,392` bytes.

Moved off-host: none.

## After

Final deployed P0 snapshot at `2026-09-05T13:23:01Z`:

- free bytes: `6,350,946,304`;
- free percent: `10.0314`;
- free inodes: `3,240,371`;
- DB bytes: `3,652,784,128`;
- WAL bytes: `27,068,432`;
- dynamic reserve: `4,793,634,816`;
- margin above reserve: `1,557,311,488`;
- state: `HEALTHY`.

The running process itself logged the `HEALTHY` transition at `2026-09-05T13:20:46Z`, followed immediately by a successful DB heartbeat.

## Database and runtime acceptance

- Read-only `PRAGMA quick_check`: `ok` in 81.335 seconds.
- Before cleanup: 5,174 scan cycles, 128,924 strategy observations, heartbeat `13:11:34Z`, outbox `SENT=54`.
- After cleanup: 5,176 scan cycles, latest `COMPLETED` at `13:19:46Z`; 128,966 strategy observations, latest at `13:22:30Z`; heartbeat `13:20:46Z`; outbox remained `SENT=54` with no retry/dead rows.
- No new `SQLITE_FULL`, `database or disk is full`, or runtime-error event was observed after cleanup.
- REST remained canonical and completed a normal 100-symbol cycle after cleanup.

## Phase 5 acceptance

The active runtime reconnected after its normal universe replacement and returned to `HEALTHY`, acknowledging all 226 expected topics. A separate release-local 120-second DB-free and Telegram-free probe reported:

- symbols: `113`;
- expected/acknowledged topics: `226/226`;
- failed/pending topics: `0/0`;
- messages: `39,180`;
- ticker updates: `35,305`;
- kline updates: `4,095`;
- parse errors: `0`;
- disconnects/reconnects/stale symbols: `0/0/0`;
- clean final probe state: `STOPPED` after explicit shutdown.

## Invariants

- Deleted production DB data: `NO`.
- Retention policy changed: `NO`.
- Active release deleted or redeployed: `NO`.
- Legacy/current rollback release deleted: `NO`.
- Current rollback backup deleted: `NO`.
- Production restarted: `NO`.
- Strategy behavior changed: `NO`.
- AUTOEXECUTION: `OFF`.

Phase 6 capacity gate is unblocked: `READY_FOR_PHASE_6_REST_WS_PARITY`.
