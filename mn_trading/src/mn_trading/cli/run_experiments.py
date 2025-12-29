# This module exists to run reproducible wave_3x3 experiment batches.

from __future__ import annotations

import argparse
import logging
from typing import Any

from mn_trading.experiments.runner import run_experiments

logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run wave_3x3 experiment batch.")
    parser.add_argument("--codes", required=True, help="comma-separated codes")
    parser.add_argument("--zones-csv", required=True, help="path to zone_ABC_report_7codes.csv")
    parser.add_argument("--runs", type=int, default=10, help="number of runs per mode")
    parser.add_argument("--seed", type=int, default=42, help="random seed")
    parser.add_argument("--mode", choices=["all", "rule", "random", "llm"], default="all")
    parser.add_argument("--out-root", default="out/mn_trading/experiments", help="output root directory")
    parser.add_argument("--walk-forward-bars", dest="walk_forward_bars", type=int, default=0)
    parser.add_argument("--wf-days", dest="walk_forward_bars", type=int, default=0)
    parser.add_argument("--src-data-dir", default="data", help="source daily CSV directory")
    parser.add_argument("--gate-mode", choices=["none", "rule", "llm"], default="none")
    parser.add_argument(
        "--llm-gate-policy",
        choices=["strong", "A", "B", "C"],
        default="C",
        help="llm gate policy (used only when --gate-mode=llm)",
    )
    parser.add_argument("--llm-model", default=None)
    parser.add_argument("--reuse-exp-id", default=None)
    parser.add_argument("--dry-run", action="store_true", help="print plan only")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.walk_forward_bars > 0 and args.runs != 1:
        raise SystemExit(
            "walk-forward-bars > 0 requires --runs 1 (engine is executed only once per "
            "trade_date for rule; repeating runs explodes engine calls)."
        )
    codes = [c.strip() for c in args.codes.split(",") if c.strip()]
    result = run_experiments(
        codes=codes,
        zones_csv=args.zones_csv,
        runs=args.runs,
        seed=args.seed,
        mode=args.mode,
        out_root=args.out_root,
        dry_run=args.dry_run,
        walk_forward_bars=args.walk_forward_bars,
        src_data_dir=args.src_data_dir,
        gate_mode=args.gate_mode,
        llm_gate_policy=args.llm_gate_policy,
        llm_model=args.llm_model,
        reuse_exp_id=args.reuse_exp_id,
    )

    if args.dry_run:
        print(result["plan"])
        return 0

    print(f"exp_id={result['exp_id']}")
    print(f"summary={result['summary']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
