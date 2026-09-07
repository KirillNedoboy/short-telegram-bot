# Architecture Phase 2C evidence — 2026-09-03T17:30Z

Classification: `A. SYMBOL_STATE_OWNERSHIP_FIX_PASS` / migrations and startup
hardening complete. No production deployment or production migration was run.

## Source and implementation

- Branch: `architecture/phase2c-migrations-recovery`
- Base SHA: `bd722c30db51237e3bb4013a6551ac34cdc938f8`
- Implementation SHAs: `82aba02`, `ba4dd5e` (final implementation)
- Documentation commit: this commit
- Runtime strategies, thresholds, admission/dedupe, root/outcome semantics,
  InstanceFence and SymbolMutationCoordinator were preserved.

## Validation

- Full suite: `336 passed, 5 skipped`.
- Migration/startup targeted tests: `9 passed`.
- Existing runtime concurrency/fence/flow and archive/retention set: `61 passed,
  4 skipped`.
- `compileall app scripts tests`: PASS.
- Ruff on changed code: PASS.
- `git diff --check`: PASS.
- Empty bootstrap, V0 adoption, invalid contract, future version, rollback,
  optional V2 pair, idempotency, read-only validator and zero-runtime-DDL
  startup checks: PASS.

The Phase 2B race witness remains synthetic, as documented previously; it does
not execute the real full-scan and fast-monitor loops.

## Migration rehearsal

Canonical source:
`/opt/short-telegram-bot-lite-admin/shared/snapshots/retention_20260902T133815Z.sqlite`.
It was copied to a disposable admin work directory and its SHA-256 matched:
`0258ad4475753d2e8afadfcf2c7b788b8bfe87cf2e97919f67c7249fccf9a007`.

Rehearsal result: structurally valid legacy V0 → explicit adoption → V1;
`--verify` PASS; second `--plan` returned `NO_MIGRATIONS_NEEDED`.
Protected logical counts and digests before/after were identical:

| Table group | Count | Digest |
|---|---:|---|
| signals | 40 | `e52993c056b1ca41a50af31b9393c90800e8b3d750a4c81a94a716cb82477824` |
| signal_provenance | 40 | `deb70d7cb1026176520fa2e52484f9b2a8d13c9681ef137c51239cbead91de62` |
| signal_outcomes | 40 | `95ad20a5cba5bc0702869ccc9f22126d0e5d722f6955705a7ab338c9aba49318` |
| event_states | 124 | `c6d553259f4ec8ae87542aceeffc041625c2439d57a5a663f9d2089811529e96` |
| telegram_delivery_outbox | 40 | `91fb134d76a2e6ef8a6c4f9af7025a03d2bb8433a0c06b62b624c9ca8bf5ac01` |
| climax_root_events | 648 | `74de7b208517e98dcbd6c872938e5d953ae9eb9bd310d7cae6c626558b6cb0d7` |
| climax_entry_attempts | 1611 | `8793552317a734b75e01689256531afd4ec60ffe7088f56067566f2bb112f393` |
| climax_entry_attempt_events | 22409 | `bd065c7d8b654008adc29d366f7633f0433fa5a818f831774a063104fccb29d4` |
| root_detector_shadow_candidates | 1832 | `7585276f04be313fcdcfc96a03f4d0dbf3ccd4876d9efafd7c01cd69b97d76d2` |
| current_root_outcomes | 433 | `219e12d12c89ebcc262929e41e8b53ffd0f2013f4fc786cc73580920507e52b8` |

No row contents were printed. The canonical snapshot remained unchanged.

## Production read-only evidence

Production before and after:

- HEAD: `261646f7e7653957438dee54b38a23104f35c4ea` (unchanged).
- `user_version`: `0` (unchanged); schema is structurally current but requires
  explicit V0 adoption.
- Production `--plan`: exit `2`, `EXPLICIT_APPLY_REQUIRED` for version 0.
- Production `--verify`: exit `2`, version 0, no structural errors.
- SQLite read-only `quick_check`: `ok`.
- Service: `active/running`, PID `33321`, `NRestarts=0`, `ExecMainStatus=0`.
- Production user changes and untracked files were preserved byte-for-byte by
  the read-only checks.

## Disk cleanup

Three explicitly approved old backup files were copied locally, verified by
size, SHA-256 and read-only `PRAGMA quick_check`, then re-hashed on Ubuntu
immediately before deletion. Only those three exact files were removed:

| File | Size | SHA-256 |
|---|---:|---|
| `bot.sqlite.pre_p0_20260816T210054Z` | 3866984448 | `9d7400629d3ef5e65174e1a774c29759b105477ea13ae299e06cdc38f60f1e13` |
| `bot_pre_f89a131_20260813T201252Z.sqlite` | 3203989504 | `ff429c2e60c7d063037508c9df9e243b60b61d360c7fae522a3f6c0dd8f6e397` |
| `bot_pre_7124868_20260813T200447Z.sqlite` | 3202719744 | `6f05dee6a26329002e4de301184bcba853b0ad117530b740c17a1f448fe6e5a5` |

Local copies and manifest remain under the Codex artifacts directory. Free
space increased from approximately 3.55 GB to 13.58 GB immediately after
cleanup; the disposable rehearsal later consumed space, leaving 7.27 GB.

## Scope and next step

Production runtime and production SQLite were not migrated or deployed. Future
deployment remains: backup → stop service → explicit migrate → verify → deploy
code → start → confirm READY, with rollback from the verified backup if needed.

Next: `READY_FOR_PHASE_3_REPLAYBUNDLE_FOUNDATION`.
