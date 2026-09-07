# Production Architecture Rollout — 2026-09-03

## RESULT

`PRODUCTION_ARCHITECTURE_ROLLOUT_PASS`

## Release

- RELEASE_SHA: `2a88e7faa6bb32415636482b10e4652c1b529334`
- Source branch: `architecture/phase4-baseline-source-faithful-replay`
- Source bundle SHA-256: `08b48b926f577c56e4009e4ab5101617af872a31dca8622e31eea36a7477dd78`
- Active release: `/opt/short-telegram-bot-lite-admin/releases/2a88e7faa6bb32415636482b10e4652c1b529334`
- Legacy rollback target: `/opt/short-telegram-bot-lite`

## Preflight

- Worktree clean; Phase 2B, Phase 2C implementation/documentation, Phase 3 and Phase 4 ancestry verified.
- Local full suite: `350 passed, 7 skipped`.
- Local contracts: `28 passed`.
- Local Phase 2–4 targeted suite: `25 passed, 4 skipped`.
- Ubuntu release full suite: `353 passed, 4 skipped`.
- Ubuntu contracts: `28 passed`.
- Ubuntu targeted Phase 2–4 suite: `28 passed, 1 skipped`.
- `compileall`, Ruff and `git diff --check`: PASS.
- Production config SHA-256: `24bce4ca7dce59354cb8b22b581528daa9889cc66003a17c7500f727d3d515e6`.
- Production config validated by the new parser; three strategies, Grade C `watch_only`, watch-send disabled, Grade C send disabled, and live delivery flags unchanged.
- Disk cleanup removed only the two authorized Phase 2C rehearsal SQLite copies; backups, releases, snapshots, archives and the pre-Phase2C backup were preserved.

## Backup

- Path: `/opt/short-telegram-bot-lite-admin/backups/pre_architecture_rollout_20260903T200737Z.sqlite`
- Size: `3,477,221,376` bytes.
- SHA-256: `a971e56fda1b59ce1ab580c2dcf5aa42eb4b8f94caeeac388cd4b87c138bbfbf`.
- Created with SQLite Online Backup API while the service was active.
- `quick_check=ok`, `integrity_check=ok`, `user_version=1`.

## Migration

- Observed production state was already V1, from the earlier Phase 2C adoption.
- New release `--plan --include-shadow-v2`: `NO_MIGRATIONS_NEEDED`, version 1.
- New release `--verify --include-shadow-v2`: PASS.
- No `--apply` was run and no schema migration occurred in this rollout.

## Protected data

Fresh-backup primary keys were fully preserved after stop and before switch:

| Table | Rows/keys | Missing keys |
| --- | ---: | ---: |
| signals | 49 | 0 |
| signal_provenance | 49 | 0 |
| signal_outcomes | 49 | 0 |
| event_states | 135 | 0 |
| telegram_delivery_outbox | 49 | 0 |
| climax_root_events | 735 | 0 |
| climax_entry_attempts | 1,831 | 0 |

## Atomic deployment

- OLD release before switch: `/opt/short-telegram-bot-lite` was the running legacy checkout; the administrative `current` link was preserved as an existing release reference.
- NEW release: `current -> releases/2a88e7faa6bb32415636482b10e4652c1b529334`.
- systemd now executes through `/opt/short-telegram-bot-lite-admin/current/.venv/bin/python` and the release `scripts/run_live.py`.
- `WorkingDirectory`, root user, restart policy, environment and production config/DB paths were preserved.
- `daemon-reload` completed successfully.

## Startup

- STARTING/RECOVERING completed by the release startup contract.
- READY: `2026-09-03 20:17:14 UTC`.
- New PID: `59867`.
- `NRestarts=0`; service active/running.
- State restore, lease reconciliation, market readiness and fast-monitor registration completed before READY.

## InstanceFence

- Second isolated invocation with the same identity exited `1`.
- Result: `SECOND_INSTANCE_BLOCKED` with `Runtime fence unavailable`.

## Symbol ownership

- `SymbolMutationCoordinator` is present in the active release and no symbol ownership/reentrancy errors occurred during observation.

## Scan health

- Cycle 1: `2026-09-03 20:21:06 UTC`, shortlist 100, symbols 100, signals 0, outcomes 69.
- Cycle 2: `2026-09-03 20:25:38 UTC`, shortlist 100, symbols 100, signals 0, outcomes 53.
- Additional cycle 3 completed at `2026-09-03 20:30:21 UTC` with shortlist 100, symbols 100, signals 0, outcomes 75.
- One Bybit API rate-limit response was retried after the client wait interval; the cycle completed successfully and no restart loop, traceback, DB lock storm or critical runtime error occurred.

## DB after

- `user_version=1`.
- `schema_version=191` before switch and after both cycles.
- `quick_check=ok` at `2026-09-03 20:26:54 UTC`.
- WAL size: `11,218,792` bytes.
- Outbox: `SENT=49`; no stale CLAIMED or DEAD surge.
- Runtime DDL: `0` observed by unchanged schema_version and validation-only runtime contract.

## Trading invariants

- Strategies: exactly 3 — `BASELINE_PULLBACK`, `VOLUME_CLIMAX_UNWIND`, `LOW_VOLUME_EXTENSION_FAILURE`.
- `ROOT_DETECTOR_SHADOW_V2`: shadow/research-only.
- AUTOEXECUTION: OFF.
- Thresholds, gates, scores, grades, admission, dedupe, liquidity rules and Telegram semantics unchanged.
- Trading behavior changed: NO.

## Rollback

- Required: NO.
- Fresh verified backup retained for rollback.
- Atomic rollback target retained at `/opt/short-telegram-bot-lite-admin/legacy-current`.

## Final classification

`PRODUCTION_ARCHITECTURE_ROLLOUT_PASS`

The Phase 4 architectural runtime is active, READY, V1-validated, protected data is preserved, and two healthy scan cycles completed without behavior drift.
