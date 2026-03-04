"""파라미터 최적화 모듈

Docs:
- docs/p1-optimizer-plan.md

Grid Search / Random Search를 통한 전략 파라미터 최적화 기능 제공.
"""

import logging
import statistics
import time
from dataclasses import dataclass, field
from functools import reduce
from itertools import product
from typing import TYPE_CHECKING, Any, Callable, Dict, Iterator, List, Literal, Optional, Tuple
import random

import pandas as pd

if TYPE_CHECKING:
    from ..client import LeanClient
    from ..models.result import BacktestResult

logger = logging.getLogger(__name__)


# ============================================================
# 1. Parameter Specification & Grid
# ============================================================

@dataclass
class ParameterSpec:
    """파라미터 정의
    
    Example:
        spec = ParameterSpec("short_window", 5, 20, 5)
        # 생성되는 값: [5, 10, 15, 20]
    """
    name: str
    min_value: float
    max_value: float
    step: float
    
    def values(self) -> List[float]:
        """가능한 값 목록 생성"""
        result = []
        current = self.min_value
        while current <= self.max_value + 1e-9:  # float 오차 보정
            # 정수 파라미터면 int로 변환
            if self.step == int(self.step) and self.min_value == int(self.min_value):
                result.append(int(current))
            else:
                result.append(round(current, 6))
            current += self.step
        return result
    
    def __len__(self) -> int:
        return len(self.values())


class ParameterGrid:
    """Grid Search용 파라미터 조합 생성기
    
    Example:
        grid = ParameterGrid([
            ParameterSpec("short", 5, 15, 5),   # [5, 10, 15]
            ParameterSpec("long", 20, 30, 10),  # [20, 30]
        ])
        
        for params in grid:
            print(params)  # {"short": 5, "long": 20}, {"short": 5, "long": 30}, ...
        
        print(len(grid))  # 6
    """
    
    def __init__(self, parameters: List[ParameterSpec]):
        self.parameters = parameters
        self._param_names = [p.name for p in parameters]
        self._param_values = [p.values() for p in parameters]
    
    def __iter__(self) -> Iterator[Dict[str, Any]]:
        """모든 파라미터 조합을 순회 (제너레이터)"""
        for combo in product(*self._param_values):
            yield dict(zip(self._param_names, combo))
    
    def __len__(self) -> int:
        """총 조합 수"""
        if not self.parameters:
            return 0
        return reduce(lambda x, y: x * y, [len(p) for p in self.parameters], 1)
    
    def sample(self, n: int, seed: Optional[int] = None) -> List[Dict[str, Any]]:
        """Random Search용 무작위 샘플링
        
        Args:
            n: 샘플 수
            seed: 랜덤 시드 (재현성용)
        
        Returns:
            무작위로 선택된 파라미터 조합 리스트
        """
        if seed is not None:
            random.seed(seed)
        
        total = len(self)
        
        if n >= total:
            # 전체보다 많이 요청하면 전체 반환 (셔플)
            all_combos = list(self)
            random.shuffle(all_combos)
            return all_combos
        
        # 큰 그리드: 인덱스 기반 샘플링
        if total > 10000:
            indices = random.sample(range(total), n)
            return [self._get_by_index(i) for i in indices]
        
        # 작은 그리드: 전체 생성 후 샘플링
        all_combos = list(self)
        return random.sample(all_combos, n)
    
    def _get_by_index(self, index: int) -> Dict[str, Any]:
        """인덱스로 특정 조합 얻기 (대용량 그리드용)"""
        result = {}
        remaining = index
        
        for i in range(len(self.parameters) - 1, -1, -1):
            param = self.parameters[i]
            values = param.values()
            value_idx = remaining % len(values)
            result[param.name] = values[value_idx]
            remaining //= len(values)
        
        return result
    
    @classmethod
    def from_tuples(cls, params: List[Tuple[str, float, float, float]]) -> "ParameterGrid":
        """튜플 리스트에서 생성
        
        Args:
            params: [(name, min, max, step), ...]
        
        Example:
            grid = ParameterGrid.from_tuples([
                ("short_window", 5, 20, 5),
                ("long_window", 20, 60, 10),
            ])
        """
        specs = [ParameterSpec(name, min_v, max_v, step) for name, min_v, max_v, step in params]
        return cls(specs)


# ============================================================
# 2. Optimization Run Result
# ============================================================

@dataclass
class OptimizationRun:
    """단일 최적화 실행 결과"""
    params: Dict[str, Any]
    result: Optional["BacktestResult"] = None
    error: Optional[str] = None
    duration_seconds: float = 0.0
    
    @property
    def success(self) -> bool:
        return self.result is not None and self.result.success
    
    @property
    def sharpe_ratio(self) -> float:
        return self.result.sharpe_ratio if self.result else 0.0
    
    @property
    def total_return_pct(self) -> float:
        return self.result.total_return_pct if self.result else 0.0
    
    @property
    def max_drawdown(self) -> float:
        return self.result.max_drawdown if self.result else 0.0


