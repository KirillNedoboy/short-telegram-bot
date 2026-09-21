# Production SQLite FULL incident evidence (2026-09-05)

Status at evidence capture: `ACTIVE/DEGRADED` during recovery; closure remains gated on production hotfix activation and final verification.

## Scope and invariants

- Production data deleted: **NO**. The only deletion was a disposable rehearsal copy listed below.
- Retention changed: **NO**.
- Strategy behavior/configuration changed: **NO**. The hotfix adds infrastructure-only capacity/error handling.
- `AUTOEXECUTION`: **OFF**.
- Phase 5 deployment: **BLOCKED** until `INCIDENT_CLOSED`.
- Production restart for storage recovery: **NO**. Existing process recovered automatically after cleanup.

## Capacity and consumers

The production root filesystem is `/dev/vda2` (ext4), 63,310,585,856 bytes total. The pre-cleanup exact-byte snapshot had 2,198,085,632 bytes available (3.47% free), with 3,227,037 free inodes. The selected rehearsal artifact was removed after verification; the post-cleanup exact-byte check reported 5,761,757,184 bytes available (91% used). The production database passed the read-only checks below and the service remained running.

Observed large consumers were conservatively classified:

| Consumer | Classification |
|---|---|
| Production DB/WAL/SHM and active release | `ACTIVE_PRODUCTION_REQUIRED` |
| Active rollback release and `pre_architecture_rollout_20260903T200737Z.sqlite` | `IMMUTABLE_ROLLBACK_REQUIRED` |
| `retention_20260902T133815Z.sqlite` research snapshot/archive | `RESEARCH_ARCHIVE_REQUIRED` |
| Other old releases/backups and `deploy-phase2c` copy | `UNKNOWN_DO_NOT_TOUCH` |

The deleted artifact was verified immediately before deletion:

- Path: `<PRIVATE_ADMIN_ROOT>/work/legacy-rollback-rehearsal-v2-20260905T054100Z/bot.sqlite`
- Classification: `TEMPORARY_REHEARSAL`
- Size: `3,566,133,248` bytes
- SHA-256: `729ce0004989770f58ac4207c098577dc9bd84b499d473d979661153004fb239`
- `realpath -e` resolved exactly beneath `<PRIVATE_ADMIN_ROOT>/work`.
- `lsof` reported no open handles.
- `result.json` was non-empty and preserved.
- Only that file was deleted; no DB, WAL, SHM, release, backup, archive, configuration, or environment file was removed.

The exact sizes of two earlier rehearsal copies are `HISTORICALLY_UNOBSERVABLE`; they are not converted to zero.

Initial production sizing used by the guard:

- DB: `3,576,197,120` bytes
- WAL: `14,106,912` bytes
- `/var/log`: `1,093,311,638` bytes
- WAL/log margin: `1,140,850,688` bytes (larger of `/var/log` and `4 × WAL`, rounded up to a 64 MiB boundary)
- Minimum reserve: `4,764,729,344` bytes

The runtime reserve is dynamic: `max(minimum_reserve, current_db_bytes + configured_wal_log_margin)`. `LOW_SPACE` is below that reserve; `CRITICAL` is exhausted bytes/inodes or an actual `SQLITE_FULL`.

## Failure episodes and recovery

### Episode 1

Window: `2026-09-04T07:34:35Z–07:35:32Z`.

- Three observable fast-monitor polls.
- Six failed strategy-observation writes (two strategies × three polls).
- Zero persisted incident-window observations, signals, or outbox rows.
- Exact main-cycle attempts: `HISTORICALLY_UNOBSERVABLE`.

### Episode 2

Window: `2026-09-05T05:38:12Z–05:40:52Z`.

- Three heartbeat-gated main-cycle attempts; zero completed scans.
- Nine observable empty-pool fast-monitor polls.
- Three `Runtime error in db-heartbeat:cycle` entries at approximately 05:38:41, 05:39:41, and 05:40:41 UTC.

Two prior rehearsal directories were removed at approximately 05:40:55Z. Writes recovered at 05:41:13Z (fast monitor), heartbeat at 05:41:41Z, and the first normal full cycle was observed at 05:44:44Z. No restart was used for recovery.

Signal-loss classification: `C. SIGNAL_PATH_DEFINITELY_BLOCKED_DURING_SQLITE_FULL`. The three episode-2 cycles stopped at the DB-heartbeat gate. Persisted data is internally complete (51/51 signals have provenance and `SENT` outbox rows), but incident-window completeness is not trusted.

## Database and service evidence

- `PRAGMA user_version`: `1`.
- Read-only `PRAGMA quick_check`: `ok`.
- Service: `active/running`.
- `NRestarts`: `0`.
- Main PID at inspection: `59867`.
- Exec start: `2026-09-03 20:17:11 UTC`.
- Heartbeat writes and scan-cycle writes resumed after cleanup.
- Current table checks showed 51 signals, 51 provenance rows, and 51 `SENT` outbox rows; signal/provenance/outbox gap query was zero.

SQLite is required before Telegram delivery. The source path is `ShortSignalBot.run_cycle` → `_evaluate_and_send_climax` / `_process_symbol` → `BotRepository.save_signal` (signal, provenance, and outbox transaction) → `_send_new_delivery` → `mark_delivery_sent`. Therefore a `SQLITE_FULL` before the transaction can prevent a valid signal from reaching Telegram even when an operational alert itself receives HTTP 200.

## Hotfix implementation

The incident branch was created from exact production base `2a88e7faa6bb32415636482b10e4652c1b529334` in an isolated worktree. It adds `app/infra/disk_capacity.py` with byte/percent/inode snapshots, dynamic reserve derivation, fail-closed copy/SQLite-backup preflight, nested `SQLITE_FULL` classification, and one global cooldown-limited in-memory incident tracker. Runtime checks run before the existing DB heartbeat; capacity warnings do not affect strategy decisions, and no disk telemetry is written to SQLite.

Tracked large-artifact paths now use the shared preflight: migration backups, baseline replay copies, V3 shadow snapshots, archive staging, and SQLite backup/rehearsal helpers. Preflight failure creates neither a destination nor a partial artifact. A static test rejects new unguarded `copyfile`, `copy2`, or SQLite `backup()` call sites.

## Verification

- Baseline at the exact production base: `350 passed, 7 skipped`.
- Focused incident/config/runtime/contracts/migrations suite: `89 passed`.
- Focused Ruff checks on changed application and script files: passed.
- `python -m compileall -q app scripts research`: passed.
- `git diff --check`: passed.
- Full suite: `361 passed, 7 skipped`.
- Production release/activation verification remains required before changing status to `RESOLVED`.

Hotfix release SHA: **record after commit and controlled production activation**. Its ancestry must begin at `2a88e7faa6bb32415636482b10e4652c1b529334`; no Phase 5 commit or strategy/configuration change is permitted.

## Closure gate

Close as `RESOLVED` only after free space exceeds the derived reserve, DB writes and `quick_check` are healthy, admin preflight and runtime incident state are active in production, full tests pass, the release SHA/base are recorded, and READY/`active/running`/PID change/heartbeat/scan/outbox/free-space/no-drift checks are complete. Disk exhaustion must not be simulated in production.
