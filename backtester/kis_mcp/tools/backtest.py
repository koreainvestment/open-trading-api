"""Backtest MCP tools — 3 tools.

run_backtest, run_preset_backtest, get_backtest_result

비동기 Job 방식:
  1. run_backtest / run_preset_backtest → { job_id, status: "running" }
  2. get_backtest_result(job_id) → polling — completed / failed / running
"""

from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional
from uuid import uuid4

import kis_backtest.strategies.preset  # noqa: F401 — side-effect import (전략 자동 등록)
from kis_backtest.codegen.generator import LeanCodeGenerator, CodeGenConfig
from kis_backtest.file.loader import StrategyFileLoader
from kis_backtest.lean.executor import LeanExecutor
from kis_backtest.lean.project_manager import LeanProjectManager
from kis_backtest.lean.result_formatter import parse_lean_value
from kis_backtest.strategies.registry import StrategyRegistry
from kis_mcp.schemas import error_response, success_response

logger = logging.getLogger(__name__)

# ─── Job Store (파일 영속화 + 메모리 캐시) ────────────────────────────────────

@dataclass
class BacktestJob:
    job_id: str
    status: Literal["pending", "running", "completed", "failed"]
    result: Optional[Dict[str, Any]] = None
    report_path: Optional[Path] = None
    error: Optional[str] = None
    strategy_name: str = ""
    symbols: List[str] = field(default_factory=list)
    start_date: str = ""
    end_date: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    finished_at: Optional[datetime] = None
    # 재시도용 메타데이터 (파일에 저장하지 않음)
    _definition: Any = field(default=None, repr=False)
    _initial_capital: float = 10_000_000
    _commission_rate: float = 0.00015
    _tax_rate: float = 0.002
    _slippage: float = 0.0


_JOB_STORE_DIR = Path.home() / ".kis" / "jobs"


class JobStore:
    """Job 상태 파일 영속화 + 메모리 캐시.

    MCP 재시작 후에도 job_id로 결과를 복구할 수 있다.
    _definition(전략 객체)은 직렬화 불가이므로 파일에 저장하지 않는다.
    """

    def __init__(self) -> None:
        _JOB_STORE_DIR.mkdir(parents=True, exist_ok=True)
        self._cache: Dict[str, BacktestJob] = {}
        self.cleanup()

    def _job_path(self, job_id: str) -> Path:
        return _JOB_STORE_DIR / f"{job_id}.json"

    def save(self, job: BacktestJob) -> None:
        """캐시와 파일에 job 상태 저장."""
        self._cache[job.job_id] = job
        data = {
            "job_id": job.job_id,
            "status": job.status,
            "result": job.result,
            "report_path": str(job.report_path) if job.report_path else None,
            "error": job.error,
            "strategy_name": job.strategy_name,
            "symbols": job.symbols,
            "start_date": job.start_date,
            "end_date": job.end_date,
            "created_at": job.created_at.isoformat(),
            "finished_at": job.finished_at.isoformat() if job.finished_at else None,
            "_initial_capital": job._initial_capital,
            "_commission_rate": job._commission_rate,
            "_tax_rate": job._tax_rate,
            "_slippage": job._slippage,
        }
        try:
            self._job_path(job.job_id).write_text(
                json.dumps(data, ensure_ascii=False), encoding="utf-8"
            )
        except Exception as exc:
            logger.warning(f"[JobStore] 파일 저장 실패 ({job.job_id}): {exc}")

    def get(self, job_id: str) -> Optional[BacktestJob]:
        """캐시 우선 조회, 없으면 파일에서 복구."""
        if job_id in self._cache:
            return self._cache[job_id]
        path = self._job_path(job_id)
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            job = BacktestJob(
                job_id=data["job_id"],
                status=data["status"],
                result=data.get("result"),
                report_path=Path(data["report_path"]) if data.get("report_path") else None,
                error=data.get("error"),
                strategy_name=data.get("strategy_name", ""),
                symbols=data.get("symbols", []),
                start_date=data.get("start_date", ""),
                end_date=data.get("end_date", ""),
                created_at=datetime.fromisoformat(data["created_at"]),
                finished_at=datetime.fromisoformat(data["finished_at"]) if data.get("finished_at") else None,
                _initial_capital=data.get("_initial_capital", 10_000_000),
                _commission_rate=data.get("_commission_rate", 0.00015),
                _tax_rate=data.get("_tax_rate", 0.002),
                _slippage=data.get("_slippage", 0.0),
            )
            self._cache[job_id] = job
            return job
        except Exception as exc:
            logger.warning(f"[JobStore] 파일 로드 실패 ({job_id}): {exc}")
            return None

    def cleanup(self, max_age_hours: int = 24) -> int:
        """24시간 이상 지난 job 파일 삭제."""
        cutoff = datetime.now().timestamp() - max_age_hours * 3600
        removed = 0
        try:
            for path in _JOB_STORE_DIR.glob("*.json"):
                if path.stat().st_mtime < cutoff:
                    path.unlink(missing_ok=True)
                    removed += 1
        except Exception as exc:
            logger.warning(f"[JobStore] cleanup 실패: {exc}")
        return removed


