# This module exists to integrate experiments with tools/backtest_signals.py via subprocess.

from __future__ import annotations

import logging
from pathlib import Path
import re
import subprocess
import sys
from typing import Any

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def _sanitize_tail(text: str, limit: int = 2000) -> str:
    if not text:
        return ""
    lines = text.splitlines()
    filtered = []
    for line in lines:
        lowered = line.lower()
        if any(token in lowered for token in ("token", "secret", "app", "key", "account")):
            continue
        filtered.append(line)
    return "\n".join(filtered)[-limit:]


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [
        re.sub(r"[^a-z0-9]+", "_", str(col).strip().lower()).strip("_") for col in df.columns
    ]
    return df


def _normalize_date_value(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    if not text:
        return ""
    parsed = pd.to_datetime(text, errors="coerce")
    if pd.isna(parsed):
        return ""
    return parsed.strftime("%Y-%m-%d")


def _load_trading_calendar(data_dir: Path, code: str) -> list[str]:
    csv_path = data_dir / f"{code}_daily.csv"
    if not csv_path.exists():
        logger.warning("backtest calendar missing: %s", csv_path)
        return []
    try:
        columns = list(pd.read_csv(csv_path, nrows=0).columns)
    except Exception as exc:
        logger.warning("backtest calendar header read failed: %s (%s)", csv_path, exc)
        return []
    date_col = next((col for col in ("date", "Date", "dt", "ymd") if col in columns), None)
    if not date_col:
        logger.warning("backtest calendar missing date column: %s", csv_path)
        return []
    try:
        df = pd.read_csv(csv_path, usecols=[date_col], dtype="string")
    except Exception as exc:
        logger.warning("backtest calendar load failed: %s (%s)", csv_path, exc)
        return []
    dates = [_normalize_date_value(value) for value in df[date_col].tolist()]
    return [date for date in dates if date]


def _parse_kv(stdout: str) -> tuple[dict[str, float], str] | None:
    patterns = {
        "trades": r"\btrades?\b\s*[:=]\s*(\d+(\.\d+)?)",
        "win_rate": r"\bwin[_\s-]*rate\b\s*[:=]\s*(\d+(\.\d+)?)",
        "expectancy_R": r"\bexpectancy\b.*?\bR\b\s*[:=]\s*(-?\d+(\.\d+)?)",
        "max_dd": r"\bmax[_\s-]*dd\b\s*[:=]\s*(-?\d+(\.\d+)?)",
    }
    values: dict[str, float] = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, stdout, flags=re.IGNORECASE)
        if match:
            values[key] = float(match.group(1))
    if not values:
        return None
    note = "parsed:kv"
    win_rate = values.get("win_rate")
    if win_rate is not None and win_rate <= 1:
        note = "parsed:kv(win_rate_fraction)"
    return values, note


def _parse_table(stdout: str) -> tuple[dict[str, float], str] | None:
    lines = stdout.splitlines()
    header_idx = None
    for idx, line in enumerate(lines):
        lowered = line.lower()
        if "label" in lowered and "trades" in lowered and "win" in lowered:
            header_idx = idx
            break
    if header_idx is None:
        return None
    block = []
    for line in lines[header_idx : header_idx + 8]:
        if line.strip():
            block.append(line)
    if len(block) < 2:
        return None
    try:
        df = pd.read_fwf(pd.io.common.StringIO("\n".join(block)))
    except Exception:
        return None
    if df.empty:
        return None
    df = _normalize_columns(df)
    label_col = "label" if "label" in df.columns else None
    if label_col:
        match = df[df[label_col].astype(str).str.lower().isin(["post", "all", "total"])]
        row = match.iloc[0] if not match.empty else df.iloc[0]
    else:
        row = df.iloc[0]

    values: dict[str, float] = {}
    for key in ("trades", "win_rate", "expectancy_r", "max_dd", "avg_r", "avg_hold_days"):
        if key in row:
            try:
                values_key = "expectancy_R" if key == "expectancy_r" else key
                values[values_key] = float(row[key])
            except Exception:
                continue
    if not values:
        return None
    note = "parsed:table"
    win_rate = values.get("win_rate")
    if win_rate is not None and win_rate <= 1:
        note = "parsed:table(win_rate_fraction)"
    return values, note


