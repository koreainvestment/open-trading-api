# This module exists to validate wave_3x3 runs and summarize signals.

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from examples_llm_trading.trading_system.wave_3x3_run.wave_3x3_run import run_wave_3x3

logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check wave_3x3 run outputs.")
    parser.add_argument("--codes", required=True, help="comma-separated codes")
    parser.add_argument("--zones-csv", required=True, help="path to zone_ABC_report_7codes.csv")
    parser.add_argument("--dry-run", action="store_true", help="do not execute engine")
    return parser.parse_args()


def _resolve_path(path: str) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return Path.cwd() / candidate


def main() -> int:
    args = parse_args()
    result = run_wave_3x3(args.codes, args.zones_csv, dry_run=args.dry_run)
    run_json_path = result.get("run_json", "")
    if not run_json_path:
        print("missing run.json path")
        return 1

    run_json = _resolve_path(run_json_path)
    if not run_json.exists():
        print(f"run.json not found: {run_json}")
        return 1

    payload = json.loads(run_json.read_text(encoding="utf-8"))
    engine_returncode = payload.get("engine_returncode")
    engine_outputs = payload.get("engine_outputs", {})
    stderr_tail = payload.get("engine_stderr_tail", "")
    engine_out_dir = payload.get("engine_out_dir", "")
    zones_csv = payload.get("zones_csv", "")
    asof = payload.get("asof")
    codes = payload.get("codes", [])

    if args.dry_run:
        print(f"dry-run run.json={run_json}")
        return 0

    print("Run Summary:")
    print(f"  run_metadata: {run_json}")
    print(f"  run_dir: {run_json.parent}")
    print(f"  engine_out_dir: {engine_out_dir}")
    print(f"  engine_returncode: {engine_returncode}")
    print(f"  zones_csv: {zones_csv}")
    if asof:
        print(f"  asof: {asof}")
    print(f"  codes: {codes}")

    print("Artifacts:")
    for key in sorted(engine_outputs.keys()):
        print(f"  - {key}: {engine_outputs[key]}")

    if engine_returncode != 0:
        if stderr_tail:
            print(stderr_tail)
        return 2

    missing_outputs = []
    resolved_outputs: dict[str, Path] = {}
    for key, path in engine_outputs.items():
        candidate = _resolve_path(path)
        if not candidate.exists():
            missing_outputs.append(str(candidate))
        else:
            resolved_outputs[key] = candidate

    if missing_outputs:
        print("missing outputs:")
        for path in missing_outputs:
            print(path)
        return 3

    csv_path = None
    for path in resolved_outputs.values():
        if path.name.endswith(".csv") and "wave_3x3_signals" in path.name:
            csv_path = path
            break

    if csv_path:
        df = pd.read_csv(csv_path, dtype={"code": "string", "CODE": "string", "Code": "string"})
        code_col = None
        for candidate in ["code", "CODE", "Code"]:
            if candidate in df.columns:
                code_col = candidate
                break

        if "action" in df.columns and code_col:
            df[code_col] = df[code_col].astype(str).str.strip().str.zfill(6)
            buy_codes = sorted(
                df[df["action"].astype(str).str.startswith("BUY")][code_col].astype(str).tolist()
            )
            sell_codes = sorted(
                df[df["action"].astype(str).str.startswith("SELL")][code_col].astype(str).tolist()
            )
            stop_codes = sorted(
                df[df["action"].astype(str).str.startswith("STOP")][code_col].astype(str).tolist()
            )
        else:
            buy_codes = []
            sell_codes = []
            stop_codes = []

        print(f"오늘 매수 신호: {', '.join(buy_codes) if buy_codes else 'none'}")
        print(f"오늘 매도 신호: {', '.join(sell_codes) if sell_codes else 'none'}")
        print(f"손절 경고: {', '.join(stop_codes) if stop_codes else 'none'}")

        if code_col:
            if code_col != "code" and "code" not in df.columns:
                df = df.rename(columns={code_col: "code"})
            df["code"] = df["code"].astype(str).str.strip().str.zfill(6)
        cols = [c for c in ["code", "price", "entry_stage", "exit_stage", "action"] if c in df.columns]
        if cols:
            print(df[cols].to_string(index=False))
    else:
        print("signals csv not found in outputs")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
