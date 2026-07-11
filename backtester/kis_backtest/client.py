"""KIS Backtest 메인 클라이언트

Lean CLI를 래핑하고 한국투자증권 API를 통합한 클라이언트.
"""

import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pandas as pd

from .models import BacktestResult, Bar, Resolution
from .models.result import OptimizationResult
from .providers import DataProvider, BrokerageProvider
from .report import KISReportGenerator, BaseTheme
from .exceptions import ConfigurationError, AlgorithmError, DockerError

# Lean 모듈
from .lean.project_manager import LeanProject, LeanProjectManager
from .lean.executor import LeanExecutor, LeanRun
from .lean.data_converter import DataConverter
from .lean.result_formatter import parse_lean_value

# 전략 시스템
from .strategies.registry import StrategyRegistry, STRATEGY_REGISTRY
from .strategies.generator import StrategyGenerator, generate_strategy
from .codegen.generator import LeanCodeGenerator

logger = logging.getLogger(__name__)


class LeanClient:
    """Lean CLI 래핑 클라이언트
    
    Lean CLI의 Container를 내부적으로 사용하되,
    외부에는 간결한 API를 노출.
    한국투자증권 API를 데이터/주문 제공자로 사용 가능.
    """
    
    def __init__(
        self,
        workspace_dir: Optional[Path] = None,
        engine_image: str = "quantconnect/lean:latest",
        data_provider: Optional[DataProvider] = None,
        brokerage_provider: Optional[BrokerageProvider] = None,
        report_theme: Optional[BaseTheme] = None
    ):
        """
        Args:
            workspace_dir: Lean 워크스페이스 디렉토리.
                          None이면 현재 디렉토리 사용.
            engine_image: LEAN 엔진 Docker 이미지.
            data_provider: 데이터 제공자 (한투 등).
            brokerage_provider: 브로커리지 제공자 (한투 등).
            report_theme: 리포트 테마.
                         None이면 KISTheme 사용.
        """
        self._workspace_dir = workspace_dir or Path.cwd()
        self._engine_image = engine_image
        
        # Provider 설정
        self._data_provider = data_provider
        self._brokerage_provider = brokerage_provider
        
        # 리포트 생성기
        self._report_generator = KISReportGenerator(theme=report_theme)
        
    @property
    def data_provider(self) -> Optional[DataProvider]:
        """데이터 제공자"""
        return self._data_provider
    
    @property
    def brokerage_provider(self) -> Optional[BrokerageProvider]:
        """브로커리지 제공자"""
        return self._brokerage_provider
    
    def backtest(
        self,
        project: Union[str, Path],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        initial_cash: float = 100_000_000,
        output_dir: Optional[Path] = None
    ) -> BacktestResult:
        """백테스트 실행 (기존 프로젝트)
        
        Args:
            project: 프로젝트 디렉토리 경로.
            start_date: 시작일 (YYYY-MM-DD).
            end_date: 종료일 (YYYY-MM-DD).
            parameters: 알고리즘 파라미터 오버라이드.
            initial_cash: 초기 현금 (KRW).
            output_dir: 결과 저장 디렉토리.
        
        Returns:
            BacktestResult: 백테스트 결과 객체.
        
        Raises:
            AlgorithmError: 알고리즘 실행 오류.
            ConfigurationError: 설정 오류.
        """
        project_path = Path(project)
        
        if not project_path.exists():
            raise ConfigurationError(f"프로젝트를 찾을 수 없습니다: {project_path}")
        
        logger.info(f"백테스트 시작: {project_path}")
        
        # Docker 확인
        if not LeanExecutor.check_docker():
            raise DockerError("Docker가 실행되지 않았습니다. Docker Desktop을 시작해주세요.")
        
        # 기존 프로젝트에서 LeanProject 생성
        run_id = project_path.name
        lean_project = LeanProjectManager.get_project(run_id)
        
        if lean_project is None:
            # 직접 LeanProject 생성
            lean_project = LeanProject(
                run_id=run_id,
                project_dir=project_path,
                data_dir=project_path.parent.parent / "data" / "equity" / "krx" / "daily",
                symbols=[],
                start_date=start_date or "",
                end_date=end_date or "",
                initial_capital=initial_cash,
            )
        
        # Lean Docker 실행
        try:
            lean_run = LeanExecutor.run(lean_project, stream_logs=False)
        except RuntimeError as e:
            raise AlgorithmError(str(e))
        
        # 결과 변환
        result = self._lean_run_to_result(lean_run, initial_cash)
        
        logger.info(f"백테스트 완료: {project_path}")
        return result
    
    def backtest_strategy(
        self,
        strategy_id: str,
        symbols: List[str],
        start_date: str,
        end_date: str,
        params: Optional[Dict[str, Any]] = None,
        initial_cash: float = 100_000_000,
        market_type: str = "krx",
        risk_management: Optional[Dict[str, Any]] = None,
    ) -> BacktestResult:
        """전략 ID로 백테스트 실행
        
        Args:
            strategy_id: 전략 ID (sma_crossover, rsi, macd 등)
            symbols: 종목코드 리스트
            start_date: 시작일 (YYYY-MM-DD)
            end_date: 종료일 (YYYY-MM-DD)
            params: 전략 파라미터 오버라이드
            initial_cash: 초기 자본금
            market_type: 시장 타입 ("krx" 또는 "us")
            risk_management: 리스크 관리 설정
        
        Returns:
            BacktestResult: 백테스트 결과 객체
        
        Example:
            result = client.backtest_strategy(
                strategy_id="sma_crossover",
                symbols=["005930"],
                start_date="2025-01-01",
                end_date="2025-12-31",
                params={"short_window": 10, "long_window": 30},
            )
        """
        # 전략 검증
        if StrategyRegistry.get(strategy_id) is None:
            raise ConfigurationError(f"알 수 없는 전략: {strategy_id}")
        
        # Docker 확인
        if not LeanExecutor.check_docker():
            raise DockerError("Docker가 실행되지 않았습니다.")
        
        # 1. 데이터 수집
        logger.info(f"[Backtest] 데이터 수집 중: {symbols}")
        data_dict = self._fetch_data(symbols, start_date, end_date, market_type)
        
        # 2. 전략 코드 생성
        logger.info(f"[Backtest] 전략 코드 생성: {strategy_id}")
        try:
            strategy_code = generate_strategy(
                strategy_id=strategy_id,
                symbols=symbols,
                start_date=start_date,
                end_date=end_date,
                initial_capital=initial_cash,
                market_type=market_type,
                params=params,
            )
        except ValueError as e:
            raise AlgorithmError(f"전략 코드 생성 오류: {e}")
        
        # 3. 프로젝트 생성
        run_id = f"bt_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:6]}"
        currency = "KRW" if market_type == "krx" else "USD"
        
        project = LeanProjectManager.create_project(
            run_id=run_id,
            symbols=symbols,
            start_date=start_date,
            end_date=end_date,
            initial_capital=initial_cash,
            strategy_type=strategy_id,
            strategy_params=params or {},
            market_type=market_type,
            currency=currency,
        )
        
        # 4. 전략 코드 저장
        project.main_py.write_text(strategy_code)
        
        # 5. 데이터 변환 및 저장
        logger.info(f"[Backtest] 데이터 변환 중")
        DataConverter.export(data_dict, str(project.data_dir), market_type)
        
        # 6. Lean Docker 실행
        logger.info(f"[Backtest] Lean 엔진 실행 중")
        try:
            lean_run = LeanExecutor.run(project, stream_logs=False)
        except RuntimeError as e:
            raise AlgorithmError(str(e))
        
        # 7. 결과 변환
        result = self._lean_run_to_result(lean_run, initial_cash)
        
        # 결과에 추가 메타데이터 저장
        result.strategy_id = strategy_id
        result.symbols = symbols
        result.run_id = run_id
        
        # 8. KOSPI 벤치마크 수집 (KRX 시장만)
        if market_type == "krx":
            result.benchmark_curve = self._fetch_benchmark(start_date, end_date)
        
        logger.info(f"[Backtest] 완료: {result.total_return_pct:.2%} 수익률")
        return result
    
    def backtest_custom(
        self,
        algorithm_code: str,
        symbols: List[str],
        start_date: str,
        end_date: str,
        data: Optional[Dict[str, pd.DataFrame]] = None,
        initial_cash: float = 100_000_000,
        market_type: str = "krx",
    ) -> BacktestResult:
        """커스텀 알고리즘 코드로 백테스트 실행
        
        Args:
            algorithm_code: QCAlgorithm Python 코드
            symbols: 종목코드 리스트
            start_date: 시작일
            end_date: 종료일
            data: 데이터 딕셔너리 (없으면 data_provider에서 가져옴)
            initial_cash: 초기 자본금
            market_type: 시장 타입
        
        Returns:
            BacktestResult: 백테스트 결과 객체
        """
        # Docker 확인
        if not LeanExecutor.check_docker():
            raise DockerError("Docker가 실행되지 않았습니다.")
        
        # 1. 데이터 준비
        if data is None:
            logger.info(f"[Backtest] 데이터 수집 중: {symbols}")
            data = self._fetch_data(symbols, start_date, end_date, market_type)
        
        # 2. 프로젝트 생성
        run_id = f"custom_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:6]}"
        currency = "KRW" if market_type == "krx" else "USD"
        
        project = LeanProjectManager.create_project(
            run_id=run_id,
            symbols=symbols,
            start_date=start_date,
            end_date=end_date,
            initial_capital=initial_cash,
            strategy_type="custom",
            market_type=market_type,
            currency=currency,
        )
        
        # 3. 알고리즘 코드 저장
        project.main_py.write_text(algorithm_code)
        
        # 4. 데이터 변환
        DataConverter.export(data, str(project.data_dir), market_type)
        
        # 5. Lean Docker 실행
        logger.info(f"[Backtest] Lean 엔진 실행 중")
        try:
            lean_run = LeanExecutor.run(project, stream_logs=False)
        except RuntimeError as e:
            raise AlgorithmError(str(e))
        
        # 6. 결과 변환
        result = self._lean_run_to_result(lean_run, initial_cash)
        result.run_id = run_id
        result.symbols = symbols
        
        # 7. KOSPI 벤치마크 수집 (KRX 시장만)
        if market_type == "krx":
            result.benchmark_curve = self._fetch_benchmark(start_date, end_date)
        
        return result
    
    def _fetch_data(
        self,
        symbols: List[str],
        start_date: str,
        end_date: str,
        market_type: str = "krx",
    ) -> Dict[str, pd.DataFrame]:
        """데이터 수집 (캐시 우선, API 호출 간격 적용)"""
        import time
        from pathlib import Path

        if self._data_provider is None:
            raise ConfigurationError("data_provider가 설정되지 않았습니다.")

        # 문자열 → date 변환
        from datetime import datetime, timedelta
        if isinstance(start_date, str):
            start_date_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
        else:
            start_date_dt = start_date
        if isinstance(end_date, str):
            end_date_dt = datetime.strptime(end_date, "%Y-%m-%d").date()
        else:
            end_date_dt = end_date

        # 캐시 디렉토리 (workspace)
        workspace = Path(".lean-workspace")
        cache_dir = workspace / "data" / "equity" / market_type / "daily"

        data_dict = {}
        api_call_count = 0

        def check_cache_coverage(csv_path: Path) -> bool:
            """캐시 파일이 요청 날짜 범위를 커버하는지 확인"""
            try:
                with open(csv_path, 'r') as f:
                    lines = f.readlines()
                if len(lines) < 2:
                    return False

                # 첫/마지막 줄에서 날짜 파싱 (YYYYMMDD 형식)
                first_date = datetime.strptime(lines[0].split(",")[0], "%Y%m%d").date()
                last_date = datetime.strptime(lines[-1].split(",")[0], "%Y%m%d").date()

                # 7일 허용 범위로 체크
                tolerance = timedelta(days=7)
                if first_date <= start_date_dt + tolerance and last_date >= end_date_dt - tolerance:
                    return True
                return False
            except Exception:
                return False

        def load_from_cache(csv_path: Path) -> pd.DataFrame:
            """캐시 파일에서 DataFrame 로드"""
            rows = []
            with open(csv_path, 'r') as f:
                for line in f:
                    parts = line.strip().split(",")
                    if len(parts) >= 6:
                        rows.append({
                            "date": datetime.strptime(parts[0], "%Y%m%d"),
                            "open": float(parts[1]),
                            "high": float(parts[2]),
                            "low": float(parts[3]),
                            "close": float(parts[4]),
                            "volume": int(parts[5]),
                        })
            return pd.DataFrame(rows)

        for symbol in symbols:
            # 1. 캐시 확인
            cache_file = cache_dir / f"{symbol.lower()}.csv"
            if cache_file.exists() and check_cache_coverage(cache_file):
                try:
                    df = load_from_cache(cache_file)
                    if not df.empty:
                        data_dict[symbol] = df
                        logger.info(f"  - {symbol}: 캐시 사용 ({len(df)}건)")
                        continue
                except Exception as e:
                    logger.warning(f"  - {symbol} 캐시 로드 실패: {e}")

            # 2. API 호출 (간격 적용)
            if api_call_count > 0:
                time.sleep(0.5)  # API 호출 간격 0.5초

            try:
                bars = self._data_provider.get_history(
                    symbol, start_date_dt, end_date_dt, Resolution.DAILY
                )
                api_call_count += 1

                # Bar 리스트 → DataFrame
                df = pd.DataFrame([
                    {
                        "date": bar.time,
                        "open": bar.open,
                        "high": bar.high,
                        "low": bar.low,
                        "close": bar.close,
                        "volume": bar.volume,
                    }
                    for bar in bars
                ])

                if not df.empty:
                    data_dict[symbol] = df
                    logger.info(f"  - {symbol}: API 조회 ({len(df)}건)")

            except Exception as e:
                logger.warning(f"  - {symbol} 데이터 수집 실패: {e}")

        if not data_dict:
            raise ConfigurationError("데이터를 수집할 수 없습니다.")

        return data_dict
    
    def _lean_run_to_result(
        self,
        lean_run: LeanRun,
        initial_cash: float,
    ) -> BacktestResult:
        """LeanRun → BacktestResult 변환

        Note: Lean 출력의 퍼센트 값은 이미 % 형식 (예: 16.985는 16.985%)
              Python의 % 포매터가 올바르게 동작하도록 0.0~1.0 범위로 정규화
        """
        stats = lean_run.get_statistics()

        # Lean 퍼센트 값 파싱 (예: "16.985%" → 16.985)
        total_return_pct_raw = parse_lean_value(stats.get("Net Profit", 0))  # 16.985
        cagr_raw = parse_lean_value(stats.get("Compounding Annual Return", 0))  # 예: 25.5
        max_drawdown_raw = parse_lean_value(stats.get("Drawdown", 0))  # 예: 15.9
        win_rate_raw = parse_lean_value(stats.get("Win Rate", 0))  # 예: 50

        # 정규화: Lean % 값 → 0.0~1.0 (Python % 포매터 호환)
        total_return_pct = total_return_pct_raw / 100  # 0.16985
        cagr = cagr_raw / 100  # 0.255
        max_drawdown = abs(max_drawdown_raw) / 100  # 0.159
        win_rate = win_rate_raw / 100  # 0.50

        # 총 수익 금액 (KRW)
        total_return = initial_cash * total_return_pct

        # equity_curve: Dict → pd.Series 변환
        equity_data = lean_run.get_equity_curve()
        equity_curve = None
        if equity_data:
            try:
                # Dict의 key는 timestamp (문자열), value는 자산 값
                timestamps = [int(ts) for ts in equity_data.keys()]
                values = list(equity_data.values())

                if timestamps and values:
                    from datetime import datetime
                    dates = pd.to_datetime([datetime.fromtimestamp(ts) for ts in timestamps])
                    equity_curve = pd.Series(values, index=dates, name="equity")
            except Exception as e:
                logger.warning(f"equity_curve 변환 실패: {e}")
                equity_curve = None

        return BacktestResult(
            success=lean_run.success,
            output_dir=lean_run.output_dir,
            start_date=lean_run.project.start_date,
            end_date=lean_run.project.end_date,
            total_return=total_return,
            total_return_pct=total_return_pct,  # 정규화된 값 (0.16985)
            cagr=cagr,  # 정규화된 값
            sharpe_ratio=parse_lean_value(stats.get("Sharpe Ratio", 0)),
            sortino_ratio=parse_lean_value(stats.get("Sortino Ratio", 0)),
            max_drawdown=max_drawdown,  # 정규화된 값
            total_trades=int(parse_lean_value(stats.get("Total Orders", 0))),
            win_rate=win_rate,  # 정규화된 값
            profit_factor=parse_lean_value(stats.get("Profit-Loss Ratio", 0)),
            average_win=parse_lean_value(stats.get("Average Win", 0)),
            average_loss=parse_lean_value(stats.get("Average Loss", 0)),
            equity_curve=equity_curve,  # pd.Series (또는 None)
            trades=lean_run.get_trades(),
            raw_statistics=stats,
            duration_seconds=lean_run.duration_seconds,
        )

    def _fetch_benchmark(
        self,
        start_date: str,
        end_date: str,
        index_code: str = "0001",
    ) -> Optional[Dict[str, float]]:
        """KOSPI 벤치마크 수익률 곡선 수집

        Returns:
            날짜별 시작 대비 수익률 % (프론트엔드 호환).
            예: {"2025-01-02": 0.0, "2025-01-03": 1.5, ...}
            수집 실패 시 None.
        """
        if self._data_provider is None:
            return None

        try:
            from datetime import datetime as dt
            start = dt.strptime(start_date, "%Y-%m-%d").date() if isinstance(start_date, str) else start_date
            end = dt.strptime(end_date, "%Y-%m-%d").date() if isinstance(end_date, str) else end_date

            bars = self._data_provider.get_index_history(index_code, start, end)
            if not bars:
                return None

            # 시작일 종가 기준 수익률 % 계산
            base_price = bars[0].close
            if base_price <= 0:
                return None

            curve: Dict[str, float] = {}
            for bar in bars:
                pct = ((bar.close - base_price) / base_price) * 100
                curve[bar.time.strftime("%Y-%m-%d")] = round(pct, 2)

            logger.info(f"[Benchmark] KOSPI 수집 완료 ({len(curve)}일)")
            return curve

        except Exception as e:
            logger.warning(f"[Benchmark] KOSPI 수집 실패: {e}")
            return None
    
    def optimize(
        self,
        strategy_id: str,
        symbols: List[str],
        start_date: str,
        end_date: str,
        parameters: List[tuple],
        target: str = "sharpe_ratio",
        target_direction: str = "max",
        strategy: str = "grid",
        max_samples: int = 100,
        max_workers: int = 4,
        initial_cash: float = 100_000_000,
        market_type: str = "krx",
        on_progress: Optional[callable] = None,
        seed: Optional[int] = None,
    ) -> OptimizationResult:
        """파라미터 최적화
        
        Grid Search 또는 Random Search를 통해 최적의 전략 파라미터를 탐색.
        
        Args:
            strategy_id: 전략 ID (sma_crossover, rsi, macd 등)
            symbols: 종목코드 리스트
            start_date: 시작일 (YYYY-MM-DD)
            end_date: 종료일 (YYYY-MM-DD)
            parameters: 파라미터 정의 리스트
                       각 튜플: (name, min_value, max_value, step)
            target: 목표 지표 (sharpe_ratio, total_return, max_drawdown 등)
            target_direction: "max" 또는 "min"
            strategy: 탐색 전략 ("grid" 또는 "random")
            max_samples: random search 시 최대 샘플 수
            max_workers: 동시 실행 수 (현재 순차 실행)
            initial_cash: 초기 자본금
            market_type: 시장 타입 ("krx" 또는 "us")
            on_progress: 진행 콜백 (completed, total, run) -> None
            seed: 랜덤 시드 (재현성용)
        
        Returns:
            OptimizationResult: 최적화 결과
        
        Example:
            result = client.optimize(
                strategy_id="sma_crossover",
                symbols=["005930"],
                start_date="2025-01-01",
                end_date="2025-12-31",
                parameters=[
                    ("short_window", 5, 20, 5),   # 5, 10, 15, 20
                    ("long_window", 20, 60, 10),  # 20, 30, 40, 50, 60
                ],
                target="sharpe_ratio",
                strategy="grid",
            )
            
            print(f"최적 파라미터: {result.best_parameters}")
            print(f"샤프 비율: {result.best_sharpe:.2f}")
        """
        from .lean.optimizer import StrategyOptimizer
        
        # 전략 검증
        if StrategyRegistry.get(strategy_id) is None:
            raise ConfigurationError(f"알 수 없는 전략: {strategy_id}")
        
        # Docker 확인
        if not LeanExecutor.check_docker():
            raise DockerError("Docker가 실행되지 않았습니다.")
        
        # 최적화기 생성 및 실행
        optimizer = StrategyOptimizer(
            client=self,
            max_workers=max_workers,
        )
        
        return optimizer.optimize(
            strategy_id=strategy_id,
            symbols=symbols,
            start_date=start_date,
            end_date=end_date,
            parameters=parameters,
            target=target,
            target_direction=target_direction,
            strategy=strategy,
            max_samples=max_samples,
            initial_cash=initial_cash,
            market_type=market_type,
            on_progress=on_progress,
            seed=seed,
        )
    
    def backtest_rule(
        self,
        rule,  # StrategyRule
        symbols: List[str],
        start_date: str,
        end_date: str,
        initial_cash: float = 100_000_000,
        market_type: str = "krx",
    ) -> BacktestResult:
        """규칙 기반 백테스트
        
        RuleBuilder로 생성한 전략을 백테스트합니다.
        
        Args:
            rule: RuleBuilder.build()로 생성한 StrategyRule
            symbols: 종목코드 리스트
            start_date: 시작일 (YYYY-MM-DD)
            end_date: 종료일 (YYYY-MM-DD)
            initial_cash: 초기 자본금
            market_type: 시장 타입 ("krx" 또는 "us")
        
        Returns:
            BacktestResult: 백테스트 결과
        
        Example:
            from kis_backtest.strategies import RuleBuilder, SMA, RSI
            
            strategy = (
                RuleBuilder("골든크로스_RSI필터")
                .buy_when((SMA(5) > SMA(20)) & (RSI(14) < 70))
                .sell_when((SMA(5) < SMA(20)) | (RSI(14) > 80))
                .stop_loss(5.0)
                .take_profit(10.0)
                .build()
            )
            
            result = client.backtest_rule(
                rule=strategy,
                symbols=["005930"],
                start_date="2025-01-01",
                end_date="2025-12-31",
            )
            
            print(f"수익률: {result.total_return_pct:.2%}")
        """
        from .dsl.builder import StrategyRule
        from .core.converters import from_definition
        from .codegen.generator import LeanCodeGenerator, CodeGenConfig

        if not isinstance(rule, StrategyRule):
            raise ConfigurationError("rule은 RuleBuilder.build()로 생성한 StrategyRule이어야 합니다.")

        # Docker 확인
        if not LeanExecutor.check_docker():
            raise DockerError("Docker가 실행되지 않았습니다.")

        logger.info(f"[Backtest] RuleBuilder 전략 실행: {rule.name}")

        # 1. 데이터 수집
        logger.info(f"[Backtest] 데이터 수집 중: {symbols}")
        data_dict = self._fetch_data(symbols, start_date, end_date, market_type)

        # 2. StrategyRule → StrategyDefinition → StrategySchema
        strategy_def = rule.to_strategy_definition()
        schema = from_definition(strategy_def)

        # 3. Lean 코드 직접 생성
        config = CodeGenConfig(
            market=market_type,
            initial_capital=initial_cash,
        )
        generator = LeanCodeGenerator(schema, config=config)
        try:
            strategy_code = generator.generate(
                symbols=symbols,
                start_date=start_date,
                end_date=end_date,
            )
        except ValueError as e:
            raise AlgorithmError(f"전략 코드 생성 오류: {e}")

        # 4. 프로젝트 생성
        run_id = f"bt_rule_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:6]}"
        currency = "KRW" if market_type == "krx" else "USD"

        project = LeanProjectManager.create_project(
            run_id=run_id,
            symbols=symbols,
            start_date=start_date,
            end_date=end_date,
            initial_capital=initial_cash,
            strategy_type=rule.name,
            strategy_params={},
            market_type=market_type,
            currency=currency,
        )

        # 5. 전략 코드 저장
        project.main_py.write_text(strategy_code)

        # 6. 데이터 변환 및 저장
        DataConverter.export(data_dict, str(project.data_dir), market_type)

        # 7. Lean Docker 실행
        try:
            lean_run = LeanExecutor.run(project, stream_logs=False)
        except RuntimeError as e:
            raise AlgorithmError(str(e))

        # 6. 결과 변환
        result = self._lean_run_to_result(lean_run, initial_cash)
        result.strategy_id = rule.name

        logger.info(f"[Backtest] 완료: {rule.name}")
        return result
    
    # ============================================================
    # 포트폴리오 분석 (P3)
    # ============================================================
    
    def analyze_portfolio(
        self,
        symbols: List[str],
        start_date: str,
        end_date: str,
        weights: Optional[Dict[str, float]] = None,
        risk_free_rate: float = 0.03,
    ):
        """포트폴리오 분석
        
        다중 자산 포트폴리오의 상관관계, 분산효과, 리스크 기여도 분석.
        
        Args:
            symbols: 종목코드 리스트
            start_date: 시작일 (YYYY-MM-DD)
            end_date: 종료일 (YYYY-MM-DD)
            weights: 비중 딕셔너리 (None이면 동일 비중)
            risk_free_rate: 무위험 이자율 (연율)
        
        Returns:
            PortfolioMetrics: 분석 결과
        
        Example:
            metrics = client.analyze_portfolio(
                symbols=["005930", "000660", "035420"],
                start_date="2024-01-01",
                end_date="2024-12-31",
                weights={"005930": 0.4, "000660": 0.3, "035420": 0.3},
            )
            
            print(f"분산 비율: {metrics.diversification_ratio:.2f}")
            print(f"상관관계:\n{metrics.correlation_matrix}")
        """
        from .portfolio import PortfolioAnalyzer, PortfolioMetrics
        
        if self._data_provider is None:
            raise ConfigurationError("data_provider가 필요합니다.")
        
        logger.info(f"[Portfolio] 분석 시작: {len(symbols)}개 종목")
        
        # 가격 데이터 수집
        prices_dict = {}
        for symbol in symbols:
            bars = self._data_provider.get_history(
                symbol=symbol,
                start=datetime.strptime(start_date, "%Y-%m-%d"),
                end=datetime.strptime(end_date, "%Y-%m-%d"),
                resolution=Resolution.DAILY,
            )
            if bars:
                prices_dict[symbol] = pd.Series(
                    {bar.time: bar.close for bar in bars}
                )
        
        if len(prices_dict) < 2:
            raise ConfigurationError("최소 2개 이상의 종목이 필요합니다.")

        # 누락된 종목 로그
        missing = set(symbols) - set(prices_dict.keys())
        if missing:
            logger.warning(f"[Portfolio] 데이터 누락 종목 (제외): {missing}")

        # DataFrame 생성
        prices_df = pd.DataFrame(prices_dict).dropna()

        # weights에서 실제 데이터가 있는 종목만 필터링 & 재정규화
        available_symbols = list(prices_df.columns)
        if weights is not None:
            weights = {s: w for s, w in weights.items() if s in available_symbols}
            total = sum(weights.values())
            if total > 0:
                weights = {s: w / total for s, w in weights.items()}

        # 분석 실행
        analyzer = PortfolioAnalyzer.from_prices(
            prices=prices_df,
            weights=weights,
            risk_free_rate=risk_free_rate,
        )
        
        metrics = analyzer.analyze()
        logger.info(f"[Portfolio] 분석 완료: 샤프={metrics.portfolio_sharpe:.2f}")
        
        return metrics
    
    def simulate_rebalance(
        self,
        symbols: List[str],
        start_date: str,
        end_date: str,
        weights: Dict[str, float],
        period: str = "monthly",
        initial_capital: float = 100_000_000,
        transaction_cost_rate: float = 0.001,
    ):
        """리밸런싱 시뮬레이션
        
        주기적 리밸런싱 vs Buy & Hold 비교.
        
        Args:
            symbols: 종목코드 리스트
            start_date: 시작일 (YYYY-MM-DD)
            end_date: 종료일 (YYYY-MM-DD)
            weights: 목표 비중 딕셔너리
            period: 리밸런싱 주기 ("daily", "weekly", "monthly", "quarterly", "yearly")
            initial_capital: 초기 자본금
            transaction_cost_rate: 거래 비용률 (편도)
        
        Returns:
            RebalanceResult: 시뮬레이션 결과
        
        Example:
            result = client.simulate_rebalance(
                symbols=["005930", "000660"],
                start_date="2024-01-01",
                end_date="2024-12-31",
                weights={"005930": 0.6, "000660": 0.4},
                period="monthly",
            )
            
            print(f"리밸런싱 효과: {result.rebalance_benefit:+.2%}")
        """
        from .portfolio import RebalanceSimulator, RebalanceResult
        
        if self._data_provider is None:
            raise ConfigurationError("data_provider가 필요합니다.")
        
        logger.info(f"[Rebalance] 시뮬레이션 시작: period={period}")
        
        # 가격 데이터 수집
        prices_dict = {}
        for symbol in symbols:
            bars = self._data_provider.get_history(
                symbol=symbol,
                start=datetime.strptime(start_date, "%Y-%m-%d"),
                end=datetime.strptime(end_date, "%Y-%m-%d"),
                resolution=Resolution.DAILY,
            )
            if bars:
                prices_dict[symbol] = pd.Series(
                    {bar.time: bar.close for bar in bars}
                )
        
        prices_df = pd.DataFrame(prices_dict).dropna()
        
        # 시뮬레이션 실행
        simulator = RebalanceSimulator(
            prices=prices_df,
            initial_weights=weights,
            initial_capital=initial_capital,
            transaction_cost_rate=transaction_cost_rate,
        )
        
        result = simulator.simulate(period=period)
        logger.info(f"[Rebalance] 완료: 효과={result.rebalance_benefit:+.2%}")
        
        return result
    
    def portfolio_report(
        self,
        metrics,  # PortfolioMetrics
        output_path: Union[str, Path],
        title: str = "포트폴리오 분석 리포트",
        frontier = None,  # Optional[pd.DataFrame]
        rebalance_result = None,  # Optional[RebalanceResult]
        symbol_names: Optional[Dict[str, str]] = None,
    ) -> Path:
        """포트폴리오 분석 리포트 생성
        
        Args:
            metrics: PortfolioMetrics 분석 결과
            output_path: 출력 파일 경로
            title: 리포트 제목
            frontier: 효율적 프론티어 DataFrame (옵션)
            rebalance_result: 리밸런싱 시뮬레이션 결과 (옵션)
            symbol_names: 종목코드 → 종목명 매핑 (옵션)
        
        Returns:
            Path: 생성된 HTML 리포트 경로
        
        Example:
            # 포트폴리오 분석
            metrics = client.analyze_portfolio(
                symbols=["005930", "000660"],
                start_date="2024-01-01",
                end_date="2024-12-31",
            )
            
            # 리포트 생성
            client.portfolio_report(
                metrics=metrics,
                output_path="portfolio_report.html",
                symbol_names={"005930": "삼성전자", "000660": "SK하이닉스"},
            )
        """
        from .report import PortfolioReportGenerator
        
        generator = PortfolioReportGenerator()
        
        return generator.generate(
            metrics=metrics,
            output_path=output_path,
            title=title,
            frontier=frontier,
            rebalance_result=rebalance_result,
            symbol_names=symbol_names,
        )
    
    def live(self) -> "LiveClient":
        """라이브 트레이딩 클라이언트 반환
        
        Returns:
            LiveClient: 라이브 트레이딩 클라이언트.
        
        Raises:
            ConfigurationError: brokerage_provider 미설정.
        """
        if self._brokerage_provider is None:
            raise ConfigurationError(
                "라이브 트레이딩을 위해 brokerage_provider를 설정해주세요."
            )
        
        return LiveClient(
            data_provider=self._data_provider,
            brokerage_provider=self._brokerage_provider
        )
    
    def report(
        self,
        result: BacktestResult,
        output_path: Union[str, Path],
        title: str = "백테스트 리포트",
        subtitle: Optional[str] = None,
        include_components: Optional[List[str]] = None,
    ) -> Path:
        """리포트 생성 (한투 스타일)
        
        Args:
            result: 백테스트 결과.
            output_path: 출력 파일 경로.
            title: 리포트 제목.
            subtitle: 부제목.
            include_components: 포함할 컴포넌트 목록.
        
        Returns:
            Path: 생성된 HTML 리포트 경로.
        
        Example:
            client.report(result, "report.html")
            # PDF가 필요하면 브라우저에서 열고 Ctrl+P → PDF로 저장
        """
        return self._report_generator.generate(
            result=result,
            output_path=Path(output_path),
            title=title,
            subtitle=subtitle,
            include_components=include_components
        )


