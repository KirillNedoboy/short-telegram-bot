# Data Retention Policy

Status: **PROVISIONAL — Phase 1C policy maturation; production dry-run only**.

This policy separates operational SQLite state from immutable research evidence. Phase 1 performs no production cleanup, DELETE, TRUNCATE, DROP, VACUUM, ALTER TABLE, or migration. Numeric day values are intentionally not prescribed until observed growth, recovery drills, and archive verification provide evidence.

## Retention rules

- `OPERATIONAL_CRITICAL`: keep in active SQLite. Do not archive automatically and do not prune in Phase 1B without a separate recovery/audit decision.
- `OPERATIONAL_RECENT`: keep the current operational window in SQLite; archive only after a future measured window proves the rows are no longer required for health/recovery. **PROVISIONAL.**
- `RESEARCH_APPEND_ONLY`: archive after the row is mature and no longer being updated, using the read-only exporter, verified manifest, and immutable Parquet files. Cleanup eligibility is conditional on a verified archive and separate Phase 1B approval.
- `DERIVED_REBUILDABLE`: none are classified here. No table is assumed rebuildable without authoritative source evidence and a deterministic reconstruction proof.
- `signal_outcomes`, root outcome ledgers, and other mutable outcome rows are not archive-eligible until their outcome horizon is terminal and the archive captures the terminal value.
- `signals`, `signal_provenance`, and delivery history remain KEEP in active SQLite. Historical evidence must retain the link from signal identity to strategy/event/evaluation/provenance/outbox.
- SQLite DELETE does not shrink the file immediately. Free pages, `auto_vacuum`, VACUUM, and backup/restore compaction require a separate controlled maintenance plan.

## Table policy matrix

