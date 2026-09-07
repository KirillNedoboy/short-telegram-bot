# ROOT_DETECTOR_SHADOW_V2 contract

## Current detector predicate inventory

| Predicate | Source | Class | Temporal dependency | Safety purpose |
|---|---|---|---|---|
| `trigger_window` | `app/events/pump_detector.py:PumpDetector.qualifies` | `STRUCTURAL_PUMP` | none | current EventState recognition |
| `live_stretch` | `app/events/pump_detector.py:PumpDetector.qualifies` | `STRUCTURAL_PUMP` | none | pump confirmation, not execution |
| `closed_candles_after_high` | `app/signals/climax.py:_common_metadata` | `TEMPORAL_MATURITY` | closed candles | maturity only |
| `liquidity` | `app/signals/climax.py:_volume_climax` | `EXECUTION_SAFETY` | none | execution safety |
| `oi_squeeze` | `app/signals/climax.py:_volume_climax` | `SQUEEZE_SAFETY` | none | squeeze protection |
| `rejection_retest` | `app/signals/climax.py:_low_volume` | `DOWNSTREAM_CONFIRMATION` | post-high | entry confirmation |

## Counterfactual diff

```text
CURRENT ROOT requires: trigger_window, live_stretch
V2 requires: v1_trigger
V2 intentionally does not wait for:
trigger_window = structural maturity delay; no execution side effect
live_stretch = structural pump admission delay; no execution-safety predicate
```

V2 reuses the existing V1 shadow trigger thresholds and introduces no new numeric thresholds. Liquidity, OI/squeeze, and downstream confirmation predicates are not mechanically copied into V2.

## Deployment safety

```text
CODE_DEFAULT=OFF
PRODUCTION_SHADOW_FLAG=ON (only after controlled deployment approval)
LIVE_EFFECT=NONE
```
