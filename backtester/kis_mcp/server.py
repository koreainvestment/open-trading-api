"""KIS Backtest MCP Server.

FastMCP 기반 MCP 2025-03-26 스펙 (streamable-http transport).

사용법:
    uv run python -m mcp.server
    # 또는
    bash scripts/start_mcp.sh

엔드포인트:
    GET  /health  — 헬스 체크
    POST /mcp     — MCP protocol (streamable-http)
"""

from __future__ import annotations

import logging
import os
from datetime import date
from typing import Any, Dict, List, Literal, Optional

from mcp.server.fastmcp import FastMCP

# ─── Tool imports ──────────────────────────────────────────────────────────────
from kis_mcp.tools.strategy import (
    list_presets,
    get_preset_yaml,
    validate_yaml,
    list_indicators,
)
from kis_mcp.tools.backtest import (
    run_backtest,
    run_preset_backtest,
    get_backtest_result,
    get_backtest_result_wait,
    retry_backtest,
    run_batch_backtest,
    run_optimize,
)
from kis_mcp.tools.report import get_report

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)

# ─── FastMCP App ───────────────────────────────────────────────────────────────

_host = os.environ.get("MCP_HOST", "127.0.0.1")
_port = int(os.environ.get("MCP_PORT", "3846"))

mcp = FastMCP(
    name="kis-backtest",
    instructions=(
        "KIS 전략 백테스팅 MCP 서버.\n"
        "전략 설계(list_presets, get_preset_yaml, validate_yaml, list_indicators) → "
        "백테스트 실행(run_backtest, run_preset_backtest) → "
        "결과 조회(get_backtest_result) → 리포트(get_report) 파이프라인을 제공합니다."
    ),
    host=_host,
    port=_port,
    streamable_http_path="/mcp",
    stateless_http=True,
)

# ─── Strategy Tools ────────────────────────────────────────────────────────────

@mcp.tool()
def list_presets_tool() -> dict:
    """10개 프리셋 전략 목록과 파라미터 정의를 반환합니다."""
    return list_presets()


@mcp.tool()
def get_preset_yaml_tool(
    strategy_id: str,
    param_overrides: Optional[Dict[str, Any]] = None,
) -> dict:
    """프리셋 전략을 .kis.yaml 문자열로 반환합니다.

    Args:
        strategy_id: 전략 ID (예: sma_crossover, momentum, trend_filter_signal)
        param_overrides: 파라미터 오버라이드 (예: {"period": 21, "oversold": 25})
    """
    return get_preset_yaml(strategy_id, param_overrides)


@mcp.tool()
def validate_yaml_tool(yaml_content: str) -> dict:
    """YAML 전략 문자열의 유효성을 검증합니다.

    Args:
        yaml_content: .kis.yaml 포맷 전략 문자열
    """
    return validate_yaml(yaml_content)


@mcp.tool()
def list_indicators_tool() -> dict:
    """지원하는 기술적 지표 목록과 파라미터 정의를 반환합니다 (70개+)."""
    return list_indicators()


# ─── Backtest Tools ───────────────────────────────────────────────────────────

@mcp.tool()
def run_backtest_tool(
    yaml_content: str,
    symbols: List[str],
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    initial_capital: float = 10_000_000,
    commission_rate: float = 0.00015,
    tax_rate: float = 0.002,
    slippage: float = 0.0,
) -> dict:
    """YAML 전략을 백테스트합니다 (비동기 — 즉시 job_id 반환).

    Args:
        yaml_content: .kis.yaml 포맷 전략 문자열
        symbols: 종목 코드 리스트 (예: ["005930", "000660"])
        start_date: 시작일 YYYY-MM-DD (기본: 1년 전)
        end_date: 종료일 YYYY-MM-DD (기본: 오늘)
        initial_capital: 초기 자본금 (원, 기본 1,000만)
        commission_rate: 수수료율 (기본 0.015%)
        tax_rate: 거래세율 (기본 0.2%)
        slippage: 슬리피지 (기본 0%, 0.001=0.1%로 설정 시 KRXSlippageModel 적용)

    Returns:
        { job_id, status: "running" }  — get_backtest_result(job_id) 로 결과 조회
    """
    today = date.today()
    return run_backtest(
        yaml_content=yaml_content,
        symbols=symbols,
        start_date=start_date or date(today.year - 1, today.month, today.day).strftime("%Y-%m-%d"),
        end_date=end_date or today.strftime("%Y-%m-%d"),
        initial_capital=initial_capital,
        commission_rate=commission_rate,
        tax_rate=tax_rate,
        slippage=slippage,
    )


