# Strategy-4 Shadow Validation

## Objective

Determine whether `TRAPPED_LONGS_REVERSAL` separates genuine reversals from continuation/re-entry setups without changing live logic during observation.

## Cohort gate

Use the first condition reached:

```text
≥30 independent post-hardening root_event_id values
OR 24 hours elapsed
```

Repeated evaluations of one root are retained for temporal diagnostics but count once. Retain symbol, trigger timeframe, event revision and episode correlation.

## Per-root record

Select the best temporally valid candidate and retain:

- decision, attempt creation and expiry timestamps;
- v1 admission and expiry-safe result;
- breakout/retest/decision/event prices;
- percentage and ATR distances;
- event-high → decision, failure → retest and retest → decision timing;
- entry class and failed-retest quality;
- OI sequence class;
- old score/grade and shadow score/breakdown;
- new-high-after-decision flag.

## Outcome contract

Where coverage exists, calculate 15m, 1h and 4h MFE/MAE, MAE before first meaningful favorable move, continued adverse movement at 5%/10%, new high after decision and the existing TP1-equivalent outcome contract. Do not invent a new TP/SL rule for the cohort.

## Comparisons

Group by:

```text
failed-retest: PREDICATE_SHAPE_ONLY / STRUCTURAL_RETEST_PRESENT /
               STRONG_STRUCTURAL_FAILED_RETEST / UNKNOWN
OI:             STRONG_TRAPPED_LONG_EVIDENCE /
               WEAK_DIRECTIONAL_OI_INFERENCE /
               OI_UNWOUND_AFTER_FAILURE / OI_UNKNOWN
entry:          continuous distance and timing values, not an initial hard threshold
score:          OLD_V1_SCORE versus SHADOW_QUALITY_SCORE
```

Report counts, medians and rates. Do not claim statistical significance from a tiny cohort.

## Controls

Signal 59 remains a negative control: it was inside its window and therefore tests quality beyond expiry. Any proposed interpretation must state whether it would reject or downgrade 59 and identify the exact evidence. Do not overfit it.

Positive controls require acceptable path quality: meaningful MFE, reasonable MAE and no extreme adverse continuation before favorable movement. Price eventually falling is not sufficient.

## Promotion decision

Choose exactly one after the cohort is complete:

- `FAILED_RETEST_V2_JUSTIFIED`
- `OI_PERSISTENCE_GATE_JUSTIFIED`
- `ENTRY_CHASE_GATE_JUSTIFIED`
- `MULTI_FACTOR_MODEL_NEEDED`
- `STRATEGY_HYPOTHESIS_WEAK`
- `INSUFFICIENT_SAMPLE`

Until then:

```text
KEEP SHADOW
KEEP LIVE TELEGRAM DELIVERY OFF
DO NOT IMPLEMENT THE RECOMMENDED CHANGE
```
