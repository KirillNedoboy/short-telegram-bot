# PHASE 1B RESULT

Status: BLOCKED before archive publication, backup, or production DELETE.
Run completed: 2026-08-28T13:14:21Z.

## Production before

- Host: `lucky-white.ptr.network` (`138.124.108.146`), accessed as `root` with the explicit `id_ed25519_138.124.108.146` identity and `IdentitiesOnly=yes`.
- HEAD: `261646f7e7653957438dee54b38a23104f35c4ea`.
- Existing checkout status was preserved exactly:
  ` M config.yaml`, `?? artifacts/`, `?? backups/`, `?? clean_epoch_P0_CLEAN_SCHEDULER_V1.json`, `?? config.yaml.pre_shadow_v2_rollback_`, `?? docs/evidence/`, `?? docs/research/`, `?? forensic_pre_clean_20260817T205952Z/`.
- `config.yaml` SHA-256: `24bce4ca7dce59354cb8b22b581528daa9889cc66003a17c7500f727d3d515e6`.
- Service: `active/running`, PID `271637`, `NRestarts=0`, `ExecMainStatus=0`.
- DB: `<APP_ROOT>/data/bot.sqlite`; before size `2,162,802,688` bytes; WAL `14,745,512` bytes; filesystem free `10,286,538,752` bytes.
- Initial production DB checks: `query_only=1`, `journal_mode=wal`, `user_version=0`, `integrity_check=ok`.

## Admin tooling

- Tooling SHA: `ab4fd795e6d91885aee07e9538fea45d28c396d2`.
- Release: `<PRIVATE_ADMIN_ROOT>/releases/ab4fd795e6d91885aee07e9538fea45d28c396d2`.
- `current` remained an admin-only symlink to that release.
- Isolated `.venv-research` import/path checks and the Phase 0/archive/full test gates were already PASS from the Phase 1 safe deploy.

## Inventory

Fresh admin inventory reported 31 tables, 0 `UNCLASSIFIED`, and 20 `RESEARCH_APPEND_ONLY` tables. The research-table logical row total at the final inventory observation was `3,675,977`. Protected baseline counts were `signals=19`, `signal_provenance=19`, `signal_outcomes=19`, `telegram_delivery_outbox=19`, and `event_states=104`.

Research data was still actively changing during observation: for example, `market_coverage_ledger` had `2,571,955` rows, `market_scan_symbol_results` had `827,799`, and `climax_monitor_events` had `74,180`. The inventory source observation reported DB SHA-256 before/after as the same value (`301b06ad8837a18b505244eb800df5dbcc04e53dafaca4471a1ccda85c6d79b9`) and `source_unchanged=true` for that read-only observation.

## Safe cutoff derivation

No defensible production DELETE cutoff was derivable. The checked-in policy is explicitly provisional and contains no numeric retention window. Current lifecycle evidence also prevents treating all old timestamped rows as terminal:

- `event_states`: `pump_detected=35`, `short_zone_active=10`, `expired=59`.
- `climax_entry_attempts`: `BREAKDOWN_PENDING=93`, `SHADOW_ACTIONABLE=23`, `RETEST_IN_PROGRESS=8`; 101 rows still had no `attempt_closed_at`.
- `current_root_outcomes`: `DATA_GAP=185`, `PARTIAL=7`, `MATURE=25`; some rows had future `outcome_next_due_at` values.
- `root_detector_shadow_v2_outcomes`: `DATA_GAP=617`, `PARTIAL=21`, `MATURE=320`; future next-due work was present.
- `strategy_observations`: `incomplete=50`, with `outcome_next_attempt_at` scheduled for retry.

These are active, pending, incomplete, or not-yet-mature identities covered by the hard rule to retain. No table received `DELETE_ELIGIBLE=YES`.

## Dry-run

Production dry-run selection was not executed because the only available cutoff would have been an invented numeric policy. The Phase 1 CLI was inspected and has no production DELETE mode; `simulate_cleanup_on_copy` is restricted to a caller-supplied disposable copy. Therefore `TOTAL_DELETE_ROWS=0` by gate, not by an unverified selection.

## Archives

- Archive publication: not started; no cutoff was safe to apply.
- Archived rows: `0`.
- Archive files: `0`.
- Archive bytes: `0`.
- Complete manifests: `0`.
- `<PRIVATE_ADMIN_ROOT>/research_archive/` remained empty.
- DuckDB parity and post-delete archive lookup: `N/A` because no authoritative production archive was published and no rows were deleted.

## Forensic linkage

No delete approval table could be formed. Active/pending outcome and scheduler evidence above is the reason for retaining all candidate identities. No protected identity was selected or modified.

## Backup

No pre-delete SQLite online backup was created because the first DELETE gate was not reached. Existing production backups were not touched or removed. This is not classified as a backup failure because no DELETE was authorized.

## Delete approval table

No rows approved:

| Table set | Safe cutoff | Rows to delete | Archive verification | Active reference check | Backup | Approved |
|---|---|---:|---|---|---|---|
| All research tables | NONE | 0 | NOT RUN | BLOCKED by active/pending lifecycle | NOT REQUIRED | NO |

## Deleted rows

- Per-table deleted research rows: `0`.
- Batches: `0`.
- Protected production data deleted: `0`.
- No SQL `DELETE`, `UPDATE`, `TRUNCATE`, `DROP`, checkpoint, `VACUUM`, migration, Telegram, systemd, or service restart command was issued.

## Runtime health

- Runtime DB errors during rollout: `0` observed.
- Service remained `active/running` with PID `271637` and `NRestarts=0`.
- No runtime restart or administrative write occurred.

## DB integrity after

- Full read-only `PRAGMA integrity_check`: `ok`.
- Final read-only `PRAGMA quick_check`: `ok`.
- Final `query_only=1`, `journal_mode=wal`, `user_version=0`.
- Protected counts remained `19/19/19/19/104` for `signals`, `signal_provenance`, `signal_outcomes`, `telegram_delivery_outbox`, and `event_states`.
- Final DB size observed: `2,163,261,440` bytes; the logical/file growth is attributable to the continuously running bot, not this admin run.

## Protected data proof

The archive tool only opens the source with SQLite `mode=ro` and `PRAGMA query_only=ON`. It has no production cleanup operation. Protected table classifications were not passed to archive or delete selection.

## Archive lookup after delete

Not applicable: no archive publication and no delete.

## Backup lookup

Not applicable: no new backup was created and no existing backup was changed.

## Disk result

- Free before: `10,286,538,752` bytes.
- Free after: `10,284,167,168` bytes.
- Archive growth from this run: `0` bytes.
- Existing `<APP_ROOT>/backups` was left untouched.

## Growth projection

This run does not establish a retention rate because no rows were archived or deleted. The inventory demonstrates ongoing append growth and should be used for a future measured retention-policy decision.

## Trading behavior

CHANGED: NO

Production HEAD, config hash, checkout state, service state/PID/restart count, schema version, and DB journal mode were preserved. Observed row growth is runtime activity and is not treated as an admin write.

## Final classification

`C. RETENTION_POLICY_NOT_MATURE`

No defensible safe cutoff exists in the current provisional policy/lifecycle state. Keep the admin tooling and refine/approve a measured retention policy before a future Phase 1B run.

NEXT: `KEEP_ARCHIVE_AND_REFINE_RETENTION_POLICY`
