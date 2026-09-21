# Source of truth

## Purpose

This document prevents the public GitHub checkout, a server release, and research artifacts from being presented as the same system.

## Evidence labels

- **Baseline-verified:** directly verified in the public checkout at `ce77d744`.
- **Production-reported:** supplied from the operator's production release inventory; the release object is not present in this shallow public clone.
- **Historical/experimental:** retained for comparison; not active production.
- **Not verified:** a claim for which this repository has no reproducible artifact.

## Release map

| Layer | Identifier | Date | Status | Evidence boundary |
|---|---|---:|---|---|
| Public GitHub baseline | `ce77d744` | 2026-09-08 | Baseline-verified | Source files and tests in this repository |
| Lane A production | `bf47d2b1d2b0b159da780dc337adefe3dcd2b6e71c13c2506721c4c816be92ea` | 2026-09-14 | Production-reported | External operator release artifact; not a Git object in this clone |
| Lane B | `dfcdb9df3e6c6a3667fa914e3ea0189f7a6f8e35db43ac530ba8db51b69f7553` | 2026-09-17 | Historical/experimental | External operator release artifact; inactive and not a Git object here |

The short identifiers are documentation aliases for the release identifiers above, not claims that those objects are reachable from `origin/main`.

## Canonical sources by topic

| Topic | Baseline source | Production status | Notes |
|---|---|---|---|
| Feature formulas | `app/features/` | Verify against the production artifact before applying operationally | This document describes baseline implementation exactly. |
| Strategy gates | `app/signals/`, `app/events/` | Production overlay may differ | See `STRATEGIES.md`. |
| Baseline score/grade | `app/signals/scoring.py`, `app/signals/engine.py` | Release-specific | Do not infer production settings from `config.example.yaml`. |
| Market-data semantics | `app/market_data/`, `app/features/builder.py` | Release-specific | See `MARKET_DATA.md`. |
| Persistence and delivery | `app/storage/`, `app/runtime/`, `app/notifications/` | Production additive warning backport reported | See `DATA_MODEL.md` and `DELIVERY.md`. |
| Deployment | `deploy/`, `docs/deployment.md` | Private operator runbook | Paths and credentials are intentionally abstracted here. |
| Research/shadow | `research/`, `docs/SHADOW_VALIDATION.md` | Non-production | Never treat shadow observations as live signals. |

## Current production boundary

The operator-reported active configuration is Lane A `bf47d2b1` with:

- `shortlist_size: 100`;
- `min_24h_volume: 5,000,000`;
- `AUTOEXECUTION=OFF`;
- manual entry only;
- Lane B inactive;
- `EARLY_DROP_WARNING` as a separate non-actionable stream.

The later `111`-symbol / `$3M` candidate is not current production. Its rollout was stopped after incomplete-data and cycle-capacity observations.

## Non-negotiable interpretation rules

```text
NO_SETUP is valid only after SCANNED_OK.
EARLY_DROP_WARNING != SHORT_SIGNAL.
WATCH != ACTIONABLE_SHORT_SIGNAL.
AUTOEXECUTION=OFF.
```

No production database, Telegram routing identifier, token, private URL, or credential is part of this repository.