# ============================================================
# 3. Parallel Executor
# ============================================================

class ParallelExecutor:
    """백테스트 실행기
    
    현재는 Docker 컨테이너 리소스 제한으로 인해 순차 실행.
    추후 asyncio 기반 병렬 실행으로 확장 가능.
    """
    
    def __init__(
        self,
        max_workers: int = 4,
        on_progress: Optional[Callable[[int, int, OptimizationRun], None]] = None
    ):
        """
        Args:
            max_workers: 최대 동시 실행 수 (현재 미사용, 순차 실행)
            on_progress: 진행 콜백 (completed, total, run) -> None
        """
        self.max_workers = max_workers
        self.on_progress = on_progress
    
    def run_grid(
        self,
        client: "LeanClient",
        strategy_id: str,
        symbols: List[str],
        start_date: str,
        end_date: str,
        parameter_grid: ParameterGrid,
        initial_cash: float = 100_000_000,
        market_type: str = "krx",
    ) -> List[OptimizationRun]:
        """Grid Search 실행
        
        모든 파라미터 조합에 대해 백테스트 실행.
        
        Args:
            client: LeanClient 인스턴스
            strategy_id: 전략 ID
            symbols: 종목코드 리스트
            start_date: 시작일
            end_date: 종료일
            parameter_grid: 파라미터 그리드
            initial_cash: 초기 자본금
            market_type: 시장 타입
        
        Returns:
            OptimizationRun 리스트
        """
        results: List[OptimizationRun] = []
        total = len(parameter_grid)
        completed = 0
        
        logger.info(f"[Optimizer] Grid Search 시작: {total}개 조합")
        
        for params in parameter_grid:
            run = self._run_single(
                client=client,
                strategy_id=strategy_id,
                symbols=symbols,
                start_date=start_date,
                end_date=end_date,
                params=params,
                initial_cash=initial_cash,
                market_type=market_type,
            )
            
            results.append(run)
            completed += 1
            
            if self.on_progress:
                self.on_progress(completed, total, run)
        
        logger.info(f"[Optimizer] Grid Search 완료: {completed}개 실행")
        return results
    
    def run_random(
        self,
        client: "LeanClient",
        strategy_id: str,
        symbols: List[str],
        start_date: str,
        end_date: str,
        parameter_grid: ParameterGrid,
        max_samples: int = 100,
        initial_cash: float = 100_000_000,
        market_type: str = "krx",
        seed: Optional[int] = None,
    ) -> List[OptimizationRun]:
        """Random Search 실행
        
        무작위로 선택된 파라미터 조합에 대해 백테스트 실행.
        
        Args:
            client: LeanClient 인스턴스
            strategy_id: 전략 ID
            symbols: 종목코드 리스트
            start_date: 시작일
            end_date: 종료일
            parameter_grid: 파라미터 그리드
            max_samples: 최대 샘플 수
            initial_cash: 초기 자본금
            market_type: 시장 타입
            seed: 랜덤 시드
        
        Returns:
            OptimizationRun 리스트
        """
        samples = parameter_grid.sample(max_samples, seed=seed)
        total = len(samples)
        
        logger.info(f"[Optimizer] Random Search 시작: {total}개 샘플")
        
        results: List[OptimizationRun] = []
        completed = 0
        
        for params in samples:
            run = self._run_single(
                client=client,
                strategy_id=strategy_id,
                symbols=symbols,
                start_date=start_date,
                end_date=end_date,
                params=params,
                initial_cash=initial_cash,
                market_type=market_type,
            )
            
            results.append(run)
            completed += 1
            
            if self.on_progress:
                self.on_progress(completed, total, run)
        
        logger.info(f"[Optimizer] Random Search 완료: {completed}개 실행")
        return results
    
    def _run_single(
        self,
        client: "LeanClient",
        strategy_id: str,
        symbols: List[str],
        start_date: str,
        end_date: str,
        params: Dict[str, Any],
        initial_cash: float,
        market_type: str,
    ) -> OptimizationRun:
        """단일 백테스트 실행"""
        start_time = time.time()
        
        try:
            result = client.backtest_strategy(
                strategy_id=strategy_id,
                symbols=symbols,
                start_date=start_date,
                end_date=end_date,
                params=params,
                initial_cash=initial_cash,
                market_type=market_type,
            )
            
            duration = time.time() - start_time
            
            return OptimizationRun(
                params=params,
                result=result,
                duration_seconds=duration
            )
            
        except Exception as e:
            duration = time.time() - start_time
            logger.warning(f"[Optimizer] 백테스트 실패: {params} - {e}")
            
            return OptimizationRun(
                params=params,
                result=None,
                error=str(e),
                duration_seconds=duration
            )


