# This module exists to apply an LLM-based wave position classifier gate with diagnostics.

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


def _date_key(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _normalize_code(value: Any) -> str:
    text = str(value).strip()
    return text.zfill(6) if text.isdigit() else text


def _load_srz_bounds(zones_csv_path: str | None) -> dict[str, tuple[float, float]]:
    if not zones_csv_path:
        return {}
    path = Path(zones_csv_path)
    if not path.exists():
        return {}
    df = pd.read_csv(path, dtype={"code": str})
    if "code" not in df.columns or "C_low" not in df.columns or "C_high" not in df.columns:
        return {}
    srz_map: dict[str, tuple[float, float]] = {}
    for _, row in df.iterrows():
        code = _normalize_code(row.get("code", ""))
        try:
            low = float(row.get("C_low"))
            high = float(row.get("C_high"))
        except (TypeError, ValueError):
            continue
        if not (pd.isna(low) or pd.isna(high)):
            srz_map[code] = (low, high)
    return srz_map


def _init_noop_counts() -> dict[str, int]:
    return {
        "schema_error": 0,
        "parse_error": 0,
        "empty_response": 0,
        "timeout": 0,
        "exception": 0,
    }


def _policy_decision(
    policy: str,
    bb50_position: str | None,
    bb20_cross: str | None,
    wave_state: str | None,
    entry_stage: int,
) -> str:
    if bb50_position != "ABOVE":
        return "ALLOW"
    if policy == "A":
        return "BLOCK" if bb20_cross == "ABOVE" else "ALLOW"
    if policy == "B":
        return "BLOCK" if wave_state == "ACTIVE" else "ALLOW"
    if policy == "C":
        return "BLOCK" if entry_stage >= 2 else "ALLOW"
    return "BLOCK"


def _call_llm_stub(payload: dict[str, Any], model: str | None) -> dict[str, Any] | None:
    if not model:
        return None
    decision = _policy_decision(
        str(payload.get("policy", "strong")),
        payload.get("bb50_position"),
        payload.get("bb20_cross"),
        payload.get("wave_state"),
        int(payload.get("entry_stage", 0)),
    )
    return {"decision": decision}


def _parse_llm_decision(response: dict[str, Any] | None) -> tuple[str | None, str | None]:
    if response is None:
        return None, "empty_response"
    if not isinstance(response, dict):
        return None, "parse_error"
    decision = response.get("decision")
    if decision not in {"ALLOW", "BLOCK"}:
        return None, "schema_error"
    return str(decision), None


def _load_daily_inputs(rule_df: pd.DataFrame, daily_data_dir: str | None) -> pd.DataFrame:
    if daily_data_dir is None:
        return pd.DataFrame()
    codes = sorted(
        {
            _normalize_code(code)
            for code in rule_df.get("code", [])
            if str(code).strip()
        }
    )
    if not codes:
        return pd.DataFrame()
    frames = []
    candidates = ["date", "Date", "dt", "ymd"]
    for code in codes:
        daily_path = Path(daily_data_dir) / f"{code}_daily.csv"
        if not daily_path.exists():
            continue
        df = pd.read_csv(daily_path)
        date_col = next((col for col in candidates if col in df.columns), None)
        if not date_col or "close" not in df.columns:
            continue
        df = df.copy()
        df["__date_key__"] = pd.to_datetime(df[date_col], errors="coerce")
        df["close"] = pd.to_numeric(df["close"], errors="coerce")
        df = df.dropna(subset=["__date_key__", "close"])
        df = df.sort_values("__date_key__")
        df["BB20_mid"] = df["close"].rolling(20).mean()
        df["BB50_mid"] = df["close"].rolling(50).mean()
        df["bb50_position"] = pd.NA
        df["bb20_cross"] = pd.NA
        df["wave_state"] = pd.NA
        bb50_ready = df["BB50_mid"].notna()
        bb20_ready = df["BB20_mid"].notna()
        df.loc[bb50_ready, "bb50_position"] = np.where(
            df.loc[bb50_ready, "close"] <= df.loc[bb50_ready, "BB50_mid"],
            "BELOW",
            "ABOVE",
        )
        df.loc[bb20_ready, "bb20_cross"] = np.where(
            df.loc[bb20_ready, "close"] >= df.loc[bb20_ready, "BB20_mid"],
            "ABOVE",
            "BELOW",
        )
        df.loc[bb20_ready, "wave_state"] = np.where(
            df.loc[bb20_ready, "close"] >= df.loc[bb20_ready, "BB20_mid"],
            "ACTIVE",
            "INACTIVE",
        )
        df["__date_key__"] = df["__date_key__"].dt.strftime("%Y-%m-%d")
        df["code"] = _normalize_code(code)
        frames.append(
            df[
                [
                    "code",
                    "__date_key__",
                    "bb50_position",
                    "bb20_cross",
                    "wave_state",
                ]
            ]
        )
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def _normalize_rule_dates(rule_df: pd.DataFrame) -> pd.DataFrame:
    date_col = "date" if "date" in rule_df.columns else "asof" if "asof" in rule_df.columns else None
    if not date_col:
        return rule_df.copy()
    df = rule_df.copy()
    df["__date_key__"] = pd.to_datetime(df[date_col], errors="coerce").dt.strftime("%Y-%m-%d")
    if "code" in df.columns:
        df["code"] = df["code"].apply(_normalize_code)
    return df


def apply_llm_gate_to_signals(
    df: pd.DataFrame,
    seed: int,
    model: str | None,
    policy: str = "C",
    zones_csv_path: str | None = None,
    daily_data_dir: str | None = None,
    daily_df: pd.DataFrame | None = None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    if df.empty:
        return df.copy(), {
            "gate_mode": "llm",
            "applied_days": 0,
            "decisions": {},
            "noop": True,
            "llm_call_total": 0,
            "llm_decision_valid": 0,
            "llm_decision_block": 0,
            "llm_decision_allow": 0,
            "llm_noop_total": 0,
            "noop_reasons": _init_noop_counts(),
            "model": model or "",
        }
    date_col = "date" if "date" in df.columns else "asof" if "asof" in df.columns else None
    if not date_col:
        return df.copy(), {
            "gate_mode": "llm",
            "applied_days": 0,
            "decisions": {},
            "noop": True,
            "llm_call_total": 0,
            "llm_decision_valid": 0,
            "llm_decision_block": 0,
            "llm_decision_allow": 0,
            "llm_noop_total": 0,
            "noop_reasons": _init_noop_counts(),
            "model": model or "",
        }

    out = _normalize_rule_dates(df)
    decisions: list[dict[str, Any]] = []
    noop_counts = _init_noop_counts()
    llm_call_total = 0
    llm_decision_valid = 0
    llm_decision_allow = 0
    llm_decision_block = 0
    llm_noop_total = 0
    mismatch_count = 0

    buy_mask = out["action"].astype(str).str.startswith("BUY")
    applied_days = 0
    if bool(buy_mask.any()):
        applied_days = int(out.loc[buy_mask].groupby(date_col).size().shape[0])

    if daily_df is None:
        daily_df = _load_daily_inputs(out, daily_data_dir)
    if not daily_df.empty:
        daily_df = daily_df.rename(columns={"__date_key__": "__date_key__"})
        out = out.merge(
            daily_df,
            how="left",
            left_on=["code", "__date_key__"],
            right_on=["code", "__date_key__"],
        )
    missing_indicator_rows = 0
    buy_rows_total = int(buy_mask.sum())
    buy_rows_bb50_above = 0
    buy_rows_bb50_below = 0
    srz_rows_total = buy_rows_total
    srz_rows_block = 0
    srz_rows_allow = 0
    srz_map = _load_srz_bounds(zones_csv_path)

    for idx, row in out.iterrows():
        action = str(row.get("action", ""))
        if not action.startswith("BUY"):
            continue
        code = _normalize_code(row.get("code", ""))
        price_raw = row.get("price", row.get("close"))
        try:
            price = float(price_raw)
        except (TypeError, ValueError):
            price = float("nan")
        in_srz = True
        if srz_map:
            bounds = srz_map.get(code)
            if bounds and not pd.isna(price):
                low, high = bounds
                in_srz = low <= price <= high
            elif bounds and pd.isna(price):
                in_srz = False
            else:
                in_srz = True
        if not in_srz:
            srz_rows_block += 1
            out.at[idx, "action"] = "HOLD"
            decisions.append(
                {
                    "date": _date_key(row.get("__date_key__")),
                    "code": code,
                    "action": action,
                    "decision": "BLOCK",
                    "bb50_position": row.get("bb50_position"),
                    "wave_state": row.get("wave_state"),
                    "entry_stage": row.get("entry_stage", 0),
                    "missing_indicator": False,
                    "srz_block": True,
                }
            )
            continue
        bb50_position = row.get("bb50_position")
        bb20_cross = row.get("bb20_cross")
        wave_state = row.get("wave_state")
        if pd.isna(bb50_position) or pd.isna(bb20_cross) or pd.isna(wave_state):
            missing_indicator_rows += 1
            srz_rows_block += 1
            out.at[idx, "action"] = "HOLD"
            decisions.append(
                {
                    "date": _date_key(row.get("__date_key__")),
                    "code": code,
                    "action": action,
                    "decision": "BLOCK",
                    "bb50_position": bb50_position,
                    "wave_state": wave_state,
                    "entry_stage": row.get("entry_stage", 0),
                    "missing_indicator": True,
                    "srz_block": True,
                }
            )
            continue
        srz_rows_allow += 1
        entry_stage_raw = row.get("entry_stage", 0)
        try:
            entry_stage = int(entry_stage_raw)
        except (TypeError, ValueError):
            entry_stage = 0
        local_decision = _policy_decision(
            policy,
            bb50_position,
            bb20_cross,
            wave_state,
            entry_stage,
        )
        llm_call_total += 1
        if bb50_position == "ABOVE":
            buy_rows_bb50_above += 1
        if bb50_position == "BELOW":
            buy_rows_bb50_below += 1
        payload = {
            "code": _normalize_code(row.get("code", "")),
            "date": _date_key(row.get("__date_key__")),
            "action": action,
            "wave_state": wave_state,
            "bb20_cross": bb20_cross,
            "bb50_position": bb50_position,
            "entry_stage": entry_stage,
            "policy": policy,
        }
        try:
            response = _call_llm_stub(payload, model)
            decision_raw, reason = _parse_llm_decision(response)
        except Exception:
            decision_raw, reason = None, "exception"

        if reason:
            noop_counts[reason] = noop_counts.get(reason, 0) + 1
            llm_noop_total += 1
            decision_raw = "ALLOW"
        else:
            llm_decision_valid += 1

        if decision_raw and decision_raw != local_decision:
            mismatch_count += 1

        if local_decision == "BLOCK":
            llm_decision_block += 1
            out.at[idx, "action"] = "HOLD"
        else:
            llm_decision_allow += 1
        decisions.append(
            {
                "date": _date_key(row.get("__date_key__")),
                "code": _normalize_code(row.get("code", "")),
                "action": action,
                "decision": local_decision,
                "bb50_position": bb50_position,
                "wave_state": wave_state,
                "entry_stage": entry_stage,
                "missing_indicator": False,
            }
        )

    summary = {
        "gate_mode": "llm",
        "llm_gate_policy": policy,
        "applied_days": applied_days,
        "decisions": decisions,
        "noop": llm_noop_total > 0,
        "llm_call_total": llm_call_total,
        "llm_decision_valid": llm_decision_valid,
        "llm_decision_block": llm_decision_block,
        "llm_decision_allow": llm_decision_allow,
        "llm_noop_total": llm_noop_total,
        "llm_policy_mismatch": mismatch_count,
        "noop_reasons": noop_counts,
        "missing_indicator_rows": missing_indicator_rows,
        "buy_rows_total": buy_rows_total,
        "buy_rows_bb50_above": buy_rows_bb50_above,
        "buy_rows_bb50_below": buy_rows_bb50_below,
        "srz_rows_total": srz_rows_total,
        "srz_rows_block": srz_rows_block,
        "srz_rows_allow": srz_rows_allow,
        "model": model or "",
    }
    return out, summary
