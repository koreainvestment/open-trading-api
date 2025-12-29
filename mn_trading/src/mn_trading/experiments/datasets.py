# This module exists to generate cut-date datasets for experiments.

from __future__ import annotations

from pathlib import Path

import pandas as pd


def prepare_cut_dataset(codes: list[str], src_data_dir: str, cut_date: str, out_root: str) -> str:
    out_dir = Path(out_root) / f"cut_{cut_date}"
    out_dir.mkdir(parents=True, exist_ok=True)

    candidates = ["date", "Date", "dt", "ymd"]
    for code in codes:
        src_path = Path(src_data_dir) / f"{code}_daily.csv"
        if not src_path.exists():
            raise FileNotFoundError(f"missing source CSV: {src_path}")
        df = pd.read_csv(src_path)
        date_col = next((col for col in candidates if col in df.columns), None)
        if not date_col:
            raise ValueError(f"date column not found in {src_path}")

        dates = pd.to_datetime(df[date_col], errors="coerce")
        if dates.isna().all():
            raise ValueError(f"invalid dates in {src_path}")
        df = df.copy()
        df["__cut_date__"] = dates.dt.strftime("%Y%m%d")
        df = df[df["__cut_date__"] <= cut_date].drop(columns=["__cut_date__"])

        out_path = out_dir / f"{code}_daily.csv"
        df.to_csv(out_path, index=False)

    return str(out_dir)


def get_last_n_trade_dates(code: str, src_data_dir: str, n: int) -> list[str]:
    if n <= 0:
        return []
    src_path = Path(src_data_dir) / f"{code}_daily.csv"
    if not src_path.exists():
        raise FileNotFoundError(f"missing source CSV: {src_path}")
    df = pd.read_csv(src_path)
    candidates = ["date", "Date", "dt", "ymd"]
    date_col = next((col for col in candidates if col in df.columns), None)
    if not date_col:
        raise ValueError(f"date column not found in {src_path}")
    dates = pd.to_datetime(df[date_col], errors="coerce")
    if dates.isna().all():
        raise ValueError(f"invalid dates in {src_path}")
    dates = dates.dropna().sort_values()
    last_dates = dates.tail(n).dt.strftime("%Y%m%d").tolist()
    return [date for date in last_dates if date]