_job_store = JobStore()

_BACKTEST_SEMAPHORE = asyncio.Semaphore(3)


# ─── Error Classification ──────────────────────────────────────────────────────

def _classify_error(msg: str) -> str:
    """에러 메시지를 원인 유형으로 분류합니다."""
    if "EGW00201" in msg or "한도 초과" in msg:
        return "rate_limit"
    msg_lower = msg.lower()
    if "docker" in msg_lower or "cannot connect" in msg_lower:
        return "docker_not_running"
    if "데이터 준비 실패" in msg:
        return "data_not_found"
    return "unknown"


_ERROR_HINTS: Dict[str, str] = {
    "rate_limit": "KIS API 한도 초과(EGW00201). 60초 후 retry_backtest(job_id)를 호출하세요.",
    "docker_not_running": "Docker Desktop이 실행되지 않았습니다. Docker를 시작한 후 retry_backtest(job_id)를 호출하세요.",
    "data_not_found": "시장 데이터를 가져오지 못했습니다. 종목 코드와 날짜 범위를 확인하세요.",
}


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _lean_run_to_result(
    lean_run: Any,
    strategy_name: str,
    symbols: List[str],
    start_date: str,
    end_date: str,
    initial_capital: float,
) -> Dict[str, Any]:
    """LeanRun → 결과 딕셔너리 변환."""
    result = lean_run.load_result()
    stats = lean_run.get_statistics()

    start_equity = parse_lean_value(stats.get("Start Equity", initial_capital))
    end_equity = parse_lean_value(stats.get("End Equity", initial_capital))
    net_profit = end_equity - start_equity
    net_profit_pct = parse_lean_value(stats.get("Net Profit", 0))

    # 자산 곡선
    equity_curve: Dict[str, float] = {}
    charts = result.get("charts", {})
    for point in charts.get("Strategy Equity", {}).get("series", {}).get("Equity", {}).get("values", []):
        if isinstance(point, list) and len(point) >= 2:
            try:
                dt = datetime.fromtimestamp(point[0])
                val = point[4] if len(point) > 4 else point[1]
                equity_curve[dt.strftime("%Y-%m-%d")] = float(val)
            except Exception:
                pass

    # 거래 내역
    orders = result.get("orders", {})
    if isinstance(orders, dict):
        orders = list(orders.values())
    trades = []
    for order in orders:
        if order.get("status") != 3:
            continue
        symbol_data = order.get("symbol", {})
        symbol_code = symbol_data.get("value", "") if isinstance(symbol_data, dict) else str(symbol_data)
        direction = order.get("direction", 0)
        trades.append({
            "symbol": symbol_code.upper(),
            "direction": "Buy" if direction == 0 else "Sell",
            "quantity": abs(order.get("quantity", 0)),
            "price": order.get("price", 0),
            "time": order.get("time", ""),
        })

    return {
        "run_id": lean_run.project.run_id,
        "strategy_name": strategy_name,
        "symbols": symbols,
        "start_date": start_date,
        "end_date": end_date,
        "initial_capital": initial_capital,
        "final_capital": end_equity,
        "net_profit": net_profit,
        "net_profit_percent": net_profit_pct,
        "metrics": {
            "basic": {
                "total_return": net_profit_pct,
                "annual_return": parse_lean_value(stats.get("Compounding Annual Return", 0)),
                "max_drawdown": parse_lean_value(stats.get("Drawdown", 0)),
                "drawdown_recovery": parse_lean_value(stats.get("Drawdown Recovery", 0)),
                "start_equity": start_equity,
                "end_equity": end_equity,
            },
            "risk": {
                "sharpe_ratio": parse_lean_value(stats.get("Sharpe Ratio", 0)),
                "sortino_ratio": parse_lean_value(stats.get("Sortino Ratio", 0)),
            },
            "trading": {
                "total_orders": int(parse_lean_value(stats.get("Total Orders", 0))),
                "win_rate": parse_lean_value(stats.get("Win Rate", 0)),
                "loss_rate": parse_lean_value(stats.get("Loss Rate", 0)),
                "avg_win": parse_lean_value(stats.get("Average Win", 0)),
                "avg_loss": parse_lean_value(stats.get("Average Loss", 0)),
                "profit_loss_ratio": parse_lean_value(stats.get("Profit-Loss Ratio", 0)),
            },
        },
        "equity_curve": equity_curve,
        "trades_count": len(trades),
        "trades": trades,
        # Lean 원본 통계 (flat key 형식) — 확장 지표 렌더링용
        "raw_statistics": stats,
    }