def _parse_heuristic(stdout: str) -> tuple[dict[str, float], str] | None:
    lines = stdout.splitlines()
    key_lines = []
    for idx, line in enumerate(lines):
        lowered = line.lower()
        if any(token in lowered for token in ("label", "trades", "win_rate", "expectancy")):
            key_lines.append(idx)
    if not key_lines:
        return None
    window_idxs = set()
    for idx in key_lines:
        for j in range(max(0, idx - 5), min(len(lines), idx + 6)):
            window_idxs.add(j)
    for idx in sorted(window_idxs):
        line = lines[idx]
        numbers = re.findall(r"-?\d+(?:\.\d+)?", line)
        if len(numbers) >= 4:
            try:
                trades = float(numbers[0])
                win_rate = float(numbers[1])
                expectancy = float(numbers[2])
                max_dd = float(numbers[3])
                note = "parsed:heuristic"
                if win_rate <= 1:
                    note = "parsed:heuristic(win_rate_fraction)"
                return {
                    "trades": trades,
                    "win_rate": win_rate,
                    "expectancy_R": expectancy,
                    "max_dd": max_dd,
                }, note
            except Exception:
                continue
    return None


def _parse_kpi(stdout: str) -> tuple[dict[str, float], str] | None:
    for parser in (_parse_kv, _parse_table, _parse_heuristic):
        parsed = parser(stdout)
        if parsed:
            return parsed
    return None


def _build_signals_df(
    source: pd.DataFrame, code: str, calendar: list[str] | None
) -> tuple[pd.DataFrame, bool]:
    if "code" not in source.columns or "action" not in source.columns:
        return pd.DataFrame(columns=["date", "signal"]), False
    date_col = "asof" if "asof" in source.columns else "date" if "date" in source.columns else None
    if not date_col:
        return pd.DataFrame(columns=["date", "signal"]), False
    subset = source[source["code"].astype(str) == code]
    subset = subset[subset["action"].astype(str).str.startswith("BUY")]
    if subset.empty:
        return pd.DataFrame(columns=["date", "signal"]), False
    subset = subset.copy()
    subset[date_col] = subset[date_col].map(_normalize_date_value)
    subset = subset[subset[date_col] != ""]
    if subset.empty:
        return pd.DataFrame(columns=["date", "signal"]), False
    shift_applied = False
    if calendar and len(calendar) >= 2:
        last_date = calendar[-1]
        prev_date = calendar[-2]
        mask = subset[date_col] == last_date
        if mask.any():
            subset.loc[mask, date_col] = prev_date
            shift_applied = True
    return (
        pd.DataFrame(
            {
                "date": subset[date_col],
                "signal": ["wave_buy"] * len(subset),
            }
        ),
        shift_applied,
    )


def _append_shift_note(note: str, shift_note: str) -> str:
    if shift_note in note:
        return note
    return f"{note};{shift_note}"


