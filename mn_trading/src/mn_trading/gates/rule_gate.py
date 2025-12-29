# This module exists to apply a deterministic rule-based gate to signals.

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from mn_trading.gates.types import GateDecision


def _date_key(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def apply_rule_gate_to_signals(
    df: pd.DataFrame, seed: int
) -> tuple[pd.DataFrame, dict[str, Any]]:
    if df.empty:
        return df.copy(), {"gate_mode": "rule", "applied_days": 0, "decisions": {}}
    date_col = "date" if "date" in df.columns else "asof" if "asof" in df.columns else None
    if not date_col:
        return df.copy(), {"gate_mode": "rule", "applied_days": 0, "decisions": {}}

    out = df.copy()
    decisions: dict[str, str] = {}
    allow_days = 0
    block_days = 0
    review_days = 0
    applied_days = 0

    grouped = out.groupby(date_col)
    for date_value, group in grouped:
        date_str = _date_key(date_value)
        buy_mask = group["action"].astype(str).str.startswith("BUY")
        buy_count = int(buy_mask.sum())
        if buy_count == 0:
            continue
        applied_days += 1

        has_missing_price = False
        if "price" in group.columns:
            buy_prices = group.loc[buy_mask, "price"]
            has_missing_price = buy_prices.isna().any()

        decision = GateDecision(
            decision="ALLOW",
            confidence=0.9,
            reason="default allow",
            risk_flags=[],
        )
        if buy_count >= 2 or has_missing_price:
            decision = GateDecision(
                decision="BLOCK",
                confidence=0.7,
                reason="multi_buy_or_missing_price",
                risk_flags=["multi_buy"] if buy_count >= 2 else ["missing_price"],
            )
        elif "entry_stage" in group.columns:
            entry_stage = pd.to_numeric(
                group.loc[buy_mask, "entry_stage"], errors="coerce"
            ).fillna(0)
            if buy_count == 1 and int(entry_stage.iloc[0]) == 0:
                decision = GateDecision(
                    decision="REVIEW",
                    confidence=0.6,
                    reason="initial_entry_review",
                    risk_flags=["early_entry"],
                )

        decisions[date_str] = decision.decision
        if decision.decision == "BLOCK":
            block_days += 1
            idxs = group.index[buy_mask]
            out.loc[idxs, "action"] = "HOLD"
        elif decision.decision == "REVIEW":
            review_days += 1
            rng = np.random.RandomState(seed + abs(hash(date_str)) % 10_000)
            idxs = group.index[buy_mask]
            drop_mask = rng.rand(len(idxs)) < 0.5
            out.loc[idxs[drop_mask], "action"] = "HOLD"
        else:
            allow_days += 1

    summary = {
        "gate_mode": "rule",
        "applied_days": applied_days,
        "allow_days": allow_days,
        "block_days": block_days,
        "review_days": review_days,
        "decisions": decisions,
    }
    return out, summary