async def _run_backtest_task(
    job_id: str,
    definition: Any,
    symbols: List[str],
    start_date: str,
    end_date: str,
    initial_capital: float,
    commission_rate: float,
    tax_rate: float,
    slippage: float = 0.0,
) -> None:
    """백그라운드 백테스트 작업 (asyncio.create_task 대상).

    동시 실행을 최대 3개로 제한하며, 완료/실패 시 파일에 영속화한다.
    에러는 원인별로 분류해 사용자 친화적 안내 메시지를 포함한다.
    """
    async with _BACKTEST_SEMAPHORE:  # 동시 실행 제한 (pending 상태에서 대기)
        job = _job_store.get(job_id)
        if job is None:
            logger.error(f"[MCP job={job_id}] job을 찾을 수 없습니다.")
            return

        job.status = "running"
        _job_store.save(job)

        try:
            manager = LeanProjectManager()
            workspace = manager.workspace

            # 벤치마크 데이터 준비 (주식보다 먼저 — Rate limit 회피)
            from backend.routes.backtest import prepare_benchmark_data, prepare_market_data
            try:
                await prepare_benchmark_data(
                    start_date=start_date,
                    end_date=end_date,
                    workspace=workspace,
                )
            except Exception as bm_exc:
                logger.warning(f"[MCP job={job_id}] 벤치마크 준비 실패 (무시): {bm_exc}")

            # Rate limit 방지: 벤치마크 다운로드 후 1초 대기
            await asyncio.sleep(1)

            # 시장 데이터 준비
            data_result = await prepare_market_data(
                symbols=symbols,
                start_date=start_date,
                end_date=end_date,
                workspace=workspace,
            )
            logger.info(f"[MCP job={job_id}] data result: {data_result}")

            if data_result["errors"] and not data_result["downloaded"] and not data_result["skipped"]:
                err = data_result["errors"][0]["error"]
                raise RuntimeError(f"데이터 준비 실패: {err}")

            # Lean 코드 생성
            config = CodeGenConfig(
                commission_rate=commission_rate,
                tax_rate=tax_rate,
                slippage=slippage,
                initial_capital=initial_capital,
            )
            generator = LeanCodeGenerator(definition, config=config)
            code = generator.generate(
                symbols=symbols,
                start_date=start_date,
                end_date=end_date,
                initial_capital=initial_capital,
            )

            # Docker 확인
            if not LeanExecutor.check_docker():
                raise RuntimeError("Docker가 실행되지 않습니다. Docker Desktop을 시작해주세요.")
            if not LeanExecutor.check_image():
                raise RuntimeError("Lean 이미지가 없습니다. 'docker pull quantconnect/lean:latest' 실행 후 재시도해주세요.")

            # 프로젝트 생성 및 실행
            project = LeanProjectManager.create_project(
                run_id=f"mcp_{job_id[:8]}_{definition.id}",
                symbols=symbols,
                start_date=start_date,
                end_date=end_date,
                initial_capital=initial_capital,
                strategy_id=definition.id,
                strategy_name=definition.name,
            )
            project.main_py.write_text(code)

            lean_run = await asyncio.to_thread(LeanExecutor.run, project)

            if lean_run.success:
                result_data = _lean_run_to_result(
                    lean_run,
                    strategy_name=definition.name,
                    symbols=symbols,
                    start_date=start_date,
                    end_date=end_date,
                    initial_capital=initial_capital,
                )
                job.status = "completed"
                job.result = result_data
                job.report_path = lean_run.output_dir
            else:
                error_msg = lean_run.error or "백테스트 실패"
                err_type = _classify_error(error_msg)
                hint = _ERROR_HINTS.get(err_type, "")
                job.status = "failed"
                job.error = f"{error_msg}\n\n💡 {hint}" if hint else error_msg

        except Exception as exc:
            logger.exception(f"[MCP job={job_id}] 실패")
            err_msg = str(exc)
            err_type = _classify_error(err_msg)
            hint = _ERROR_HINTS.get(err_type, "")
            job.status = "failed"
            job.error = f"{err_msg}\n\n💡 {hint}" if hint else err_msg
        finally:
            job.finished_at = datetime.now()
            _job_store.save(job)


