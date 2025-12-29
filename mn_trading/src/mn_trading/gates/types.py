# This module exists to define gate decision types shared across gate modes.

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class GateDecision:
    decision: Literal["ALLOW", "BLOCK", "REVIEW"]
    confidence: float
    reason: str
    risk_flags: list[str]
