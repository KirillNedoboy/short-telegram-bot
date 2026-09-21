# Architecture Phase 1C — Retention Policy Maturation Evidence

Date: 2026-08-28 15:05:28 UTC
Policy: `phase1c-v1`
Scope: offline/admin retention evaluation and safe release preflight. No production DELETE, VACUUM, migration, schema/config/strategy change, service restart, Telegram action, or archive publication was performed.

## Result and classification

Policy maturity classification: **B. `RETENTION_POLICY_MATURE_NO_DELETE_COHORT_YET`**.

The lifecycle contract and dependency graph are complete, all observed tables
are classified, and no unknown rows were found. The default policy intentionally
has no numeric hot window, so the first production run produced no delete
cohort. The admin activation gate was not promoted to a deployment PASS because
the continuously running bot changed the live SQLite file during the long
read-only scan (`source_unchanged=false`). The new admin symlink was therefore
atomically restored to its previous target, as required for a post-activation
failure. This is not treated as an admin write or a trading/runtime change.

## Source and deterministic package

- Branch: `architecture/phase1-research-archive`.
- Initial Phase 1C source commit used for the production smoke: `dd761486bc6ca566e3ce524321dd56db8bde23b7`.
- Final defensive source commit: `d03d8fbdbfa838323d02eebd96e23b28b34c53c3`.
- Initial smoke archive: 170 tracked files, SHA-256 `96f9da48dd717687b237db81358d57e9f6eb795766db6b8fbd926e605c9ac42e`.
- Final defensive archive: 171 tracked files, SHA-256 `0f9a70fd0273760da1aa2174c8df81623d99f2e80a0c6668034326a914f2f922`.
- Representative hashes were verified for `app/research/archive.py`,
  `scripts/archive_research.py`, and `requirements-research.txt`.
- Bundle scan found no `.git`, `.env`, credentials, private keys, databases,
  caches, or untracked `evidence/` artifacts.
- Initial smoke release: `<PRIVATE_ADMIN_ROOT>/releases/dd761486bc6ca566e3ce524321dd56db8bde23b7`.
- Final verified release: `<PRIVATE_ADMIN_ROOT>/releases/d03d8fbdbfa838323d02eebd96e23b28b34c53c3` (non-current after the stability gate failure).
- Previous release `ab4fd795e6d91885aee07e9538fea45d28c396d2` was not modified.
- Isolated release venv: `.venv-research`; `include-system-site-packages=false`.
  PyArrow/DuckDB were installed only there. Import paths resolved inside the
  new admin release and the production checkout was absent from `sys.path`.

## Production preflight and final invariants

| Invariant | Before / final observation |
|---|---|
| Production HEAD | `261646f7e7653957438dee54b38a23104f35c4ea` / unchanged |
| Production status | pre-existing `config.yaml` modification plus known operational artifacts; unchanged |
| `config.yaml` SHA-256 | `24bce4ca7dce59354cb8b22b581528daa9889cc66003a17c7500f727d3d515e6` / unchanged |
| Service | `active/running`, `MainPID=271637`, `NRestarts=0`, `ExecMainStatus=0` |
| DB | `journal_mode=wal`, `user_version=0`, `query_only=1` |
| DB integrity | read-only `PRAGMA integrity_check` = `ok`; quick check = `ok` |
| Disk | approximately `9.5 GiB` available on `/opt`, above 5 GiB gate |
| Admin `current` after rollback | `releases/ab4fd795e6d91885aee07e9538fea45d28c396d2` |

Operational counts observed before/final were `signals=19`,
`signal_provenance=19`, `signal_outcomes=19`, `event_states=105`. Earlier
`event_states=104` to `105` growth is attributable to the continuously running
bot and is observational, not an admin write.

## Policy and graph

The immutable JSON policy defines all 31 known tables. Categories are:

- A `OPERATIONAL_STATE`: 10 protected state/heartbeat/signal/root/attempt
  tables;
- B `OPERATIONAL_HISTORY`: runtime heartbeat history;
- C `RESEARCH_APPEND_ONLY_TERMINAL`: reject, monitor, coverage, scan-result,
  and audited mapping records;
