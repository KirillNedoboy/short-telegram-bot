# REST Data-Quality Recovery Implementation Plan

> **For Hermes:** Execute this plan task-by-task with verification after each step.

**Goal:** Reduce Bybit rate-limit-induced incomplete market evidence without changing signal strategy gates, thresholds, lifecycle semantics, or Telegram admission policy.

**Architecture:** Keep `REST_ONLY` and the existing `RequestScheduler` boundary. Make every retry attempt pass through the shared global rate limiter, and classify retry exhaustion as the existing data-quality failure path. Preserve fail-closed liquidity/OI semantics. No schema or strategy changes.

**Tech Stack:** Python 3.12, asyncio, tenacity-compatible scheduler, pytest, clean hotfix workspace.

---

## Scope lock

Must not change:

- strategy thresholds or scoring;
- rejection, structural, second-leg, OI, liquidity, or confirmation gates;
- lifecycle/root lifetime or attempt bookkeeping;
- SQLite schema or production data;
- Telegram formatting or delivery policy;
- AUTOEXECUTION, REST_ONLY, SQLITE_ONLY, or Storage Stage B state;
- active release or running service during implementation.

Allowed:

- clean hotfix workspace only: `/opt/short-telegram-bot-lite-hotfix`;
- request retry/rate-limit scheduling;
- focused tests and external evidence report.

## Task 1: Reproduce retry scheduling defect

Files:

- Test: `tests/test_request_scheduler.py`
- Inspect: `app/infra/request_scheduler.py`, `app/infra/rate_limiter.py`

Write a deterministic fake rate limiter and sync function that fails once with a Bybit 10006-like exception then succeeds. Assert the limiter is acquired for the initial call and the retry, and that the final result is returned.

Run:

```bash
.venv/bin/pytest -q tests/test_request_scheduler.py -k retry
```

Expected RED: retry path currently acquires the limiter only once.

## Task 2: Implement per-attempt rate limiting

File:

- Modify: `app/infra/request_scheduler.py`

Replace the decorator-only retry path with a bounded async retry loop or an equivalent tenacity hook. Every attempt must acquire the shared limiter before invoking the sync provider call. Preserve three total attempts and exponential waits capped at four seconds. Do not catch and convert successful provider responses or alter error types.

Run:

```bash
.venv/bin/pytest -q tests/test_request_scheduler.py -k retry
```

Expected GREEN: focused scheduler tests pass.

## Task 3: Preserve provider fail-closed behavior

Files:

- Test: `tests/test_market_scanner_derivatives.py`
- Test: existing liquidity tests
- Modify only if required: `app/market/scanner.py`

Verify that rate-limit exhaustion remains `RATE_LIMITED`/`bybit_rate_limit`, missing liquidity remains unavailable, and no incomplete payload becomes actionable. Add a test only if the current contract lacks coverage. Do not turn UNKNOWN liquidity into a pass.

Run:

```bash
.venv/bin/pytest -q tests/test_request_scheduler.py tests/test_market_scanner_derivatives.py tests/test_climax_engine.py
```

## Task 4: Regression and scope verification

Run from the hotfix workspace:

```bash
.venv/bin/pytest -q
.venv/bin/python -m compileall -q app scripts
.venv/bin/ruff check app/infra/request_scheduler.py tests/test_request_scheduler.py
 git diff --check
 git diff --stat
```

Verify no changes to strategy files/config/schema:

```bash
git diff -- app/signals app/config.py app/storage app/main.py config.yaml
```

Expected: empty for protected paths.

## Task 5: Release/runtime gate

Before deployment, record the current service PID and active release. Package only after all tests pass. Deployment requires one controlled restart and separate authorization at the execution step; no restart is part of this implementation phase.

After eventual activation, verify:

- active release SHA;
- fresh PID and `NRestarts`;
- `Runtime READY` and DB heartbeat;
- completed cycles;
- rate-limit count decreases or is bounded;
- liquidity completeness improves;
- actionable/evaluation/provenance chain remains intact.
