"""Report MCP tool — 1 tool.

get_report: job_id 기반 HTML / JSON 리포트 생성
"""

from __future__ import annotations

import json
import logging
import tempfile
import time
from pathlib import Path
from typing import Literal

from kis_backtest.models.result import BacktestResult
from kis_backtest.report import KISReportGenerator
from kis_mcp.schemas import error_response, success_response
from kis_mcp.tools.backtest import _job_store

logger = logging.getLogger(__name__)


def get_report(
    job_id: str,
    format: Literal["json", "html"] = "json",
) -> dict:
    """백테스트 결과 리포트를 생성합니다.

    Args:
        job_id: run_backtest / run_preset_backtest 반환값의 job_id
        format: "json" (요약 지표) 또는 "html" (전체 HTML 리포트 파일 경로)

    Returns:
        format="json": 핵심 지표 요약 딕셔너리
        format="html": 생성된 HTML 파일 경로
    """
    job = _job_store.get(job_id)
    if job is None:
        return error_response(f"job_id '{job_id}'를 찾을 수 없습니다.")

    if job.status != "completed":
        return error_response(
            f"백테스트가 완료되지 않았습니다. 현재 상태: {job.status}",
            details={"job_id": job_id, "status": job.status},
        )

    result_data = job.result
    if not result_data:
        return error_response("결과 데이터가 없습니다.")

    if format == "json":
        metrics = result_data.get("metrics", {})
        basic = metrics.get("basic", {})
        risk = metrics.get("risk", {})
        trading = metrics.get("trading", {})
        summary = {
            "strategy_name": result_data.get("strategy_name", ""),
            "symbols": result_data.get("symbols", []),
            "period": f"{result_data.get('start_date', '')} ~ {result_data.get('end_date', '')}",
            "initial_capital": result_data.get("initial_capital", 0),
            "final_capital": result_data.get("final_capital", 0),
            "net_profit": result_data.get("net_profit", 0),
            "net_profit_percent": result_data.get("net_profit_percent", 0),
            "total_return_pct": basic.get("total_return", 0),
            "annual_return_pct": basic.get("annual_return", 0),
            "max_drawdown_pct": basic.get("max_drawdown", 0),
            "sharpe_ratio": risk.get("sharpe_ratio", 0),
            "sortino_ratio": risk.get("sortino_ratio", 0),
            "total_trades": trading.get("total_orders", 0),
            "win_rate": trading.get("win_rate", 0),
            "profit_loss_ratio": trading.get("profit_loss_ratio", 0),
        }
        return success_response(summary)

    # HTML 리포트 생성
    try:
        import pandas as pd

        # BacktestResult 객체 생성 (HTML 렌더링용)
        metrics = result_data.get("metrics", {})
        basic = metrics.get("basic", {})
        risk = metrics.get("risk", {})
        trading = metrics.get("trading", {})

        # equity_curve: dict → pd.Series(DatetimeIndex) — 차트 컴포넌트가 요구하는 형식
        raw_curve = result_data.get("equity_curve")
        if isinstance(raw_curve, dict) and raw_curve:
            equity_series = pd.Series(raw_curve, dtype=float)
            equity_series.index = pd.to_datetime(equity_series.index)
            equity_series = equity_series.sort_index()
        else:
            equity_series = None

        # 벤치마크 커브 (KOSPI % 수익률 곡선)
        from backend.routes.backtest import _load_benchmark_curve
        from kis_backtest.lean.project_manager import LeanProjectManager
        benchmark_curve = _load_benchmark_curve(
            workspace=LeanProjectManager.workspace,
            start_date=job.start_date,
            end_date=job.end_date,
        )

        br = BacktestResult(
            success=True,
            strategy_id=job.strategy_name,
            symbols=job.symbols,
            start_date=job.start_date,
            end_date=job.end_date,
            total_return=result_data.get("net_profit", 0),
            total_return_pct=basic.get("total_return", 0) / 100,
            cagr=basic.get("annual_return", 0) / 100,
            max_drawdown=basic.get("max_drawdown", 0) / 100,
            sharpe_ratio=risk.get("sharpe_ratio", 0),
            sortino_ratio=risk.get("sortino_ratio", 0),
            total_trades=int(trading.get("total_orders", 0)),
            win_rate=trading.get("win_rate", 0) / 100,
            profit_factor=trading.get("profit_loss_ratio", 0),
            average_win=trading.get("avg_win", 0),
            average_loss=trading.get("avg_loss", 0),
            equity_curve=equity_series,
            trades=result_data.get("trades", []),
            raw_statistics=result_data.get("raw_statistics", {}),
            benchmark_curve=benchmark_curve,
        )

        output_path = Path(tempfile.gettempdir()) / "kis_reports" / f"{job_id}_{int(time.time())}.html"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        gen = KISReportGenerator()
        generated = gen.generate(
            result=br,
            output_path=output_path,
            title=f"백테스트 리포트 — {job.strategy_name}",
        )

        import subprocess, sys
        if sys.platform == "darwin":
            subprocess.Popen(["open", str(generated)])

        return success_response(
            {"path": str(generated), "job_id": job_id},
            message=f"HTML 리포트 생성 완료: {generated}",
        )

    except Exception as exc:
        logger.exception("get_report: HTML 생성 실패")
        return error_response(f"HTML 리포트 생성 실패: {exc}")
