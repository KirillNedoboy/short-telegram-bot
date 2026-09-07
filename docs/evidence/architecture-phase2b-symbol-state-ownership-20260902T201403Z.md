# PHASE 2B RESULT

## Source

- Branch: `architecture/phase2b-symbol-state-ownership`
- Base SHA: `5e3ad3d7acc926e13d8d86042df61fd6e047f10a`
- Final implementation SHA: `21a6f363917555126d4cfffa5eb61e83dafa7db6`
- Documentation/evidence is committed after the implementation SHA.

## Proven Phase 2A race

The shared mutable object was a detached `EventState` keyed by symbol. Full scan
read a state, awaited market work, and later saved it; fast monitor loaded and
saved the same symbol in between. The old deterministic witness forced
`full-read → fast-write → stale-full-write`, losing `SIGNAL_SENT`, `signal_id`,
`signal_sent_at`, and fresh features.

## Ownership design

`ShortSignalBot` owns one `SymbolMutationCoordinator`. Its registry key is
`symbol.upper()`; DB and market symbol values are unchanged. A lane tracks
waiters, contention, owner task, and wait duration, removes itself after its
last user leaves, and rejects reentrant acquisition. No global lock or timeout
was introduced.

## Mutation boundaries

Full scan fetches snapshots/frames outside the lane, then acquires one symbol
lane, reloads the authoritative state with the original active predicate,
runs `_process_symbol`, saves the returned state, and releases. Fast monitor
uses the same lane around candidate revalidation, state reload, event-id check,
and `_evaluate_and_send_climax`. TTL candidate cleanup rechecks under the lane.
No path takes more than one symbol lane.

## Full scan integration

The initial `load_active` time is captured before the read. Per-symbol reload
preserves `IDLE`, `EXPIRED`, and `expires_at <= reference_time` filtering.
Detached initial states are used only to extend the scan universe.

## Fast monitor integration

Batch frame fetch remains outside ownership. Candidate and event identity are
checked again after waiting for the lane, preventing a replaced candidate from
being evaluated or removed incorrectly.

## Other writers

Phase 2A inventory found two concurrent `EventState` writers: full scan and
fast monitor. Repository `expire_symbol` is not called by runtime paths. Signal,
watch, outbox, outcome, scanner-cache, and heartbeat writes do not write the
shared `EventState` object and were not placed under symbol lanes.

## Deterministic interleaving tests

The original detached-snapshot reproducer now passes only when the fast writer
waits for the full writer and then reloads its result. Additional tests cover
same-symbol serialization, mixed-case identity, different-symbol overlap,
reentrant acquisition, exception release, cancellation release, and registry
cleanup. No sleep-based race ordering is used.

## Different-symbol concurrency test

Two independent lanes overlap concurrently; the test observes a maximum active
transition count of two while same-symbol transitions remain strictly ordered.

## Failure/cancellation safety

All lane ownership uses `finally`. After a durable signal or watch row is
created, delivery exception/cancellation finalizes the corresponding state
marker before propagating the exception. Finalization storage failure is logged
and remains an explicit Phase 2C recovery risk. Provisional pool entries are
rechecked against persisted state.

## InstanceFence retained

Yes. `InstanceFence` and its entrypoint ordering were not changed.

## Linux flock validation status

PENDING on this Windows workstation. Existing Linux subprocess tests remain
available and must be run on Linux before production deployment: owner acquires,
second process is rejected, owner exits, third process acquires.

## Performance

The deterministic lane tests demonstrate serial same-symbol access and overlap
for different symbols. No global queue or exchange-wide lock was introduced.

## Regression

- Contracts: `28 passed`.
- Phase 2A targeted tests: `5 passed, 3 skipped`.
- Ownership plus race tests: `4 passed`.
- Integration subset: `29 passed`.
- Full suite baseline before Phase 2B: `324 passed, 5 skipped`.
- Full suite after implementation: `327 passed, 5 skipped`.
- `compileall`, changed-scope Ruff, and `git diff --check`: PASS before evidence commit.

## Trading behavior

CHANGED = NO. Strategy definitions, thresholds, scoring, admission, dedupe,
event identity, timestamps, grades, Telegram behavior, and outcome semantics
were not intentionally changed.

## Production deployment

NO. No service, production DB, credentials, or live entrypoint was used.

## Remaining runtime risks

Linux fence subprocess validation is pending. Storage failure after a durable
signal but before marker finalization remains a recovery concern for Phase 2C.
Startup DDL/readiness and explicit migration hardening remain out of scope.

## Classification

`A. SYMBOL_STATE_OWNERSHIP_FIX_PASS`