def _submit_job(
    definition: Any,
    symbols: List[str],
    start_date: str,
    end_date: str,
    initial_capital: float,
    commission_rate: float = 0.00015,
    tax_rate: float = 0.002,
    slippage: float = 0.0,
) -> str:
    """Job 등록 후 job_id 반환."""
    job_id = str(uuid4())
    job = BacktestJob(
        job_id=job_id,
        status="pending",
        strategy_name=getattr(definition, "name", ""),
        symbols=symbols,
        start_date=start_date,
        end_date=end_date,
        _definition=definition,
        _initial_capital=initial_capital,
        _commission_rate=commission_rate,
        _tax_rate=tax_rate,
        _slippage=slippage,
    )
    _job_store.save(job)

    asyncio.create_task(
        _run_backtest_task(
            job_id=job_id,
            definition=definition,
            symbols=symbols,
            start_date=start_date,
            end_date=end_date,
            initial_capital=initial_capital,
            commission_rate=commission_rate,
            tax_rate=tax_rate,
            slippage=slippage,
        )
    )
    return job_id


# ─── MCP Tool Functions ────────────────────────────────────────────────────────

def run_backtest(
    yaml_content: str,
    symbols: List[str],
    start_date: str,
    end_date: str,
    initial_capital: float = 10_000_000,
    commission_rate: float = 0.00015,
    tax_rate: float = 0.002,
    slippage: float = 0.0,
) -> dict:
    """YAML 전략을 백테스트합니다 (비동기 — 즉시 job_id 반환).

    Args:
        yaml_content: .kis.yaml 포맷 전략 문자열
        symbols: 종목 코드 리스트 (예: ["005930", "000660"])
        start_date: 시작일 (YYYY-MM-DD)
        end_date: 종료일 (YYYY-MM-DD)
        initial_capital: 초기 자본 (원, 기본 1000만)
        commission_rate: 수수료율 (기본 0.015%)
        tax_rate: 세율 (기본 0.2%)
        slippage: 슬리피지 (기본 0%, KRXSlippageModel 적용)

    Returns:
        { job_id, status: "running" }  — get_backtest_result(job_id) 로 결과 조회
    """
    try:
        definition = StrategyFileLoader.load_from_string(yaml_content).to_strategy_definition()
    except ValueError as exc:
        return error_response(f"YAML 파싱 오류: {exc}")
    except Exception as exc:
        logger.exception("run_backtest: YAML 로드 실패")
        return error_response(str(exc))

    try:
        job_id = _submit_job(
            definition=definition,
            symbols=symbols,
            start_date=start_date,
            end_date=end_date,
            initial_capital=initial_capital,
            commission_rate=commission_rate,
            tax_rate=tax_rate,
            slippage=slippage,
        )
        return success_response(
            {"job_id": job_id, "status": "running"},
            message="백테스트 시작됨. get_backtest_result(job_id)로 결과를 조회하세요.",
        )
    except Exception as exc:
        logger.exception("run_backtest: job 제출 실패")
        return error_response(str(exc))


def run_preset_backtest(
    strategy_id: str,
    symbols: List[str],
    start_date: str,
    end_date: str,
    initial_capital: float = 10_000_000,
    param_overrides: Optional[Dict[str, Any]] = None,
    commission_rate: float = 0.00015,
    tax_rate: float = 0.002,
    slippage: float = 0.0,
) -> dict:
    """프리셋 전략을 백테스트합니다 (비동기 — 즉시 job_id 반환).

    Args:
        strategy_id: 전략 ID (예: "sma_crossover", "momentum")
        symbols: 종목 코드 리스트 (예: ["005930"])
        start_date: 시작일 (YYYY-MM-DD)
        end_date: 종료일 (YYYY-MM-DD)
        initial_capital: 초기 자본 (원, 기본 1000만)
        param_overrides: 파라미터 오버라이드 (예: {"period": 21})
        commission_rate: 수수료율
        tax_rate: 세율

    Returns:
        { job_id, status: "running" }
    """
    try:
        overrides = param_overrides or {}
        definition = StrategyRegistry.build_with_params(strategy_id, **overrides)
        if definition is None:
            return error_response(
                f"전략 '{strategy_id}'를 찾을 수 없습니다.",
                details={"available": [s["id"] for s in StrategyRegistry.list_all()]},
            )
    except Exception as exc:
        logger.exception("run_preset_backtest: 전략 빌드 실패")
        return error_response(str(exc))

    try:
        job_id = _submit_job(
            definition=definition,
            symbols=symbols,
            start_date=start_date,
            end_date=end_date,
            initial_capital=initial_capital,
            commission_rate=commission_rate,
            tax_rate=tax_rate,
            slippage=slippage,
        )
        return success_response(
            {
                "job_id": job_id,
                "status": "running",
                "strategy_id": strategy_id,
                "strategy_name": definition.name,
            },
            message="백테스트 시작됨. get_backtest_result(job_id)로 결과를 조회하세요.",
        )
    except Exception as exc:
        logger.exception("run_preset_backtest: job 제출 실패")
        return error_response(str(exc))


