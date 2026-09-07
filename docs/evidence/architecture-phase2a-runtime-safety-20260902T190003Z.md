# PHASE 2A RESULT

Timestamp: `2026-09-02T19:00:03Z`.

## Source

- Branch: `architecture/phase2a-runtime-safety`
- Base SHA: `5d7f40a9eb730f38ff8c84ec1e92d3228a7fdbe8`
- Final implementation SHA: `8416e84612e30685597e1cd5e8996e4c02a1860`
- Evidence metadata is committed after the implementation SHA and does not
  change runtime behavior.
- Production HEAD observed: `261646f7e7653957438dee54b38a23104f35c4ea`

## Regression baseline

- Phase 0 contracts: `28 passed`
- Full pre-change suite: `319 passed, 2 skipped`
- Compileall: PASS

## Inspected source facts

- `scripts/run_live.py` and `scripts/run_once.py` now route execution through
  `app.runtime.instance_fence.run_fenced` before `ShortSignalBot.from_files()`.
- `app/main.py`: `startup()` creates `_run_fast_monitor()` with
  `asyncio.create_task` only after notifier/storage/reconciliation/outbox work;
  `run_forever()` awaits each `run_cycle()` serially.
- `app/main.py`: the fast monitor reads a selected active candidate through
  `self._state_store.load(symbol)` and may call
  `_evaluate_and_send_climax(..., fast_monitor=True)` while a full scan holds a
  state returned by `load_active()` and later calls `state_store.save()`.
- `app/storage/repository.py`: event-state reads reconstruct `EventState`
  values from models and `upsert_event_state()` overwrites all persisted state
  fields for a symbol; there is no revision or compare-and-swap predicate.
- `app/infra/request_scheduler.py`: a semaphore and rate limiter constrain API
  calls, not symbol-state writes.
- Production unit was read-only over SSH and matches the example: `Restart=always`,
  `RestartSec=10`, `WorkingDirectory=/opt/short-telegram-bot-lite`,
  `ExecStart=/opt/short-telegram-bot-lite/.venv/bin/python scripts/run_live.py`,
  `User=root`, `KillSignal=15`, and `TimeoutStopUSec=1min 30s`. No unit change
  or restart was performed.

## Test evidence

The implementation is accompanied by `tests/test_runtime_fence.py` and
`tests/test_runtime_concurrency.py`.

- Fence tests exercise acquisition-before-entrypoint, logged non-zero rejection,
  fail-closed Windows behavior, and a Linux-only subprocess contention contract.
  The subprocess test waits for parent stdin instead of sleeping. On this
  Windows workstation the Linux subprocess cases are skipped; they remain
  required for Linux CI before deployment.
- The concurrency test uses explicit `asyncio.Event` barriers and detached state
  copies. It proves the current ordering `full read -> fast write -> stale full
  write`, and intentionally passes only when the final stored state is stale.

No ownership serialization was added. That race witness is evidence for Phase
2B, not a test expecting a Phase 2A failure.

## Runtime task graph

One main loop runs serial full scans; `startup()` creates one named
`climax-fast-monitor` task when enabled. Scanner `gather()` calls are bounded
request batches, while outcome and outbox workers are awaited synchronously from
the full scan. The fast monitor can overlap full scan at every network/DB await.

## Shared mutable state and DB writers

Shared in-memory objects are the active climax pool, monitor cursor/sequence,
scanner TTL caches, request scheduler semaphore/rate limiter, notifier started
flag, health/error counters, and detached `EventState` values. The repository
opens short-lived SQLAlchemy sessions with SQLite WAL and 5-second busy timeout;
event-state, signal/provenance, outbox, outcome, shadow, heartbeat, coverage,
and observation methods are the runtime DB writers. Phase 1 archive source reads
use `mode=ro` plus `PRAGMA query_only=ON`; disposable-copy cleanup is isolated.

## Race analysis

`full read → await → fast read/write → await → stale full write` is classified
`POSSIBLE_RACE_SIGNAL_IMPACT`; the deterministic witness passes with the stale
state as the final value. No state fix is included.

## Single-instance fencing

Linux `fcntl.flock` fence: IMPLEMENTED. Same-path second process: blocked by the
Linux contract test (not executed on this Windows workstation). Owner exit:
kernel lock is reacquirable; lockfile pathname may remain. Fence failure occurs
before bot construction, DB writes, Telegram initialization, or background task
creation. Windows real entrypoints fail closed.

## Final verification

- Contracts: `28 passed`.
- Targeted Phase 2A tests: `5 passed, 3 skipped` (Linux subprocess cases skipped
  on Windows).
- Full suite: `324 passed, 5 skipped`.
- `python -m compileall -q app tests scripts`: PASS.
- Changed-scope Ruff: PASS.
- Whole-scope Ruff: 18 pre-existing violations outside the Phase 2A changed
  files; no changed-scope violations.
- `git diff --check`: PASS.

## Startup schema mutation audit

Found runtime mutations: `Base.metadata.create_all`, SQLite `ALTER TABLE ADD
COLUMN`, conditional `CREATE INDEX`, enriched signal unique-index repair, and
`__db_heartbeat` create/update. Count: 5 mutation families; none removed.

## Recovery contract

Outbox semantics are at-least-once with 120-second leases and retry/dead-letter
transition after five attempts. Event state is fully persisted but in-memory
candidate pool is reconstructed with rescan. Target explicit migration and
schema-validation ordering remains Phase 2B work.

## Production behavior assessment

TRADING BEHAVIOR CHANGED: NO
DB SCHEMA CHANGED: NO
PRODUCTION MODIFIED: NO

## Final classification

`B. SHARED_WRITER_RACE_PROVEN`

NEXT: `PHASE_2B_SYMBOL_STATE_OWNERSHIP_FIX`
