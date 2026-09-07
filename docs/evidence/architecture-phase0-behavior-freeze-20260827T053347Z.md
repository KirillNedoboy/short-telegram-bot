# PHASE 0 RESULT

**PASS** for the isolated behavior-freeze change set.

## Production/reference state

- Expected HEAD: `261646f7e7653957438dee54b38a23104f35c4ea`.
- Actual HEAD: `261646f7e7653957438dee54b38a23104f35c4ea`.
- Last commit: `261646f Downgrade low-volume extension gate to warning`.
- Production checkout pre-change working tree: existing untracked `artifacts/`, `docs/data_readiness_report.md`, and `docs/evidence/`; preserved and not modified.
- Isolated worktree: branch `architecture/phase0-behavior-freeze`, created from actual HEAD. Only Phase 0 documentation/tests are untracked there.
- Requested service: `short-telegram-bot-lite.service`.
- Service state: **UNAVAILABLE FROM THIS WORKSTATION**. `systemctl` is not installed on this Windows host, so `ActiveState`, `SubState`, `MainPID`, `NRestarts`, and `ExecMainStatus` could not be observed. No restart or production mutation was attempted.

## Existing tests before

- Command: `python -m pytest`
- Result: **267 passed**.
- Failures: 0.
- Warnings: none reported by the captured pytest output.
- Pytest duration: 30.07 seconds.

## Trading contracts frozen

### BASELINE_PULLBACK

- Inputs: fixed `SymbolFeatures`, `EventState`, `ShortZone`, `signal_time`, and `AppConfig`.
- State: only `PULLBACK_OBSERVED`/`SHORT_ZONE_ACTIVE` evaluation; expiry, age, zone, core filters, score, liquidity, squeeze, continuation, public-grade, and watch gates remain unchanged.
- Score: stretch + exhaustion + volume + event quality + pullback maturity + zone quality + derivatives bonus, less risk penalties, rounded/clamped 0–100; squeeze penalty remains mode-dependent.
- Grade: A >=80, B >=65, C otherwise.
- Admission: actionable `SignalDecision`; A/B only; `AGGRESSIVE` requires score >=75 plus strong rejection, otherwise `CONFIRM`; WATCH is non-actionable.
- Dedupe: event state signal ID plus `(symbol,event_id,strategy_subtype,model_version)` persistence identity; baseline model version `baseline-v1` and null subtype.

### VOLUME_CLIMAX_UNWIND

- Inputs: event state, features, 1m frame, and climax config; common metadata retains current closed-candle, volume-window, post-high, OI, and liquidity semantics.
- Hard gates: OI availability, price/OI acceleration veto, extreme volume, ret5/ret15 pump thresholds, rejection, entry distance, and climax liquidity.
- Score: five boolean gates ×15 +10, capped at 100.
- Grade: A >=85, B >=70, C otherwise; subtype/actionable requires no veto and score >=70.
- Dedupe: `(symbol,event_id,VOLUME_CLIMAX_UNWIND,climax-v1)` plus runtime event guard.

### LOW_VOLUME_EXTENSION_FAILURE

- Inputs: established event, equal volume windows, closed candles, age, event high/retest, extension, volume ratio/efficiency, post-high closes, OI, rejection, distance, and liquidity.
- Hard gates: comparable windows, maturity/age, no new high, low second-leg volume, breakout close, lower-high + failed retest, microstructure break, OI/squeeze/acceleration/rejection/distance/liquidity protections.
- Warning-only: `extension_below_threshold` remains data quality and does not veto.
- Score: seven boolean gates ×15 +10, capped at 100. Warning liquidity caps score at the climax minimum (70) and grade B in warn mode.
- Grade: A >=85, B >=70, C otherwise; missing/negative OI can force/downgrade to B.
- Current source fact frozen: `micro_break == close_below_breakout`; `microstructure_break_confirmed` is assigned from that value. No correction was made.
- Dedupe: `(symbol,event_id,LOW_VOLUME_EXTENSION_FAILURE,climax-v1)`; a new event ID remains an independent evaluation path.