- D `RESEARCH_WITH_MATURATION`: strategy, shadow, V2, episode, and current-root
  outcome lifecycle rows;
- E `RESEARCH_REFERENCED_BY_ACTIVE_STATE`: evaluations, observations, attempt
  events, scan aggregates, root links, and predicate snapshots;
- F `UNKNOWN`: fail-closed fallback for absent metadata, unsupported schema,
  missing identity, or unresolved dependencies.

The graph contains 22 deterministic edges and the production report marked it
complete. It includes signal/provenance/outcome/outbox/observation links,
evaluation and event/root/attempt references, episode and V2 outcome links,
rotation/cycle/result/coverage links, and legacy mapping/observation links.
Protected identity counts from the dry-run were: active events `2`, active
roots `435`, active attempts `105`, pending signal outcomes `0`, pending
strategy outcomes `214`, and pending scheduler outcomes `1508`.

The evaluator uses repository-compatible attempt terminal states, active event
state expiry, non-invalidated roots, scheduler due fields, and signal outcome
completion. `MATURE`/`complete` or explicitly proven terminal data-gap state is
required for outcome maturity. `PARTIAL`, `incomplete`, retryable `unknown`,
and `RETRYABLE_ERROR` remain protected. No default numeric hot window exists.

## Production retention dry-run

Command mode: `--retention-dry-run`, policy artifact `phase1c-v1`, literal
observation boundary `2026-08-28T15:00:49Z`, sample limit `30`.

Raw machine-readable evidence remains at:
`<PRIVATE_ADMIN_ROOT>/shared/evidence/dd761486bc6ca566e3ce524321dd56db8bde23b7/retention-dry-run-20260828T150049Z.json`.

| Aggregate | Count |
|---|---:|
| Tables | 31 |
| Rows evaluated | 3,781,469 |
| KEEP | 304,532 |
| ARCHIVE_ONLY | 3,476,937 |
| ARCHIVE_AND_DELETE_ELIGIBLE | 0 |
| UNKNOWN | 0 |
| Representative cases | 30 |
| Graph complete | true |
| `verification_status` | `DRY_RUN` |
| `query_only` | `1` |
| Archive output files before/after | `0 / 0` |

The source hash changed from
`1193b13b7a5d2bd3281a6bb1ff1ad59e02e9812cc47a32175917128f60ccef5b` to
`8735481f4d82f905246692446e69c4d408273acf05e2c5bc010e0491d72349bf` during
the scan. The CLI correctly returned a non-zero gate status rather than
claiming source stability. No DELETE-capable command was run.

The production smoke executed against the initial release. The final
`d03d8fb…` release contains only the subsequent schema fail-closed guard and
its regression test; it was independently installed and fully tested in its
isolated venv, but was not activated or run against production after the same
source-stability failure had already been established. The current symlink
remains on the prior verified admin release.

## Verification

- Local: contracts `28 passed`; archive/retention `31 passed`; full suite
  `326 passed`; compileall exit `0`; Ruff exit `0` on
  `app/research`, `scripts/archive_research.py`, and `tests/archive`.
- Initial admin release: contracts `28 passed`; archive/retention `31 passed`;
  full suite `326 passed` with 136 pre-existing NumPy deprecation warnings;
  compileall exit `0`; Ruff unavailable in the isolated venv.
- Final defensive admin release: contracts `28 passed`; archive/retention
  `32 passed`; full suite `327 passed` with 136 pre-existing NumPy deprecation
  warnings; compileall exit `0`; Ruff unavailable in the isolated venv.
- CLI `--help` exposed all retention flags.
- Production DB remained read-only; archive root remained empty.
- Production trading behavior, service state, configuration, schema, and
  database semantics were unchanged.

## Next action

`RERUN_PHASE_1C_READ_ONLY_SNAPSHOT_DURING_A_STABLE_DB_WINDOW`, then only after
an unchanged source snapshot and explicit policy evidence consider
`RERUN_PHASE_1B_CONTROLLED_RETENTION_ROLLOUT`. Phase 1B remains out of scope.
