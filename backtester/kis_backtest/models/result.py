"""결과 모델
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

import pandas as pd

from .trading import Order


class BacktestResult(BaseModel):
    """백테스트 결과"""
    
    model_config = {"arbitrary_types_allowed": True}
    
    success: bool = Field(..., description="성공 여부")
    output_dir: Optional[Path] = Field(None, description="결과 디렉토리")
    
    # 메타데이터
    run_id: Optional[str] = Field(None, description="실행 ID")
    strategy_id: Optional[str] = Field(None, description="전략 ID")
    symbols: List[str] = Field(default_factory=list, description="종목 리스트")
    
    # 기간
    start_date: Optional[str] = Field(None, description="시작일")
    end_date: Optional[str] = Field(None, description="종료일")
    
    # 핵심 통계 (퍼센트 값은 0.0~1.0 범위, Python % 포매터 호환)
    total_return: float = Field(0.0, description="총 수익 금액 (KRW)")
    total_return_pct: float = Field(0.0, description="총 수익률 (0.0~1.0, 예: 0.17 = 17%)")
    cagr: float = Field(0.0, description="연환산 수익률 (0.0~1.0)")
    sharpe_ratio: float = Field(0.0, description="샤프 지수 (비율)")
    sortino_ratio: float = Field(0.0, description="소티노 지수 (비율)")
    max_drawdown: float = Field(0.0, description="최대 낙폭 (0.0~1.0, 예: 0.15 = 15%)")

    # 거래 통계
    total_trades: int = Field(0, description="총 거래 수")
    win_rate: float = Field(0.0, description="승률 (0.0~1.0, 예: 0.50 = 50%)")
    profit_factor: float = Field(0.0, description="수익 팩터 (비율)")
    average_win: float = Field(0.0, description="평균 이익")
    average_loss: float = Field(0.0, description="평균 손실")
    
    # 시계열 데이터
    equity_curve: Optional[Any] = Field(None, description="자산 곡선 (Dict 또는 Series)")
    benchmark_curve: Optional[Dict[str, float]] = Field(
        None, description="벤치마크 수익률 곡선 (날짜 → 시작 대비 %). 예: {'2025-01-02': 0.0, '2025-01-03': 1.5}"
    )
    daily_returns: Optional[pd.Series] = Field(None, description="일간 수익률")
    
    # 거래 내역
    orders: List[Order] = Field(default_factory=list, description="주문 목록")
    trades: List[Dict[str, Any]] = Field(default_factory=list, description="거래 내역")
    
    # 원시 데이터
    raw_statistics: Dict[str, Any] = Field(default_factory=dict)
    raw_runtime_statistics: Dict[str, Any] = Field(default_factory=dict)
    logs: str = Field("", description="로그")
    
    # 실행 정보
    duration_seconds: float = Field(0.0, description="실행 시간 (초)")
    
    def to_dataframe(self) -> pd.DataFrame:
        """통계를 DataFrame으로 변환"""
        stats = {
            "총 수익률": f"{self.total_return_pct:.2%}",
            "연환산 수익률": f"{self.cagr:.2%}",
            "샤프 지수": f"{self.sharpe_ratio:.2f}",
            "소티노 지수": f"{self.sortino_ratio:.2f}",
            "최대 낙폭": f"{self.max_drawdown:.2%}",
            "총 거래 수": self.total_trades,
            "승률": f"{self.win_rate:.1%}",
            "수익 팩터": f"{self.profit_factor:.2f}",
        }
        return pd.DataFrame([stats]).T.rename(columns={0: "값"})
    
    def get_monthly_returns(self) -> Optional[pd.DataFrame]:
        """월별 수익률 피벗 테이블"""
        if self.equity_curve is None:
            return None
        
        monthly = self.equity_curve.resample('M').last().pct_change()
        pivot = monthly.groupby([
            monthly.index.year,
            monthly.index.month
        ]).first().unstack()
        
        pivot.columns = ['1월', '2월', '3월', '4월', '5월', '6월',
                        '7월', '8월', '9월', '10월', '11월', '12월']
        return pivot


class OptimizationResult(BaseModel):
    """최적화 결과
    
    Grid Search / Random Search를 통해 얻은 파라미터 최적화 결과.
    
    Example:
        result = client.optimize(
            strategy_id="sma_crossover",
            parameters=[("short_window", 5, 20, 5), ("long_window", 20, 60, 10)],
            ...
        )
        
        print(f"최적 파라미터: {result.best_parameters}")
        print(f"샤프 비율: {result.best_sharpe:.2f}")
        print(result.results_df.sort_values("sharpe_ratio", ascending=False))
    """
    
    model_config = {"arbitrary_types_allowed": True}
    
    success: bool = Field(..., description="성공 여부")
    
    # 최적 결과 (퍼센트 값은 0.0~1.0 범위, Python % 포매터 호환)
    best_parameters: Dict[str, Any] = Field(default_factory=dict, description="최적 파라미터")
    best_sharpe: float = Field(0.0, description="최적 샤프 비율 (비율)")
    best_return: float = Field(0.0, description="최적 수익률 (0.0~1.0, 예: 0.17 = 17%)")
    best_drawdown: float = Field(0.0, description="최적 조합의 최대 낙폭 (0.0~1.0, 예: 0.15 = 15%)")
    
    # 전체 결과
    all_results: List[Dict[str, Any]] = Field(default_factory=list, description="모든 실행 결과")
    results_df: Optional[pd.DataFrame] = Field(None, description="결과 DataFrame")
    
    # 메타데이터
    total_backtests: int = Field(0, description="총 백테스트 수")
    successful_backtests: int = Field(0, description="성공한 백테스트 수")
    failed_backtests: int = Field(0, description="실패한 백테스트 수")
    elapsed_time: float = Field(0.0, description="소요시간 (초)")
    
    # 요약 통계
    statistics: Optional[Dict[str, Any]] = Field(None, description="요약 통계")
    
    # 최적화 설정
    target: str = Field("sharpe_ratio", description="목표 지표")
    target_direction: str = Field("max", description="목표 방향")
    strategy: str = Field("grid", description="탐색 전략")
    
    def get_top_n(self, n: int = 10, sort_by: str = "sharpe_ratio") -> pd.DataFrame:
        """상위 N개 결과 반환
        
        Args:
            n: 반환할 개수
            sort_by: 정렬 기준 컬럼
        
        Returns:
            상위 N개 결과 DataFrame
        """
        if self.results_df is None:
            return pd.DataFrame()
        
        return self.results_df.nlargest(n, sort_by)
    
    def plot_heatmap(self, param1: str, param2: str, metric: str = "sharpe_ratio"):
        """2D 파라미터 히트맵 생성 (Plotly)
        
        Args:
            param1: X축 파라미터
            param2: Y축 파라미터
            metric: 색상으로 표시할 지표
        
        Returns:
            Plotly Figure
        """
        if self.results_df is None:
            return None
        
        try:
            import plotly.express as px
            
            pivot = self.results_df.pivot_table(
                index=param2, 
                columns=param1, 
                values=metric,
                aggfunc='mean'
            )
            
            fig = px.imshow(
                pivot,
                labels=dict(x=param1, y=param2, color=metric),
                title=f"파라미터 최적화: {metric}",
                color_continuous_scale="RdYlGn",
            )
            
            return fig
            
        except ImportError:
            return None
    
    def summary(self) -> str:
        """결과 요약 문자열"""
        lines = [
            "=" * 50,
            "파라미터 최적화 결과",
            "=" * 50,
            f"탐색 전략: {self.strategy}",
            f"목표 지표: {self.target} ({self.target_direction})",
            f"총 백테스트: {self.total_backtests}",
            f"성공/실패: {self.successful_backtests}/{self.failed_backtests}",
            f"소요 시간: {self.elapsed_time:.1f}초",
            "",
            "최적 파라미터:",
        ]
        
        for k, v in self.best_parameters.items():
            lines.append(f"  - {k}: {v}")
        
        lines.extend([
            "",
            f"최적 샤프 비율: {self.best_sharpe:.2f}",
            f"최적 수익률: {self.best_return:.2%}",
            f"최적 최대 낙폭: {self.best_drawdown:.2%}",
            "=" * 50,
        ])
        
        return "\n".join(lines)