## Global invariants

- Grade C does not become a public/actionable signal: **PASS**.
- Explicit bad liquidity does not become actionable: **PASS** for baseline and climax characterization paths.
- Dangerous low-volume squeeze remains a hard veto: **PASS**.
- Repeating the same fixed strategy input produces the same `StrategyDecision`/evaluation output: **PASS**.
- Fixed input timestamp makes evaluation independent of wall-clock time: **PASS** by repeated frozen-input characterization.
- Signal evaluation does not activate autoexecution: **PASS**; no exchange order execution path exists and evaluation is usable without a notifier/client.
- WATCH delivery is disabled in checked-in `config.yaml`: **PASS** (`send_watch_to_telegram: false`).

## Runtime/state inventory

| Area | Reads | Writes | Source |
|---|---|---|---|
| Full scan | active event states, ticker universe/shortlist, closed/deep 1m frames, derivatives/liquidity | event creation/advance/reset/expiry, zones, signal/reject/coverage/outcome rows, pool add/remove | `app/main.py:run_cycle`, `_process_symbol`; event modules |
| Fast monitor | only bounded active climax pool keys, selected frames, matching event state | climax evaluation/delivery, pool expiry/removal, heartbeat and append-only monitor events | `app/main.py:_run_fast_monitor` |
| Event creation | closed 1m rows and feature trigger/stretch | `PUMP_DETECTED` state with event high/base/range/times, snapshot, trigger, expiry | `app/events/pump_detector.py` |
| Pullback/zone | event high/base, price, VWAP, floor, ATR/config | `PULLBACK_OBSERVED`, `SHORT_ZONE_ACTIVE`, pullback metrics, zone bounds | `app/events/pullback_tracker.py`, `short_zone.py` |
| Signal terminal | decision and persistence result | `SIGNAL_SENT`, signal ID/time; outbox retry remains separate | `app/main.py`, `PullbackTracker.mark_signal_sent` |
| Replacement/expiry | newer high, expiry/kill conditions | reset to `PUMP_DETECTED` or terminal `EXPIRED` | `PullbackTracker`, repository state mapping |

### Event transition mapping

| Transition | Source function | Persisted fields written |
|---|---|---|
| `IDLE`/`EXPIRED` → `PUMP_DETECTED` (event creation) | `PumpDetector.build_event` | event ID, state, start/high/base/range and high time, feature snapshot, trigger window, expiry, updated time |
| Active event → `PUMP_DETECTED` (new confirmed high) | `PullbackTracker.reset_after_confirmed_high` | high/time/range; clears pullback low/depth/time and zone bounds; state and updated time |
| `PUMP_DETECTED` → `PULLBACK_OBSERVED` | `PullbackTracker.advance` | pullback detected time/depth/low and updated time |
| `PULLBACK_OBSERVED` → `SHORT_ZONE_ACTIVE` | `ShortSignalBot._process_symbol` + `ShortZoneBuilder.build` | zone low/high and state |
| Active event → `SIGNAL_SENT` | `PullbackTracker.mark_signal_sent` | state, signal ID/time, updated time |
| Active event → `EXPIRED` (timeout/kill) | `PullbackTracker.advance` or `_process_symbol` | state, expiry time, updated time |
| Climax candidate replacement/expiry | `_track_climax_candidate`, `_run_fast_monitor` | pool membership; monitor event; shadow attempt closure where enabled |

No optimistic locking or schema change was added. Full scan and fast monitor can both evaluate the same event; runtime and database dedupe are the current protections.

## DTO/live-replay inventory