| Table | Classification | Active SQLite target | Archive policy | Cleanup eligibility | Minimum forensic retention | Reason |
|---|---|---|---|---|---|---|
| `__db_heartbeat` | OPERATIONAL_CRITICAL | KEEP_FOREVER_OPERATIONAL | Do not automate | Never in Phase 1B by default | Current runtime evidence | Singleton DB health probe |
| `event_states` | OPERATIONAL_CRITICAL | KEEP_FOREVER_OPERATIONAL | Do not automate | Never without recovery proof | Current and last known state | Live lifecycle continuity |
| `signals` | OPERATIONAL_CRITICAL | KEEP_FOREVER_OPERATIONAL | Optional separately verified copy; not automatic | KEEP | Signal lifetime | Canonical emitted signal identity |
| `signal_provenance` | OPERATIONAL_CRITICAL | KEEP_FOREVER_OPERATIONAL | Optional separately verified copy; not automatic | KEEP | Signal lifetime | Immutable branch/evaluation evidence |
| `signal_outcomes` | OPERATIONAL_CRITICAL | KEEP_FOREVER_OPERATIONAL | Only after terminal outcome and separate EvidencePack design | KEEP | Signal lifetime | Historical KPI and outcome link |
| `telegram_delivery_outbox` | OPERATIONAL_CRITICAL | KEEP_FOREVER_OPERATIONAL | Do not archive automatically before recovery review | KEEP | Delivery/retry lifetime | At-least-once recovery and audit |
| `watch_candidates` | OPERATIONAL_CRITICAL | KEEP_FOREVER_OPERATIONAL | No automatic archive in Phase 1 | KEEP until delivery/research review | Candidate lifetime | Pending non-actionable delivery and denominator |
| `climax_root_events` | OPERATIONAL_CRITICAL | KEEP_FOREVER_OPERATIONAL | Do not automate | KEEP while runtime uses root state | Root lifetime | Shadow/runtime causal identity |
| `climax_entry_attempts` | OPERATIONAL_CRITICAL | KEEP_FOREVER_OPERATIONAL | Do not automate | KEEP while attempts can recover | Attempt lifetime | Current lifecycle recovery |
| `runtime_heartbeats` | OPERATIONAL_RECENT | KEEP current singleton | Archive only as part of measured health snapshot | Future measured window | Incident window | Current liveness |
| `runtime_heartbeat_history` | OPERATIONAL_RECENT | KEEP measured recent window | Archive after measured operational window | After verified archive and recovery review | Incident/audit window | Lag, errors, and restart evidence |
| `climax_evaluations` | RESEARCH_APPEND_ONLY | KEEP recent operationally | Archive after evaluation maturity | After COMPLETE manifest + verification | FORENSIC_LONG_TERM | Exact live/shadow evaluator evidence |
| `volume_climax_observations` | RESEARCH_APPEND_ONLY | KEEP recent operationally | Archive after observation maturity | After verified archive | FORENSIC_LONG_TERM | Independent climax observation stream |
| `strategy_observations` | RESEARCH_APPEND_ONLY | KEEP recent operationally | Archive after outcome maturity | After verified archive | FORENSIC_LONG_TERM | Denominator, fingerprints, and outcomes |
| `climax_entry_attempt_events` | RESEARCH_APPEND_ONLY | KEEP recent operationally | Archive after attempt terminality | After verified archive | FORENSIC_LONG_TERM | Append-only lifecycle transitions |
| `climax_monitor_events` | RESEARCH_APPEND_ONLY | KEEP recent operationally | Archive after monitor event maturity | After verified archive | FORENSIC_LONG_TERM | Pool/concurrency/timing evidence |
| `market_coverage_ledger` | RESEARCH_APPEND_ONLY | KEEP recent operationally | Archive after scan rotation maturity | After verified archive | FORENSIC_LONG_TERM | Universe coverage denominator |
| `market_scan_cycles` | RESEARCH_APPEND_ONLY | KEEP recent operationally | Archive after cycle maturity | After verified archive | FORENSIC_LONG_TERM | Scan aggregate and latency evidence |
| `market_scan_rotations` | RESEARCH_APPEND_ONLY | KEEP recent operationally | Archive after rotation maturity | After verified archive | FORENSIC_LONG_TERM | Eligible-universe rotation evidence |
| `market_scan_symbol_results` | RESEARCH_APPEND_ONLY | KEEP recent operationally | Archive after rotation maturity | After verified archive | FORENSIC_LONG_TERM | Per-symbol failure/terminal evidence |
| `reject_stats` | RESEARCH_APPEND_ONLY | KEEP recent operationally | Archive after reject row maturity | After verified archive | FORENSIC_LONG_TERM | Rejection denominator and policy evidence |
| `root_detector_shadow_candidates` | RESEARCH_APPEND_ONLY | KEEP recent operationally | Archive after candidate outcome maturity | After verified archive | FORENSIC_LONG_TERM | Legacy detector forensic evidence |
| `root_detector_shadow_episodes` | RESEARCH_APPEND_ONLY | KEEP recent operationally | Archive after episode closure | After verified archive | FORENSIC_LONG_TERM | Cohort/episode identity |
| `root_detector_shadow_observations` | RESEARCH_APPEND_ONLY | KEEP recent operationally | Archive after observation maturity | After verified archive | FORENSIC_LONG_TERM | V1 detector time series |
| `root_detector_shadow_episode_outcomes` | RESEARCH_APPEND_ONLY | KEEP recent operationally | Archive after outcome terminality | After verified archive | FORENSIC_LONG_TERM | Detector outcome and method version |
| `root_detector_shadow_episode_root_links` | RESEARCH_APPEND_ONLY | KEEP recent operationally | Archive after link creation | After verified archive | FORENSIC_LONG_TERM | Episode/root lineage |
| `root_detector_shadow_legacy_mappings` | RESEARCH_APPEND_ONLY | KEEP recent operationally | Archive after migration audit | After verified archive | FORENSIC_LONG_TERM | Legacy mapping evidence |
| `root_detector_shadow_v2_roots` | RESEARCH_APPEND_ONLY | KEEP recent operationally | Archive after V2 root maturity | After verified archive | FORENSIC_LONG_TERM | Counterfactual root contract |
| `root_detector_shadow_v2_outcomes` | RESEARCH_APPEND_ONLY | KEEP recent operationally | Archive after outcome terminality | After verified archive | FORENSIC_LONG_TERM | V2 outcome evidence |
| `current_root_outcomes` | RESEARCH_APPEND_ONLY | KEEP until terminal outcome | Archive only after terminal outcome | After verified archive | FORENSIC_LONG_TERM | Live-root outcome treatment evidence |
| `current_root_predicate_snapshots` | RESEARCH_APPEND_ONLY | KEEP recent operationally | Archive after snapshot maturity | After verified archive | FORENSIC_LONG_TERM | Predicate-level detector evidence |