def get_backtest_result(job_id: str) -> dict:
    """백테스트 결과를 즉시 조회합니다 (단발성).

    Args:
        job_id: run_backtest / run_preset_backtest 반환값의 job_id

    Returns:
        완료 전: { job_id, status: "running"|"pending" }
        완료 후: { job_id, status: "completed", result: { ... } }
        실패 시: { job_id, status: "failed", error: "..." }
    """
    job = _job_store.get(job_id)
    if job is None:
        return error_response(f"job_id '{job_id}'를 찾을 수 없습니다.")

    return _job_to_response(job)


async def get_backtest_result_wait(
    job_id: str,
    poll_interval: float = 3.0,
    timeout: float = 300.0,
) -> dict:
    """백테스트 완료까지 내부 폴링 후 결과를 반환합니다.

    MCP tool에서 한 번만 호출하면 완료/실패까지 대기 후 결과를 돌려준다.
    외부 폴링이 필요 없으므로 tool 승인 요청이 1회로 줄어든다.

    Args:
        job_id: run_backtest / run_preset_backtest 반환값의 job_id
        poll_interval: 폴링 간격 (초, 기본 3초)
        timeout: 최대 대기 시간 (초, 기본 300초=5분)

    Returns:
        완료: { job_id, status: "completed", result: { ... } }
        실패: { job_id, status: "failed", error: "..." }
        타임아웃: { job_id, status: "running", message: "..." }
    """
    job = _job_store.get(job_id)
    if job is None:
        return error_response(f"job_id '{job_id}'를 찾을 수 없습니다.")

    elapsed = 0.0
    while elapsed < timeout:
        job = _job_store.get(job_id)
        if job is None:
            return error_response(f"job_id '{job_id}'가 사라졌습니다.")

        if job.status in ("completed", "failed"):
            return _job_to_response(job)

        await asyncio.sleep(poll_interval)
        elapsed += poll_interval

    return success_response(
        {
            "job_id": job_id,
            "status": job.status if job else "unknown",
            "waited_seconds": round(elapsed, 1),
        },
        message=f"타임아웃 ({timeout}초). 백테스트가 아직 실행 중입니다. 다시 호출하세요.",
    )


def _job_to_response(job: BacktestJob) -> dict:
    """BacktestJob → MCP 응답 딕셔너리 변환."""
    payload: Dict[str, Any] = {
        "job_id": job.job_id,
        "status": job.status,
        "strategy_name": job.strategy_name,
        "symbols": job.symbols,
        "created_at": job.created_at.isoformat(),
    }

    if job.status == "completed":
        payload["result"] = job.result
        payload["finished_at"] = job.finished_at.isoformat() if job.finished_at else None
        elapsed = (job.finished_at - job.created_at).total_seconds() if job.finished_at else 0
        payload["elapsed_seconds"] = round(elapsed, 1)
        return success_response(payload, message="백테스트 완료")

    if job.status == "failed":
        payload["error"] = job.error
        return error_response(f"백테스트 실패: {job.error}", details=payload)

    # pending / running — optimize job의 진행률 포함
    if job.result and "progress" in job.result:
        payload["progress"] = job.result["progress"]
    return success_response(payload, message="백테스트 진행 중...")


def retry_backtest(job_id: str) -> dict:
    """실패한 백테스트를 재시도합니다 (rate limit 오류 등으로 실패 시).

    캐시된 종목 데이터는 재다운로드하지 않습니다.
    EGW00201(한도 초과) 오류 이후 충분히 대기한 뒤 호출하세요.

    Args:
        job_id: 실패한 run_backtest / run_preset_backtest 의 job_id

    Returns:
        { new_job_id, status: "running" }  — get_backtest_result(new_job_id) 로 결과 조회
    """
    job = _job_store.get(job_id)
    if job is None:
        return error_response(f"job_id '{job_id}'를 찾을 수 없습니다.")

    if job.status == "completed":
        return error_response(
            "이미 완료된 백테스트입니다.",
            details={"job_id": job_id, "status": "completed"},
        )

    if job.status in ("pending", "running"):
        return error_response(
            "백테스트가 아직 실행 중입니다.",
            details={"job_id": job_id, "status": job.status},
        )

    if job._definition is None:
        return error_response(
            "재시도에 필요한 전략 정보가 없습니다. run_preset_backtest 또는 run_backtest로 새로 실행하세요."
        )

    try:
        new_job_id = _submit_job(
            definition=job._definition,
            symbols=job.symbols,
            start_date=job.start_date,
            end_date=job.end_date,
            initial_capital=job._initial_capital,
            commission_rate=job._commission_rate,
            tax_rate=job._tax_rate,
            slippage=job._slippage,
        )
        return success_response(
            {
                "new_job_id": new_job_id,
                "original_job_id": job_id,
                "status": "running",
                "strategy_name": job.strategy_name,
                "symbols": job.symbols,
            },
            message="재시도 시작됨. get_backtest_result(new_job_id)로 결과를 조회하세요.",
        )
    except Exception as exc:
        logger.exception("retry_backtest: job 제출 실패")
        return error_response(str(exc))


