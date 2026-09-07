# TRAPPED_LONGS_REVERSAL Implementation Plan

> **For Hermes:** Implement this plan task-by-task with strict TDD and review each task against the scope lock.

**Goal:** Add an independent live `TRAPPED_LONGS_REVERSAL` short strategy without modifying the three existing strategy evaluators or their selected-result path.

**Architecture:** A standalone evaluator/lifecycle module receives the existing immutable state/features/frame snapshot. It produces its own candidate/evaluation/admission decision and routes through a dedicated strategy branch, provenance identity, dedupe namespace, and delivery flag. It is called alongside, not inside, the existing climax bundle.

**Tech Stack:** Python 3.12, pytest, SQLAlchemy/SQLite existing models and repository, existing SignalDecision/provenance/outbox contracts.

---

### Task 1: Add configuration contract
- Files: `app/config.py`, `config.yaml`, `tests/test_config.py` or existing config tests.
- Add disabled-by-default schema fields for the new branch and conservative live values; production activation is explicit in the final config patch.
- Test non-default values load and survive config fingerprinting.

### Task 2: Add independent evaluator RED/GREEN
- Files: create `app/signals/trapped_longs.py`, create `tests/test_trapped_longs.py`.
- Write failing tests for OI confirmation, close below breakout, failed retest, new-high cancellation, missing-data veto, liquidity block, score/grade, and no mutation of existing state.
- Implement a standalone evaluator returning its own dataclass result; never import or call `evaluate_climax_bundle`.

### Task 3: Add independent lifecycle RED/GREEN
- Files: same module/tests.
- Test breakout -> OI confirmed -> failure pending -> retesting -> ready -> admitted/rejected/expired transitions, revision identity, and bounded lifetime.
- Implement explicit lifecycle transitions and `trapped_longs:` root identity.

### Task 4: Add separate persistence/admission wiring
- Files: `app/domain.py`, `app/storage/models.py`, `app/storage/repository.py`, migrations if required, tests.
- Extend existing branch constraints and repository mapping for `TRAPPED_LONGS_REVERSAL`; preserve old branch constraints and rows.
- Add own decision/evaluation/admission identity and dedupe lookup. Do not reuse old `EventState.signal_id`.

### Task 5: Wire parallel runtime path
- Files: `app/main.py`, delivery policy/formatter, tests.
- Invoke the standalone evaluator in the cycle/fast-monitor path alongside old evaluation, not through the old selected result.
- Add explicit delivery flag and provenance branch. Verify old bundle output is byte-for-byte/equivalent in existing regression fixtures.

### Task 6: Enable live config and verify
- Create external rollback backup before final config/source deployment.
- Run targeted tests, full pytest, compileall, Ruff, and git diff check.
- Commit final patch, build release, perform one controlled restart, and verify service/runtime/DB/outbox invariants plus AUTOEXECUTION=OFF.
- Observe a natural candidate or report that no candidate appeared; never synthesize a signal.