## Cleanup readiness gate

A future controlled rollout may consider a research table only when all conditions hold:

1. The exact source snapshot and cutoff are identified.
2. The source is opened `mode=ro` with `PRAGMA query_only=ON` for export.
3. The complete manifest hashes every file and records schema, null, numeric, timestamp, and identity checks.
4. Parquet row counts and query results match the source snapshot.
5. Signal/provenance/outbox dependencies are not lost.
6. A disposable-copy cleanup simulation records rows before/eligible/remaining and does not use VACUUM against production.
7. Recovery/audit approval explicitly authorizes the cleanup.

Phase 1 does not implement this rollout or any production delete command.

## Phase 1C lifecycle policy (`phase1c-v1`)

Phase 1C adds the packaged, immutable policy artifact
`app/research/retention_policy_v1.json` and the read-only evaluator in
`app/research/retention.py`. Every observed row is assigned exactly one of
`KEEP`, `ARCHIVE_ONLY`, or `ARCHIVE_AND_DELETE_ELIGIBLE`; the evaluator also
emits reason counts, dependency edges, deterministic hashes, and a bounded
diagnostic sample. The three-way invariant is `TOTAL = KEEP + ARCHIVE_ONLY +
DELETE_ELIGIBLE` for every classified table.

The policy covers all 31 known tables and uses these fail-closed classes:

- **A — `OPERATIONAL_STATE`**: heartbeat singleton, event state, signals,
  provenance, outcomes, outbox, watch candidates, root events, entry attempts,
  and current runtime heartbeat. These rows remain `KEEP`.
- **B — `OPERATIONAL_HISTORY`**: runtime heartbeat history. It requires a
  measured operational window and recovery review; it is not an automatic
  delete cohort.
- **C — `RESEARCH_APPEND_ONLY_TERMINAL`**: append-only reject, monitor,
  coverage, scan-result, and audited mapping records.
- **D — `RESEARCH_WITH_MATURATION`**: strategy observations, shadow
  candidates/episodes/outcomes, V2 outcomes, and current-root outcomes.
- **E — `RESEARCH_REFERENCED_BY_ACTIVE_STATE`**: evaluations, observations,
  attempt events, scan aggregates, root links, and predicate snapshots whose
  identities may still be referenced by active state.
- **F — `UNKNOWN`**: absent metadata, unsupported schema, missing identity, or
  unresolved dependency. These rows fail closed to `KEEP`.

Decision precedence is active event/root/attempt protection, pending signal
outcome, retryable or incomplete outcome, non-terminal maturation, archive-only
eligibility, then delete eligibility. Only `MATURE`/`complete`, or an
explicitly proven terminal state with no future scheduler work, can satisfy
outcome maturity. `PARTIAL`, `incomplete`, retryable `unknown`, and
`RETRYABLE_ERROR` remain protected. Active event states, non-invalidated roots,
non-closed attempts, scheduler due rows, and pending signal outcomes are
protected through the dependency graph and repository-compatible terminal
semantics.

There is deliberately no numeric default hot window. Without an explicit,
versioned hot-window input, a row can be `KEEP` or `ARCHIVE_ONLY`, never delete
eligible. Archive eligibility always precedes delete eligibility: a verified
archive identity and an explicitly expired hot window are both required before
`ARCHIVE_AND_DELETE_ELIGIBLE` can be returned. Phase 1C itself never executes
DELETE, VACUUM, cleanup, checkpoint, migration, backup, or archive
publication. Production is opened with SQLite `mode=ro` and
`PRAGMA query_only=ON`; the dry-run is observational and the supplied `as-of`
timestamp is not a retention or deletion policy cutoff.
