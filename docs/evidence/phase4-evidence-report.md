# Phase 4 evidence report

Classification is one of:

- `BASELINE_CORE_REPLAY_PASS`
- `BASELINE_CORE_REPLAY_PASS_ADMISSION_UNOBSERVABLE`
- `CONTROL_REPLAY_MISMATCH`
- `DATA_GAP_CENSORED`
- `HISTORICAL_UNOBSERVABLE`
- `REPLAY_NOT_RUN`

The generated evidence must identify the replay-code SHA, proven historical
live-code SHA `a51d2acc682388693247159f2e374ee23175c450`, dataset epoch,
production universe, normalized artifact hashes, counts, and zero violations
of `max_input_availability_time_utc <= decision_time_utc`.  Outcomes are
computed only after the decision stream is sealed and never affect lifecycle
or signal selection.
