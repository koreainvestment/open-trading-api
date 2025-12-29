# This module exists to orchestrate reproducible experiment runs for wave_3x3.

from __future__ import annotations

import json
import logging
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

import pandas as pd

from mn_trading.experiments.datasets import get_last_n_trade_dates, prepare_cut_dataset
from mn_trading.experiments.metrics import compute_metrics
from mn_trading.experiments.perturbations import perturb_actions
from mn_trading.gates.llm_gate import apply_llm_gate_to_signals
from mn_trading.gates.rule_gate import apply_rule_gate_to_signals
from mn_trading.strategy.wave_3x3.adapter import run_wave_3x3_engine
from mn_trading.strategy.wave_3x3.types import Wave3x3RunRequest

logger = logging.getLogger(__name__)


def _exp_id(codes_count: int) -> str:
    return f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{codes_count}codes"


def _run_id(index: int) -> str:
    return f"run_{index:03d}"


def _find_signals_csv(engine_out_dir: Path) -> Path | None:
    candidates = sorted(engine_out_dir.glob("wave_3x3_signals_*.csv"))
    for path in candidates:
        if path.name.endswith(".random.csv"):
            continue
        return path
    return None


def _normalize_for_aggregation(df: pd.DataFrame) -> pd.DataFrame | None:
    if df.empty:
        return None
    if "asof" in df.columns:
        df = df.copy()
        df["date"] = df["asof"]
        return df
    if "date" in df.columns:
        return df.copy()
    return None


def count_gate_applied_days(rule_df: pd.DataFrame) -> int:
    if rule_df.empty:
        return 0
    date_col = "date" if "date" in rule_df.columns else "asof" if "asof" in rule_df.columns else None
    if not date_col or "action" not in rule_df.columns:
        return 0
    buy_mask = rule_df["action"].astype(str).str.startswith("BUY")
    if not bool(buy_mask.any()):
        return 0
    grouped = rule_df.loc[buy_mask].groupby(date_col)
    return int(grouped.size().shape[0])