# ============================================================
# 4. Result Aggregator
# ============================================================

class ResultAggregator:
    """최적화 결과 집계"""
    
    @staticmethod
    def find_best(
        runs: List[OptimizationRun],
        target: str = "sharpe_ratio",
        direction: Literal["max", "min"] = "max"
    ) -> Optional[OptimizationRun]:
        """최적의 파라미터 조합 찾기
        
        Args:
            runs: OptimizationRun 리스트
            target: 목표 지표
            direction: "max" 또는 "min"
        
        Returns:
            최적의 OptimizationRun 또는 None
        """
        valid_runs = [r for r in runs if r.success]
        
        if not valid_runs:
            return None
        
        def get_metric(run: OptimizationRun) -> float:
            result = run.result
            if result is None:
                return float('-inf') if direction == "max" else float('inf')
            
            metric_map = {
                "sharpe_ratio": result.sharpe_ratio,
                "sortino_ratio": result.sortino_ratio,
                "total_return": result.total_return_pct,
                "total_return_pct": result.total_return_pct,
                "max_drawdown": result.max_drawdown,
                "win_rate": result.win_rate,
                "profit_factor": result.profit_factor,
                "cagr": result.cagr,
            }
            return metric_map.get(target, 0.0)
        
        if direction == "max":
            return max(valid_runs, key=get_metric)
        else:
            return min(valid_runs, key=get_metric)
    
    @staticmethod
    def to_dataframe(runs: List[OptimizationRun]) -> pd.DataFrame:
        """결과를 DataFrame으로 변환
        
        Args:
            runs: OptimizationRun 리스트
        
        Returns:
            결과 DataFrame
        """
        rows = []
        
        for run in runs:
            row = {**run.params}
            
            if run.result and run.result.success:
                row.update({
                    "sharpe_ratio": run.result.sharpe_ratio,
                    "sortino_ratio": run.result.sortino_ratio,
                    "total_return_pct": run.result.total_return_pct,
                    "cagr": run.result.cagr,
                    "max_drawdown": run.result.max_drawdown,
                    "win_rate": run.result.win_rate,
                    "profit_factor": run.result.profit_factor,
                    "total_trades": run.result.total_trades,
                    "duration_seconds": run.duration_seconds,
                    "success": True,
                })
            else:
                row.update({
                    "error": run.error,
                    "duration_seconds": run.duration_seconds,
                    "success": False,
                })
            
            rows.append(row)
        
        return pd.DataFrame(rows)
    
    @staticmethod
    def summary_statistics(runs: List[OptimizationRun]) -> Dict[str, Any]:
        """요약 통계 계산
        
        Args:
            runs: OptimizationRun 리스트
        
        Returns:
            통계 딕셔너리
        """
        valid_runs = [r for r in runs if r.success]
        failed_runs = [r for r in runs if not r.success]
        
        if not valid_runs:
            return {
                "total_runs": len(runs),
                "successful_runs": 0,
                "failed_runs": len(runs),
            }
        
        sharpes = [r.sharpe_ratio for r in valid_runs]
        returns = [r.total_return_pct for r in valid_runs]
        drawdowns = [r.max_drawdown for r in valid_runs]
        durations = [r.duration_seconds for r in runs]
        
        return {
            "total_runs": len(runs),
            "successful_runs": len(valid_runs),
            "failed_runs": len(failed_runs),
            
            # 샤프 통계
            "sharpe_mean": statistics.mean(sharpes),
            "sharpe_std": statistics.stdev(sharpes) if len(sharpes) > 1 else 0,
            "sharpe_min": min(sharpes),
            "sharpe_max": max(sharpes),
            
            # 수익률 통계
            "return_mean": statistics.mean(returns),
            "return_std": statistics.stdev(returns) if len(returns) > 1 else 0,
            "return_min": min(returns),
            "return_max": max(returns),
            
            # 최대 낙폭 통계
            "drawdown_mean": statistics.mean(drawdowns),
            "drawdown_max": max(drawdowns),
            
            # 실행 시간
            "total_duration_seconds": sum(durations),
            "avg_duration_seconds": statistics.mean(durations) if durations else 0,
        }


# ============================================================
# 5. Main Optimizer Class
# ============================================================

