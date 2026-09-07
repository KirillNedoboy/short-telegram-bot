# Database migrations and runtime schema contract

The live process is validation-only. It opens an existing SQLite database,
checks `PRAGMA user_version` and the structural contract, and fails before any
worker, scan, Telegram delivery, or heartbeat write when the check fails.
Runtime never calls `create_all`, `ALTER TABLE`, `CREATE INDEX`, `DROP`, or
schema-repair code.

Schema version 0 is the historical, unversioned schema. An administrator may
adopt it only after the complete legacy contract (tables, columns, primary
keys, required unique identities, and optional V2 pair) passes validation.
Adoption stamps version 1 as the final operation. Version 1 is current and
idempotent. A future, partial, unknown, or structurally incompatible version
fails closed; no downgrade or guessed repair exists.

Use `python -m scripts.migrate_db --db PATH --plan` for a read-only plan,
`--verify` for validation, `--apply --backup PATH` for an explicit migration,
or `--apply --bootstrap` for an empty database. `--include-shadow-v2` is
required when the V2 capability is part of the deployment. Apply performs
preflight, backup validation, one SQLite migration transaction, postflight,
and only then the version stamp. It does not run against production in this
phase.

The contract accepts SQLite's stable type spellings and equivalent named
unique constraints/indexes, while requiring ordered identity columns and
declared primary keys. V2 is an all-or-nothing optional pair. Secondary index
absence and duplicate identities are migration errors, not runtime repairs.

The Phase 2C rehearsal uses a disposable copy of the immutable retention
snapshot. Counts and streaming digests for signals, provenance, outcomes,
event states, outbox, and root/event dependencies must match before and after.
The canonical snapshot is never modified.
