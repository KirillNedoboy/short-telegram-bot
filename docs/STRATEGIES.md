# Strategy Contracts

## Delivery matrix

| Strategy | Evaluation | Live Telegram | Autoexecution |
|---|---:|---:|---:|
| `BASELINE_PULLBACK` | ON | ON by explicit flag | OFF |
| `VOLUME_CLIMAX_UNWIND` | ON | ON by explicit flag | OFF |
| `LOW_VOLUME_EXTENSION_FAILURE` | ON | ON by explicit flag | OFF |
| `TRAPPED_LONGS_REVERSAL` | ON | OFF | OFF |

The delivery policy is allow-listed. Shadow or WATCH states cannot become live signals through formatting or persistence.

## BASELINE_PULLBACK

The baseline branch requires a detected pump, a mature pullback, and current price inside the configured short zone. It then applies core filters: VWAP distance, rejection/candle structure, volume, pullback bounds, liquidity and squeeze/breakout protections. Score and grade are calculated only after hard filters.

Typical state path:

```text
IDLE/EXPIRED → PUMP_DETECTED → PULLBACK_OBSERVED → SHORT_ZONE_ACTIVE → SIGNAL_SENT
```

A confirmed new high resets stale pullback/zone state without silently reusing the prior entry.

## VOLUME_CLIMAX_UNWIND

This branch looks for a high-volume extension/climax followed by evidence of exhaustion and unwind. It requires valid derivatives context where configured, volume/pump evidence, rejection, acceptable entry distance and liquidity. Missing or contradictory evidence vetoes the branch.

It is evaluated independently from the low-volume branch. One branch cannot relax another branch's gates.

## LOW_VOLUME_EXTENSION_FAILURE

This branch targets a weak extension whose volume efficiency is low and whose high fails. It requires comparable volume windows, closed candles after the high, no resumed high, close/retest structure, rejection, liquidity and configured distance limits. It remains a live unchanged strategy.

## TRAPPED_LONGS_REVERSAL

This is an experimental shadow-only hypothesis. Its intended sequence is:

```text
long-side extension/breakout
 → failure/rejection
 → failed retest
 → possible short reversal
```

Required diagnostic fields include:

- `breakout_reference` — structural breakout level;
- `failed_retest_high` — highest observed retest/event high used for diagnosis;
- `decision_price` — price at evaluation;
- `event_high` — event high;
- `entry_reference` — the explicit reference used for distance diagnostics, not a presentation band;
- entry/chase classification;
- OI sequence classification;
- failed-retest quality;
- shadow quality score and breakdown.

### Lifecycle invariants

For Strategy 4 only:

```text
decision_time < confirmation_expires_at
confirmation_expires_at > attempt_created_at
```

If the decision is after expiry, the result is blocked with:

```text
CONFIRMATION_WINDOW_EXPIRED
```

If the attempt is born expired, the result includes:

```text
BORN_EXPIRED_ATTEMPT
```

The implementation must not extend the window, re-arm an expired root, or create a replacement window.

### Current evidence limits

The existing failed-retest predicate is diagnostic shape evidence (`PREDICATE_SHAPE_ONLY`), not proof of a structurally valid retest. Existing OI logic is directional and does not prove persistence through breakout, failure and decision. Score saturation is a research defect, not a reason to change thresholds blindly.

The `breakout_reference * 0.99 … * 1.01` presentation band must not be described as an admission zone unless the code contract explicitly makes it one.

## Scoring and grades

Scores are strategy-specific. A high score indicates that configured booleans/bonuses passed; it is not a calibrated probability, expected return or guarantee. Grade is a presentation/admission tier and does not override hard vetoes.

Do not tune thresholds from a small set of failed signals. Use time-ordered, cost-aware, out-of-sample evidence.