def run_backtest_for_signals(
    mode: str,
    run_dir: Path,
    signals_csv: Path | None,
    signals_json: Path | None,
    codes: list[str],
    data_dir: Path | None = None,
) -> dict[str, Any]:
    shift_note = "signal_date_shift:none"
    if signals_csv is None or not signals_csv.exists():
        return {
            "trades": 0,
            "win_rate": float("nan"),
            "expectancy_R": float("nan"),
            "max_dd": float("nan"),
            "avg_hold_days": float("nan"),
            "avg_R": float("nan"),
            "raw_stdout_tail": "",
            "raw_stderr_tail": "",
            "returncode": 1,
            "note": _append_shift_note("signals not found; backtest skipped", shift_note),
        }

    try:
        df = pd.read_csv(signals_csv, dtype="string")
    except Exception as exc:
        return {
            "trades": 0,
            "win_rate": float("nan"),
            "expectancy_R": float("nan"),
            "max_dd": float("nan"),
            "avg_hold_days": float("nan"),
            "avg_R": float("nan"),
            "raw_stdout_tail": "",
            "raw_stderr_tail": "",
            "returncode": 1,
            "note": _append_shift_note(f"signals read failed: {exc}", shift_note),
        }

    data_dir_path = data_dir or Path("data")
    calendar_cache: dict[str, list[str]] = {}
    shift_applied = False

    totals = {
        "trades": 0,
        "win_rate": float("nan"),
        "expectancy_R": float("nan"),
        "max_dd": float("nan"),
        "avg_hold_days": float("nan"),
        "avg_R": float("nan"),
    }
    weighted = {"win_rate": 0.0, "expectancy_R": 0.0, "avg_R": 0.0, "avg_hold_days": 0.0}
    total_trades = 0
    max_dd = 0.0
    stdout_tail = ""
    stderr_tail = ""
    last_returncode = 0
    parsed_note: str | None = None

    for code in codes:
        if code not in calendar_cache:
            calendar_cache[code] = _load_trading_calendar(data_dir_path, code)
        signals_df, shifted = _build_signals_df(df, code, calendar_cache[code])
        if shifted:
            shift_applied = True
        if signals_df.empty:
            continue

        temp_path = run_dir / f"signals_{code}_{mode}.csv"
        signals_df.to_csv(temp_path, index=False)

        cmd = [sys.executable, "tools/backtest_signals.py", "--code", code]
        daily_path = data_dir_path / f"{code}_daily.csv"
        if daily_path.exists():
            cmd.extend(["--input", str(daily_path)])
        cmd.extend(["--signals", str(temp_path)])
        result = subprocess.run(cmd, capture_output=True, text=True, check=False, cwd=Path.cwd())
        last_returncode = result.returncode
        stdout_tail = _sanitize_tail(result.stdout)
        stderr_tail = _sanitize_tail(result.stderr)
        if result.returncode != 0:
            continue

        parsed = _parse_kpi(result.stdout)
        parsed_values: dict[str, float] = {}
        if parsed:
            parsed_values, parsed_note = parsed

        trades = int(parsed_values.get("trades", 0)) if parsed_values else 0
        win_rate = float(parsed_values.get("win_rate", float("nan"))) if parsed_values else float("nan")
        expectancy = float(parsed_values.get("expectancy_R", float("nan"))) if parsed_values else float("nan")
        avg_r = float(parsed_values.get("avg_R", float("nan"))) if parsed_values else float("nan")
        avg_hold = float(parsed_values.get("avg_hold_days", float("nan"))) if parsed_values else float("nan")
        max_dd = max(max_dd, float(parsed_values.get("max_dd", 0.0)) if parsed_values else 0.0)

        if trades > 0:
            total_trades += trades
            weighted["win_rate"] += win_rate * trades
            weighted["expectancy_R"] += expectancy * trades
            weighted["avg_R"] += avg_r * trades
            weighted["avg_hold_days"] += avg_hold * trades

    if total_trades > 0:
        totals["trades"] = total_trades
        totals["win_rate"] = round(weighted["win_rate"] / total_trades, 2)
        totals["expectancy_R"] = round(weighted["expectancy_R"] / total_trades, 3)
        totals["avg_R"] = round(weighted["avg_R"] / total_trades, 3)
        totals["avg_hold_days"] = round(weighted["avg_hold_days"] / total_trades, 2)
        totals["max_dd"] = round(max_dd, 2)
        note = parsed_note or "parsed:table"
    else:
        totals["max_dd"] = round(max_dd, 2)
        if parsed_note:
            note = "placeholder:no_closed_trades_suspected"
        elif last_returncode != 0:
            note = "placeholder:backtest_rc_nonzero"
        elif not stdout_tail:
            note = "placeholder:empty_stdout"
        else:
            lowered = stdout_tail.lower()
            if "trades" in lowered and "0" in lowered:
                note = "placeholder:no_closed_trades_suspected"
            else:
                note = "placeholder:no_kpi_lines"

    if shift_applied:
        shift_note = "signal_date_shift:-1bar"
    note = _append_shift_note(note, shift_note)

    return {
        **totals,
        "raw_stdout_tail": stdout_tail,
        "raw_stderr_tail": stderr_tail,
        "returncode": last_returncode,
        "note": note,
    }
