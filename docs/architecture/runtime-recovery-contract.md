# Runtime recovery contract

## Current startup and single-instance behavior

The live and one-shot entrypoints must acquire the Linux instance fence before
configuration loading or bot construction. A held fence, an unavailable Linux
`flock`, or an OS-level fence error returns non-zero and logs the fence
identity, lock path, and reason. Non-Linux execution fails closed instead of
claiming equivalent protection. The lockfile is retained after exit; ownership
is represented by the open descriptor lock, so a stale pathname never blocks a
later process.

On normal shutdown `ShortSignalBot.shutdown()` clears the fast-monitor flag,
cancels and gathers its task, then closes the notifier. The fence's `finally`
closes after the async entrypoint returns or raises. Process death also releases
the kernel-held flock when its descriptor is closed by the OS.

Actual order before the Phase 2A entrypoint fence was: `from_files()` config
load and constructor → SQLite `create_all`/schema repair → repository metadata
setup → notifier construction; then `startup()` notifier initialization → DB
heartbeat → shadow lifecycle reconciliation → outbox reclaim/drain → fast
monitor task creation; finally `run_forever()` enters the full scan loop. There
is no explicit READY state, and a failed startup health check returns from
`startup()` without preventing the caller from entering `run_forever()`.

## Current recovery semantics

`startup()` starts the notifier, performs a writable storage heartbeat, then
reconciles shadow lifecycle records when that repository capability is present.
It drains due delivery records before starting the fast monitor. `run_cycle()`
performs the same storage health check and drains delivery records before market
work; its outer exception handler records an error and returns an empty cycle.

Delivery recovery is durable and at-least-once. `claim_due_deliveries()` leases
pending/retry items for 120 seconds, converts expired in-flight leases back to
retry (or dead after the maximum attempt threshold), and increments attempts.
`_deliver_outbox_item()` marks success sent; errors and false returns schedule a
retry one minute later. An interrupted delivery can therefore be retried and
may be delivered more than once.

For SQLite, `Database` configures `WAL`, `busy_timeout=5000`, and a transactional
heartbeat write. Those mechanisms improve local database behavior but are not a
multi-process ownership protocol. The new process fence is authoritative for
the two production runtime entrypoints only.

## Operations boundary

The production unit was inspected read-only over SSH and matches the example:
`Restart=always`, `RestartSec=10`, `WorkingDirectory=/opt/short-telegram-bot-lite`,
`ExecStart=/opt/short-telegram-bot-lite/.venv/bin/python scripts/run_live.py`,
`User=root`, `KillSignal=15`, and `TimeoutStopUSec=1min 30s`. No service
restart, deployment, production-unit edit, credential inspection, or database
migration was performed in Phase 2A.

## Schema mutation audit

Before Phase 2C, `ShortSignalBot.__init__()` called `Database.create_all()` and
SQLite startup could execute additive `ALTER TABLE`, index repair, and
heartbeat-table creation. Phase 2C moves those operations to the explicit
admin migration command. Runtime schema validation and heartbeat are now
read-only with respect to DDL.

## Target startup and recovery (Phase 2C)

The Phase 2C contract is: validate config → acquire fence → open DB →
read-only schema validation → restore persisted state → reclaim stale outbox
leases without sending → reconcile required unfinished work → bounded REST
readiness probe → initialize workers → report READY. Until READY, scans,
evaluation, Telegram delivery, and enqueue are closed by the lifecycle gate.
Startup failure cleans up and propagates a non-zero result. Historical outcome
work remains bounded and may continue after READY; startup does not perform an
unbounded backfill.

## Open recovery risk

The instance fence and Phase 2B symbol coordinator are independent: the fence
serializes processes, while the coordinator serializes one symbol inside the
runtime and permits different symbols to overlap.