# ─── Batch & Optimize Helpers ─────────────────────────────────────────────────

def _extract_metric(result_data: Optional[Dict[str, Any]], metric: str) -> float:
    """result dict에서 지표 값 추출 (metrics.basic / metrics.risk / metrics.trading 계층)."""
    if not result_data:
        return 0.0
    m = result_data.get("metrics", {})
    lookup: Dict[str, float] = {
        "sharpe_ratio": m.get("risk", {}).get("sharpe_ratio", 0.0),
        "sortino_ratio": m.get("risk", {}).get("sortino_ratio", 0.0),
        "total_return": m.get("basic", {}).get("total_return", 0.0),
        "annual_return": m.get("basic", {}).get("annual_return", 0.0),
        "max_drawdown": m.get("basic", {}).get("max_drawdown", 0.0),
        "win_rate": m.get("trading", {}).get("win_rate", 0.0),
        "profit_loss_ratio": m.get("trading", {}).get("profit_loss_ratio", 0.0),
    }
    return float(lookup.get(metric, 0.0))


def _build_comparison(runs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """run 결과 리스트 → 샤프/수익률/낙폭 순 비교 딕셔너리."""
    successful = [r for r in runs if r.get("status") == "completed" and r.get("result")]

    def _row(r: Dict[str, Any]) -> Dict[str, Any]:
        res = r.get("result") or {}
        return {
            "job_id": r.get("job_id"),
            "strategy_name": r.get("strategy_name") or res.get("strategy_name", ""),
            "symbols": r.get("symbols") or res.get("symbols", []),
            "sharpe_ratio": _extract_metric(res, "sharpe_ratio"),
            "total_return": _extract_metric(res, "total_return"),
            "annual_return": _extract_metric(res, "annual_return"),
            "max_drawdown": _extract_metric(res, "max_drawdown"),
            "win_rate": _extract_metric(res, "win_rate"),
        }

    return {
        "total_submitted": len(runs),
        "completed": len(successful),
        "failed": len(runs) - len(successful),
        "comparison": {
            "by_sharpe": [_row(r) for r in sorted(successful, key=lambda x: _extract_metric(x.get("result"), "sharpe_ratio"), reverse=True)],
            "by_return": [_row(r) for r in sorted(successful, key=lambda x: _extract_metric(x.get("result"), "total_return"), reverse=True)],
            "by_drawdown": [_row(r) for r in sorted(successful, key=lambda x: _extract_metric(x.get("result"), "max_drawdown"))],
        },
    }


# ─── Batch Backtest ────────────────────────────────────────────────────────────

async def run_batch_backtest(
    items: List[Dict[str, Any]],
    start_date: str,
    end_date: str,
    initial_capital: float = 10_000_000,
    commission_rate: float = 0.00015,
    tax_rate: float = 0.002,
) -> dict:
    """여러 전략을 동시에 백테스트한 뒤 비교 결과를 반환합니다.

    Args:
        items: 전략 목록. 각 항목에 다음 키 포함:
               - {"strategy_id": "sma_crossover", "symbols": ["005930"], "param_overrides": {...}}
               - {"yaml_content": "...", "symbols": ["005930"]}
        start_date: 공통 시작일 (YYYY-MM-DD)
        end_date: 공통 종료일 (YYYY-MM-DD)
        initial_capital: 공통 초기 자본금
        commission_rate: 공통 수수료율
        tax_rate: 공통 세율

    Returns:
        { completed, failed, comparison: { by_sharpe, by_return, by_drawdown }, runs, job_ids }
    """
    if not items:
        return error_response("items가 비어있습니다.")

    job_ids: List[str] = []
    submission_errors: List[Dict[str, Any]] = []

    for i, item in enumerate(items):
        try:
            symbols = item.get("symbols") or []
            if not symbols:
                submission_errors.append({"index": i, "error": "symbols 누락", "item": item})
                continue

            if "strategy_id" in item:
                overrides = item.get("param_overrides") or {}
                definition = StrategyRegistry.build_with_params(item["strategy_id"], **overrides)
                if definition is None:
                    submission_errors.append({
                        "index": i,
                        "error": f"전략 '{item['strategy_id']}'를 찾을 수 없습니다.",
                        "item": item,
                    })
                    continue
            elif "yaml_content" in item:
                definition = StrategyFileLoader.load_from_string(item["yaml_content"]).to_strategy_definition()
            else:
                submission_errors.append({"index": i, "error": "strategy_id 또는 yaml_content 필요", "item": item})
                continue

            jid = _submit_job(
                definition=definition,
                symbols=symbols,
                start_date=start_date,
                end_date=end_date,
                initial_capital=initial_capital,
                commission_rate=commission_rate,
                tax_rate=tax_rate,
                slippage=item.get("slippage", 0.0),
            )
            job_ids.append(jid)
        except Exception as exc:
            submission_errors.append({"index": i, "error": str(exc), "item": item})

    if not job_ids:
        return error_response("제출된 job이 없습니다.", details={"errors": submission_errors})

    # 모든 job 동시 대기 (asyncio.gather — N개 순차 대기보다 훨씬 빠름)
    wait_results = await asyncio.gather(*[get_backtest_result_wait(jid) for jid in job_ids])

    runs: List[Dict[str, Any]] = []
    for jid, resp in zip(job_ids, wait_results):
        job = _job_store.get(jid)
        resp_data = resp.get("data", {}) if resp.get("success") else {}
        runs.append({
            "job_id": jid,
            "status": resp_data.get("status", "failed"),
            "strategy_name": job.strategy_name if job else "",
            "symbols": job.symbols if job else [],
            "result": resp_data.get("result"),
            "error": resp.get("error") if not resp.get("success") else None,
            "elapsed_seconds": resp_data.get("elapsed_seconds"),
        })

    comparison = _build_comparison(runs)
    comparison["job_ids"] = job_ids
    comparison["submission_errors"] = submission_errors
    comparison["runs"] = runs

    return success_response(
        comparison,
        message=f"배치 백테스트 완료: {comparison['completed']}/{comparison['total_submitted']}개 성공",
    )


# ─── Optimize ─────────────────────────────────────────────────────────────────

async def _run_optimize_task(
    parent_job_id: str,
    strategy_id: str,
    symbols: List[str],
    start_date: str,
    end_date: str,
    param_combinations: List[Dict[str, Any]],
    target: str,
    initial_capital: float,
    commission_rate: float,
    tax_rate: float,
    slippage: float = 0.0,
) -> None:
    """파라미터 최적화 백그라운드 작업. asyncio.gather로 sub-job 병렬 실행."""
    parent_job = _job_store.get(parent_job_id)
    if parent_job is None:
        return

    total = len(param_combinations)
    parent_job.status = "running"
    parent_job.result = {"progress": {"done": 0, "total": total}}
    _job_store.save(parent_job)

    # 모든 sub-job 제출 (semaphore는 _run_backtest_task 내부에서 처리)
    sub_job_ids: List[Optional[str]] = []
    for params in param_combinations:
        try:
            definition = StrategyRegistry.build_with_params(strategy_id, **params)
            if definition is None:
                sub_job_ids.append(None)
                continue
            jid = _submit_job(
                definition=definition,
                symbols=symbols,
                start_date=start_date,
                end_date=end_date,
                initial_capital=initial_capital,
                commission_rate=commission_rate,
                tax_rate=tax_rate,
                slippage=slippage,
            )
            sub_job_ids.append(jid)
        except Exception as exc:
            logger.warning(f"[optimize parent={parent_job_id}] sub-job 제출 실패 params={params}: {exc}")
            sub_job_ids.append(None)

    done_count = 0

    async def _wait_one(params: Dict[str, Any], sub_jid: Optional[str]) -> Dict[str, Any]:
        nonlocal done_count
        if sub_jid is None:
            done_count += 1
            pj = _job_store.get(parent_job_id)
            if pj and pj.result:
                pj.result = {**pj.result, "progress": {"done": done_count, "total": total}}
                _job_store.save(pj)
            return {"params": params, "job_id": None, "status": "failed", "error": "sub-job 제출 실패", "result": None}

        resp = await get_backtest_result_wait(sub_jid)
        done_count += 1
        pj = _job_store.get(parent_job_id)
        if pj and pj.result:
            pj.result = {**pj.result, "progress": {"done": done_count, "total": total}}
            _job_store.save(pj)

        resp_data = resp.get("data", {}) if resp.get("success") else {}
        return {
            "params": params,
            "job_id": sub_jid,
            "status": resp_data.get("status", "failed"),
            "result": resp_data.get("result"),
            "error": resp.get("error") if not resp.get("success") else None,
        }

    all_run_results: List[Dict[str, Any]] = await asyncio.gather(*[
        _wait_one(params, sub_jid)
        for params, sub_jid in zip(param_combinations, sub_job_ids)
    ])

    successful = [r for r in all_run_results if r.get("status") == "completed" and r.get("result")]

    _minimize_targets = {"max_drawdown"}
    if successful:
        if target in _minimize_targets:
            best: Optional[Dict[str, Any]] = min(successful, key=lambda r: _extract_metric(r.get("result"), target))
        else:
            best = max(successful, key=lambda r: _extract_metric(r.get("result"), target))
    else:
        best = None

    final_result: Dict[str, Any] = {
        "best_params": best["params"] if best else None,
        "best_job_id": best["job_id"] if best else None,
        "best_metrics": {
            "sharpe_ratio": _extract_metric(best.get("result"), "sharpe_ratio"),
            "total_return": _extract_metric(best.get("result"), "total_return"),
            "annual_return": _extract_metric(best.get("result"), "annual_return"),
            "max_drawdown": _extract_metric(best.get("result"), "max_drawdown"),
            "win_rate": _extract_metric(best.get("result"), "win_rate"),
        } if best else None,
        "target": target,
        "total_runs": total,
        "successful_runs": len(successful),
        "failed_runs": total - len(successful),
        "all_runs": [
            {
                "params": r["params"],
                "job_id": r.get("job_id"),
                "status": r.get("status"),
                "sharpe_ratio": _extract_metric(r.get("result"), "sharpe_ratio"),
                "total_return": _extract_metric(r.get("result"), "total_return"),
                "max_drawdown": _extract_metric(r.get("result"), "max_drawdown"),
                "win_rate": _extract_metric(r.get("result"), "win_rate"),
                "error": r.get("error"),
            }
            for r in all_run_results
        ],
        "progress": {"done": total, "total": total},
    }

    pj = _job_store.get(parent_job_id)
    if pj:
        pj.status = "completed"
        pj.result = final_result
        pj.finished_at = datetime.now()
        _job_store.save(pj)


def run_optimize(
    strategy_id: str,
    symbols: List[str],
    start_date: str,
    end_date: str,
    parameters: List[Dict[str, Any]],
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

    Args:
        strategy_id: 전략 ID (예: "sma_crossover")
        symbols: 종목 코드 리스트 (예: ["005930"])
        start_date: 시작일 (YYYY-MM-DD)
        end_date: 종료일 (YYYY-MM-DD)
        parameters: 파라미터 정의 [{"name": "fast_period", "min": 5, "max": 20, "step": 5}, ...]
        search_type: "grid" (전체 탐색) 또는 "random" (무작위 샘플링)
        max_samples: random search 최대 샘플 수
        target: 최적화 목표 ("sharpe_ratio", "total_return", "max_drawdown", "win_rate")
        initial_capital: 초기 자본금 (원)
        commission_rate: 수수료율
        tax_rate: 세율
        seed: random search 재현성 시드
        slippage: 슬리피지 (기본 0%, 0.001=0.1%로 설정 시 KRXSlippageModel 적용)

    Returns:
        { job_id, status: "running", total_combinations, search_type }
        — get_backtest_result(job_id)로 진행률/최종 결과 조회
    """
    try:
        test_def = StrategyRegistry.build_with_params(strategy_id)
        if test_def is None:
            return error_response(
                f"전략 '{strategy_id}'를 찾을 수 없습니다.",
                details={"available": [s["id"] for s in StrategyRegistry.list_all()]},
            )
    except Exception as exc:
        return error_response(f"전략 검증 실패: {exc}")

    try:
        from kis_backtest.lean.optimizer import ParameterGrid, ParameterSpec
        specs = [ParameterSpec(p["name"], p["min"], p["max"], p["step"]) for p in parameters]
        grid = ParameterGrid(specs)
        param_combinations = grid.sample(max_samples, seed=seed) if search_type == "random" else list(grid)
        total_combinations = len(param_combinations)
    except Exception as exc:
        return error_response(f"파라미터 그리드 생성 실패: {exc}")

    if total_combinations == 0:
        return error_response("파라미터 조합이 없습니다. parameters 범위를 확인하세요.")

    parent_job_id = str(uuid4())
    parent_job = BacktestJob(
        job_id=parent_job_id,
        status="pending",
        strategy_name=f"{strategy_id} [optimize/{search_type}]",
        symbols=symbols,
        start_date=start_date,
        end_date=end_date,
        _initial_capital=initial_capital,
        _commission_rate=commission_rate,
        _tax_rate=tax_rate,
    )
    parent_job.result = {"progress": {"done": 0, "total": total_combinations}}
    _job_store.save(parent_job)

    asyncio.create_task(
        _run_optimize_task(
            parent_job_id=parent_job_id,
            strategy_id=strategy_id,
            symbols=symbols,
            start_date=start_date,
            end_date=end_date,
            param_combinations=param_combinations,
            target=target,
            initial_capital=initial_capital,
            commission_rate=commission_rate,
            tax_rate=tax_rate,
            slippage=slippage,
        )
    )

    return success_response(
        {
            "job_id": parent_job_id,
            "status": "running",
            "strategy_id": strategy_id,
            "search_type": search_type,
            "total_combinations": total_combinations,
            "target": target,
        },
        message=f"최적화 시작됨 ({total_combinations}개 조합). get_backtest_result(job_id)로 진행/결과를 조회하세요.",
    )
