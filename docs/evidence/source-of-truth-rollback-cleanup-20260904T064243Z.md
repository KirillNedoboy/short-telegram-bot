# Source-of-Truth / Rollback Cleanup — 2026-09-04

## Classification

`SOURCE CLEANUP: BLOCKED`

`LEGACY_ROLLBACK_REHEARSAL=LEGACY_ROLLBACK_NOT_SAFE`

The historical startup path was exercised against a SQLite Online Backup API
copy. It reached config loading, database open/schema handling, heartbeat and
persisted-state restore with Telegram and live-scan calls trapped. The run was
not promoted to `legacy-current` because startup reconciliation changed five
expired rows in `climax_entry_attempts`; the protected logical digest changed.
This is a fail-closed rehearsal result, not a production mutation.

## Local Git

- `MAIN_BEFORE`: `261646f7e7653957438dee54b38a23104f35c4ea`
- Explicit no-ff `MERGE_SHA`: `1f8cc9b62bd33f940d86e02a2bed2cbeca7e1287`
- `MAIN_SHA` (formatting-only follow-up): `247588ddf96de480e8ed95f4e892a42b2ab93a7c`
- `main` is clean and contains Phase 2B, Phase 2C implementation/docs,
  Phase 3, Phase 4 and both production-rollout evidence commits.
- Seven pre-existing untracked entries remain physically in place and are
  ignored only through repository-local `.git/info/exclude`.
- No push, PR, rebase, squash or history rewrite was performed.

## Verification

- Full pytest: `350 passed, 7 skipped`.
- Contracts: `28 passed`.
- Compileall: PASS.
- Ruff changed Python scope: PASS.
- Range and working-tree `git diff --check`: PASS after the standalone
  whitespace-normalization commit.

## Immutable legacy release

- Source commit: `261646f7e7653957438dee54b38a23104f35c4ea`.
- Release: `<PRIVATE_ADMIN_ROOT>/releases/261646f7e7653957438dee54b38a23104f35c4ea-legacy/`.
- Deterministic source archive SHA-256:
  `e8b11e88404717bee81bbc4a2c30ad4c01ade9acb3b7711e200c8cb8893304a9`.
- Release manifest was generated with source/file hashes, Python,
  requirements and pip-freeze hashes, and external config/.env/DB references;
  215 source files were sealed outside shared production resources.
- Historical requirements venv, compileall and entrypoint import passed.
- Existing production config loaded through explicit external paths without
  printing secrets.

## Rollback rehearsal

- Disposable DB copy was made with SQLite Online Backup API from a read-only
  production source URI.
- Telegram notifier and live scanner were trapped; autoexecution and
  derivatives were disabled; no production DB writable handle was opened.
- Captured DDL attempts (all on the disposable copy): four `CREATE INDEX IF
  NOT EXISTS` statements and creation of `__db_heartbeat`.
- `quick_check=ok`, `integrity_check=ok`, required schema compatible.
- Protected counts were unchanged, but `climax_entry_attempts` digest changed
  from `90569b108f2518b55d91dfbadc0efa0f52f144b5c75c6cd964db3e06be02f77c` to
  `e0ca6bd8f43b83853e45f8af56c96d71192c12df21823fa5070d220634287bae`.
- Therefore `legacy-current` remains `<APP_ROOT>` and was
  not repointed.
- Marker `LEGACY_CHECKOUT_NOT_ROLLBACK_SOURCE` was not asserted because the
  required rehearsal gate did not pass.

## Production invariants

- Active release remains `2a88e7faa6bb32415636482b10e4652c1b529334`.
- `current` was not changed.
- Service remained `active/running`, `MainPID=59867`, `NRestarts=0`;
  `ExecMainStartTimestamp=Thu 2026-09-03 20:17:11 UTC` and the invocation ID
  were unchanged in the post-rehearsal observation.
- Unit SHA-256:
  `6dada4137e82f713ff2f6e390e2e6cf35974b69cc967b9a3429c8d527257402e`.
- Production config SHA-256:
  `24bce4ca7dce59354cb8b22b581528daa9889cc66003a17c7500f727d3d515e6`.
- Production `.env` SHA-256:
  `a3d45490149154249795fc83fe6a08f3604b5b1a8ad3ada6e42408858996c51e`.
- Read-only production DB probe reported `user_version=1` and
  `quick_check=ok`; cleanup opened no writable production connection.
- `PRODUCTION_RESTARTED=NO`; `PRODUCTION_DB_MODIFIED_BY_CLEANUP=NO`;
  trading behavior unchanged.

## Next action

Do not use the dirty checkout as rollback source. Resolve the five historical
reconciliation mutations (or define an approved non-mutating legacy startup
mode), rerun the rehearsal to obtain `LEGACY_ROLLBACK_REHEARSAL=PASS`, then and
only then atomically repoint `legacy-current`.
