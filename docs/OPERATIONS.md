# Operations Runbook

## Safety invariants

Before any production action verify:

```text
AUTOEXECUTION=OFF
TRAPPED_LONGS live delivery=OFF unless separately approved
SQLite Diet Stage B=not started unless separately approved
old three strategies remain unchanged
```

Do not restart or deploy merely to collect shadow evidence.

## Health checks

```bash
systemctl is-active short-telegram-bot-lite.service
systemctl show short-telegram-bot-lite.service \
  -p MainPID -p NRestarts -p ExecMainStatus -p WorkingDirectory
journalctl -u short-telegram-bot-lite.service -n 100 --no-pager
```

Look for recent `DB heartbeat OK`, completed scan cycles, provider error rates, outbox progress and outcome scheduler progress.

## SQLite checks

Use read-only access for inspection:

```bash
sqlite3 'file:<APP_ROOT>/data/bot.sqlite?mode=ro' \
  'PRAGMA query_only=ON; PRAGMA journal_mode; PRAGMA integrity_check;'
```

Do not copy or vacuum production SQLite while the disk is below reserve without a reviewed storage plan.

## Disk-capacity response

The service emits `DISK_CAPACITY_LOW` when free bytes fall below the derived reserve and `DISK_CAPACITY_CRITICAL` on a critical transition. First inspect filesystem usage and reconstructable caches. Preserve production DB/WAL, current release, rollback backups and research evidence. Remove only explicitly classified caches or obsolete staging artifacts, then verify `df`, service health and disk state transition.

Do not run broad cleanup, SQLite migrations, Docker prune, or delete rollback backups without an inventory and retention decision.

## Delivery incident funnel

Trace one UTC window through:

```text
scan cycles → evaluations → actionable evaluations → signals
→ outbox rows → SENT/DEAD
```

Interpretation:

- no cycles/evaluations: runtime/provider/scheduler issue;
- evaluations but no actionable: inspect normalized veto reasons;
- actionable but no signal: admission/dedupe/persistence issue;
- signal but no SENT: outbox/Telegram transport issue.

Never send a test Telegram message from production to validate delivery.

## Deployment checklist

1. Work in a clean hotfix branch.
2. Run focused and full tests, compile and Ruff.
3. Scan tracked files for secrets and production data.
4. Review `git diff --check` and protected strategy/config paths.
5. Create a verified rollback backup before activation.
6. Deploy only with explicit restart authorization.
7. Verify new PID, service state, DB heartbeat, scan cycles, delivery policy and no unexpected signals.
8. Record the exact commit and runtime evidence.
