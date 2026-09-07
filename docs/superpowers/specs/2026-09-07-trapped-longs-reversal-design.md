# TRAPPED_LONGS_REVERSAL Design

## Goal
Add a fourth independent live short-signal strategy that detects a failed breakout with long-side open-interest buildup, without changing or competing with BASELINE_PULLBACK, VOLUME_CLIMAX_UNWIND, or LOW_VOLUME_EXTENSION_FAILURE.

## Scope lock
- Do not add the strategy to `evaluate_climax_bundle()` or its `selected` result.
- Do not change the three existing evaluators, thresholds, scoring, lifecycle, dedupe, or admission semantics.
- Keep `AUTOEXECUTION=OFF`, REST_ONLY, SQLITE_ONLY, and existing Telegram UX.
- The new branch may emit Telegram signals only after its own admission path passes.

## Independent architecture
`TRAPPED_LONGS_REVERSAL` has its own evaluator, lifecycle, root/attempt/evaluation/admission identity, dedupe namespace, provenance branch, model version, config enable/delivery flags, and delivery policy branch. It reads the same immutable market/features snapshot but never mutates the existing EventState signal identity or participates in old climax selection.

## Signal contract
1. Established event and a frozen pre-breakout reference are available.
2. A structural high breaks the reference with positive OI participation.
3. At least two closed structural candles are available after the breakout.
4. Price closes back below the breakout reference.
5. A failed retest/lower-high is confirmed without a new high beyond tolerance.
6. OI evidence is present; missing derivatives data is a hard veto.
7. Liquidity data is present and does not breach hard spread/slippage/depth limits.
8. Candidate remains inside a bounded post-failure lifetime.
9. Score is at least 70 and grade is A/B.

Initial configuration is conservative and configurable: OI 15m minimum +1%, two closed 5m structural candles, 15-minute candidate lifetime, 0.30% new-high tolerance, minimum rejection 1.0%, and live delivery enabled only for the new branch.

## Identity and dedupe
Root IDs use the `trapped_longs:` namespace and include symbol plus breakout identity. Dedupe is scoped to `(strategy_branch, root_event_id, revision)`. An old strategy's `event_id` or `signal_id` cannot suppress a new Strategy 4 candidate.

## Admission and persistence
The branch persists its candidate/evaluation/admission evidence through existing compatible persistence paths, using the new strategy branch and model version. No new heavy telemetry table is added. Existing signal/provenance/outbox invariants must remain valid.

## Verification
- RED tests first for evaluator gates, failed-retest lifecycle, own dedupe identity, independent selection, missing-data fail-closed behavior, delivery policy, and old-bundle invariance.
- Targeted tests, full suite, compileall, Ruff, and diff check before deployment.
- One controlled deployment of the final image.
- Verify active release, runtime identity, AUTOEXECUTION=OFF, old strategies unchanged, and first natural Strategy 4 candidate/signal path.
