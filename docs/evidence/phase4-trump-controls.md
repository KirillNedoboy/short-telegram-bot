# Phase 4 TRUMP control report

This file is a report template produced by the staged replay command.  It is
not a substitute for reconstructed candles, state, features or orderbook
evidence.

| Control | Decision time (UTC) | Expected |
|---|---:|---|
| TRUMP-1 | 2026-08-22 04:22:57 | `73 / B / Confirm` |
| TRUMP-2 | 2026-08-22 05:04:11 | `77 / B / Aggressive` |

The report must include distinct event identities, ordered transition and input
fingerprints, max input availability, and the first divergent layer when a
control fails.  Broad replay is prohibited unless the generated report is
sealed with `classification=CONTROL_REPLAY_PASS`.
