"""Independent TRAPPED_LONGS_REVERSAL evaluator and lifecycle."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

import pandas as pd

from app.domain import EventState, SymbolFeatures

TRAPPED_LONGS_REVERSAL = "TRAPPED_LONGS_REVERSAL"
TRAPPED_LONGS_MODEL_VERSION = "trapped-longs-v1"


@dataclass(slots=True)
class TrappedLongsEvaluation:
    subtype: str | None
    score: int
    grade: str
    metadata: dict[str, Any]
    veto_reasons: list[str]
    data_quality: list[str]

    @property
    def actionable(self) -> bool:
        return self.subtype == TRAPPED_LONGS_REVERSAL and not self.veto_reasons and self.grade in {"A", "B"}


@dataclass(slots=True)
class TrappedLongsLifecycle:
    state: str
    event_revision: int
    root_created_at: datetime
    breakout_at: datetime
    last_observed_at: datetime
    veto_reasons: list[str]
    expired: bool = False


def _cfg(config: Any, name: str, default: Any) -> Any:
    return getattr(config, name, default)


def evaluate_trapped_longs_reversal(
    state: EventState, features: SymbolFeatures, frame: pd.DataFrame, config: Any
) -> TrappedLongsEvaluation:
    """Evaluate only the trapped-long reversal contract; never mutates ``state``."""
    metadata: dict[str, Any] = {"strategy_type": "TRAPPED_LONGS", "strategy_subtype": TRAPPED_LONGS_REVERSAL, "model_version": TRAPPED_LONGS_MODEL_VERSION}
    vetoes: list[str] = []
    reference = (state.event_features_snapshot or {}).get("breakout_reference")
    if reference is None or not state.event_id:
        vetoes.append("breakout_reference_missing" if reference is None else "no_established_event")
        reference = float(reference or 0)
    reference = float(reference)
    metadata["breakout_reference"] = reference
    event_high = float(state.event_high or 0)
    metadata["event_high"] = event_high
    if reference <= 0 or event_high <= 0:
        vetoes.append("invalid_breakout_reference")

    asof = pd.Timestamp(features.asof).tz_convert("UTC")
    if "timestamp" in frame and not frame.empty:
        timestamps = pd.to_datetime(frame["timestamp"], utc=True, errors="coerce")
        closed = frame.loc[(timestamps + pd.Timedelta(minutes=5)) <= asof]
        breakout_time = pd.Timestamp(state.event_high_time or state.event_start_time or features.asof)
        breakout_time = breakout_time.tz_localize("UTC") if breakout_time.tzinfo is None else breakout_time.tz_convert("UTC")
        after_breakout = closed.loc[timestamps.loc[closed.index] > breakout_time]
    else:
        after_breakout = frame.iloc[0:0]
    closed_count = len(after_breakout)
    metadata["closed_structural_candles"] = closed_count
    if closed_count < int(_cfg(config, "trapped_longs_min_closed_candles", 2)):
        vetoes.append("insufficient_closed_structural_candles")

    observed_high = max([event_high, float(features.last_high or 0)] + ([float(after_breakout["high"].max())] if not after_breakout.empty else []))
    tolerance = float(_cfg(config, "trapped_longs_new_high_tolerance_pct", 0.30))
    if observed_high > event_high * (1 + tolerance / 100):
        vetoes.append("new_high_before_delivery")
    breakout = observed_high > reference
    if not breakout:
        vetoes.append("breakout_not_confirmed")
    close = float(features.last_close or features.price)
    if close >= reference:
        vetoes.append("close_not_below_breakout_reference")
    if not features.latest_failed_retest:
        vetoes.append("failed_retest_missing")
    rejection = float(features.rejection_from_high_pct or 0)
    if rejection < float(_cfg(config, "trapped_longs_min_rejection_pct", 1.0)):
        vetoes.append("rejection_below_threshold")

    oi = features.oi_change_15m
    metadata["oi_change_15m_pct"] = oi
    if oi is None or features.derivatives_status in {"MISSING", "RATE_LIMITED", "API_ERROR"}:
        vetoes.append("oi_missing")
    elif oi < float(_cfg(config, "trapped_longs_min_oi_change_15m_pct", 1.0)):
        vetoes.append("oi_below_threshold")

    if not features.liquidity_available:
        vetoes.append("liquidity_unavailable")
    else:
        if features.spread_pct is None or features.slippage_pct is None or features.orderbook_depth_usdt_1pct is None or features.orderbook_depth_usdt_2pct is None:
            vetoes.append("liquidity_incomplete")
        elif (features.spread_pct > _cfg(config, "trapped_longs_max_spread_pct", .80) or features.slippage_pct > _cfg(config, "trapped_longs_max_slippage_pct", 1.0) or features.orderbook_depth_usdt_1pct < _cfg(config, "trapped_longs_min_depth_1pct_usdt", 5000) or features.orderbook_depth_usdt_2pct < _cfg(config, "trapped_longs_min_depth_2pct_usdt", 10000)):
            vetoes.append("liquidity_block")

    flags = [bool(state.event_id), breakout, closed_count >= 2, close < reference, bool(features.latest_failed_retest), oi is not None and oi >= 1.0, not any(r == "new_high_before_delivery" for r in vetoes)]
    score = min(100, 10 + 15 * sum(flags))
    grade = "A" if score >= 85 else "B" if score >= 70 else "C"
    metadata.update({"close_below_breakout_reference": close < reference, "failed_retest_confirmed": bool(features.latest_failed_retest), "no_new_high": "new_high_before_delivery" not in vetoes, "rejection_pct": rejection})
    admitted = not vetoes and score >= int(_cfg(config, "trapped_longs_min_signal_score", 70)) and grade in {"A", "B"}
    return TrappedLongsEvaluation(TRAPPED_LONGS_REVERSAL if admitted else None, score, grade, metadata, vetoes, [])


def advance_trapped_longs_lifecycle(*, root_created_at: datetime, breakout_at: datetime, observed_at: datetime, event_revision: int, breakout_confirmed: bool, oi_confirmed: bool, closed_candles: int, close_below_reference: bool, failed_retest: bool, no_new_high: bool, liquidity_ok: bool, rejection_ok: bool, max_lifetime_minutes: int = 15) -> TrappedLongsLifecycle:
    if observed_at < root_created_at:
        raise ValueError("observed_at cannot precede root_created_at")
    base = dict(event_revision=event_revision, root_created_at=root_created_at, breakout_at=breakout_at, last_observed_at=observed_at)
    if observed_at - root_created_at > timedelta(minutes=max_lifetime_minutes):
        return TrappedLongsLifecycle(state="EXPIRED", veto_reasons=["root_lifetime_expired"], expired=True, **base)
    checks = [(breakout_confirmed, "breakout_not_confirmed"), (oi_confirmed, "oi_not_confirmed"), (closed_candles >= 2, "insufficient_closed_structural_candles"), (close_below_reference, "close_not_below_breakout_reference"), (failed_retest, "failed_retest_missing"), (no_new_high, "new_high_before_delivery"), (liquidity_ok, "liquidity_not_confirmed"), (rejection_ok, "rejection_missing")]
    reasons = [reason for passed, reason in checks if not passed]
    return TrappedLongsLifecycle(state="ADMITTED" if not reasons else "RETEST_IN_PROGRESS", veto_reasons=reasons, **base)


def trapped_longs_root_event_id(symbol: str, breakout_identity: str) -> str:
    return f"trapped_longs:{symbol}:{breakout_identity}"


def _identity(kind: str, symbol: str, breakout_identity: str, revision: int) -> str:
    return f"trapped_longs:{kind}:{symbol}:{breakout_identity}:r{revision}"


def trapped_longs_attempt_id(symbol: str, breakout_identity: str, revision: int = 1) -> str:
    return _identity("attempt", symbol, breakout_identity, revision)


def trapped_longs_evaluation_id(symbol: str, breakout_identity: str, revision: int = 1) -> str:
    return _identity("evaluation", symbol, breakout_identity, revision)


def trapped_longs_admission_id(symbol: str, breakout_identity: str, revision: int = 1) -> str:
    return _identity("admission", symbol, breakout_identity, revision)
