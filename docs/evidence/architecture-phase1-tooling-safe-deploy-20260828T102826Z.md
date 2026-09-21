# Phase 1 Tooling Safe Deploy Evidence

## Local source

- Branch: `architecture/phase1-research-archive`.
- Base HEAD before source commit: `a28ddf8b0ba0da28f8e875fcb891a3a21437165d`.
- `PHASE1_TOOLING_SHA`: `ab4fd795e6d91885aee07e9538fea45d28c396d2`.
- Source commit: `feat: add read-only research archive tooling`.
- Exactly 11 Phase 1 files were committed.
- Generated `evidence/phase1-*` Parquet/manifests remained known untracked artifacts and were excluded from the bundle.
- Local validation: 28 contract tests passed; 8 archive tests passed; full suite 303 passed; compileall passed; Ruff passed.

## Production before

- Host: `lucky-white.ptr.network` / `138.124.108.146`.
- Project: `<APP_ROOT>`.
- HEAD: `261646f7e7653957438dee54b38a23104f35c4ea`.
- Existing production status was preserved exactly:

```text
 M config.yaml
?? artifacts/
?? backups/
?? clean_epoch_P0_CLEAN_SCHEDULER_V1.json
?? config.yaml.pre_shadow_v2_rollback_
?? docs/evidence/
?? docs/research/
?? forensic_pre_clean_20260817T205952Z/
```

- `config.yaml` SHA-256: `24bce4ca7dce59354cb8b22b581528daa9889cc66003a17c7500f727d3d515e6`.
- Service: `active/running`, `MainPID=271637`, `NRestarts=0`, `ExecMainStatus=0`.
- Root filesystem: 83% used, 10,751,627,264 bytes available.
- DB: `query_only=1`, `journal_mode=wal`, `user_version=0`, `integrity_check=ok`.
- Operational counts: `signals=19`, `signal_provenance=19`, `signal_outcomes=19`, `event_states=104`.

## Admin release

- Release: `<PRIVATE_ADMIN_ROOT>/releases/ab4fd795e6d91885aee07e9538fea45d28c396d2`.
- Stable current symlink: `<PRIVATE_ADMIN_ROOT>/current`.
- Research output root: `<PRIVATE_ADMIN_ROOT>/research_archive/`.
- Bundle: 165 tracked files, 165 extracted files.
- Bundle SHA-256: `b7519c6ba4fa1100fa69fec08d85faa3af25bb3708879ffa7fc6da20dc979d38`.
- Representative hashes matched local manifest; forbidden paths found: 0; generated evidence packaged: `false`.
- Research venv: `<PRIVATE_ADMIN_ROOT>/releases/ab4fd795e6d91885aee07e9538fea45d28c396d2/.venv-research`.
- Installed research dependencies: PyArrow 25.0.1 and DuckDB 1.5.5.
- `include-system-site-packages=false`.
- `app.research.archive` imported from the admin release; production checkout was absent from `sys.path`.

## Dependencies

- Installed in the isolated research venv only from `requirements.txt` and `requirements-research.txt`.
- `pip freeze` recorded at `<PRIVATE_ADMIN_ROOT>/shared/evidence/ab4fd795e6d91885aee07e9538fea45d28c396d2/pip-freeze.txt`.
- Ruff was not installed in the server venv; local Ruff validation passed.

## Tests

- Phase 0 contract tests: **28 passed**.
- Phase 1 archive tests: **8 passed**.
- Full server suite: **303 passed**, 136 pre-existing NumPy deprecation warnings.
- Server compileall: **PASS**.
- Module-form CLI help: **PASS**.
- Direct file-form CLI required explicit `PYTHONPATH` to expose the release root; the final smoke used that explicit root and module-form help also passed. No source change was made for this invocation detail.

## Production read-only smoke

- Inventory: **PASS**.
- Tables: 31 total; 20 research/audit; 9 operational-critical; 0 unclassified.
- Inventory DB contract: `query_only=1`, `journal_mode=wal`, `source_unchanged=True`.
- Bounded dry-run: **PASS**, table `reject_stats`, selected rows `2389`, status `DRY_RUN`.
- Research output files after dry-run: 0.
- Smoke evidence: `<PRIVATE_ADMIN_ROOT>/shared/evidence/ab4fd795e6d91885aee07e9538fea45d28c396d2/`.
- No archive publication, backup, DELETE, VACUUM, checkpoint, migration, Telegram, or systemd mutation was executed.

## Production after

- HEAD: `261646f7e7653957438dee54b38a23104f35c4ea`.
- Status: identical to the before snapshot.
- `config.yaml` SHA-256: `24bce4ca7dce59354cb8b22b581528daa9889cc66003a17c7500f727d3d515e6`.
- Service: `active/running`, `MainPID=271637`, `NRestarts=0`, `ExecMainStatus=0`.
- DB: `query_only=1`, `journal_mode=wal`, `user_version=0`, `integrity_check=ok`.
- Operational counts: `signals=19`, `signal_provenance=19`, `signal_outcomes=19`, `event_states=104`.
- Admin current resolves to the exact release SHA.
- Research output files: 0.

## Production modification

- Live checkout changed: **NO**.
- Service restarted: **NO**.
- DB written: **NO**.
- Trading behavior changed: **NO**.
- Live production venv changed: **NO**.

## Classification

**A. TOOLING_SAFE_DEPLOY_PASS**

## Next

`RERUN_PHASE_1B_CONTROLLED_RETENTION_ROLLOUT`

Phase 1B was not started automatically.
