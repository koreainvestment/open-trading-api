"""포트폴리오 분석기

Docs:
- docs/p2-portfolio-plan.md

상관관계 분석, 분산 효과 측정, 효율적 프론티어 계산 등.

Lean 기존 기능 활용:
- QuantConnect.Statistics.PortfolioStatistics: alpha, beta, sharpe 등
- QuantConnect.Algorithm.Framework.Portfolio.IPortfolioOptimizer: 최적화 인터페이스
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Literal, Optional, Tuple, Union

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


# ============================================================
# 1. PortfolioMetrics - 분석 결과 모델
# ============================================================

@dataclass
class PortfolioMetrics:
    """포트폴리오 분석 결과
    
    Attributes:
        correlation_matrix: 종목간 상관관계 매트릭스
        returns: 일별 수익률 DataFrame
        volatilities: 개별 종목 변동성 (연율화)
        portfolio_return: 포트폴리오 기대 수익률 (연율화)
        portfolio_volatility: 포트폴리오 변동성 (연율화)
        portfolio_sharpe: 샤프 비율
        diversification_ratio: 분산 비율 (>1 이면 분산 효과 있음)
        risk_contributions: 리스크 기여도
        weights: 현재 비중
        covariance_matrix: 공분산 행렬
        efficient_frontier: 효율적 프론티어 (옵션)
        optimal_weights: 최적 비중 (옵션)
    """
    # 상관관계
    correlation_matrix: pd.DataFrame
    
    # 수익률/변동성
    returns: pd.DataFrame
    volatilities: pd.Series
    
    # 포트폴리오 통계
    portfolio_return: float
    portfolio_volatility: float
    portfolio_sharpe: float
    
    # 분산 효과
    diversification_ratio: float
    
    # 리스크 기여도
    risk_contributions: pd.Series
    
    # 비중
    weights: pd.Series
    
    # 공분산
    covariance_matrix: pd.DataFrame
    
    # 효율적 프론티어 (옵션)
    efficient_frontier: Optional[pd.DataFrame] = None
    optimal_weights: Optional[pd.Series] = None
    
    def summary(self) -> Dict[str, float]:
        """요약 통계 반환"""
        return {
            "기대수익률": self.portfolio_return,
            "변동성": self.portfolio_volatility,
            "샤프비율": self.portfolio_sharpe,
            "분산비율": self.diversification_ratio,
        }
    
    def __repr__(self) -> str:
        return (
            f"PortfolioMetrics(\n"
            f"  기대수익률={self.portfolio_return:.2%},\n"
            f"  변동성={self.portfolio_volatility:.2%},\n"
            f"  샤프비율={self.portfolio_sharpe:.2f},\n"
            f"  분산비율={self.diversification_ratio:.2f}\n"
            f")"
        )


# ============================================================
# 2. PortfolioAnalyzer - 핵심 분석 클래스
# ============================================================

class PortfolioAnalyzer:
    """포트폴리오 분석기
    
    일별 수익률 데이터를 기반으로 포트폴리오 분석 수행.
    
    Example:
        import pandas as pd
        
        # 수익률 데이터 (columns=종목, index=날짜)
        returns = pd.DataFrame({
            "005930": [...],  # 삼성전자
            "000660": [...],  # SK하이닉스
        })
        
        analyzer = PortfolioAnalyzer(
            returns=returns,
            weights={"005930": 0.6, "000660": 0.4},
        )
        
        metrics = analyzer.analyze()
        print(f"분산 비율: {metrics.diversification_ratio:.2f}")
    """
    
    def __init__(
        self,
        returns: pd.DataFrame,
        weights: Optional[Dict[str, float]] = None,
        risk_free_rate: float = 0.03,
        trading_days: int = 252,
    ):
        """
        Args:
            returns: 일별 수익률 DataFrame (columns=종목, index=날짜)
            weights: 비중 딕셔너리. None이면 동일 비중.
            risk_free_rate: 무위험 이자율 (연율)
            trading_days: 연간 거래일 수
        """
        self.returns = returns.dropna()
        self.symbols = list(returns.columns)
        self.risk_free_rate = risk_free_rate
        self.trading_days = trading_days
        
        # 비중 설정
        if weights is None:
            n = len(self.symbols)
            self.weights = pd.Series({s: 1/n for s in self.symbols})
        else:
            self.weights = pd.Series(weights)
            # 비중 정규화 (합이 1이 되도록)
            self.weights = self.weights / self.weights.sum()
        
        logger.info(f"포트폴리오 분석기 초기화: {len(self.symbols)}개 종목, {len(self.returns)}일 데이터")
    
    def analyze(self) -> PortfolioMetrics:
        """전체 분석 실행
        
        Returns:
            PortfolioMetrics: 분석 결과
        """
        logger.info("포트폴리오 분석 시작")
        
        # 상관관계 매트릭스
        corr = self.returns.corr()
        
        # 개별 종목 변동성 (연율화)
        volatilities = self.returns.std() * np.sqrt(self.trading_days)
        
        # 공분산 행렬 (연율화)
        cov = self.returns.cov() * self.trading_days
        
        # 개별 종목 기대 수익률 (연율화)
        mean_returns = self.returns.mean() * self.trading_days
        
        # 포트폴리오 수익률
        w = self.weights.values
        portfolio_return = float(np.dot(w, mean_returns))
        
        # 포트폴리오 변동성
        portfolio_volatility = float(np.sqrt(np.dot(w.T, np.dot(cov, w))))
        
        # 샤프 비율
        if portfolio_volatility > 0:
            portfolio_sharpe = (portfolio_return - self.risk_free_rate) / portfolio_volatility
        else:
            portfolio_sharpe = 0.0
        
        # 분산 비율 (Diversification Ratio)
        # DR = 가중평균 변동성 / 포트폴리오 변동성
        # DR > 1 이면 분산 효과 있음
        weighted_vol = float((volatilities * self.weights).sum())
        if portfolio_volatility > 0:
            diversification_ratio = weighted_vol / portfolio_volatility
        else:
            diversification_ratio = 1.0
        
        # 리스크 기여도 (Marginal Risk Contribution)
        if portfolio_volatility > 0:
            marginal_contrib = np.dot(cov, w) / portfolio_volatility
            risk_contributions = pd.Series(
                self.weights.values * marginal_contrib,
                index=self.symbols
            )
        else:
            risk_contributions = pd.Series(0, index=self.symbols)
        
        logger.info(f"분석 완료: 샤프={portfolio_sharpe:.2f}, 분산비율={diversification_ratio:.2f}")
        
        return PortfolioMetrics(
            correlation_matrix=corr,
            returns=self.returns,
            volatilities=volatilities,
            portfolio_return=portfolio_return,
            portfolio_volatility=portfolio_volatility,
            portfolio_sharpe=portfolio_sharpe,
            diversification_ratio=diversification_ratio,
            risk_contributions=risk_contributions,
            weights=self.weights,
            covariance_matrix=cov,
        )
    
    def efficient_frontier(
        self,
        n_points: int = 50,
        allow_short: bool = False,
    ) -> pd.DataFrame:
        """효율적 프론티어 계산
        
        Args:
            n_points: 프론티어 포인트 수
            allow_short: 공매도 허용 여부
        
        Returns:
            DataFrame with columns: [return, volatility, sharpe, weight_종목1, ...]
        """
        try:
            from scipy.optimize import minimize
        except ImportError:
            logger.error("scipy가 필요합니다: pip install scipy")
            return pd.DataFrame()
        
        logger.info(f"효율적 프론티어 계산: {n_points}개 포인트")
        
        n = len(self.symbols)
        cov = self.returns.cov() * self.trading_days
        mean_returns = self.returns.mean() * self.trading_days
        
        # 목표 수익률 범위
        min_ret = float(mean_returns.min())
        max_ret = float(mean_returns.max())
        target_returns = np.linspace(min_ret, max_ret, n_points)
        
        results = []
        
        for target in target_returns:
            # 최소 분산 포트폴리오 찾기
            def portfolio_vol(w):
                return np.sqrt(np.dot(w.T, np.dot(cov.values, w)))
            
            constraints = [
                {"type": "eq", "fun": lambda w: np.sum(w) - 1},  # 비중 합 = 1
                {"type": "eq", "fun": lambda w, t=target: np.dot(w, mean_returns.values) - t},
            ]
            
            if allow_short:
                bounds = tuple((-1, 1) for _ in range(n))
            else:
                bounds = tuple((0, 1) for _ in range(n))
            
            init = np.array([1/n] * n)
            
            try:
                result = minimize(
                    portfolio_vol,
                    init,
                    method="SLSQP",
                    bounds=bounds,
                    constraints=constraints,
                    options={"maxiter": 1000},
                )
                
                if result.success:
                    vol = result.fun
                    sharpe = (target - self.risk_free_rate) / vol if vol > 0 else 0
                    
                    row = {
                        "return": target,
                        "volatility": vol,
                        "sharpe": sharpe,
                    }
                    for i, sym in enumerate(self.symbols):
                        row[f"weight_{sym}"] = result.x[i]
                    
                    results.append(row)
            except Exception as e:
                logger.debug(f"목표수익률 {target:.4f}에서 최적화 실패: {e}")
                continue
        
        df = pd.DataFrame(results)
        logger.info(f"효율적 프론티어 계산 완료: {len(df)}개 포인트")
        return df
    
    def optimal_weights(
        self,
        objective: Literal["sharpe", "min_variance", "max_return"] = "sharpe",
        allow_short: bool = False,
        max_weight: float = 1.0,
        min_weight: float = 0.0,
    ) -> Tuple[pd.Series, PortfolioMetrics]:
        """최적 비중 계산
        
        Args:
            objective: 목표 함수
                - "sharpe": 최대 샤프 비율
                - "min_variance": 최소 변동성
                - "max_return": 최대 수익률
            allow_short: 공매도 허용 여부
            max_weight: 개별 종목 최대 비중
            min_weight: 개별 종목 최소 비중
        
        Returns:
            (최적 비중, 해당 비중의 분석 결과)
        """
        try:
            from scipy.optimize import minimize
        except ImportError:
            raise ImportError("scipy가 필요합니다: pip install scipy")
        
        logger.info(f"최적 비중 계산: objective={objective}")
        
        n = len(self.symbols)
        cov = self.returns.cov() * self.trading_days
        mean_returns = self.returns.mean() * self.trading_days
        
        if objective == "sharpe":
            def neg_sharpe(w):
                ret = np.dot(w, mean_returns.values)
                vol = np.sqrt(np.dot(w.T, np.dot(cov.values, w)))
                if vol > 0:
                    return -(ret - self.risk_free_rate) / vol
                return 0
            obj_func = neg_sharpe
            
        elif objective == "min_variance":
            def variance(w):
                return np.dot(w.T, np.dot(cov.values, w))
            obj_func = variance
            
        elif objective == "max_return":
            def neg_return(w):
                return -np.dot(w, mean_returns.values)
            obj_func = neg_return
        
        else:
            raise ValueError(f"알 수 없는 목표: {objective}")
        
        constraints = [{"type": "eq", "fun": lambda w: np.sum(w) - 1}]
        
        if allow_short:
            bounds = tuple((-max_weight, max_weight) for _ in range(n))
        else:
            bounds = tuple((min_weight, max_weight) for _ in range(n))
        
        init = np.array([1/n] * n)
        
        result = minimize(
            obj_func,
            init,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
            options={"maxiter": 1000},
        )
        
        if not result.success:
            raise ValueError(f"최적화 실패: {result.message}")
        
        weights = pd.Series(result.x, index=self.symbols)
        
        # 해당 비중으로 분석
        analyzer = PortfolioAnalyzer(
            self.returns,
            weights.to_dict(),
            self.risk_free_rate,
            self.trading_days,
        )
        metrics = analyzer.analyze()
        metrics.optimal_weights = weights
        
        logger.info(f"최적 비중 계산 완료: 샤프={metrics.portfolio_sharpe:.2f}")
        
        return weights, metrics
    
    @classmethod
    def from_prices(
        cls,
        prices: pd.DataFrame,
        weights: Optional[Dict[str, float]] = None,
        risk_free_rate: float = 0.03,
    ) -> "PortfolioAnalyzer":
        """가격 데이터에서 분석기 생성
        
        Args:
            prices: 일별 가격 DataFrame (columns=종목, index=날짜)
            weights: 비중 딕셔너리
            risk_free_rate: 무위험 이자율
        
        Returns:
            PortfolioAnalyzer 인스턴스
        """
        returns = prices.pct_change().dropna()
        return cls(returns, weights, risk_free_rate)