def build_llm_signals_from_rule(
    rule_df: pd.DataFrame,
    gate_mode: str,
    seed: int,
    llm_model: str | None,
    llm_gate_policy: str,
    zones_csv_path: str | None,
    daily_data_dir: str | None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    if rule_df.empty:
        return rule_df.copy(), {
            "gate_mode": gate_mode,
            "noop": True,
            "applied_days": 0,
            "llm_call_total": 0,
            "llm_decision_valid": 0,
            "llm_decision_block": 0,
            "llm_decision_allow": 0,
            "llm_noop_total": 0,
            "noop_reasons": {},
            "model": llm_model or "",
        }
    if gate_mode == "none":
        return rule_df.copy(), {
            "gate_mode": "none",
            "noop": True,
            "applied_days": 0,
            "llm_call_total": 0,
            "llm_decision_valid": 0,
            "llm_decision_block": 0,
            "llm_decision_allow": 0,
            "llm_noop_total": 0,
            "noop_reasons": {},
            "model": llm_model or "",
        }
    if gate_mode == "rule":
        df, summary = apply_rule_gate_to_signals(rule_df, seed)
        summary["gate_mode"] = "rule"
        summary.setdefault("llm_call_total", 0)
        summary.setdefault("llm_decision_valid", 0)
        summary.setdefault("llm_decision_block", 0)
        summary.setdefault("llm_decision_allow", 0)
        summary.setdefault("llm_noop_total", 0)
        summary.setdefault("noop_reasons", {})
        summary.setdefault("model", llm_model or "")
        return df, summary
    df, summary = apply_llm_gate_to_signals(
        rule_df,
        seed,
        llm_model,
        policy=llm_gate_policy,
        zones_csv_path=zones_csv_path,
        daily_data_dir=daily_data_dir,
    )
    summary["gate_mode"] = "llm"
    summary["llm_gate_policy"] = llm_gate_policy
    return df, summary


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _as_relative(path: Path) -> str:
    try:
        return str(path.relative_to(Path.cwd()))
    except ValueError:
        return str(path)


def run_experiments(
    codes: list[str],
    zones_csv: str,
    runs: int,
    seed: int,
    mode: str,
    out_root: str,
    dry_run: bool,
    walk_forward_bars: int,
    src_data_dir: str,
    gate_mode: str,
    llm_gate_policy: str,
    llm_model: str | None,
    reuse_exp_id: str | None,
) -> dict[str, Any]:
    modes = ["rule", "random", "llm"] if mode == "all" else [mode]
    exp_id = reuse_exp_id or _exp_id(len(codes))
    root_dir = Path(out_root) / exp_id
    dataset_root = Path(out_root).parent / "datasets"

    plan = {
        "exp_id": exp_id,
        "modes": modes,
        "runs": runs,
        "out_root": _as_relative(root_dir),
        "gate_mode": gate_mode,
        "llm_gate_policy": llm_gate_policy,
    }
    trade_dates: list[str] = []
    if walk_forward_bars > 0:
        if runs != 1:
            raise ValueError(
                "walk-forward-bars > 0 requires --runs 1 (engine is executed only once per "
                "trade_date for rule; repeating runs explodes engine calls)."
            )
        trade_dates = get_last_n_trade_dates(codes[0], src_data_dir, walk_forward_bars)
        plan["walk_forward_bars"] = walk_forward_bars
        plan["trade_dates_range"] = (
            f"{trade_dates[0]}..{trade_dates[-1]}" if trade_dates else "n/a"
        )
        plan["dataset_root"] = _as_relative(dataset_root)
        if reuse_exp_id:
            plan["reuse_exp_id"] = reuse_exp_id

    if dry_run:
        return {"plan": plan}

    root_dir.mkdir(parents=True, exist_ok=True)
    summary_rows: list[dict[str, Any]] = []
    dataset_cache: dict[str, str] = {}

    if walk_forward_bars > 0 and not trade_dates:
        raise ValueError("walk-forward bars requested but no trade dates available")

    if walk_forward_bars > 0:
        run_label = _run_id(1)
        rule_mode = "rule"
        rule_dir = root_dir / rule_mode
        rule_run_dir = rule_dir / run_label
        rule_signals_dir = rule_dir / "signals"
        rule_engine_out_dir = rule_dir / "engine_out"
        rule_signals_dir.mkdir(parents=True, exist_ok=True)
        rule_engine_out_dir.mkdir(parents=True, exist_ok=True)

        aggregated_path = rule_signals_dir / "aggregated_signals.csv"
        if reuse_exp_id:
            if not aggregated_path.exists():
                raise ValueError(
                    f"reuse-exp-id requires existing rule aggregated_signals.csv at {aggregated_path}"
                )
            engine_returncodes = []
        elif not aggregated_path.exists():
            aggregated_frames: list[pd.DataFrame] = []
            engine_returncodes: list[int] = []
            for trade_date in trade_dates:
                if trade_date not in dataset_cache:
                    dataset_cache[trade_date] = prepare_cut_dataset(
                        codes=codes,
                        src_data_dir=src_data_dir,
                        cut_date=trade_date,
                        out_root=str(dataset_root),
                    )
                cut_data_dir = Path(dataset_cache[trade_date])
                engine_out_date_dir = rule_engine_out_dir / trade_date
                req = Wave3x3RunRequest(
                    codes=codes,
                    zones_csv=zones_csv,
                    engine_out_dir=str(engine_out_date_dir),
                    data_dir=str(cut_data_dir),
                    asof=None,
                    extra_args=[],
                )
                result = run_wave_3x3_engine(req)
                engine_returncodes.append(result.returncode)
                if result.returncode != 0:
                    continue
                signals_path = _find_signals_csv(engine_out_date_dir)
                if not signals_path:
                    continue
                df = pd.read_csv(signals_path)
                normalized = _normalize_for_aggregation(df)
                if normalized is not None:
                    aggregated_frames.append(normalized)
            aggregated_df = (
                pd.concat(aggregated_frames, ignore_index=True) if aggregated_frames else pd.DataFrame()
            )
            aggregated_df.to_csv(aggregated_path, index=False)
        else:
            engine_returncodes = []

        if reuse_exp_id:
            data_dir_path = Path(src_data_dir)
        else:
            data_dir_path = (
                Path(dataset_cache[trade_dates[-1]]) if trade_dates else Path(src_data_dir)
            )
        if reuse_exp_id:
            rule_returncode = 0
        else:
            rule_returncode = max(engine_returncodes) if engine_returncodes else 0
        if aggregated_path.exists():
            rule_df_cache = pd.read_csv(aggregated_path)
        else:
            rule_df_cache = pd.DataFrame()
        gate_applied_days = count_gate_applied_days(rule_df_cache)

        for mode_name in modes:
            mode_dir = root_dir / mode_name
            mode_run_dir = mode_dir / run_label
            mode_signals_dir = mode_dir / "signals"
            mode_signals_dir.mkdir(parents=True, exist_ok=True)
            mode_run_dir.mkdir(parents=True, exist_ok=True)

            run_meta: dict[str, Any] = {
                "exp_id": exp_id,
                "mode": mode_name,
                "run_id": run_label,
                "seed": seed,
                "codes": codes,
                "zones_csv": zones_csv,
                "walk_forward_bars": walk_forward_bars,
                "walk_forward_dates": {
                    "start": trade_dates[0],
                    "end": trade_dates[-1],
                    "count": len(trade_dates),
                },
            }
            if reuse_exp_id:
                run_meta["reuse_exp_id"] = reuse_exp_id

            if mode_name == "rule":
                mode_signals_path = aggregated_path
                run_meta["engine_returncode"] = rule_returncode
            else:
                mode_signals_path = mode_signals_dir / "aggregated_signals.csv"
                aggregated_df = rule_df_cache.copy()
                if mode_name == "random" and not aggregated_df.empty:
                    aggregated_df, changes = perturb_actions(aggregated_df, seed=seed, p=0.3)
                    run_meta["perturbation"] = {"p": 0.3, "changes": changes}
                if mode_name == "llm":
                    aggregated_df, gate_summary = build_llm_signals_from_rule(
                        aggregated_df,
                        gate_mode=gate_mode,
                        seed=seed,
                        llm_model=llm_model,
                        llm_gate_policy=llm_gate_policy,
                        zones_csv_path=zones_csv,
                        daily_data_dir=str(data_dir_path),
                    )
                    run_meta["gate_summary"] = gate_summary
                    run_meta["gate_mode"] = gate_summary.get("gate_mode", gate_mode)
                aggregated_df.to_csv(mode_signals_path, index=False)
                run_meta["engine_returncode"] = rule_returncode

            run_meta["aggregated_signals"] = _as_relative(mode_signals_path)

            metrics = compute_metrics(
                mode=mode_name,
                run_dir=mode_run_dir,
                signals_csv=mode_signals_path,
                signals_json=None,
                codes=codes,
                data_dir=data_dir_path,
            )
            note = metrics.get("note", "")
            reuse_label = reuse_exp_id or "none"
            llm_label = llm_model or "none"
            if mode_name == "llm":
                gate_days = gate_applied_days if gate_mode in {"rule", "llm"} else 0
                gate_summary = run_meta.get("gate_summary", {}) or {}
                llm_call_total = int(gate_summary.get("llm_call_total", 0))
                llm_decision_valid = int(gate_summary.get("llm_decision_valid", 0))
                llm_decision_block = int(gate_summary.get("llm_decision_block", 0))
                llm_decision_allow = int(gate_summary.get("llm_decision_allow", 0))
                llm_noop_total = int(gate_summary.get("llm_noop_total", 0))
                missing_indicator_rows = int(gate_summary.get("missing_indicator_rows", 0))
                buy_rows_bb50_above = int(gate_summary.get("buy_rows_bb50_above", 0))
                buy_rows_bb50_below = int(gate_summary.get("buy_rows_bb50_below", 0))
                llm_policy_mismatch = int(gate_summary.get("llm_policy_mismatch", 0))
                srz_rows_total = int(gate_summary.get("srz_rows_total", 0))
                srz_rows_block = int(gate_summary.get("srz_rows_block", 0))
                srz_rows_allow = int(gate_summary.get("srz_rows_allow", 0))
                noop_reasons = gate_summary.get("noop_reasons", {}) or {}
                reason_keys = ["schema_error", "parse_error", "empty_response", "timeout", "exception"]
                reasons_summary = ",".join(
                    f"{key}={int(noop_reasons.get(key, 0))}" for key in reason_keys
                )
                extra_flags = []
                if gate_summary.get("noop") and gate_mode == "llm":
                    extra_flags.append("llm_gate:noop_fallback")
                if gate_mode == "none":
                    extra_flags.append("llm_gate:noop")
                suffix_parts = [
                    f"reuse_exp_id:{reuse_label}",
                    f"gate_mode:{gate_mode}",
                    f"llm_gate_policy:{llm_gate_policy}",
                    f"llm_model:{llm_label}",
                    f"gate_applied_days:{gate_days}",
                    f"llm_call_total:{llm_call_total}",
                    f"llm_decision_valid:{llm_decision_valid}",
                    f"llm_decision_block:{llm_decision_block}",
                    f"llm_decision_allow:{llm_decision_allow}",
                    f"llm_noop_total:{llm_noop_total}",
                    f"llm_policy_mismatch:{llm_policy_mismatch}",
                    f"missing_indicator_rows:{missing_indicator_rows}",
                    f"buy_rows_bb50_above:{buy_rows_bb50_above}",
                    f"buy_rows_bb50_below:{buy_rows_bb50_below}",
                    f"srz_rows_total:{srz_rows_total}",
                    f"srz_rows_block:{srz_rows_block}",
                    f"srz_rows_allow:{srz_rows_allow}",
                ]
                if llm_noop_total and reasons_summary:
                    suffix_parts.append(f"llm_noop_reason:{reasons_summary}")
                suffix_parts.extend(extra_flags)
            else:
                suffix_parts = [
                    f"reuse_exp_id:{reuse_label}",
                    f"gate_mode:{gate_mode}",
                    f"llm_model:{llm_label}",
                    "gate_applied_days:0",
                ]
            suffix = ";".join(suffix_parts)
            metrics["note"] = f"{note};{suffix}" if note else suffix
            metrics_path = mode_run_dir / "metrics.json"
            _write_json(metrics_path, metrics)
            run_meta["metrics_path"] = _as_relative(metrics_path)

            run_path = mode_run_dir / "run.json"
            _write_json(run_path, run_meta)

            summary_rows.append(
                {
                    "exp_id": exp_id,
                    "mode": mode_name,
                    "run_id": run_label,
                    "seed": seed,
                    "returncode": rule_returncode,
                    "trades": metrics.get("trades"),
                    "win_rate": metrics.get("win_rate"),
                    "expectancy_R": metrics.get("expectancy_R"),
                    "max_dd": metrics.get("max_dd"),
                    "metrics_note": metrics.get("note"),
                }
            )

        summary_path = root_dir / "summary.csv"
        pd.DataFrame(summary_rows).to_csv(summary_path, index=False)
        return {"exp_id": exp_id, "summary": _as_relative(summary_path)}

    for run_index in range(1, runs + 1):
        run_label = _run_id(run_index)
        for mode_name in modes:
            run_dir = root_dir / mode_name / run_label
            engine_out_dir = run_dir / "engine_out"
            run_dir.mkdir(parents=True, exist_ok=True)

            run_meta: dict[str, Any] = {
                "exp_id": exp_id,
                "mode": mode_name,
                "run_id": run_label,
                "seed": seed,
                "codes": codes,
                "zones_csv": zones_csv,
                "engine_out_dir": _as_relative(engine_out_dir),
            }
            metrics_input_path: Path | None = None
            data_dir_path = Path(src_data_dir)
            engine_returncode = 1
            engine_outputs: dict[str, str] = {}

            if walk_forward_bars > 0:
                signals_dir = run_dir / "signals"
                signals_dir.mkdir(parents=True, exist_ok=True)
                aggregated_frames: list[pd.DataFrame] = []
                engine_returncodes: list[int] = []
                for trade_date in trade_dates:
                    if trade_date not in dataset_cache:
                        dataset_cache[trade_date] = prepare_cut_dataset(
                            codes=codes,
                            src_data_dir=src_data_dir,
                            cut_date=trade_date,
                            out_root=str(dataset_root),
                        )
                    cut_data_dir = Path(dataset_cache[trade_date])
                    engine_out_date_dir = engine_out_dir / trade_date
                    req = Wave3x3RunRequest(
                        codes=codes,
                        zones_csv=zones_csv,
                        engine_out_dir=str(engine_out_date_dir),
                        data_dir=str(cut_data_dir),
                        asof=None,
                        extra_args=[],
                    )
                    result = run_wave_3x3_engine(req)
                    engine_returncodes.append(result.returncode)
                    if result.returncode != 0:
                        continue
                    signals_path = _find_signals_csv(engine_out_date_dir)
                    if not signals_path:
                        continue
                    df = pd.read_csv(signals_path)
                    normalized = _normalize_for_aggregation(df)
                    if normalized is not None:
                        aggregated_frames.append(normalized)
                aggregated_df = (
                    pd.concat(aggregated_frames, ignore_index=True) if aggregated_frames else pd.DataFrame()
                )
                if mode_name == "random" and not aggregated_df.empty:
                    aggregated_df, changes = perturb_actions(aggregated_df, seed=seed, p=0.3)
                    run_meta["perturbation"] = {"p": 0.3, "changes": changes}
                if mode_name == "llm":
                    if signals_path and signals_path.exists():
                        df = pd.read_csv(signals_path)
                    else:
                        df = pd.DataFrame()
                    gated_df, gate_summary = build_llm_signals_from_rule(
                        df,
                        gate_mode=gate_mode,
                        seed=seed,
                        llm_model=llm_model,
                        llm_gate_policy=llm_gate_policy,
                        zones_csv_path=zones_csv,
                        daily_data_dir=str(data_dir_path),
                    )
                    run_meta["gate_summary"] = gate_summary
                    run_meta["gate_mode"] = gate_summary.get("gate_mode", gate_mode)
                    gated_path = engine_out_dir / f"{signals_path.stem}.gated.csv"
                    gated_df.to_csv(gated_path, index=False)
                    run_meta["engine_outputs"]["wave_3x3_signals_gated_csv"] = _as_relative(
                        gated_path
                    )
                    signals_path = gated_path

                agg_name = (
                    "aggregated_signals.csv"
                    if runs == 1
                    else f"aggregated_signals_{run_label}.csv"
                )
                metrics_input_path = signals_dir / agg_name
                aggregated_df.to_csv(metrics_input_path, index=False)
                run_meta["aggregated_signals"] = _as_relative(metrics_input_path)

                engine_returncode = max(engine_returncodes) if engine_returncodes else 1
                run_meta["engine_returncode"] = engine_returncode
                run_meta["engine_returncodes"] = engine_returncodes
                run_meta["walk_forward_bars"] = walk_forward_bars
                run_meta["walk_forward_dates"] = {
                    "start": trade_dates[0],
                    "end": trade_dates[-1],
                    "count": len(trade_dates),
                }
                data_dir_path = Path(dataset_cache[trade_dates[-1]])
            else:
                req = Wave3x3RunRequest(
                    codes=codes,
                    zones_csv=zones_csv,
                    engine_out_dir=str(engine_out_dir),
                    asof=None,
                    extra_args=[],
                )
                result = run_wave_3x3_engine(req)
                engine_returncode = result.returncode
                run_meta["engine_returncode"] = result.returncode
                run_meta["engine_outputs"] = result.outputs

                signals_path = None
                if result.returncode == 0:
                    signals_path = _find_signals_csv(engine_out_dir)

                if mode_name == "random" and signals_path:
                    df = pd.read_csv(signals_path)
                    df_perturbed, changes = perturb_actions(df, seed=seed, p=0.3)
                    random_csv = engine_out_dir / f"{signals_path.stem}.random.csv"
                    random_json = engine_out_dir / f"{signals_path.stem}.random.json"
                    df_perturbed.to_csv(random_csv, index=False)
                    df_perturbed.to_json(random_json, orient="records", force_ascii=False, indent=2)
                    run_meta["perturbation"] = {"p": 0.3, "changes": changes}
                    run_meta["engine_outputs"]["wave_3x3_signals_random_csv"] = _as_relative(random_csv)
                    run_meta["engine_outputs"]["wave_3x3_signals_random_json"] = _as_relative(random_json)
                    signals_path = random_csv

                if mode_name == "llm":
                    if signals_path and signals_path.exists():
                        df = pd.read_csv(signals_path)
                    else:
                        df = pd.DataFrame()
                    gated_df, gate_summary = build_llm_signals_from_rule(
                        df,
                        gate_mode=gate_mode,
                        seed=seed,
                        llm_model=llm_model,
                        llm_gate_policy=llm_gate_policy,
                        zones_csv_path=zones_csv,
                        daily_data_dir=str(data_dir_path),
                    )
                    run_meta["gate_summary"] = gate_summary
                    run_meta["gate_mode"] = gate_summary.get("gate_mode", gate_mode)
                    gated_path = engine_out_dir / f"{signals_path.stem}.gated.csv"
                    gated_df.to_csv(gated_path, index=False)
                    run_meta["engine_outputs"]["wave_3x3_signals_gated_csv"] = _as_relative(
                        gated_path
                    )
                    signals_path = gated_path

                metrics_input_path = signals_path

            metrics = compute_metrics(
                mode=mode_name,
                run_dir=run_dir,
                signals_csv=metrics_input_path,
                signals_json=None,
                codes=codes,
                data_dir=data_dir_path,
            )
            note = metrics.get("note", "")
            reuse_label = reuse_exp_id or "none"
            llm_label = llm_model or "none"
            if mode_name == "llm":
                gate_days = count_gate_applied_days(df) if gate_mode in {"rule", "llm"} else 0
                gate_summary = run_meta.get("gate_summary", {}) or {}
                llm_call_total = int(gate_summary.get("llm_call_total", 0))
                llm_decision_valid = int(gate_summary.get("llm_decision_valid", 0))
                llm_decision_block = int(gate_summary.get("llm_decision_block", 0))
                llm_decision_allow = int(gate_summary.get("llm_decision_allow", 0))
                llm_noop_total = int(gate_summary.get("llm_noop_total", 0))
                missing_indicator_rows = int(gate_summary.get("missing_indicator_rows", 0))
                buy_rows_bb50_above = int(gate_summary.get("buy_rows_bb50_above", 0))
                buy_rows_bb50_below = int(gate_summary.get("buy_rows_bb50_below", 0))
                llm_policy_mismatch = int(gate_summary.get("llm_policy_mismatch", 0))
                srz_rows_total = int(gate_summary.get("srz_rows_total", 0))
                srz_rows_block = int(gate_summary.get("srz_rows_block", 0))
                srz_rows_allow = int(gate_summary.get("srz_rows_allow", 0))
                noop_reasons = gate_summary.get("noop_reasons", {}) or {}
                reason_keys = ["schema_error", "parse_error", "empty_response", "timeout", "exception"]
                reasons_summary = ",".join(
                    f"{key}={int(noop_reasons.get(key, 0))}" for key in reason_keys
                )
                extra_flags = []
                if gate_summary.get("noop") and gate_mode == "llm":
                    extra_flags.append("llm_gate:noop_fallback")
                if gate_mode == "none":
                    extra_flags.append("llm_gate:noop")
                suffix_parts = [
                    f"reuse_exp_id:{reuse_label}",
                    f"gate_mode:{gate_mode}",
                    f"llm_gate_policy:{llm_gate_policy}",
                    f"llm_model:{llm_label}",
                    f"gate_applied_days:{gate_days}",
                    f"llm_call_total:{llm_call_total}",
                    f"llm_decision_valid:{llm_decision_valid}",
                    f"llm_decision_block:{llm_decision_block}",
                    f"llm_decision_allow:{llm_decision_allow}",
                    f"llm_noop_total:{llm_noop_total}",
                    f"llm_policy_mismatch:{llm_policy_mismatch}",
                    f"missing_indicator_rows:{missing_indicator_rows}",
                    f"buy_rows_bb50_above:{buy_rows_bb50_above}",
                    f"buy_rows_bb50_below:{buy_rows_bb50_below}",
                    f"srz_rows_total:{srz_rows_total}",
                    f"srz_rows_block:{srz_rows_block}",
                    f"srz_rows_allow:{srz_rows_allow}",
                ]
                if llm_noop_total and reasons_summary:
                    suffix_parts.append(f"llm_noop_reason:{reasons_summary}")
                suffix_parts.extend(extra_flags)
            else:
                suffix_parts = [
                    f"reuse_exp_id:{reuse_label}",
                    f"gate_mode:{gate_mode}",
                    f"llm_model:{llm_label}",
                    "gate_applied_days:0",
                ]
            suffix = ";".join(suffix_parts)
            metrics["note"] = f"{note};{suffix}" if note else suffix
            metrics_path = run_dir / "metrics.json"
            _write_json(metrics_path, metrics)
            run_meta["metrics_path"] = _as_relative(metrics_path)

            if walk_forward_bars > 0:
                mode_dir = root_dir / mode_name
                mode_metrics_name = "metrics.json" if runs == 1 else f"metrics_{run_label}.json"
                _write_json(mode_dir / mode_metrics_name, metrics)

            run_path = run_dir / "run.json"
            _write_json(run_path, run_meta)

            summary_rows.append(
                {
                    "exp_id": exp_id,
                    "mode": mode_name,
                    "run_id": run_label,
                    "seed": seed,
                    "returncode": engine_returncode,
                    "trades": metrics.get("trades"),
                    "win_rate": metrics.get("win_rate"),
                    "expectancy_R": metrics.get("expectancy_R"),
                    "max_dd": metrics.get("max_dd"),
                    "metrics_note": metrics.get("note"),
                }
            )

    summary_path = root_dir / "summary.csv"
    pd.DataFrame(summary_rows).to_csv(summary_path, index=False)
    return {"exp_id": exp_id, "summary": _as_relative(summary_path)}
