"""포트폴리오 분석 리포트 생성기

Docs:
- docs/p2-portfolio-plan.md

포트폴리오 분석 결과를 HTML 리포트로 생성.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from ..portfolio import PortfolioMetrics, RebalanceResult

logger = logging.getLogger(__name__)

# Plotly 임포트
try:
    import plotly.graph_objects as go
    import plotly.io as pio
    from plotly.subplots import make_subplots
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False


class PortfolioReportGenerator:
    """포트폴리오 분석 리포트 생성기
    
    Example:
        from kis_backtest.report import PortfolioReportGenerator
        
        generator = PortfolioReportGenerator()
        generator.generate(
            metrics=portfolio_metrics,
            frontier=frontier_df,
            rebalance_result=rebalance_result,
            output_path="portfolio_report.html",
        )
    """
    
    def __init__(self):
        """리포트 생성기 초기화"""
        if not HAS_PLOTLY:
            raise ImportError("plotly가 필요합니다: pip install plotly")
    
    def generate(
        self,
        metrics: "PortfolioMetrics",
        output_path: Union[str, Path],
        title: str = "포트폴리오 분석 리포트",
        frontier: Optional["pd.DataFrame"] = None,
        rebalance_result: Optional["RebalanceResult"] = None,
        symbol_names: Optional[Dict[str, str]] = None,
    ) -> Path:
        """리포트 생성
        
        Args:
            metrics: PortfolioMetrics 분석 결과
            output_path: 출력 파일 경로
            title: 리포트 제목
            frontier: 효율적 프론티어 DataFrame (옵션)
            rebalance_result: 리밸런싱 시뮬레이션 결과 (옵션)
            symbol_names: 종목코드 → 종목명 매핑 (옵션)
        
        Returns:
            생성된 파일 경로
        """
        import pandas as pd
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"포트폴리오 리포트 생성 시작: {output_path}")
        
        # 종목명 매핑
        if symbol_names is None:
            symbol_names = {s: s for s in metrics.weights.index}
        
        # HTML 컨텐츠 생성
        html_parts = []
        
        # 1. 헤더
        html_parts.append(self._generate_header(title))
        
        # 2. 요약 카드
        html_parts.append(self._generate_summary_card(metrics))
        
        # 3. 상관관계 히트맵
        html_parts.append(self._generate_correlation_section(metrics, symbol_names))
        
        # 4. 비중 & 리스크 기여도
        html_parts.append(self._generate_weights_section(metrics, symbol_names))
        
        # 5. 효율적 프론티어 (옵션)
        if frontier is not None and len(frontier) > 0:
            html_parts.append(self._generate_frontier_section(metrics, frontier, symbol_names))
        
        # 6. 리밸런싱 분석 (옵션)
        if rebalance_result is not None:
            html_parts.append(self._generate_rebalance_section(rebalance_result))
        
        # 7. 상세 테이블
        html_parts.append(self._generate_detail_tables(metrics, symbol_names))
        
        # 8. 푸터
        html_parts.append(self._generate_footer())
        
        # HTML 조합
        full_html = self._wrap_html(title, "\n".join(html_parts))
        
        # 파일 저장
        output_path.write_text(full_html, encoding="utf-8")
        logger.info(f"포트폴리오 리포트 생성 완료: {output_path}")
        
        return output_path
    
    def _generate_header(self, title: str) -> str:
        """헤더 HTML 생성"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        return f"""
        <header class="report-header">
            <h1>{title}</h1>
            <p class="report-date">생성일시: {now}</p>
        </header>
        """
    
    def _generate_summary_card(self, metrics: "PortfolioMetrics") -> str:
        """요약 카드 HTML 생성"""
        # 분산 효과 해석
        if metrics.diversification_ratio > 1.2:
            div_status = "🟢 우수"
            div_comment = f"분산 투자로 위험이 {(metrics.diversification_ratio - 1) * 100:.1f}% 감소"
        elif metrics.diversification_ratio > 1.0:
            div_status = "🟡 보통"
            div_comment = "약간의 분산 효과가 있습니다"
        else:
            div_status = "🔴 미흡"
            div_comment = "분산 효과가 없거나 음의 상관관계입니다"
        
        return f"""
        <section class="summary-section">
            <h2>📊 포트폴리오 요약</h2>
            <div class="summary-cards">
                <div class="card">
                    <div class="card-label">기대 수익률 (연율)</div>
                    <div class="card-value {'positive' if metrics.portfolio_return > 0 else 'negative'}">
                        {metrics.portfolio_return:+.2%}
                    </div>
                </div>
                <div class="card">
                    <div class="card-label">변동성 (연율)</div>
                    <div class="card-value">{metrics.portfolio_volatility:.2%}</div>
                </div>
                <div class="card">
                    <div class="card-label">샤프 비율</div>
                    <div class="card-value {'positive' if metrics.portfolio_sharpe > 0 else 'negative'}">
                        {metrics.portfolio_sharpe:.2f}
                    </div>
                </div>
                <div class="card highlight">
                    <div class="card-label">분산 비율</div>
                    <div class="card-value">{metrics.diversification_ratio:.2f}</div>
                    <div class="card-status">{div_status}</div>
                    <div class="card-comment">{div_comment}</div>
                </div>
            </div>
        </section>
        """
    
    def _generate_correlation_section(
        self,
        metrics: "PortfolioMetrics",
        symbol_names: Dict[str, str],
    ) -> str:
        """상관관계 히트맵 섹션"""
        from ..portfolio import PortfolioVisualizer
        
        fig = PortfolioVisualizer.correlation_heatmap(
            metrics,
            title="종목간 상관관계 매트릭스",
            width=600,
            height=500,
        )
        
        chart_html = pio.to_html(fig, full_html=False, include_plotlyjs=False)
        
        # 상관관계 해석
        corr = metrics.correlation_matrix
        avg_corr = corr.values[~np.eye(len(corr), dtype=bool)].mean()
        
        if avg_corr < 0.3:
            corr_comment = "🟢 상관관계가 낮아 분산 효과가 좋습니다"
        elif avg_corr < 0.6:
            corr_comment = "🟡 적당한 상관관계입니다"
        else:
            corr_comment = "🔴 상관관계가 높아 분산 효과가 제한적입니다"
        
        return f"""
        <section class="chart-section">
            <h2>🔗 상관관계 분석</h2>
            <p class="section-comment">{corr_comment} (평균 상관계수: {avg_corr:.2f})</p>
            <div class="chart-container">
                {chart_html}
            </div>
        </section>
        """
    
    def _generate_weights_section(
        self,
        metrics: "PortfolioMetrics",
        symbol_names: Dict[str, str],
    ) -> str:
        """비중 및 리스크 기여도 섹션"""
        from ..portfolio import PortfolioVisualizer
        
        # 비중 차트
        fig1 = PortfolioVisualizer.weight_bar(metrics, title="포트폴리오 비중")
        chart1_html = pio.to_html(fig1, full_html=False, include_plotlyjs=False)
        
        # 리스크 기여도 차트
        fig2 = PortfolioVisualizer.risk_contribution_pie(metrics, title="리스크 기여도")
        chart2_html = pio.to_html(fig2, full_html=False, include_plotlyjs=False)
        
        return f"""
        <section class="chart-section">
            <h2>⚖️ 비중 및 리스크 기여도</h2>
            <div class="chart-row">
                <div class="chart-container half">
                    {chart1_html}
                </div>
                <div class="chart-container half">
                    {chart2_html}
                </div>
            </div>
        </section>
        """
    
    def _generate_frontier_section(
        self,
        metrics: "PortfolioMetrics",
        frontier: "pd.DataFrame",
        symbol_names: Dict[str, str],
    ) -> str:
        """효율적 프론티어 섹션"""
        from ..portfolio import PortfolioVisualizer
        
        fig = PortfolioVisualizer.efficient_frontier_plot(
            metrics,
            frontier,
            title="효율적 프론티어",
        )
        chart_html = pio.to_html(fig, full_html=False, include_plotlyjs=False)
        
        # 최대 샤프 포인트 정보
        if len(frontier) > 0:
            max_idx = frontier["sharpe"].idxmax()
            max_sharpe = frontier.loc[max_idx]
            
            weights_str = ", ".join([
                f"{symbol_names.get(s, s)}: {max_sharpe.get(f'weight_{s}', 0):.1%}"
                for s in metrics.weights.index
            ])
            
            optimal_info = f"""
            <div class="optimal-info">
                <h4>🌟 최적 포트폴리오 (최대 샤프)</h4>
                <p>기대 수익률: {max_sharpe['return']:.2%} | 변동성: {max_sharpe['volatility']:.2%} | 샤프: {max_sharpe['sharpe']:.2f}</p>
                <p>최적 비중: {weights_str}</p>
            </div>
            """
        else:
            optimal_info = ""
        
        return f"""
        <section class="chart-section">
            <h2>📈 효율적 프론티어</h2>
            {optimal_info}
            <div class="chart-container">
                {chart_html}
            </div>
        </section>
        """
    
    def _generate_rebalance_section(self, result: "RebalanceResult") -> str:
        """리밸런싱 분석 섹션"""
        from ..portfolio import PortfolioVisualizer
        
        fig = PortfolioVisualizer.rebalance_comparison(
            result,
            title="리밸런싱 효과 비교",
        )
        chart_html = pio.to_html(fig, full_html=False, include_plotlyjs=False)
        
        # 효과 해석
        if result.rebalance_benefit > 0.01:
            benefit_status = "🟢 리밸런싱이 효과적입니다"
        elif result.rebalance_benefit > -0.01:
            benefit_status = "🟡 리밸런싱 효과가 미미합니다"
        else:
            benefit_status = "🔴 리밸런싱이 오히려 손해입니다"
        
        return f"""
        <section class="chart-section">
            <h2>🔄 리밸런싱 분석</h2>
            <div class="rebalance-summary">
                <p class="benefit-status">{benefit_status}</p>
                <div class="rebalance-stats">
                    <span>리밸런싱 수익률: <strong>{result.final_return:+.2%}</strong></span>
                    <span>Buy & Hold: <strong>{result.no_rebalance_return:+.2%}</strong></span>
                    <span>효과: <strong class="{'positive' if result.rebalance_benefit > 0 else 'negative'}">{result.rebalance_benefit:+.2%}</strong></span>
                    <span>리밸런싱 횟수: <strong>{result.rebalance_count}회</strong></span>
                    <span>총 회전율: <strong>{result.turnover:.1%}</strong></span>
                    <span>거래비용: <strong>₩{result.transaction_cost:,.0f}</strong></span>
                </div>
            </div>
            <div class="chart-container">
                {chart_html}
            </div>
        </section>
        """
    
    def _generate_detail_tables(
        self,
        metrics: "PortfolioMetrics",
        symbol_names: Dict[str, str],
    ) -> str:
        """상세 테이블 섹션"""
        # 개별 종목 통계
        rows = []
        for symbol in metrics.weights.index:
            name = symbol_names.get(symbol, symbol)
            weight = metrics.weights[symbol]
            vol = metrics.volatilities[symbol]
            ret = float(metrics.returns[symbol].mean() * 252)
            risk_contrib = metrics.risk_contributions[symbol]
            
            rows.append(f"""
                <tr>
                    <td>{name}</td>
                    <td>{symbol}</td>
                    <td>{weight:.1%}</td>
                    <td class="{'positive' if ret > 0 else 'negative'}">{ret:+.2%}</td>
                    <td>{vol:.2%}</td>
                    <td>{risk_contrib:.2%}</td>
                </tr>
            """)
        
        return f"""
        <section class="table-section">
            <h2>📋 개별 종목 상세</h2>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>종목명</th>
                        <th>코드</th>
                        <th>비중</th>
                        <th>기대수익률</th>
                        <th>변동성</th>
                        <th>리스크기여</th>
                    </tr>
                </thead>
                <tbody>
                    {"".join(rows)}
                </tbody>
            </table>
        </section>
        """
    
    def _generate_footer(self) -> str:
        """푸터 HTML 생성"""
        return """
        <footer class="report-footer">
            <p>본 리포트는 과거 데이터를 기반으로 분석한 결과이며, 미래 수익을 보장하지 않습니다.</p>
            <p>kis_backtest로 생성됨</p>
        </footer>
        """
    
    def _wrap_html(self, title: str, content: str) -> str:
        """전체 HTML 래핑"""
        return f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        {self._get_css()}
    </style>
</head>
<body>
    <div class="container">
        {content}
    </div>
</body>
</html>"""
    
    def _get_css(self) -> str:
        """CSS 스타일"""
        return """
        :root {
            --primary: #245BEE;
            --secondary: #1A47B8;
            --accent: #4A7AFF;
            --success: #38a169;
            --danger: #e53e3e;
            --warning: #d69e2e;
            --bg: #f7fafc;
            --card-bg: #ffffff;
            --text: #2d3748;
            --text-light: #718096;
            --border: #e2e8f0;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        .report-header {
            text-align: center;
            padding: 2rem;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
            border-radius: 12px;
            margin-bottom: 2rem;
        }
        
        .report-header h1 {
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }
        
        .report-date {
            opacity: 0.8;
        }
        
        section {
            background: var(--card-bg);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        section h2 {
            color: var(--primary);
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid var(--border);
        }
        
        .summary-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
        }
        
        .card {
            background: var(--bg);
            border-radius: 8px;
            padding: 1.5rem;
            text-align: center;
        }
        
        .card.highlight {
            background: linear-gradient(135deg, #ebf8ff, #bee3f8);
            border: 2px solid var(--accent);
        }
        
        .card-label {
            font-size: 0.875rem;
            color: var(--text-light);
            margin-bottom: 0.5rem;
        }
        
        .card-value {
            font-size: 1.75rem;
            font-weight: 700;
        }
        
        .card-value.positive { color: var(--success); }
        .card-value.negative { color: var(--danger); }
        
        .card-status {
            font-size: 0.875rem;
            margin-top: 0.5rem;
        }
        
        .card-comment {
            font-size: 0.75rem;
            color: var(--text-light);
            margin-top: 0.25rem;
        }
        
        .section-comment {
            color: var(--text-light);
            margin-bottom: 1rem;
        }
        
        .chart-container {
            width: 100%;
            overflow-x: auto;
        }
        
        .chart-row {
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
        }
        
        .chart-container.half {
            flex: 1;
            min-width: 300px;
        }
        
        .optimal-info {
            background: linear-gradient(135deg, #faf5ff, #e9d8fd);
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 1rem;
        }
        
        .optimal-info h4 {
            color: #553c9a;
            margin-bottom: 0.5rem;
        }
        
        .rebalance-summary {
            margin-bottom: 1rem;
        }
        
        .benefit-status {
            font-size: 1.25rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }
        
        .rebalance-stats {
            display: flex;
            flex-wrap: wrap;
            gap: 1.5rem;
        }
        
        .rebalance-stats span {
            color: var(--text-light);
        }
        
        .rebalance-stats strong {
            color: var(--text);
        }
        
        .rebalance-stats strong.positive { color: var(--success); }
        .rebalance-stats strong.negative { color: var(--danger); }
        
        .data-table {
            width: 100%;
            border-collapse: collapse;
        }
        
        .data-table th,
        .data-table td {
            padding: 0.75rem;
            text-align: right;
            border-bottom: 1px solid var(--border);
        }
        
        .data-table th {
            background: var(--bg);
            font-weight: 600;
            color: var(--text-light);
        }
        
        .data-table td:first-child,
        .data-table th:first-child {
            text-align: left;
        }
        
        .data-table td.positive { color: var(--success); }
        .data-table td.negative { color: var(--danger); }
        
        .report-footer {
            text-align: center;
            padding: 2rem;
            color: var(--text-light);
            font-size: 0.875rem;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 1rem;
            }
            
            .summary-cards {
                grid-template-columns: 1fr 1fr;
            }
            
            .chart-row {
                flex-direction: column;
            }
        }
        
        @media print {
            body {
                background: white;
            }
            
            .container {
                max-width: none;
            }
            
            section {
                page-break-inside: avoid;
            }
        }
        """


# numpy 임포트 (상관관계 계산용)
import numpy as np