class StrategyOptimizer:
    """전략 파라미터 최적화기
    
    LeanClient에서 사용하는 고수준 API.
    
    Example:
        optimizer = StrategyOptimizer(client)
        
        result = optimizer.optimize(
            strategy_id="sma_crossover",
            symbols=["005930"],
            start_date="2025-01-01",
            end_date="2025-12-31",
            parameters=[
                ("short_window", 5, 20, 5),
                ("long_window", 20, 60, 10),
            ],
            target="sharpe_ratio",
        )
    """
    
    def __init__(
        self,
        client: "LeanClient",
        max_workers: int = 4,
    ):
        """
        Args:
            client: LeanClient 인스턴스
            max_workers: 최대 동시 실행 수
        """
        self.client = client
        self.max_workers = max_workers
    
    def optimize(
        self,
        strategy_id: str,
        symbols: List[str],
        start_date: str,
        end_date: str,
        parameters: List[Tuple[str, float, float, float]],
        target: str = "sharpe_ratio",
        target_direction: Literal["max", "min"] = "max",
        strategy: Literal["grid", "random"] = "grid",
        max_samples: int = 100,
        initial_cash: float = 100_000_000,
        market_type: str = "krx",
        on_progress: Optional[Callable[[int, int, OptimizationRun], None]] = None,
        seed: Optional[int] = None,
    ):
        """파라미터 최적화 실행
        
        Args:
            strategy_id: 전략 ID
            symbols: 종목코드 리스트
            start_date: 시작일
            end_date: 종료일
            parameters: 파라미터 정의 [(name, min, max, step), ...]
            target: 목표 지표
            target_direction: "max" 또는 "min"
            strategy: 탐색 전략 ("grid" 또는 "random")
            max_samples: random search용 최대 샘플 수
            initial_cash: 초기 자본금
            market_type: 시장 타입
            on_progress: 진행 콜백
            seed: 랜덤 시드
        
        Returns:
            OptimizationResult
        """
        from ..models.result import OptimizationResult
        
        start_time = time.time()
        
        # 파라미터 그리드 생성
        grid = ParameterGrid.from_tuples(parameters)
        total_combinations = len(grid)
        
        logger.info(f"[Optimizer] 최적화 시작")
        logger.info(f"  - 전략: {strategy_id}")
        logger.info(f"  - 종목: {symbols}")
        logger.info(f"  - 기간: {start_date} ~ {end_date}")
        logger.info(f"  - 탐색 전략: {strategy}")
        logger.info(f"  - 총 조합 수: {total_combinations}")
        
        # 실행기 생성
        executor = ParallelExecutor(
            max_workers=self.max_workers,
            on_progress=on_progress,
        )
        
        # 최적화 실행
        if strategy == "grid":
            runs = executor.run_grid(
                client=self.client,
                strategy_id=strategy_id,
                symbols=symbols,
                start_date=start_date,
                end_date=end_date,
                parameter_grid=grid,
                initial_cash=initial_cash,
                market_type=market_type,
            )
        else:
            runs = executor.run_random(
                client=self.client,
                strategy_id=strategy_id,
                symbols=symbols,
                start_date=start_date,
                end_date=end_date,
                parameter_grid=grid,
                max_samples=max_samples,
                initial_cash=initial_cash,
                market_type=market_type,
                seed=seed,
            )
        
        # 결과 집계
        elapsed_time = time.time() - start_time
        
        best_run = ResultAggregator.find_best(runs, target, target_direction)
        results_df = ResultAggregator.to_dataframe(runs)
        stats = ResultAggregator.summary_statistics(runs)
        
        # 결과 생성
        result = OptimizationResult(
            success=best_run is not None,
            best_parameters=best_run.params if best_run else {},
            best_sharpe=best_run.sharpe_ratio if best_run else 0.0,
            best_return=best_run.total_return_pct if best_run else 0.0,
            best_drawdown=best_run.max_drawdown if best_run else 0.0,
            all_results=[
                {
                    "params": run.params,
                    "sharpe_ratio": run.sharpe_ratio,
                    "total_return_pct": run.total_return_pct,
                    "max_drawdown": run.max_drawdown,
                    "success": run.success,
                    "error": run.error,
                    "duration_seconds": run.duration_seconds,
                }
                for run in runs
            ],
            results_df=results_df,
            total_backtests=len(runs),
            successful_backtests=len([r for r in runs if r.success]),
            failed_backtests=len([r for r in runs if not r.success]),
            elapsed_time=elapsed_time,
            statistics=stats,
            target=target,
            target_direction=target_direction,
            strategy=strategy,
        )
        
        logger.info(f"[Optimizer] 최적화 완료")
        logger.info(f"  - 소요 시간: {elapsed_time:.1f}초")
        logger.info(f"  - 성공/실패: {result.successful_backtests}/{result.failed_backtests}")
        
        if best_run:
            logger.info(f"  - 최적 파라미터: {best_run.params}")
            logger.info(f"  - 최적 {target}: {getattr(best_run.result, target, 'N/A')}")
        
        return result
