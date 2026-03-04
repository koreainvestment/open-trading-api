"""포트폴리오 시각화

Docs:
- docs/p2-portfolio-plan.md

상관관계 히트맵, 효율적 프론티어, 리스크 기여도 차트 등.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional

import pandas as pd

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .analyzer import PortfolioMetrics
    from .rebalance import RebalanceResult

# Plotly 임포트 (선택적)
try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False
    logger.warning("plotly가 설치되지 않았습니다. 시각화 기능이 제한됩니다.")


class PortfolioVisualizer:
    """포트폴리오 시각화 클래스
    
    정적 메서드로 다양한 차트 생성 기능 제공.
    
    Example:
        from kis_backtest.portfolio import PortfolioVisualizer
        
        # 상관관계 히트맵
        fig = PortfolioVisualizer.correlation_heatmap(metrics)
        fig.show()
    """
    
    @staticmethod
    def _check_plotly():
        """Plotly 설치 확인"""
        if not HAS_PLOTLY:
            raise ImportError(
                "plotly가 필요합니다. 설치: pip install plotly"
            )
    
    @staticmethod
    def correlation_heatmap(
        metrics: "PortfolioMetrics",
        title: str = "종목간 상관관계",
        width: int = 600,
        height: int = 500,
        colorscale: str = "RdBu",
    ) -> "go.Figure":
        """상관관계 히트맵
        
        Args:
            metrics: PortfolioMetrics 객체
            title: 차트 제목
            width: 차트 너비
            height: 차트 높이
            colorscale: 색상 스케일
        
        Returns:
            Plotly Figure
        """
        PortfolioVisualizer._check_plotly()
        
        corr = metrics.correlation_matrix
        
        fig = go.Figure(data=go.Heatmap(
            z=corr.values,
            x=corr.columns.tolist(),
            y=corr.index.tolist(),
            colorscale=colorscale,
            zmid=0,
            zmin=-1,
            zmax=1,
            text=corr.round(2).values,
            texttemplate="%{text}",
            textfont={"size": 12},
            hovertemplate="종목1: %{y}<br>종목2: %{x}<br>상관계수: %{z:.3f}<extra></extra>",
        ))
        
        fig.update_layout(
            title=dict(text=title, font=dict(size=16)),
            width=width,
            height=height,
            xaxis=dict(title="", tickangle=45),
            yaxis=dict(title=""),
        )
        
        return fig
    
    @staticmethod
    def risk_contribution_pie(
        metrics: "PortfolioMetrics",
        title: str = "리스크 기여도",
        width: int = 500,
        height: int = 400,
    ) -> "go.Figure":
        """리스크 기여도 파이 차트
        
        각 종목이 포트폴리오 전체 리스크에 얼마나 기여하는지 시각화.
        """
        PortfolioVisualizer._check_plotly()
        
        contrib = metrics.risk_contributions
        
        # 음수 값이 있으면 절대값 사용 (공매도 포지션)
        contrib_abs = contrib.abs()
        
        fig = go.Figure(data=[go.Pie(
            labels=contrib.index.tolist(),
            values=contrib_abs.values,
            textinfo="label+percent",
            hovertemplate="종목: %{label}<br>기여도: %{percent}<extra></extra>",
        )])
        
        fig.update_layout(
            title=dict(text=title, font=dict(size=16)),
            width=width,
            height=height,
        )
        
        return fig
    
    @staticmethod
    def weight_bar(
        metrics: "PortfolioMetrics",
        title: str = "포트폴리오 비중",
        width: int = 600,
        height: int = 400,
    ) -> "go.Figure":
        """포트폴리오 비중 막대 차트"""
        PortfolioVisualizer._check_plotly()
        
        weights = metrics.weights
        
        fig = go.Figure(data=[go.Bar(
            x=weights.index.tolist(),
            y=weights.values,
            text=[f"{w:.1%}" for w in weights.values],
            textposition="auto",
        )])
        
        fig.update_layout(
            title=dict(text=title, font=dict(size=16)),
            width=width,
            height=height,
            xaxis=dict(title="종목"),
            yaxis=dict(title="비중", tickformat=".0%"),
        )
        
        return fig
    
    @staticmethod
    def efficient_frontier_plot(
        metrics: "PortfolioMetrics",
        frontier: pd.DataFrame,
        title: str = "효율적 프론티어",
        width: int = 700,
        height: int = 500,
        show_cml: bool = True,
    ) -> "go.Figure":
        """효율적 프론티어 차트
        
        Args:
            metrics: 현재 포트폴리오 분석 결과
            frontier: efficient_frontier() 결과 DataFrame
            title: 차트 제목
            show_cml: 자본시장선(CML) 표시 여부
        """
        PortfolioVisualizer._check_plotly()
        
        fig = go.Figure()
        
        # 효율적 프론티어 라인
        fig.add_trace(go.Scatter(
            x=frontier["volatility"],
            y=frontier["return"],
            mode="lines",
            name="효율적 프론티어",
            line=dict(color="blue", width=2),
            hovertemplate="변동성: %{x:.2%}<br>수익률: %{y:.2%}<extra></extra>",
        ))
        
        # 최대 샤프 포인트
        if len(frontier) > 0:
            max_sharpe_idx = frontier["sharpe"].idxmax()
            max_sharpe = frontier.loc[max_sharpe_idx]
            
            fig.add_trace(go.Scatter(
                x=[max_sharpe["volatility"]],
                y=[max_sharpe["return"]],
                mode="markers",
                name=f"최대 샤프 ({max_sharpe['sharpe']:.2f})",
                marker=dict(size=15, symbol="star", color="gold"),
                hovertemplate=(
                    f"최대 샤프 비율<br>"
                    f"변동성: %{{x:.2%}}<br>"
                    f"수익률: %{{y:.2%}}<extra></extra>"
                ),
            ))
        
        # 개별 종목
        for sym in metrics.volatilities.index:
            ret = float(metrics.returns[sym].mean() * 252)
            vol = float(metrics.volatilities[sym])
            
            fig.add_trace(go.Scatter(
                x=[vol],
                y=[ret],
                mode="markers+text",
                name=sym,
                text=[sym],
                textposition="top center",
                marker=dict(size=10),
                hovertemplate=f"{sym}<br>변동성: %{{x:.2%}}<br>수익률: %{{y:.2%}}<extra></extra>",
            ))
        
        # 현재 포트폴리오
        fig.add_trace(go.Scatter(
            x=[metrics.portfolio_volatility],
            y=[metrics.portfolio_return],
            mode="markers",
            name="현재 포트폴리오",
            marker=dict(size=15, symbol="diamond", color="red"),
            hovertemplate="현재 포트폴리오<br>변동성: %{x:.2%}<br>수익률: %{y:.2%}<extra></extra>",
        ))
        
        fig.update_layout(
            title=dict(text=title, font=dict(size=16)),
            width=width,
            height=height,
            xaxis=dict(title="변동성 (연율)", tickformat=".0%"),
            yaxis=dict(title="기대수익률 (연율)", tickformat=".0%"),
            legend=dict(x=0.02, y=0.98),
        )
        
        return fig
    
    @staticmethod
    def rebalance_comparison(
        result: "RebalanceResult",
        title: str = "리밸런싱 효과 비교",
        width: int = 800,
        height: int = 450,
        show_rebalance_points: bool = True,
    ) -> "go.Figure":
        """리밸런싱 vs Buy & Hold 비교 차트
        
        Args:
            result: RebalanceResult 객체
            title: 차트 제목
            show_rebalance_points: 리밸런싱 시점 표시 여부
        """
        PortfolioVisualizer._check_plotly()
        
        fig = go.Figure()
        
        # 리밸런싱 곡선
        fig.add_trace(go.Scatter(
            x=result.equity_curve.index,
            y=result.equity_curve.values,
            mode="lines",
            name=f"리밸런싱 ({result.final_return:+.2%})",
            line=dict(color="blue", width=2),
        ))
        
        # Buy & Hold 곡선
        fig.add_trace(go.Scatter(
            x=result.no_rebalance_curve.index,
            y=result.no_rebalance_curve.values,
            mode="lines",
            name=f"Buy & Hold ({result.no_rebalance_return:+.2%})",
            line=dict(color="gray", width=2, dash="dash"),
        ))
        
        # 리밸런싱 시점 표시
        if show_rebalance_points and result.rebalance_dates:
            for date in result.rebalance_dates:
                fig.add_vline(
                    x=date,
                    line_dash="dot",
                    line_color="orange",
                    opacity=0.3,
                )
        
        # 리밸런싱 효과 표시 (annotation)
        benefit_text = f"리밸런싱 효과: {result.rebalance_benefit:+.2%}"
        fig.add_annotation(
            x=result.equity_curve.index[-1],
            y=result.equity_curve.iloc[-1],
            text=benefit_text,
            showarrow=True,
            arrowhead=2,
            font=dict(size=12, color="blue"),
        )
        
        fig.update_layout(
            title=dict(
                text=f"{title} (효과: {result.rebalance_benefit:+.2%})",
                font=dict(size=16),
            ),
            width=width,
            height=height,
            xaxis=dict(title="날짜"),
            yaxis=dict(title="포트폴리오 가치", tickformat=","),
            legend=dict(x=0.02, y=0.98),
            hovermode="x unified",
        )
        
        return fig
    
    @staticmethod
    def period_comparison_bar(
        comparison_df: pd.DataFrame,
        title: str = "리밸런싱 주기별 비교",
        width: int = 700,
        height: int = 400,
    ) -> "go.Figure":
        """리밸런싱 주기별 비교 막대 차트
        
        Args:
            comparison_df: RebalanceSimulator.compare_periods() 결과
        """
        PortfolioVisualizer._check_plotly()
        
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=["수익률", "거래비용"],
            specs=[[{"type": "bar"}, {"type": "bar"}]],
        )
        
        # 수익률 비교
        fig.add_trace(
            go.Bar(
                x=comparison_df["period"],
                y=comparison_df["final_return"],
                text=[f"{r:.2%}" for r in comparison_df["final_return"]],
                textposition="auto",
                name="수익률",
                marker_color="steelblue",
            ),
            row=1, col=1,
        )
        
        # 거래비용 비교
        fig.add_trace(
            go.Bar(
                x=comparison_df["period"],
                y=comparison_df["transaction_cost"],
                text=[f"{c:,.0f}" for c in comparison_df["transaction_cost"]],
                textposition="auto",
                name="거래비용",
                marker_color="coral",
            ),
            row=1, col=2,
        )
        
        fig.update_layout(
            title=dict(text=title, font=dict(size=16)),
            width=width,
            height=height,
            showlegend=False,
        )
        
        fig.update_yaxes(tickformat=".0%", row=1, col=1)
        fig.update_yaxes(tickformat=",", row=1, col=2)
        
        return fig
    
    @staticmethod
    def portfolio_dashboard(
        metrics: "PortfolioMetrics",
        frontier: Optional[pd.DataFrame] = None,
        width: int = 1000,
        height: int = 800,
    ) -> "go.Figure":
        """포트폴리오 분석 대시보드 (종합)
        
        4개 차트를 하나의 Figure에 배치:
        - 상관관계 히트맵
        - 비중 막대
        - 리스크 기여도
        - 효율적 프론티어 (옵션)
        """
        PortfolioVisualizer._check_plotly()
        
        if frontier is not None and len(frontier) > 0:
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=[
                    "상관관계 매트릭스",
                    "포트폴리오 비중",
                    "리스크 기여도",
                    "효율적 프론티어",
                ],
                specs=[
                    [{"type": "heatmap"}, {"type": "bar"}],
                    [{"type": "pie"}, {"type": "scatter"}],
                ],
                vertical_spacing=0.12,
                horizontal_spacing=0.08,
            )
        else:
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=[
                    "상관관계 매트릭스",
                    "포트폴리오 비중",
                    "리스크 기여도",
                    "수익률-변동성",
                ],
                specs=[
                    [{"type": "heatmap"}, {"type": "bar"}],
                    [{"type": "pie"}, {"type": "scatter"}],
                ],
                vertical_spacing=0.12,
                horizontal_spacing=0.08,
            )
        
        corr = metrics.correlation_matrix
        weights = metrics.weights
        contrib = metrics.risk_contributions.abs()
        
        # 1. 상관관계 히트맵
        fig.add_trace(
            go.Heatmap(
                z=corr.values,
                x=corr.columns.tolist(),
                y=corr.index.tolist(),
                colorscale="RdBu",
                zmid=0,
                zmin=-1,
                zmax=1,
                text=corr.round(2).values,
                texttemplate="%{text}",
                showscale=False,
            ),
            row=1, col=1,
        )
        
        # 2. 비중 막대
        fig.add_trace(
            go.Bar(
                x=weights.index.tolist(),
                y=weights.values,
                text=[f"{w:.1%}" for w in weights.values],
                textposition="auto",
                marker_color="steelblue",
                showlegend=False,
            ),
            row=1, col=2,
        )
        
        # 3. 리스크 기여도 파이
        fig.add_trace(
            go.Pie(
                labels=contrib.index.tolist(),
                values=contrib.values,
                textinfo="label+percent",
                showlegend=False,
            ),
            row=2, col=1,
        )
        
        # 4. 효율적 프론티어 또는 개별 종목
        if frontier is not None and len(frontier) > 0:
            fig.add_trace(
                go.Scatter(
                    x=frontier["volatility"],
                    y=frontier["return"],
                    mode="lines",
                    name="효율적 프론티어",
                    line=dict(color="blue"),
                    showlegend=False,
                ),
                row=2, col=2,
            )
        
        # 개별 종목 추가
        for sym in metrics.volatilities.index:
            ret = float(metrics.returns[sym].mean() * 252)
            vol = float(metrics.volatilities[sym])
            fig.add_trace(
                go.Scatter(
                    x=[vol],
                    y=[ret],
                    mode="markers+text",
                    text=[sym],
                    textposition="top center",
                    marker=dict(size=8),
                    showlegend=False,
                ),
                row=2, col=2,
            )
        
        # 현재 포트폴리오
        fig.add_trace(
            go.Scatter(
                x=[metrics.portfolio_volatility],
                y=[metrics.portfolio_return],
                mode="markers",
                marker=dict(size=12, symbol="diamond", color="red"),
                name="현재",
                showlegend=False,
            ),
            row=2, col=2,
        )
        
        # 레이아웃 설정
        fig.update_layout(
            title=dict(
                text=f"포트폴리오 분석 대시보드 (샤프: {metrics.portfolio_sharpe:.2f}, 분산비율: {metrics.diversification_ratio:.2f})",
                font=dict(size=18),
            ),
            width=width,
            height=height,
        )
        
        fig.update_yaxes(tickformat=".0%", row=1, col=2)
        fig.update_xaxes(tickformat=".0%", row=2, col=2)
        fig.update_yaxes(tickformat=".0%", row=2, col=2)
        
        return fig
