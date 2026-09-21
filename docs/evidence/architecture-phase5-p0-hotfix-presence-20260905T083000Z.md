# P0 hotfix presence gate before Phase 6

- Evidence time: 2026-09-05T08:30:00Z
- Original Phase 5 production: `eff29afac127511d02c0b1479744ec7b02fc6074`
- Original P0 hotfix: `6f74fafce5ee7f0fc40389786e102d7f15bd8182`
- Common ancestor: `2a88e7faa6bb32415636482b10e4652c1b529334`
- Initial classification: **C. HOTFIX_ABSENT_FROM_PHASE5_RELEASE**

## Content and patch equivalence

The exact P0 delta from common ancestor changed 15 paths: `app/infra/disk_capacity.py`, runtime/config/repository and observation handling, three archive/replay/migration call sites, config examples, the incident evidence document, and `tests/test_disk_capacity.py`, `tests/test_runtime_flow.py`, and `tests/test_config_runtime.py`.

`git cherry eff29afac127511d02c0b1479744ec7b02fc6074 6f74fafce5ee7f0fc40389786e102d7f15bd8182` returned `+ 6f74faf…`; the P0 patch was not independently present in Phase 5. The P0 delta patch-id was `3b33173803789be7fa446b687d9edb23482de042`.

P0 was integrated by normal merge (`187c0b4`, parent `6f74faf…` and Phase 5), then finalized as combined release `d7d54fa8af070241711d5072cffbf8208f482b5d` with a direct migration-script bootstrap fix.

## Required protections

All are PRESENT in `d7d54fa…`: filesystem byte/percent/inode snapshots; dynamic reserve; SQLite/copy preflight; `SQLITE_FULL` classification; cooldown/dedup tracker; runtime capacity check before DB heartbeat; guarded copy/backup/rehearsal call sites; no disk telemetry writes to SQLite; recovery alerts/state; and corresponding tests.

## Gates and ancestry

- `eff29af…` ancestor of `d7d54fa…`: exit 0.
- `6f74faf…` ancestor of `d7d54fa…`: exit 0.
- Combined local full suite: `386 passed, 7 skipped`.
- Combined Ubuntu release suite: `389 passed, 4 skipped`.
- compileall, Ruff on all changed Python files, and `git diff --check`: PASS.
- Strategy config fingerprint unchanged: `d35e71128fcae2a02746fa46d7ada459c708eee83642c6304b393d4f089d661c`.
- Migration plan: `NO_MIGRATIONS_NEEDED`; verify: valid, no missing/unexpected schema objects.

## Production runtime

- Current release: `<PRIVATE_ADMIN_ROOT>/releases/d7d54fa8af070241711d5072cffbf8208f482b5d`.
- Service: `active`, `READY`, MainPID `108366`, `NRestarts=0`; current resolves to combined release.
- Disk guard is active before DB heartbeat and reports: free bytes `3,568,746,496`, free percent `5.64`, free inodes `3,142,784`, DB bytes `3,599,515,648`, WAL bytes `27,068,432`, dynamic reserve `4,764,729,344`, state `LOW_SPACE`.
- Read-only SQLite `PRAGMA quick_check`: `ok`.
- WS: `252/252` topics acknowledged (126 eligible symbols), `parse_errors=0`. Expected Bybit sequence/timestamp regressions were logged and did not alter REST authority; one controlled universe-resubscribe reconnect completed at `08:29:57Z`–`08:29:59Z`, with no stale/disconnect loop.
- REST: healthy cycle completions at `08:23:55Z` and `08:28:55Z`; DB heartbeat remained successful. A transient Bybit REST rate-limit retry (`10006`) was observed during a later fast-monitor poll and recovered without a strategy error.
- Strategy behavior unchanged; AUTOEXECUTION remains OFF; no rollback performed.

## Gate outcome

The P0 protections are now present and deployed, but the strict production acceptance item `disk guard HEALTHY` is not met because the host is genuinely below the configured reserve. No DB cleanup, disk-exhaustion simulation, or destructive action was performed. Phase 6 remains blocked until free capacity is restored above reserve.