class LiveClient:
    """라이브 트레이딩 클라이언트
    
    BrokerageProvider를 통해 실제 주문 실행.
    실시간 데이터 구독 및 트레이딩 루프 지원.
    """
    
    def __init__(
        self,
        data_provider: Optional[DataProvider] = None,
        brokerage_provider: Optional[BrokerageProvider] = None
    ):
        self._data_provider = data_provider
        self._brokerage = brokerage_provider
        self._running = False
        self._ws_client = None
    
    def submit_order(
        self,
        symbol: str,
        side: str,
        quantity: int,
        order_type: str = "market",
        price: Optional[float] = None
    ):
        """주문 제출"""
        if self._brokerage is None:
            raise ConfigurationError("brokerage_provider가 설정되지 않았습니다.")
        
        from .models import OrderSide, OrderType
        
        side_enum = OrderSide.BUY if side.lower() == "buy" else OrderSide.SELL
        type_enum = OrderType.MARKET if order_type.lower() == "market" else OrderType.LIMIT
        
        return self._brokerage.submit_order(
            symbol=symbol,
            side=side_enum,
            quantity=quantity,
            order_type=type_enum,
            price=price
        )
    
    def cancel_order(self, order_id: str) -> bool:
        """주문 취소"""
        if self._brokerage is None:
            raise ConfigurationError("brokerage_provider가 설정되지 않았습니다.")
        
        return self._brokerage.cancel_order(order_id)
    
    def get_positions(self):
        """현재 포지션 조회"""
        if self._brokerage is None:
            raise ConfigurationError("brokerage_provider가 설정되지 않았습니다.")
        
        return self._brokerage.get_positions()
    
    def get_balance(self):
        """계좌 잔고 조회"""
        if self._brokerage is None:
            raise ConfigurationError("brokerage_provider가 설정되지 않았습니다.")
        
        return self._brokerage.get_balance()
    
    def get_quote(self, symbol: str):
        """현재 호가 조회"""
        if self._data_provider is None:
            raise ConfigurationError("data_provider가 설정되지 않았습니다.")
        
        return self._data_provider.get_quote(symbol)
    
    def get_history(self, symbol: str, start, end, resolution=None):
        """과거 데이터 조회"""
        if self._data_provider is None:
            raise ConfigurationError("data_provider가 설정되지 않았습니다.")
        
        from .models import Resolution
        resolution = resolution or Resolution.DAILY
        
        return self._data_provider.get_history(symbol, start, end, resolution)
    
    def subscribe_realtime(
        self,
        symbols: List[str],
        on_bar,
        timeout: Optional[float] = None
    ):
        """실시간 데이터 구독
        
        Args:
            symbols: 종목코드 리스트
            on_bar: 콜백 함수 (symbol, Bar) -> None
            timeout: 타임아웃 (초). None이면 무한 실행
        """
        if self._data_provider is None:
            raise ConfigurationError("data_provider가 설정되지 않았습니다.")
        
        return self._data_provider.subscribe_realtime(symbols, on_bar, timeout=timeout)
    
    def subscribe_fills(self, on_fill, timeout: Optional[float] = None):
        """체결 통보 구독
        
        Args:
            on_fill: 콜백 함수 (Order) -> None
            timeout: 타임아웃 (초). None이면 무한 실행
        """
        if self._brokerage is None:
            raise ConfigurationError("brokerage_provider가 설정되지 않았습니다.")
        
        return self._brokerage.subscribe_fills(on_fill, timeout=timeout)
    
    def run_strategy(
        self,
        symbols: List[str],
        on_bar,
        on_fill=None,
        timeout: Optional[float] = None
    ):
        """전략 실행 (실시간 데이터 + 체결 통보)
        
        Args:
            symbols: 종목코드 리스트
            on_bar: 실시간 데이터 콜백 (symbol, Bar) -> None
            on_fill: 체결 통보 콜백 (Order) -> None
            timeout: 타임아웃 (초). None이면 무한 실행
        
        사용 예:
            def on_bar(symbol, bar):
                if bar.close > threshold:
                    live.submit_order(symbol, "buy", 1)
            
            def on_fill(order):
                print(f"체결: {order.symbol} {order.filled_quantity}주")
            
            live.run_strategy(["005930"], on_bar, on_fill, timeout=3600)
        """
        if self._data_provider is None:
            raise ConfigurationError("data_provider가 설정되지 않았습니다.")
        
        # WebSocket 클라이언트 설정
        ws_client = self._data_provider.subscribe_realtime_async(symbols, on_bar)
        
        # 체결 통보 구독 (동일한 WebSocket에 추가)
        if on_fill and self._brokerage:
            # kis_auth.py 기반 HTS ID 사용
            try:
                from .models import Order, OrderSide, OrderType, OrderStatus
                
                def notice_to_order(notice):
                    try:
                        side = OrderSide.BUY if notice.side == "02" else OrderSide.SELL
                        status = OrderStatus.FILLED if notice.is_fill else OrderStatus.SUBMITTED
                        
                        if notice.is_rejected:
                            status = OrderStatus.REJECTED
                        
                        order = Order(
                            id=notice.order_no,
                            symbol=notice.symbol,
                            side=side,
                            order_type=OrderType.LIMIT,
                            quantity=notice.order_qty,
                            price=float(notice.fill_price) if notice.fill_price else None,
                            filled_quantity=notice.fill_qty,
                            average_price=float(notice.fill_price) if notice.fill_price else 0,
                            status=status,
                            created_at=datetime.now(),
                            updated_at=datetime.now()
                        )
                        on_fill(order)
                    except Exception as e:
                        logger.error(f"Order 변환 오류: {e}")
                
                # kis_devlp.yaml에 my_htsid가 설정되어 있으면 자동 구독
                ws_client.subscribe_fills(notice_to_order)
            except Exception as e:
                logger.warning(f"체결 통보 구독 실패 (my_htsid 미설정?): {e}")
        
        self._ws_client = ws_client
        self._running = True
        
        logger.info(f"전략 실행 시작: {symbols}")
        
        # 블로킹 실행
        ws_client.start(timeout=timeout)
        
        self._running = False
        logger.info("전략 실행 종료")
    
    def stop(self):
        """전략 실행 중지"""
        if self._ws_client:
            self._ws_client.stop()
        self._running = False
        logger.info("전략 중지 요청")
    
    @property
    def is_running(self) -> bool:
        """실행 상태"""
        return self._running