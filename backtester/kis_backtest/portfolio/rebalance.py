"""리밸런싱 시뮬레이터

Docs:
- docs/p2-portfolio-plan.md

주기적 리밸런싱 시뮬레이션 및 Buy&Hold 비교.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Literal, Optional, Tuple

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


# ============================================================
# 1. RebalanceResult - 시뮬레이션 결과 모델
# ============================================================

@dataclass
class RebalanceResult:
    """리밸런싱 시뮬레이션 결과
    
    Attributes:
        equity_curve: 리밸런싱 포트폴리오 자산 곡선
        no_rebalance_curve: Buy & Hold 자산 곡선
        final_return: 리밸런싱 최종 수익률
        no_rebalance_return: Buy & Hold 최종 수익률
        rebalance_benefit: 리밸런싱 효과 (수익률 차이)
        rebalance_dates: 리밸런싱 실행 날짜 목록
        turnover: 총 회전율
        rebalance_count: 리밸런싱 횟수
        transaction_cost: 총 거래 비용 (예상)
    """
    # 자산 곡선
    equity_curve: pd.Series
    no_rebalance_curve: pd.Series
    
    # 수익률
    final_return: float
    no_rebalance_return: float
    rebalance_benefit: float
    
    # 리밸런싱 이력
    rebalance_dates: List[datetime]
    rebalance_count: int
    turnover: float
    
    # 비용
    transaction_cost: float
    
    def summary(self) -> Dict[str, float]:
        """요약 통계"""
        return {
            "리밸런싱_수익률": self.final_return,
            "BuyHold_수익률": self.no_rebalance_return,
            "리밸런싱_효과": self.rebalance_benefit,
            "리밸런싱_횟수": self.rebalance_count,
            "총_회전율": self.turnover,
            "거래비용": self.transaction_cost,
        }
    
    def __repr__(self) -> str:
        return (
            f"RebalanceResult(\n"
            f"  리밸런싱 수익률={self.final_return:.2%},\n"
            f"  Buy&Hold 수익률={self.no_rebalance_return:.2%},\n"
            f"  리밸런싱 효과={self.rebalance_benefit:+.2%},\n"
            f"  리밸런싱 횟수={self.rebalance_count}\n"
            f")"
        )


# ============================================================
# 2. RebalanceSimulator - 리밸런싱 시뮬레이터
# ============================================================

class RebalanceSimulator:
    """리밸런싱 시뮬레이터
    
    주기적 리밸런싱 vs Buy & Hold 비교 시뮬레이션.
    
    Example:
        simulator = RebalanceSimulator(
            prices=price_df,
            initial_weights={"005930": 0.6, "000660": 0.4},
            initial_capital=100_000_000,
        )
        
        result = simulator.simulate(period="monthly")
        print(f"리밸런싱 효과: {result.rebalance_benefit:+.2%}")
    """
    
    def __init__(
        self,
        prices: pd.DataFrame,
        initial_weights: Dict[str, float],
        initial_capital: float = 100_000_000,
        transaction_cost_rate: float = 0.001,  # 0.1% 거래비용
    ):
        """
        Args:
            prices: 가격 DataFrame (columns=종목, index=날짜)
            initial_weights: 초기 목표 비중
            initial_capital: 초기 자본금
            transaction_cost_rate: 거래 비용률 (편도)
        """
        self.prices = prices.dropna()
        self.initial_weights = pd.Series(initial_weights)
        self.initial_weights = self.initial_weights / self.initial_weights.sum()
        self.initial_capital = initial_capital
        self.transaction_cost_rate = transaction_cost_rate
        
        self.symbols = list(prices.columns)
        
        logger.info(
            f"리밸런싱 시뮬레이터 초기화: "
            f"{len(self.symbols)}개 종목, "
            f"{len(self.prices)}일 데이터"
        )
    
    def simulate(
        self,
        period: Literal["daily", "weekly", "monthly", "quarterly", "yearly"] = "monthly",
        threshold: Optional[float] = None,
    ) -> RebalanceResult:
        """리밸런싱 시뮬레이션 실행
        
        Args:
            period: 리밸런싱 주기
                - "daily": 매일
                - "weekly": 매주 월요일
                - "monthly": 매월 첫 거래일
                - "quarterly": 매분기 첫 거래일
                - "yearly": 매년 첫 거래일
            threshold: 비중 이탈 임계값 (예: 0.05).
                      설정 시 period 무시하고 threshold 기반 리밸런싱.
        
        Returns:
            RebalanceResult: 시뮬레이션 결과
        """
        logger.info(f"리밸런싱 시뮬레이션 시작: period={period}, threshold={threshold}")
        
        returns = self.prices.pct_change().dropna()
        
        # Buy & Hold 시뮬레이션
        no_rebalance_equity = self._buy_and_hold(returns)
        
        # 리밸런싱 시뮬레이션
        rebalance_equity, rebalance_dates, turnover, total_cost = self._with_rebalance(
            returns, period, threshold
        )
        
        # 수익률 계산
        final_return = (rebalance_equity.iloc[-1] / self.initial_capital) - 1
        no_rebalance_return = (no_rebalance_equity.iloc[-1] / self.initial_capital) - 1
        
        result = RebalanceResult(
            equity_curve=rebalance_equity,
            no_rebalance_curve=no_rebalance_equity,
            final_return=final_return,
            no_rebalance_return=no_rebalance_return,
            rebalance_benefit=final_return - no_rebalance_return,
            rebalance_dates=rebalance_dates,
            rebalance_count=len(rebalance_dates),
            turnover=turnover,
            transaction_cost=total_cost,
        )
        
        logger.info(
            f"시뮬레이션 완료: 리밸런싱={final_return:.2%}, "
            f"B&H={no_rebalance_return:.2%}, "
            f"효과={result.rebalance_benefit:+.2%}"
        )
        
        return result
    
    def _buy_and_hold(self, returns: pd.DataFrame) -> pd.Series:
        """Buy & Hold 시뮬레이션
        
        초기 비중으로 매수 후 끝까지 보유.
        """
        # 초기 투자금 배분
        initial_values = self.initial_weights * self.initial_capital
        
        # 일별 포트폴리오 가치 계산
        cumulative_returns = (1 + returns).cumprod()
        
        # 각 종목별 가치 변화
        values = cumulative_returns * initial_values
        portfolio_values = values.sum(axis=1)
        
        # 첫 날 추가
        start_date = returns.index[0] - pd.Timedelta(days=1)
        equity = pd.concat([
            pd.Series([self.initial_capital], index=[start_date]),
            portfolio_values
        ])
        
        return equity
    
    def _with_rebalance(
        self,
        returns: pd.DataFrame,
        period: str,
        threshold: Optional[float],
    ) -> Tuple[pd.Series, List[datetime], float, float]:
        """리밸런싱 시뮬레이션
        
        Returns:
            (자산곡선, 리밸런싱날짜들, 총회전율, 총거래비용)
        """
        target_weights = self.initial_weights
        current_values = target_weights * self.initial_capital
        
        portfolio_values = [self.initial_capital]
        rebalance_dates = []
        total_turnover = 0.0
        total_cost = 0.0
        
        # 리밸런싱 일자 마스크 생성
        rebalance_mask = self._get_rebalance_mask(returns.index, period)
        
        for i, date in enumerate(returns.index):
            # 일별 수익 반영
            daily_returns = returns.loc[date]
            current_values = current_values * (1 + daily_returns)
            total_value = current_values.sum()
            
            # 현재 비중
            current_weights = current_values / total_value
            
            # 리밸런싱 조건 확인
            should_rebalance = False
            
            if threshold is not None:
                # 임계값 기반 리밸런싱
                max_deviation = (current_weights - target_weights).abs().max()
                if max_deviation > threshold:
                    should_rebalance = True
            elif rebalance_mask[i]:
                should_rebalance = True
            
            if should_rebalance:
                # 회전율 계산 (편도)
                turnover = float((current_weights - target_weights).abs().sum()) / 2
                total_turnover += turnover
                
                # 거래 비용 계산
                trade_value = turnover * total_value
                cost = trade_value * self.transaction_cost_rate * 2  # 양방향
                total_cost += cost
                
                # 비용 차감 후 리밸런싱
                total_value -= cost
                current_values = target_weights * total_value
                rebalance_dates.append(date)
            
            portfolio_values.append(total_value)
        
        # 자산 곡선 생성
        start_date = returns.index[0] - pd.Timedelta(days=1)
        equity = pd.Series(
            portfolio_values,
            index=[start_date] + list(returns.index)
        )
        
        return equity, rebalance_dates, total_turnover, total_cost
    
    def _get_rebalance_mask(
        self,
        dates: pd.DatetimeIndex,
        period: str,
    ) -> List[bool]:
        """리밸런싱 일자 마스크 생성"""
        mask = []
        
        if period == "daily":
            mask = [True] * len(dates)
        
        elif period == "weekly":
            # 매주 첫 거래일 (월요일 또는 그 주 첫 거래일)
            week_nums = dates.isocalendar().week
            for i, date in enumerate(dates):
                if i == 0:
                    mask.append(True)
                elif week_nums.iloc[i] != week_nums.iloc[i-1]:
                    mask.append(True)
                else:
                    mask.append(False)
        
        elif period == "monthly":
            # 매월 첫 거래일
            months = dates.month
            for i, date in enumerate(dates):
                if i == 0:
                    mask.append(True)
                elif months[i] != months[i-1]:
                    mask.append(True)
                else:
                    mask.append(False)
        
        elif period == "quarterly":
            # 매분기 첫 거래일
            quarters = dates.quarter
            for i, date in enumerate(dates):
                if i == 0:
                    mask.append(True)
                elif quarters[i] != quarters[i-1]:
                    mask.append(True)
                else:
                    mask.append(False)
        
        elif period == "yearly":
            # 매년 첫 거래일
            years = dates.year
            for i, date in enumerate(dates):
                if i == 0:
                    mask.append(True)
                elif years[i] != years[i-1]:
                    mask.append(True)
                else:
                    mask.append(False)
        
        else:
            raise ValueError(f"알 수 없는 주기: {period}")
        
        return mask
    
    def compare_periods(
        self,
        periods: List[str] = ["weekly", "monthly", "quarterly", "yearly"],
    ) -> pd.DataFrame:
        """여러 리밸런싱 주기 비교
        
        Args:
            periods: 비교할 주기 목록
        
        Returns:
            DataFrame with comparison results
        """
        results = []
        
        for period in periods:
            result = self.simulate(period=period)
            results.append({
                "period": period,
                "final_return": result.final_return,
                "rebalance_benefit": result.rebalance_benefit,
                "rebalance_count": result.rebalance_count,
                "turnover": result.turnover,
                "transaction_cost": result.transaction_cost,
            })
        
        # Buy & Hold 추가
        results.append({
            "period": "buy_and_hold",
            "final_return": result.no_rebalance_return,
            "rebalance_benefit": 0,
            "rebalance_count": 0,
            "turnover": 0,
            "transaction_cost": 0,
        })
        
        return pd.DataFrame(results)