@mcp.tool()
def run_preset_backtest_tool(
    strategy_id: str,
    symbols: List[str],
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    initial_capital: float = 10_000_000,
    param_overrides: Optional[Dict[str, Any]] = None,
    commission_rate: float = 0.00015,
    tax_rate: float = 0.002,
    slippage: float = 0.0,
) -> dict:
    """프리셋 전략을 백테스트합니다 (비동기 — 즉시 job_id 반환).

    Args:
        strategy_id: 전략 ID (예: sma_crossover, momentum, trend_filter_signal)
        symbols: 종목 코드 리스트 (예: ["005930"])
        start_date: 시작일 YYYY-MM-DD (기본: 1년 전)
        end_date: 종료일 YYYY-MM-DD (기본: 오늘)
        initial_capital: 초기 자본금 (원, 기본 1,000만)
        param_overrides: 파라미터 오버라이드 (예: {"period": 21})
        commission_rate: 수수료율
        tax_rate: 거래세율
        slippage: 슬리피지 (기본 0%, 0.001=0.1%로 설정 시 KRXSlippageModel 적용)
    """
    today = date.today()
    return run_preset_backtest(
        strategy_id=strategy_id,
        symbols=symbols,
        start_date=start_date or date(today.year - 1, today.month, today.day).strftime("%Y-%m-%d"),
        end_date=end_date or today.strftime("%Y-%m-%d"),
        initial_capital=initial_capital,
        param_overrides=param_overrides,
        commission_rate=commission_rate,
        tax_rate=tax_rate,
        slippage=slippage,
    )


@mcp.tool()
async def get_backtest_result_tool(
    job_id: str,
    wait: bool = True,
    timeout: float = 300.0,
) -> dict:
    """백테스트 결과를 조회합니다.

    기본 동작(wait=True): 완료/실패까지 서버 내부에서 대기한 뒤 결과를 반환합니다.
    한 번의 호출로 최종 결과를 받을 수 있으므로 반복 폴링이 필요 없습니다.

    Args:
        job_id: run_backtest_tool / run_preset_backtest_tool 반환값의 job_id
        wait: True(기본)면 완료까지 대기, False면 즉시 현재 상태 반환
        timeout: 최대 대기 시간 (초, 기본 300초=5분). wait=True일 때만 적용

    Returns:
        완료: { status: "completed", result: { 수익률, MDD, 샤프지수, ... } }
        실패: { status: "failed", error: "..." }
        타임아웃/즉시: { status: "running"|"pending" }
    """
    if wait:
        return await get_backtest_result_wait(job_id, timeout=timeout)
    return get_backtest_result(job_id)


@mcp.tool()
def retry_backtest_tool(job_id: str) -> dict:
    """실패한 백테스트를 재시도합니다.

    EGW00201(API 호출 한도 초과) 등으로 실패한 job을 재실행합니다.
    이미 다운로드된 종목 데이터는 캐시에서 재사용하므로 빠르게 이어서 실행됩니다.

    Args:
        job_id: 실패한 run_backtest_tool / run_preset_backtest_tool 의 job_id

    Returns:
        { new_job_id, original_job_id, status: "running" }
        — get_backtest_result(new_job_id)로 결과 조회
    """
    return retry_backtest(job_id)


# ─── Report Tool ──────────────────────────────────────────────────────────────

@mcp.tool()
def get_report_tool(
    job_id: str,
    format: Literal["json", "html"] = "json",
) -> dict:
    """백테스트 리포트를 생성합니다.

    Args:
        job_id: 완료된 백테스트의 job_id
        format: "json" (핵심 지표 요약) 또는 "html" (전체 HTML 리포트 파일 경로)
    """
    return get_report(job_id=job_id, format=format)


# ─── Batch & Optimize Tools ───────────────────────────────────────────────────

