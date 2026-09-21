# Deployment and rollback

This is a sanitized operator guide. Replace placeholders with local values; never commit the resulting configuration, database, logs containing secrets, or service environment.

## Preconditions

1. Pin the exact release identifier.
2. Validate Python/dependency compatibility.
3. Review effective configuration and secret separation.
4. Check migration compatibility and make a non-destructive backup.
5. Confirm `AUTOEXECUTION=OFF` and manual-entry delivery.

## Start/verify sequence

```bash
python -m compileall -q app tests research
pytest -q
systemctl is-active <SERVICE_NAME>
# inspect application health, data connection, scan result, and outbox state
```

A running process is insufficient. Verification requires database heartbeat, market-data connectivity, successful scan completion, absence of unexplained deadline/incomplete-data failures, and delivery/outbox evidence.

## Rollback

1. Stop or pause the affected service according to the local runbook.
2. Select the previously verified release without rewriting source history.
3. Run only compatible additive migrations.
4. Preserve the production SQLite database; do not delete, reset, or rewrite it.
5. Restart the service and verify the exact release provenance, heartbeat, data connection, scan, and outbox.
6. Record the result and keep the failed release available for forensic comparison.

## Release-specific note

The active operator-reported production choice is Lane A `bf47d2b1`; Lane B `dfcdb9df` is historical/inactive. The 111-symbol / `$3M` candidate was rolled back after capacity/data-quality observations and must not be treated as active.
