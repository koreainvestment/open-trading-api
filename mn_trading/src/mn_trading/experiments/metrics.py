# This module exists to compute experiment KPIs from signals outputs.

from __future__ import annotations

from pathlib import Path
from typing import Any

from mn_trading.experiments.backtest_adapter import run_backtest_for_signals


def compute_metrics(
    mode: str,
    run_dir: Path,
    signals_csv: Path | None,
    signals_json: Path | None,
    codes: list[str],
    data_dir: Path | None = None,
) -> dict[str, Any]:
    return run_backtest_for_signals(
        mode=mode,
        run_dir=run_dir,
        signals_csv=signals_csv,
        signals_json=signals_json,
        codes=codes,
        data_dir=data_dir,
    )
