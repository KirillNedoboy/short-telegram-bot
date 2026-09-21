# Early Drop Warning

`EARLY_DROP_WARNING` is a separate, non-actionable observation stream.

## Contract

- It is evaluated independently from ordinary short admission.
- It has a separate persistence entity and outbox type in the production backport.
- It may classify weakening or data degradation.
- It has its own freshness and cooldown controls.
- It never changes ordinary short scoring, gates, or lifecycle.
- It never authorizes an order or copy-trading action.
- A warning is not a short signal and must not be rendered as one.

## State distinction

```text
ordinary scan → short strategy → ACTIONABLE/WATCH/NO_SETUP
separate evaluator → EARLY_DROP_WARNING or no warning
```

A data-quality warning can coexist with ordinary `NO_SETUP`, but the two records answer different questions. `NO_SETUP` is valid only after `SCANNED_OK`; a warning does not convert an invalid scan into a valid strategy result.

## Production overlay

The operator-reported Lane A backport enables the warning evaluator and Telegram warning delivery while keeping Lane B disabled. The warning table migration is additive; existing signal tables are not rewritten. Public documentation intentionally omits production database paths, chat identifiers, and credentials.

## Verification

The backport was reported with dedicated tests and full-suite verification. Runtime warning records were observed for `DATA_DEGRADED` and `WEAKENING`; no confirmed `WARNING` classification had been observed at the time of the provenance report. This is runtime evidence for that observation window, not a guarantee about future markets.