| Object | Defined in | Used by live | Used by replay/shadow | Serializable | Deterministic with frozen inputs |
|---|---|---:|---:|---:|---:|
| `EventState` | `app/domain.py` | Yes | Shadow/research state paths | Yes, via repository JSON mapping | Yes |
| `SymbolFeatures` | `app/domain.py` | Yes | Replay/shadow evaluators as input | Yes, via dataclass/JSON mapping | Yes |
| `SignalDecision` | `app/domain.py` | Yes | No canonical replay consumer currently | Yes, via dataclass/JSON mapping | Yes |
| `CandidateEvaluation` | `app/domain.py` | Yes | No canonical replay consumer currently | Yes, nested decision mapping | Yes |
| `ClimaxEvaluation`/`Bundle` | `app/signals/climax.py` | Yes | Shadow variant uses same evaluator | Yes, metadata JSON-safe | Yes |
| `SignalProvenanceInput` | `app/domain.py` | Yes, persistence boundary | No | Yes, immutable dataclass fields | Evidence is frozen; runtime IDs/times are contextual |
| `SignalRecord`/`SignalOutcome` | `app/domain.py` | Yes, persisted/outcome paths | Research reports | Yes, repository conversion | Yes for stored rows |
| `StrategyObservation` | `app/observability/strategy_observations.py` | Climax observation | Shadow/research observation | Yes, canonical JSON + fingerprint | Yes for frozen canonical input |
| `VolumeClimaxLifecycle` | `app/signals/climax.py` | Shadow lifecycle | Shadow/replay lifecycle | Yes, field mapping required | Yes for fixed observation sequence |
| `V2RootDecision` | `app/observability/root_detector_shadow_v2.py` | Shadow telemetry only | Yes | Yes, explicit UTC JSON contract | Yes |

`SignalDecision` is already the current canonical live strategy output; no new canonical abstraction was created.

## Config behavior

`AppConfig.model_config` is `ConfigDict(extra="ignore", validate_assignment=True, hide_input_in_errors=True)`. Unknown mapping keys are **currently ignored silently**; they are not rejected or warned. The checked-in `config.yaml` includes `climax_block_price_oi_accelerating_together`, which is not an `AppConfig` field and is consequently ignored. The characterization test covers an unknown Phase 0 key. Existing legacy volume-climax key migration remains warning-producing and was not changed.

## Outbox/provenance invariants

- Decision → signal DB row → provenance → `SIGNAL` outbox row occurs before delivery claim: **PASS**.
- Signal outbox idempotency key remains `telegram:signal:<signal_id>`: **PASS**.
- Proved delivery claim is exclusive while leased; after lease expiry the row can be claimed again: **PASS**, preserving current at-least-once semantics.
- Retry state remains durable (`RETRY`); existing repository logic dead-letters at attempt five: existing tests pass and no logic changed.
- Provenance retains strategy family/branch, event identity, code/config/runtime identity, timestamps, and climax evaluation references where required: **PASS** through existing and new persistence characterization.
- No direct Telegram-before-persist path was introduced; notifier is called only after persistence/claim in current runtime flow.

## Files changed

- `docs/architecture/current-trading-contract.md`
- `docs/evidence/architecture-phase0-behavior-freeze-20260827T053347Z.md`
- `tests/contracts/helpers.py`
- `tests/contracts/test_baseline_contract.py`
- `tests/contracts/test_volume_climax_contract.py`
- `tests/contracts/test_low_volume_contract.py`
- `tests/contracts/test_global_signal_invariants.py`

Production runtime modules, `config.yaml`, and database schema files were not changed.

## Tests after

- New contract layer command: `python -m pytest tests/contracts -q` → **28 passed in 2.27 seconds**.
- New contract test count: **28**.
- Targeted lint: `ruff check tests/contracts` → **All checks passed**.
- Full suite command: `python -m pytest -q` → **295 passed in 31.87 seconds**.
- Compile command: `python -m compileall -q app tests` → **PASS** (chained after the full suite; no output).

## Behavioral change assessment

**TRADING BEHAVIOR CHANGED: NO**

Evidence: isolated worktree contains only docs/tests/helper additions; no files under `app/signals/`, `app/events/`, `app/main.py`, `config.yaml`, or storage schema/runtime were modified.

## Ready for next phase

**READY_FOR_PHASE_1_DB_RETENTION_ARCHIVE: YES**.
