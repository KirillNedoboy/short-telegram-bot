# Runtime concurrency model

## Scope and process boundary

`scripts/run_live.py` and `scripts/run_once.py` now call `run_fenced()` before
`ShortSignalBot.from_files()`. On Linux this acquires one non-blocking
`fcntl.flock(LOCK_EX | LOCK_NB)` on
`/run/short-telegram-bot-lite.lock`; the descriptor stays open for the
entrypoint lifetime and `close()` does not unlink the file. A contending process
or unsupported platform logs its identity, path, and reason, returns exit code
1, and never constructs the bot. The fence is process-level only: it does not
serialize tasks inside the winning process.

The production unit was inspected read-only over SSH.
It matches the checked-in example: `Type=simple`, `WorkingDirectory=/opt/short-telegram-bot-lite`,
`ExecStart=/opt/short-telegram-bot-lite/.venv/bin/python scripts/run_live.py`,
`Restart=always`, `RestartSec=10`, `User=root`, `KillSignal=15`, and
`TimeoutStopUSec=1min 30s`. No unit file was changed. A systemd restart can
therefore overlap only if the old process has not exited; the Linux fence rejects
the new process during that overlap.

## Task and writer inventory

| Task/loop | Created in | Lifetime/frequency | Shared reads/writes | DB/network | Overlap |
|---|---|---|---|---|---|
| Main full scan | `run_forever()` | one `run_cycle()` then `scan_interval_sec` sleep | loads active states; mutates returned states; updates health and rotation id | scanner REST, repository writes, Telegram sends | overlaps fast monitor |
| Fast monitor | `startup()` via `asyncio.create_task` | process lifetime while enabled; bounded poll interval | reads/writes `_active_climax_pool`, cursor/sequence, detached event states | scanner REST, monitor/evaluation writes, Telegram sends | overlaps full scan |
| Scanner gathers | `MarketScanner.fetch_*` | per request batch | scanner snapshot/derivatives caches | concurrent Bybit calls through shared scheduler | overlap within each batch |
| Shadow outcome scheduler | awaited in full scan | once per cycle | repository outcome rows | grouped Bybit calls and DB writes | not a separate task |
| Outbox drain | startup and each cycle | bounded batches | no in-memory owner; DB lease state | Telegram network plus outbox DB writes | can interleave with fast monitor |

`EventStateStore.load_active()` and `load()` return separate detached dataclass
copies. `upsert_event_state()` writes every persisted field for the symbol with
no revision predicate. The only proven harmful writer pair is full scan plus fast
monitor; scanner caches and request scheduling can duplicate work but do not own
event state.

## In-process execution

One `ShortSignalBot` instance owns the event loop. `run_forever()` awaits one
complete `run_cycle()` then sleeps for `scan_interval_sec`, so full scans do not
overlap each other. During `startup()`, when both climax flags are enabled, it
also creates `_run_fast_monitor()` as an `asyncio` task. That task sleeps for
`climax_fast_poll_sec`, then fetches only a bounded slice of
`_active_climax_pool`; it never performs the market-snapshot universe scan.

Both paths can nevertheless interleave at every network/database `await`:

```text
run_cycle: load_active -> fetch snapshots/frames -> process -> state_store.save
fast monitor: sleep -> load(symbol) -> evaluate -> may state_store.save
```

`MarketScanner.fetch_symbol_frames()` itself gathers per-symbol work
concurrently, while `RequestScheduler` limits individual exchange calls with
one semaphore and a rate limiter. `TelegramNotifier` uses the Telegram client
directly and is not governed by that scheduler. These controls limit request
pressure; they do not impose ownership or an ordering rule on a symbol state.

## Verified Phase 2B input

`tests/test_runtime_concurrency.py` uses `asyncio.Event` barriers and detached
state snapshots to force this sequence: full scan reads `initial`; fast monitor
loads and persists `fast-monitor-fresh`; the paused full scan persists its
earlier `full-scan-stale` snapshot. The passing witness asserts that the final
store value is `full-scan-stale`.

This is intentional evidence of the present stale-overwrite risk, classified
`POSSIBLE_RACE_SIGNAL_IMPACT` and reproduced deterministically. No global lock,
per-symbol lock, queue, actor, revision field, schema change, or strategy change
was introduced. Phase 2B must choose and implement the ownership/serialization
rule.

## Phase 2B ownership model

The Phase 2A race is fixed with one in-process `SymbolMutationCoordinator` owned
by `ShortSignalBot`. Its registry key is `symbol.upper()`; the market/DB symbol
value is unchanged. A lane owns the complete read-modify-write transition for
one symbol. The registry removes an idle entry after its last waiter leaves, and
an attempt by the owning task to acquire the same lane raises immediately.

The full scan fetches its universe and frames before entering a lane. Inside the
lane it reloads the authoritative symbol state using the same IDLE/EXPIRED and
`expires_at` predicate as `load_active`, runs `_process_symbol`, and persists the
returned state. The fast monitor enters the same lane before rechecking its
candidate and event id, loading state, and running `_evaluate_and_send_climax`.
TTL candidate cleanup also takes that symbol lane and rechecks the candidate.
There is no global lock: transitions for BTCUSDT and ETHUSDT may overlap.

Network awaits that are part of a decision remain inside the lane because moving
them would change the decision input or reopen the transition. Repository calls
are short synchronous transactions and are not held across network awaits. If a
durable signal/watch row exists and delivery is cancelled, the state marker is
finalized before ownership is released; a finalization storage failure is logged
and remains a recovery risk for Phase 2C. InstanceFence continues to protect the
process boundary; symbol lanes protect only writers inside that process.
