# This module exists to invoke the wave_3x3 engine via subprocess safely.

from __future__ import annotations

import logging
from pathlib import Path
import subprocess
import sys
from typing import Iterable

from mn_trading.strategy.wave_3x3.types import Wave3x3RunRequest, Wave3x3RunResult

logger = logging.getLogger(__name__)


def _find_outputs(base_dir: Path) -> dict[str, str]:
    outputs: dict[str, str] = {}
    candidates = [
        "wave_3x3_signals_*.csv",
        "wave_3x3_signals_*.json",
        "position_state.json",
    ]

    for pattern in candidates:
        matches = sorted(base_dir.glob(pattern))
        for match in matches:
            if match.exists():
                key = match.name
                try:
                    outputs[key] = str(match.relative_to(Path.cwd()))
                except ValueError:
                    outputs[key] = str(match)

    return outputs


def _sanitize_args(args: Iterable[str]) -> list[str]:
    return [arg for arg in args if arg]


def run_wave_3x3_engine(req: Wave3x3RunRequest) -> Wave3x3RunResult:
    codes = [c.strip() for c in req.codes if c.strip()]
    cmd = [
        sys.executable,
        "tools/wave_3x3_engine.py",
        "--codes",
        ",".join(codes),
        "--zones-csv",
        req.zones_csv,
        "--out",
        req.engine_out_dir,
    ]
    if req.data_dir:
        cmd.extend(["--data-dir", req.data_dir])
    if req.extra_args:
        cmd.extend(_sanitize_args(req.extra_args))

    engine_out = Path(req.engine_out_dir)
    engine_out.mkdir(parents=True, exist_ok=True)

    logger.info("wave_3x3 subprocess command=%s", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    logger.info("wave_3x3 returncode=%s", result.returncode)
    if result.stderr:
        logger.warning("wave_3x3 stderr detected (len=%s)", len(result.stderr))

    outputs = {} if result.returncode != 0 else _find_outputs(engine_out)
    return Wave3x3RunResult(
        returncode=result.returncode,
        stdout=result.stdout,
        stderr=result.stderr,
        outputs=outputs,
        asof=req.asof,
        codes=codes,
    )
