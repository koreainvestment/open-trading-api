# This module exists to provide a KIS-style one-line runner for wave_3x3.

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
import subprocess
import sys
from typing import Any

logger = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _repo_root() -> Path:
    return ROOT


def _build_env() -> dict[str, str]:
    env = os.environ.copy()
    pythonpath = env.get("PYTHONPATH", "")
    root = _repo_root()
    mn_path = str(root / "mn_trading" / "src")
    if pythonpath:
        env["PYTHONPATH"] = f"{mn_path}{os.pathsep}{pythonpath}"
    else:
        env["PYTHONPATH"] = mn_path
    return env


def _find_run_json(stdout: str, root: Path) -> Path | None:
    for line in stdout.splitlines():
        if line.startswith("run_metadata="):
            path = line.split("=", 1)[1].strip()
            candidate = Path(path)
            if not candidate.is_absolute():
                candidate = root / candidate
            return candidate

    run_root = root / "out" / "mn_trading" / "run_wave_3x3"
    if not run_root.exists():
        return None
    candidates = sorted(run_root.glob("*/run.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0] if candidates else None


def run_wave_3x3(codes: str, zones_csv: str, dry_run: bool = False) -> dict[str, Any]:
    root = _repo_root()
    cmd = [
        sys.executable,
        "mn_trading/src/mn_trading/cli/run_wave_3x3.py",
        "--codes",
        codes,
        "--zones-csv",
        zones_csv,
    ]
    if dry_run:
        cmd.append("--dry-run")

    logger.info("run_wave_3x3 cmd=%s", " ".join(cmd))
    result = subprocess.run(cmd, cwd=root, env=_build_env(), capture_output=True, text=True, check=False)
    if result.stderr:
        logger.warning("run_wave_3x3 stderr detected (len=%s)", len(result.stderr))

    run_json = _find_run_json(result.stdout, root)
    engine_returncode = None
    engine_outputs: dict[str, str] = {}

    if run_json and run_json.exists():
        try:
            payload = json.loads(run_json.read_text(encoding="utf-8"))
            engine_returncode = payload.get("engine_returncode")
            engine_outputs = payload.get("engine_outputs", {})
        except json.JSONDecodeError:
            logger.warning("run_wave_3x3 run.json parse failed")

    return {
        "run_json": str(run_json) if run_json else "",
        "engine_returncode": engine_returncode,
        "engine_outputs": engine_outputs,
    }
