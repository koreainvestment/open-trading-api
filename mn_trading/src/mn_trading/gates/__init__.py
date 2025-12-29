# This module exists to expose a unified gate interface across rule and LLM modes.

from __future__ import annotations

from typing import Any

import pandas as pd

from mn_trading.gates.llm_gate import apply_llm_gate_to_signals
from mn_trading.gates.rule_gate import apply_rule_gate_to_signals


def apply_gate_to_signals(
    df: pd.DataFrame,
    gate_mode: str,
    seed: int,
    llm_model: str | None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    if gate_mode == "rule":
        return apply_rule_gate_to_signals(df, seed)
    if gate_mode == "llm":
        return apply_llm_gate_to_signals(df, seed, llm_model)
    summary = {
        "gate_mode": "none",
        "applied_days": 0,
        "decisions": {},
    }
    return df.copy(), summary