@mcp.tool()
async def run_batch_backtest_tool(
    items: List[Dict[str, Any]],
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    initial_capital: float = 10_000_000,
    commission_rate: float = 0.00015,
    tax_rate: float = 0.002,
) -> dict:
    """여러 전략을 동시에 백테스트하고 비교 결과를 반환합니다.

    모든 job을 병렬로 제출한 뒤 asyncio.gather로 동시 대기합니다.
    Semaphore(3)로 실제 실행은 최대 3개로 제한됩니다.

    Args:
        items: 전략 목록. 각 항목에 다음 키 포함:
               - {"strategy_id": "sma_crossover", "symbols": ["005930"], "param_overrides": {...}}
               - {"yaml_content": "...", "symbols": ["000660"]}
        start_date: 공통 시작일 YYYY-MM-DD (기본: 1년 전)
        end_date: 공통 종료일 YYYY-MM-DD (기본: 오늘)
        initial_capital: 공통 초기 자본금 (원, 기본 1,000만)
        commission_rate: 공통 수수료율
        tax_rate: 공통 세율

    Returns:
        { completed, failed, comparison: { by_sharpe, by_return, by_drawdown }, runs, job_ids }
    """
    today = date.today()
    return await run_batch_backtest(
        items=items,
        start_date=start_date or date(today.year - 1, today.month, today.day).strftime("%Y-%m-%d"),
        end_date=end_date or today.strftime("%Y-%m-%d"),
        initial_capital=initial_capital,
        commission_rate=commission_rate,
        tax_rate=tax_rate,
    )


@mcp.tool()
def optimize_strategy_tool(
    strategy_id: str,
    symbols: List[str],
    parameters: List[Dict[str, Any]],
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    search_type: str = "grid",
    max_samples: int = 20,
    target: str = "sharpe_ratio",
    initial_capital: float = 10_000_000,
    commission_rate: float = 0.00015,
    tax_rate: float = 0.002,
    seed: Optional[int] = None,
    slippage: float = 0.0,
) -> dict:
    """전략 파라미터 최적화를 시작합니다 (비동기 — 즉시 job_id 반환).

    Grid Search 또는 Random Search로 파라미터 조합을 탐색합니다.
    결과는 get_backtest_result_tool(job_id)로 조회하며, 실행 중에는 진행률을 포함합니다.

    Args:
        strategy_id: 전략 ID (예: "sma_crossover", "golden_cross")
        symbols: 종목 코드 리스트 (예: ["005930"])
        parameters: 파라미터 정의 리스트.
                    예: [{"name": "fast_period", "min": 5, "max": 20, "step": 5},
                         {"name": "slow_period", "min": 20, "max": 60, "step": 10}]
        start_date: 시작일 YYYY-MM-DD (기본: 1년 전)
        end_date: 종료일 YYYY-MM-DD (기본: 오늘)
        search_type: "grid" (전체 탐색) 또는 "random" (무작위 샘플링)
        max_samples: random search 최대 샘플 수 (기본 20)
        target: 최적화 목표 ("sharpe_ratio" | "total_return" | "max_drawdown" | "win_rate")
        initial_capital: 초기 자본금 (원, 기본 1,000만)
        commission_rate: 수수료율
        tax_rate: 세율
        seed: random search 재현성 시드
        slippage: 슬리피지 (기본 0%, 0.001=0.1%로 설정 시 KRXSlippageModel 적용)

    Returns:
        { job_id, status: "running", total_combinations, search_type, target }
        — get_backtest_result_tool(job_id) 로 진행률/최종 결과 조회
        — 완료 시 result: { best_params, best_metrics, all_runs, total_runs, successful_runs }
    """
    today = date.today()
    return run_optimize(
        strategy_id=strategy_id,
        symbols=symbols,
        start_date=start_date or date(today.year - 1, today.month, today.day).strftime("%Y-%m-%d"),
        end_date=end_date or today.strftime("%Y-%m-%d"),
        parameters=parameters,
        search_type=search_type,
        max_samples=max_samples,
        target=target,
        initial_capital=initial_capital,
        commission_rate=commission_rate,
        tax_rate=tax_rate,
        seed=seed,
        slippage=slippage,
    )


# ─── Custom Routes ────────────────────────────────────────────────────────────

@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Any) -> Any:
    """헬스 체크 엔드포인트."""
    from starlette.responses import JSONResponse
    return JSONResponse({"status": "ok", "version": "0.1.0", "server": "kis-backtest"})


# ─── Entry Point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    logger.info(f"KIS Backtest MCP Server 시작: http://{_host}:{_port}/mcp")
    mcp.run(transport="streamable-http")
