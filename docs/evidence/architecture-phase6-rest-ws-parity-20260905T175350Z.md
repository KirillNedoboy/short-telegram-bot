# Architecture Phase 6 REST/WS Parity — Production Evidence

## Result

- Phase 6: `PASS`
- Classification: `PARITY_PASS_BACKFILL_PROBE_ONLY`
- Original Phase 6 SHA: `aa975526b306a0df86d211fe09a172f8b9eb4063`
- Phase 6 code SHA: `a51b006602a16978e6e25287b8bbb540a2aa603a`
- Production release: `/opt/short-telegram-bot-lite-admin/releases/a51b006602a16978e6e25287b8bbb540a2aa603a`
- REST canonical: `YES`; WS shadow: `YES`; production automatic backfill: `OFF`.

## Serialization fix and source

The focused regression reproduced the Ubuntu `datetime` failure before the fix and passed after every Phase 6 Markdown JSON section adopted the existing `_json_default` serializer. The actual `write_evidence()` path published both formats successfully.

The deterministic source archive was generated twice from the exact code SHA and produced SHA-256 `357c1fb68688f92ed533b079fe5fa81263d61b74123f15452a95e8ad7c423396` at 2,119,680 bytes. The remote hash matched before extraction. Required ancestors `aa9755…`, `d7d54fa…`, and `ab835ca…` all passed.

## Ubuntu release gate

- Full suite: `431 passed, 4 skipped`.
- Compileall, Ruff 0.16.6, and diff-check equivalent: `PASS`.
- Migration plan: `NO_MIGRATIONS_NEEDED`; V1 verify: `PASS`.
- Database user version: `1`; schema version: `191`; no migration or backup was run.
- Every capacity gate was `HEALTHY`. Immediately before switch: free 5,624,074,240; reserve 4,841,672,704; margin 782,401,536 bytes.

## Real parity probe

- Duration: `600.838s`; ticker probes: `21`; intersection symbols: `105`.
- Ticker field comparisons: `24,255`; exact observed: `22,836` (`31` in-window, `20,932` nearest-before, `1,873` nearest-after).
- Temporal differences: `0`; WS field unobserved: `1,155`; WS stale: `264`.
- HTTP latency: min `0.303318s`, median `0.421735s`, p95 `1.170698s`, max `1.546067s`.
- Resource use: CPU `63.226s`, peak RSS `107,752 KiB`, parity buffer high-water `551`, queue drops `0`.
- Standalone isolation: `20` FD samples, maximum production DB descriptors `0`; repositories, strategies, lifecycle and Telegram were not instantiated.

## Closed kline, gap, reconnect, and backfill

- Deterministic nine-symbol sample: `90/90` exact confirmed closed-1m candles; true mismatches `0`.
- Dedicated withheld-middle-candle gap: `PASS`; one missing interval detected and restored.
- Controlled probe reconnect, resubscription, new connection generation, and ticker reinitialization: `PASS`.
- Probe-only REST backfill: `SUCCESS`; conflicts `0`; source confirmations `1`; future leakage violations `0`.
- Backfill timestamps were serialized in Markdown, including `request_started_at=2026-09-05T17:31:04.924929+00:00` and `response_received_at=2026-09-05T17:31:05.541972+00:00`.
- REST rate-limit impact: `NONE`.

Published remote artifacts:

- JSON: 145,852 bytes, SHA-256 `2c512149988d57a7c59fa25b0c0e0a2c6ddda17bef6436f88c60438c8c807665`.
- Markdown: 1,996 bytes, SHA-256 `f9fedd78a1ee1d9e6dc2bbea6e1935a0c356e0b325951d866bfaec50407b0ce1`.

## Production acceptance

The `current` symlink was atomically switched from `d7d54fa8af070241711d5072cffbf8208f482b5d` to the immutable Phase 6 code release. The service reached READY with new PID `123943`, stayed `active/running`, and retained `NRestarts=0`.

Two complete REST cycles finished with shortlist/symbols `100/100`, signals `0`, and outcomes `100`. WS returned HEALTHY after each expected universe replacement and acknowledged `208/208` topics. Parse-error, traceback/error, rate-limit, and SQLite-error counts were all `0`.

Final DB `quick_check=ok`, user version `1`, schema version `191`. Disk remained `HEALTHY` with free 5,621,383,168, reserve 4,844,195,840, and margin 777,187,328 bytes. Strategy manifests were byte-identical, no exchange order path exists, `AUTOEXECUTION OFF`, and production backfill remains unwired.

## Next

`PHASE_6_COMPLETE`

`READY_FOR_PHASE_7_HOT_SYMBOL_EVIDENCE`
