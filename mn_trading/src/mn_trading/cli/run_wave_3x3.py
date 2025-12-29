# This module exists to provide a placeholder CLI for the mn_trading 3x3 runner.

from __future__ import annotations

import argparse
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from mn_trading.config.settings import load_settings
from mn_trading.strategy.wave_3x3.adapter import run_wave_3x3_engine
from mn_trading.strategy.wave_3x3.types import Wave3x3RunRequest

logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="mn_trading wave_3x3 placeholder runner.")
    parser.add_argument("--codes", required=True, help="comma-separated codes")
    parser.add_argument("--asof", help="asof date (YYYY-MM-DD)")
    parser.add_argument("--dry-run", action="store_true", help="do not execute, only log metadata")
    parser.add_argument("--zones-csv", required=True, help="path to zone_ABC_report_7codes.csv")
    parser.add_argument("--extra-args", nargs="*", default=[], help="extra args for future engine calls")
    return parser.parse_args()


def build_run_metadata(
    codes: list[str],
    asof: str | None,
    dry_run: bool,
    extra_args: list[str],
    zones_csv: str | None,
    engine_out_dir: str,
) -> dict[str, Any]:
    settings = load_settings()
    return {
        "timestamp": datetime.now().isoformat(),
        "codes": codes,
        "asof": asof,
        "dry_run": dry_run,
        "extra_args": extra_args,
        "zones_csv": zones_csv,
        "engine_out_dir": engine_out_dir,
        "settings": {
            "mode": settings.mode,
            "product": settings.product,
            "out_dir": settings.out_dir,
            "state_file": settings.state_file,
            "openai_model": settings.openai_model,
            "openai_temperature": settings.openai_temperature,
        },
        "engine_invoked": False,
        "engine_returncode": None,
        "engine_outputs": {},
        "engine_stdout_tail": "",
        "engine_stderr_tail": "",
    }


def main() -> int:
    args = parse_args()
    codes = [c.strip() for c in args.codes.split(",") if c.strip()]
    settings = load_settings()
    out_dir = Path(settings.out_dir)
    run_dir = out_dir / "mn_trading" / "run_wave_3x3" / datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir.mkdir(parents=True, exist_ok=True)
    engine_out_dir = run_dir / "engine_out"
    metadata = build_run_metadata(
        codes,
        args.asof,
        args.dry_run,
        args.extra_args,
        args.zones_csv,
        str(engine_out_dir),
    )
    run_path = run_dir / "run.json"

    if not args.dry_run:
        extra_args = list(args.extra_args)
        if "--zones-csv" not in extra_args:
            extra_args = ["--zones-csv", args.zones_csv] + extra_args
        req = Wave3x3RunRequest(
            codes=codes,
            zones_csv=args.zones_csv,
            engine_out_dir=str(engine_out_dir),
            asof=args.asof,
            extra_args=extra_args,
        )
        result = run_wave_3x3_engine(req)
        metadata["engine_invoked"] = True
        metadata["engine_returncode"] = result.returncode
        metadata["engine_outputs"] = result.outputs
        metadata["engine_stdout_tail"] = result.stdout[-1000:] if result.stdout else ""
        metadata["engine_stderr_tail"] = result.stderr[-1000:] if result.stderr else ""

    run_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    print(f"settings.mode={metadata['settings']['mode']}")
    print(f"dry_run={metadata['dry_run']}")
    print(f"run_metadata={run_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
