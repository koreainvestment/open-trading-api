# This module exists to apply reproducible perturbations for experiment baselines.

from __future__ import annotations

import logging
import random
from typing import Tuple

import pandas as pd

logger = logging.getLogger(__name__)


def perturb_actions(df: pd.DataFrame, seed: int, p: float = 0.3) -> Tuple[pd.DataFrame, int]:
    rng = random.Random(seed)
    if "action" not in df.columns:
        return df, 0

    updated = df.copy()
    changes = 0
    actions = updated["action"].astype(str)
    new_actions = []
    for action in actions:
        if action.startswith("STOP"):
            new_actions.append(action)
            continue
        if action.startswith("BUY") or action.startswith("SELL"):
            if rng.random() < p:
                new_actions.append("NONE")
                changes += 1
            else:
                new_actions.append(action)
        else:
            new_actions.append(action)

    updated["action"] = new_actions
    logger.info("perturb_actions changes=%s p=%s", changes, p)
    return updated, changes
