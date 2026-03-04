"""Backtest API Routes.

Lean Docker 기반 백테스트 실행.
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import date, datetime, timedelta
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.schemas.backtest import (
    BacktestRequest,
    BacktestResponse,
)
from kis_backtest.strategies.registry import StrategyRegistry
from kis_backtest.codegen.generator import LeanCodeGenerator, CodeGenConfig
from kis_backtest.lean.executor import LeanExecutor, LeanRun
from kis_backtest.lean.project_manager import LeanProjectManager
from kis_backtest.lean.data_converter import DataConverter
from kis_backtest.lean.result_formatter import parse_lean_value
import kis_backtest.strategies.preset  # 전략 자동 등록


def _load_benchmark_curve(
    workspace: Path,
    start_date: str,
    end_date: str,
) -> Optional[Dict[str, float]]:
    """KOSPI 벤치마크 수익률 곡선 로드

    Returns:
        날짜별 수익률 % (시작일 대비). 예: {"2024-01-02": 0.0, "2024-01-03": 1.5, ...}
    """
    csv_path = workspace / "data" / "index" / "krx" / "daily" / "kospi.csv"

    if not csv_path.exists():
        return None

    try:
        # 날짜 범위
        req_start = datetime.strptime(start_date, "%Y-%m-%d").date()
        req_end = datetime.strptime(end_date, "%Y-%m-%d").date()

        # CSV 파싱 (YYYYMMDD,open,high,low,close,volume)
        prices = {}
        with open(csv_path, "r") as f:
            for line in f:
                parts = line.strip().split(",")
                if len(parts) < 5:
                    continue
                try:
                    dt = datetime.strptime(parts[0], "%Y%m%d").date()
                    close = float(parts[4])
                    if req_start <= dt <= req_end:
                        prices[dt] = close
                except (ValueError, IndexError):
                    continue

        if not prices:
            return None

        # 시작일 기준 수익률 계산
        sorted_dates = sorted(prices.keys())
        base_price = prices[sorted_dates[0]]

        if base_price <= 0:
            return None

        # 데이터가 종료일에 충분히 가깝지 않으면 None 반환
        # (낡은 캐시로 인한 절반짜리 선 방지 — 없는 게 잘리는 것보다 낫다)
        last_data_date = sorted_dates[-1]
        if last_data_date < req_end - timedelta(days=14):
            logging.getLogger(__name__).warning(
                f"[Benchmark] 데이터 종료일 부족: 데이터={last_data_date}, 요청={req_end} "
                f"→ 벤치마크 선 비활성화"
            )
            return None

        curve = {}
        for dt in sorted_dates:
            pct = ((prices[dt] - base_price) / base_price) * 100
            curve[dt.strftime("%Y-%m-%d")] = round(pct, 2)

        return curve

    except Exception as e:
        logging.getLogger(__name__).warning(f"벤치마크 로드 실패: {e}")
        return None


def _lean_run_to_api_response(
    lean_run: LeanRun,
    strategy_name: str,
    symbols: List[str],
    start_date: str,
    end_date: str,
    initial_capital: float,
    workspace: Optional[Path] = None,
) -> Dict[str, Any]:
    """LeanRun을 프론트엔드 API 응답 형식으로 변환"""
    if not lean_run.success:
        raise ValueError(lean_run.error or "백테스트 실패")

    result = lean_run.load_result()
    stats = lean_run.get_statistics()

    # 기본 통계
    net_profit_pct = parse_lean_value(stats.get("Net Profit", 0))
    start_equity = parse_lean_value(stats.get("Start Equity", initial_capital))
    end_equity = parse_lean_value(stats.get("End Equity", initial_capital))
    net_profit = end_equity - start_equity

    # 자산 곡선 (date -> value dict)
    equity_curve = {}
    charts = result.get("charts", {})
    strategy_equity = charts.get("Strategy Equity", {})
    series = strategy_equity.get("series", {})
    equity_series = series.get("Equity", {})
    values = equity_series.get("values", [])
    for point in values:
        if isinstance(point, list) and len(point) >= 2:
            try:
                dt = datetime.fromtimestamp(point[0])
                val = point[4] if len(point) > 4 else point[1]
                equity_curve[dt.strftime("%Y-%m-%d")] = float(val)
            except:
                pass

    # 거래 내역
    orders = result.get("orders", {})
    if isinstance(orders, dict):
        orders = list(orders.values())
    trades = []
    for order in orders:
        if order.get("status") != 3:  # Filled only
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
                "start_equity": start_equity,
                "end_equity": end_equity,
            },
            "risk": {
                "sharpe_ratio": parse_lean_value(stats.get("Sharpe Ratio", 0)),
                "sortino_ratio": parse_lean_value(stats.get("Sortino Ratio", 0)),
                "probabilistic_sharpe": parse_lean_value(stats.get("Probabilistic Sharpe Ratio", 0)),
            },
            "greeks": {
                "alpha": parse_lean_value(stats.get("Alpha", 0)),
                "beta": parse_lean_value(stats.get("Beta", 0)),
            },
            "volatility": {
                "annual_std_dev": parse_lean_value(stats.get("Annual Standard Deviation", 0)),
                "annual_variance": parse_lean_value(stats.get("Annual Variance", 0)),
            },
            "benchmark": {
                "information_ratio": parse_lean_value(stats.get("Information Ratio", 0)),
                "tracking_error": parse_lean_value(stats.get("Tracking Error", 0)),
                "treynor_ratio": parse_lean_value(stats.get("Treynor Ratio", 0)),
            },
            "trading": {
                "total_orders": int(parse_lean_value(stats.get("Total Orders", 0))),
                "win_rate": parse_lean_value(stats.get("Win Rate", 0)),
                "loss_rate": parse_lean_value(stats.get("Loss Rate", 0)),
                "avg_win": parse_lean_value(stats.get("Average Win", 0)),
                "avg_loss": parse_lean_value(stats.get("Average Loss", 0)),
                "profit_loss_ratio": parse_lean_value(stats.get("Profit-Loss Ratio", 0)),
                "expectancy": parse_lean_value(stats.get("Expectancy", 0)),
            },
            "other": {
                "total_fees": parse_lean_value(stats.get("Total Fees", 0)),
                "portfolio_turnover": parse_lean_value(stats.get("Portfolio Turnover", 0)),
                "drawdown_recovery": parse_lean_value(stats.get("Drawdown Recovery", 0)),
            },
        },
        "equity_curve": equity_curve,
        "benchmark_curve": _load_benchmark_curve(workspace, start_date, end_date) if workspace else None,
        "trades_count": len(trades),
        "trades": trades,
    }

logger = logging.getLogger(__name__)
router = APIRouter()


def _classify_lean_error(error: str, output: str) -> str:
    """Lean 에러 메시지를 사용자 친화적으로 분류

    Args:
        error: stderr 내용
        output: stdout 내용

    Returns:
        사용자 친화적 에러 메시지
    """
    combined = f"{error} {output}".lower()

    # 데이터 관련
    if "no data" in combined or "data not found" in combined:
        return "종목 데이터가 없습니다. 종목 코드를 확인하거나 다른 기간을 선택해주세요."

    if "invalid symbol" in combined or "unknown symbol" in combined:
        return "잘못된 종목 코드입니다. 종목 코드를 확인해주세요."

    # 지표 관련
    if "indicator" in combined and ("not found" in combined or "undefined" in combined):
        return "지표 초기화 실패. 전략의 지표 설정을 확인해주세요."

    if "update" in combined and "tradebar" in combined:
        return "지표 업데이트 오류. 해당 지표는 TradeBar 데이터가 필요합니다."

    # Python 문법
    if "syntaxerror" in combined or "indentationerror" in combined:
        return "전략 코드 생성 오류. 전략 정의를 확인해주세요."

    if "nameerror" in combined or "attributeerror" in combined:
        return f"전략 실행 오류: 정의되지 않은 변수나 속성 참조. ({error[:100]})"

    # 메모리/타임아웃
    if "timeout" in combined or "타임아웃" in combined:
        return "백테스트 시간 초과. 기간을 줄이거나 전략을 단순화해주세요."

    if "memory" in combined or "out of memory" in combined:
        return "메모리 부족. 백테스트 기간을 줄여주세요."

    # Docker 관련
    if "docker" in combined and ("daemon" in combined or "not running" in combined):
        return "Docker가 실행되지 않습니다. Docker Desktop을 시작해주세요."

    # 일반 에러
    if len(error) > 200:
        return f"백테스트 실패: {error[:200]}..."

    return f"백테스트 실패: {error}"


async def prepare_market_data(
    symbols: List[str],
    start_date: str,
    end_date: str,
    workspace: Path,
) -> dict:
    """백테스트용 시장 데이터 준비 (KIS API → Lean CSV)
    
    Returns:
        {"downloaded": [...], "skipped": [...], "errors": [...]}
    """
    from kis_backtest.providers.kis.auth import KISAuth
    from kis_backtest.providers.kis.data import KISDataProvider
    
    output_dir = workspace / "data" / "equity" / "krx" / "daily"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    result = {"downloaded": [], "skipped": [], "errors": []}
    
    # 요청 날짜 파싱
    req_start = datetime.strptime(start_date, "%Y-%m-%d").date()
    req_end = datetime.strptime(end_date, "%Y-%m-%d").date()
    
    def check_date_coverage(csv_path: Path) -> bool:
        """CSV 파일이 요청 날짜 범위를 커버하는지 확인 (관대한 체크)

        캐싱 정책:
        1. 종료일: 7일(주말 포함 5영업일) 허용 - 휴장일/주말 대응
        2. 시작일: 데이터 시작 후면 OK - 과거 데이터 불필요
        3. 커버리지: 85% 이상이면 캐시 사용
        """
        try:
            with open(csv_path, 'r') as f:
                lines = f.readlines()
                if len(lines) < 2:
                    return False

                # 첫번째/마지막 줄에서 날짜 추출 (YYYYMMDD 형식)
                first_date_str = lines[0].split(',')[0].strip()
                last_date_str = lines[-1].split(',')[0].strip()

                first_date = datetime.strptime(first_date_str, "%Y%m%d").date()
                last_date = datetime.strptime(last_date_str, "%Y%m%d").date()

                # 관대한 날짜 체크
                tolerance_days = 7  # 주말 포함 약 5 영업일
                coverage_threshold = 0.85  # 85% 이상 커버 시 캐시 사용

                # 1. 종료일 체크: tolerance_days 허용
                if req_end > last_date + timedelta(days=tolerance_days):
                    logger.info(f"[Data] 종료일 초과: 요청={req_end}, 데이터={last_date} (허용={tolerance_days}일)")
                    return False

                # 2. 시작일 체크: 데이터 시작 후면 OK (너무 이전 데이터 요청 시만 실패)
                # 요청 시작일이 데이터보다 30일 이상 앞서면 재다운로드
                if req_start < first_date - timedelta(days=30):
                    logger.info(f"[Data] 시작일 부족: 요청={req_start}, 데이터 시작={first_date}")
                    return False

                # 3. 커버리지 체크
                req_days = (req_end - req_start).days
                if req_days <= 0:
                    return True  # 당일 요청

                # 실제 커버 가능한 범위 계산
                effective_start = max(req_start, first_date)
                effective_end = min(req_end, last_date)
                covered_days = (effective_end - effective_start).days

                coverage = covered_days / req_days if req_days > 0 else 1.0

                if coverage < coverage_threshold:
                    logger.info(f"[Data] 커버리지 부족: {coverage:.1%} < {coverage_threshold:.0%}")
                    return False

                logger.debug(f"[Data] 캐시 사용: {csv_path.name} (커버리지={coverage:.1%})")
                return True

        except Exception as e:
            logger.warning(f"[Data] 날짜 체크 실패: {e}")
            return False
    
    # 이미 있는 파일 확인 - 날짜 범위도 체크
    for symbol in symbols:
        csv_path = output_dir / f"{symbol.lower()}.csv"
        if csv_path.exists() and csv_path.stat().st_size > 100:
            if check_date_coverage(csv_path):
                result["skipped"].append(symbol)
                continue
            else:
                # 날짜 범위 불일치 - 파일 삭제 후 재다운로드
                logger.info(f"[Data] {symbol} 날짜 범위 불일치로 재다운로드")
                csv_path.unlink()
    
    symbols_to_download = [s for s in symbols if s not in result["skipped"]]
    
    if not symbols_to_download:
        logger.info("[Data] 모든 종목 데이터 캐시 사용")
        return result
    
    # KIS 인증
    try:
        auth = KISAuth.from_env()
        provider = KISDataProvider(auth)
    except Exception as e:
        logger.warning(f"[Data] KIS 인증 실패: {e} - 기존 캐시만 사용")
        for s in symbols_to_download:
            result["errors"].append({"symbol": s, "error": str(e)})
        return result
    
    # 데이터 다운로드
    for symbol in symbols_to_download:
        try:
            logger.info(f"[Data] 다운로드 중: {symbol}")
            bars = provider.get_history(symbol, req_start, req_end)
            
            if bars:
                # Lean CSV 변환
                DataConverter.bars_to_lean_csv(bars, symbol, output_dir)
                result["downloaded"].append(symbol)
                logger.info(f"[Data] 완료: {symbol} ({len(bars)} bars)")
            else:
                result["errors"].append({"symbol": symbol, "error": "데이터 없음"})
                
        except Exception as e:
            logger.error(f"[Data] {symbol} 다운로드 실패: {e}")
            result["errors"].append({"symbol": symbol, "error": str(e)})
    
    return result


async def prepare_benchmark_data(
    start_date: str,
    end_date: str,
    workspace: Path,
    index_code: str = "0001",  # KOSPI
) -> bool:
    """KOSPI 벤치마크 데이터 준비

    Args:
        start_date: 시작일 (YYYY-MM-DD)
        end_date: 종료일 (YYYY-MM-DD)
        workspace: Lean 워크스페이스 경로
        index_code: 지수코드 (0001=KOSPI, 1001=KOSDAQ)

    Returns:
        성공 여부
    """
    from kis_backtest.providers.kis.auth import KISAuth
    from kis_backtest.providers.kis.data import KISDataProvider

    # 지수 코드 → 파일명 매핑
    index_names = {"0001": "kospi", "1001": "kosdaq"}
    index_name = index_names.get(index_code, index_code)

    output_dir = workspace / "data" / "index" / "krx" / "daily"
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / f"{index_name}.csv"

    # 요청 날짜 파싱
    req_start = datetime.strptime(start_date, "%Y-%m-%d").date()
    req_end = datetime.strptime(end_date, "%Y-%m-%d").date()

    # 캐시 확인 (시작일 커버리지 필수)
    if csv_path.exists() and csv_path.stat().st_size > 100:
        try:
            with open(csv_path, 'r') as f:
                lines = f.readlines()
                if len(lines) >= 2:
                    first_date_str = lines[0].split(',')[0].strip()
                    last_date_str = lines[-1].split(',')[0].strip()
                    first_date = datetime.strptime(first_date_str, "%Y%m%d").date()
                    last_date = datetime.strptime(last_date_str, "%Y%m%d").date()

                    # 시작일 근처 데이터 필수 (7일 이내)
                    start_tolerance = timedelta(days=7)
                    end_tolerance = timedelta(days=7)

                    # 시작일과 종료일 모두 커버해야 캐시 사용
                    if first_date <= req_start + start_tolerance and last_date >= req_end - end_tolerance:
                        req_days = (req_end - req_start).days
                        if req_days > 0:
                            effective_start = max(req_start, first_date)
                            effective_end = min(req_end, last_date)
                            covered_days = (effective_end - effective_start).days
                            if covered_days / req_days >= 0.85:
                                logger.info(f"[Benchmark] 캐시 사용: {csv_path} (범위: {first_date} ~ {last_date})")
                                return True
                    else:
                        logger.info(f"[Benchmark] 캐시 범위 불일치 - 요청: {req_start}~{req_end}, 캐시: {first_date}~{last_date}")
                        # 낡은 캐시 삭제 — 다운로드 실패 시 절반짜리 데이터가 남지 않도록
                        csv_path.unlink(missing_ok=True)
        except Exception as e:
            logger.warning(f"[Benchmark] 캐시 체크 실패: {e}")
            csv_path.unlink(missing_ok=True)  # 손상된 캐시 제거

    # KIS API 다운로드
    try:
        auth = KISAuth.from_env()
        provider = KISDataProvider(auth)

        logger.info(f"[Benchmark] 다운로드 중: {index_name} ({index_code})")
        bars = provider.get_index_history(index_code, req_start, req_end)

        if bars:
            with open(csv_path, "w") as f:
                for bar in bars:
                    f.write(bar.to_lean_csv_line() + "\n")
            logger.info(f"[Benchmark] 저장 완료: {len(bars)}건")
            return True
        else:
            logger.warning(f"[Benchmark] 데이터 없음: {index_name}")
            return False

    except Exception as e:
        logger.error(f"[Benchmark] 다운로드 실패: {e}")
        return False


@router.post(
    "/run",
    response_model=BacktestResponse,
    summary="백테스트 실행",
    description="전략을 백테스트합니다 (Lean Docker). param_overrides로 파라미터 변경 가능.",
)
async def run_backtest(request: BacktestRequest) -> BacktestResponse:
    """백테스트 실행

    param_overrides 예시:
        {"period": 21, "oversold": 25}
    """

    # 전략 빌드 (param_overrides 적용)
    try:
        if request.param_overrides:
            definition = StrategyRegistry.build_with_params(
                request.strategy_id,
                **request.param_overrides,
            )
        else:
            definition = StrategyRegistry.build(request.strategy_id)
    except KeyError:
        raise HTTPException(
            status_code=404,
            detail=f"Strategy not found: {request.strategy_id}"
        )
    
    # 날짜 검증
    start_date = request.start_date
    end_date = request.end_date
    
    if isinstance(start_date, date):
        start_date = start_date.isoformat()
    if isinstance(end_date, date):
        end_date = end_date.isoformat()
    
    # 워크스페이스 경로
    manager = LeanProjectManager()
    workspace = manager.workspace
    
    # 시장 데이터 준비 (KIS API → Lean CSV)
    try:
        data_result = await prepare_market_data(
            symbols=request.symbols,
            start_date=start_date,
            end_date=end_date,
            workspace=workspace,
        )
        logger.info(f"[Data] 결과: {data_result}")
        
        # 데이터 없으면 에러
        if data_result["errors"] and not data_result["downloaded"] and not data_result["skipped"]:
            error_msg = data_result["errors"][0]["error"] if data_result["errors"] else "데이터 다운로드 실패"
            raise HTTPException(status_code=400, detail=f"데이터 준비 실패: {error_msg}")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"데이터 준비 실패: {e}")

    # 벤치마크 데이터 준비 (KOSPI)
    try:
        await prepare_benchmark_data(
            start_date=start_date,
            end_date=end_date,
            workspace=workspace,
        )
    except Exception as e:
        logger.warning(f"[Benchmark] 준비 실패 (무시): {e}")

    # Lean 코드 생성
    try:
        # 거래 비용 설정
        config = CodeGenConfig(
            commission_rate=request.commission_rate or 0.00015,
            tax_rate=request.tax_rate or 0.002,
            slippage=request.slippage or 0.0,
            initial_capital=request.initial_capital,
        )
        generator = LeanCodeGenerator(definition, config=config)
        code = generator.generate(
            symbols=request.symbols,
            start_date=start_date,
            end_date=end_date,
            initial_capital=request.initial_capital,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Code generation failed: {e}")

    # Docker 환경 확인
    if not LeanExecutor.check_docker():
        raise HTTPException(
            status_code=503,
            detail="Docker가 실행되지 않습니다. Docker Desktop을 시작해주세요."
        )

    if not LeanExecutor.check_image():
        raise HTTPException(
            status_code=503,
            detail="Lean 이미지가 없습니다. 'docker pull quantconnect/lean:latest' 실행 후 재시도해주세요."
        )

    # 프로젝트 생성 및 백테스트 실행
    try:
        project = LeanProjectManager.create_project(
            run_id=f"bt_{definition.id}",
            symbols=request.symbols,
            start_date=start_date,
            end_date=end_date,
            initial_capital=request.initial_capital,
            strategy_id=definition.id,
            strategy_name=definition.name,
        )
        # 코드 저장
        project.main_py.write_text(code)

        lean_run = LeanExecutor.run(project)

        if lean_run.success:
            result_data = _lean_run_to_api_response(
                lean_run, definition.name, request.symbols,
                start_date, end_date, request.initial_capital,
                workspace=workspace,
            )
            return BacktestResponse(
                success=True,
                data=result_data,
                message="백테스트 완료",
            )
        else:
            # 에러 메시지 분류
            error = lean_run.error or "Unknown error"
            error_detail = _classify_lean_error(error, lean_run.output)
            raise HTTPException(status_code=500, detail=error_detail)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"백테스트 실행 오류: {e}")



class CustomBacktestRequest(BaseModel):
    """커스텀 백테스트 요청"""
    yaml_content: str
    symbols: List[str]
    start_date: str
    end_date: str
    initial_capital: float = 100_000_000
    param_overrides: Optional[Dict[str, Any]] = None  # $param_name 오버라이드
    commission_rate: Optional[float] = 0.00015  # 수수료율 (기본 0.015%)
    tax_rate: Optional[float] = 0.002  # 거래세율 (기본 0.2%)
    slippage: Optional[float] = 0.0  # 슬리피지 (기본 0%)


@router.post(
    "/run-custom",
    response_model=BacktestResponse,
    summary="커스텀 전략 백테스트",
    description="YAML 정의로 커스텀 전략을 백테스트합니다. param_overrides로 $param_name 값 변경 가능.",
)
async def run_custom_backtest(request: CustomBacktestRequest) -> BacktestResponse:
    """커스텀 전략 백테스트 - 스키마 기반

    param_overrides로 YAML의 $param_name 값을 오버라이드할 수 있습니다.
    예: {"period": 21, "oversold": 25}
    """
    from kis_backtest.file.loader import StrategyFileLoader

    # YAML 파싱 → StrategySchema (타입 안전, param_overrides 적용)
    try:
        schema = StrategyFileLoader.load_schema_with_params(
            request.yaml_content,
            param_overrides=request.param_overrides,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid YAML: {e}")
    
    # 워크스페이스 경로
    manager = LeanProjectManager()
    workspace = manager.workspace
    
    # 시장 데이터 준비 (KIS API → Lean CSV)
    try:
        data_result = await prepare_market_data(
            symbols=request.symbols,
            start_date=request.start_date,
            end_date=request.end_date,
            workspace=workspace,
        )
        logger.info(f"[Data] 결과: {data_result}")
        
        # 데이터 없으면 에러
        if data_result["errors"] and not data_result["downloaded"] and not data_result["skipped"]:
            error_msg = data_result["errors"][0]["error"] if data_result["errors"] else "데이터 다운로드 실패"
            raise HTTPException(status_code=400, detail=f"데이터 준비 실패: {error_msg}")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"데이터 준비 실패: {e}")

    # 벤치마크 데이터 준비 (KOSPI)
    try:
        await prepare_benchmark_data(
            start_date=request.start_date,
            end_date=request.end_date,
            workspace=workspace,
        )
    except Exception as e:
        logger.warning(f"[Benchmark] 준비 실패 (무시): {e}")

    # Lean 코드 생성 (스키마 기반)
    try:
        if schema is None:
            raise HTTPException(status_code=400, detail="전략 스키마 생성 실패")
        
        # 거래 비용 설정
        config = CodeGenConfig(
            commission_rate=request.commission_rate or 0.00015,
            tax_rate=request.tax_rate or 0.002,
            slippage=request.slippage or 0.0,
            initial_capital=request.initial_capital,
        )
        generator = LeanCodeGenerator(schema, config=config)
        code = generator.generate(
            symbols=request.symbols,
            start_date=request.start_date,
            end_date=request.end_date,
            initial_capital=request.initial_capital,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Code generation failed: {e}")
    
    # Docker 환경 확인
    if not LeanExecutor.check_docker():
        raise HTTPException(
            status_code=503,
            detail="Docker가 실행되지 않습니다. Docker Desktop을 시작해주세요."
        )

    if not LeanExecutor.check_image():
        raise HTTPException(
            status_code=503,
            detail="Lean 이미지가 없습니다. 'docker pull quantconnect/lean:latest' 실행 후 재시도해주세요."
        )

    # 프로젝트 생성 및 백테스트 실행
    try:
        project = LeanProjectManager.create_project(
            run_id=f"bt_custom_{schema.id}",
            symbols=request.symbols,
            start_date=request.start_date,
            end_date=request.end_date,
            initial_capital=request.initial_capital,
            strategy_id=schema.id,
            strategy_name=schema.name,
        )
        # 코드 저장
        project.main_py.write_text(code)

        lean_run = LeanExecutor.run(project)

        if lean_run.success:
            result_data = _lean_run_to_api_response(
                lean_run, schema.name, request.symbols,
                request.start_date, request.end_date, request.initial_capital,
                workspace=workspace,
            )
            return BacktestResponse(
                success=True,
                data=result_data,
                message="백테스트 완료",
            )
        else:
            # 에러 메시지 분류
            error = lean_run.error or "Unknown error"
            error_detail = _classify_lean_error(error, lean_run.output)
            raise HTTPException(status_code=500, detail=error_detail)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"백테스트 실행 오류: {e}")
