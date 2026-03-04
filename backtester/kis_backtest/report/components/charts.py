"""차트 컴포넌트

Plotly 기반 인터랙티브 차트. 프론트엔드 UI 색상 매칭.
"""

from typing import TYPE_CHECKING, Dict, List, Optional, Union
import pandas as pd

if TYPE_CHECKING:
    from ...models.result import BacktestResult
    from ..themes import KISTheme

# 프론트엔드 UI 색상
CHART_COLORS = {
    "strategy": "#245bee",
    "benchmark": "#f59e0b",
    "buy": "#22c55e",
    "sell": "#ef4444",
    "drawdown": "#ef4444",
    "grid": "#e2e8f0",
    "reference": "#94a3b8",
}


class EquityCurveChart:
    """자산 곡선 차트 (드로다운 서브차트 포함)"""

    def __init__(self, theme: "KISTheme" = None):
        from ..themes import KISTheme
        self.theme = theme or KISTheme()

    def render(
        self,
        result: "BacktestResult",
        benchmark: Optional[pd.Series] = None
    ) -> str:
        """Plotly 차트 HTML (2-row subplot: 자산곡선 + 드로다운)"""
        try:
            import plotly.graph_objects as go
            from plotly.subplots import make_subplots
        except ImportError:
            return "<p>Plotly가 필요합니다: pip install plotly</p>"

        if result.equity_curve is None:
            return '<div class="card"><p class="empty-state">자산 곡선 데이터 없음</p></div>'

        equity = result.equity_curve
        equity_values = equity.values
        initial_cash = equity_values[0] if len(equity_values) > 0 else 0

        # numpy → Python list 변환 (bdata 직렬화 방지)
        equity_list = equity_values.tolist()
        equity_dates = [d.isoformat() for d in equity.index]

        # Y축 범위 계산
        y_min = equity_values.min() * 0.95
        y_max = equity_values.max() * 1.05

        # 드로다운 계산
        running_max = equity.cummax()
        drawdown = (equity - running_max) / running_max
        drawdown_pct_list = (drawdown.values * 100).tolist()
        drawdown_dates = [d.isoformat() for d in drawdown.index]

        # 2-row subplot
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            row_heights=[0.75, 0.25],
            vertical_spacing=0.03,
        )

        # --- Row 1: 자산 곡선 ---
        # 베이스라인 (fill 기준선, y_min 값)
        fig.add_trace(go.Scatter(
            x=equity_dates,
            y=[y_min] * len(equity),
            mode='lines',
            line=dict(width=0),
            showlegend=False,
            hoverinfo='skip',
        ), row=1, col=1)

        # 자산곡선 (tonexty: 베이스라인까지만 채움)
        fig.add_trace(go.Scatter(
            x=equity_dates,
            y=equity_list,
            name="전략",
            line=dict(color=CHART_COLORS["strategy"], width=2),
            fill='tonexty',
            fillcolor="rgba(36, 94, 238, 0.08)",
            mode='lines',
        ), row=1, col=1)

        # 초기자본 기준선
        fig.add_trace(go.Scatter(
            x=[equity.index[0], equity.index[-1]],
            y=[initial_cash, initial_cash],
            name="초기자본",
            line=dict(color=CHART_COLORS["reference"], width=1, dash='dash'),
            mode='lines',
            showlegend=False,
        ), row=1, col=1)

        # 벤치마크
        benchmark_curve = self._get_benchmark(result, benchmark, initial_cash)
        if benchmark_curve is not None:
            fig.add_trace(go.Scatter(
                x=[d.isoformat() for d in benchmark_curve.index],
                y=benchmark_curve.values.tolist(),
                name="KOSPI",
                line=dict(color=CHART_COLORS["benchmark"], width=1.5, dash='dash'),
                mode='lines',
            ), row=1, col=1)

        # 매수/매도 마커
        self._add_trade_markers(fig, result, equity)

        # --- Row 2: 드로다운 ---
        # 드로다운 베이스라인 (0% 기준)
        fig.add_trace(go.Scatter(
            x=drawdown_dates,
            y=[0] * len(drawdown),
            mode='lines',
            line=dict(width=0),
            showlegend=False,
            hoverinfo='skip',
        ), row=2, col=1)

        fig.add_trace(go.Scatter(
            x=drawdown_dates,
            y=drawdown_pct_list,
            name="낙폭",
            line=dict(color=CHART_COLORS["drawdown"], width=1),
            fill='tonexty',
            fillcolor="rgba(239, 68, 68, 0.15)",
            showlegend=False,
        ), row=2, col=1)

        # 레이아웃
        fig.update_layout(
            height=500,
            margin=dict(l=60, r=20, t=10, b=30),
            xaxis2=dict(gridcolor=CHART_COLORS["grid"], showgrid=True),
            yaxis=dict(
                title="자산가치",
                gridcolor=CHART_COLORS["grid"],
                showgrid=True,
                tickformat=",d",
                range=[y_min, y_max],
            ),
            yaxis2=dict(
                title="낙폭 (%)",
                gridcolor=CHART_COLORS["grid"],
                showgrid=True,
                ticksuffix="%",
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(size=11),
            ),
            hovermode='x unified',
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(family="Pretendard, sans-serif", size=11),
        )

        chart_html = fig.to_html(include_plotlyjs=False, full_html=False)

        # 카드 래퍼 + 커스텀 레전드
        legend_items = [
            f'<span class="legend-item"><span class="legend-line" style="background:{CHART_COLORS["strategy"]}"></span> 전략</span>',
        ]
        if benchmark_curve is not None:
            legend_items.append(
                f'<span class="legend-item"><span class="legend-line" style="background:{CHART_COLORS["benchmark"]}"></span> KOSPI</span>'
            )
        has_markers = bool(result.orders or result.trades)
        if has_markers:
            legend_items.extend([
                f'<span class="legend-item"><span class="legend-dot" style="background:{CHART_COLORS["buy"]}"></span> 매수</span>',
                f'<span class="legend-item"><span class="legend-dot" style="background:{CHART_COLORS["sell"]}"></span> 매도</span>',
            ])

        return f"""
        <div class="card">
            <div class="chart-header">
                <h3>자산 추이</h3>
                <div class="chart-legend">{''.join(legend_items)}</div>
            </div>
            {chart_html}
        </div>
        """

    def _get_benchmark(
        self,
        result: "BacktestResult",
        benchmark: Optional[pd.Series],
        initial_cash: float,
    ) -> Optional[pd.Series]:
        """벤치마크 데이터 처리 (수익률 % → 절대값 변환)

        benchmark_curve 형식: {"2025-01-02": 0.0, "2025-01-03": 1.5, ...}
        값은 시작일 대비 수익률 % (0.0 = 0%, 1.5 = 1.5%)
        """
        if benchmark is not None:
            return benchmark

        # result에 benchmark_curve가 있는 경우
        bm = getattr(result, "benchmark_curve", None)
        if bm is None:
            return None

        if isinstance(bm, dict):
            if not bm:
                return None
            bm_series = pd.Series(bm, dtype=float)
            bm_series.index = pd.to_datetime(bm_series.index)
            bm_series = bm_series.sort_index()
        elif isinstance(bm, pd.Series):
            bm_series = bm
        else:
            return None

        if bm_series.empty:
            return None

        # 수익률 % → 절대값 변환 (프론트엔드와 동일: initialCash * (1 + pct/100))
        # 값이 이미 절대 자산가치(>10000)인 경우 변환 불필요
        if abs(bm_series.iloc[0]) < 1000:
            bm_series = initial_cash * (1 + bm_series / 100)

        return bm_series

    def _add_trade_markers(
        self,
        fig,
        result: "BacktestResult",
        equity: pd.Series,
    ) -> None:
        """매수/매도 마커 추가 (Order 객체 또는 Dict 지원)"""
        import plotly.graph_objects as go

        trades_data = result.orders if result.orders else result.trades
        if not trades_data:
            return

        buy_dates, buy_values, buy_texts = [], [], []
        sell_dates, sell_values, sell_texts = [], [], []

        equity_index = equity.index
        equity_values = equity.values

        for trade in trades_data:
            info = self._parse_trade(trade)
            if info is None:
                continue

            trade_date, symbol, side, price, qty = info

            # 가장 가까운 날짜의 자산값 찾기
            try:
                if hasattr(trade_date, 'tzinfo') and trade_date.tzinfo is not None:
                    trade_date = trade_date.replace(tzinfo=None)

                if trade_date in equity_index:
                    eq_val = equity.loc[trade_date]
                else:
                    idx = equity_index.get_indexer([trade_date], method='nearest')[0]
                    eq_val = equity_values[idx]
            except Exception:
                continue

            text = f"{symbol}<br>{qty:,}주<br>{price:,.0f}원"

            if side == "buy":
                buy_dates.append(trade_date)
                buy_values.append(eq_val)
                buy_texts.append(text)
            else:
                sell_dates.append(trade_date)
                sell_values.append(eq_val)
                sell_texts.append(text)

        if buy_dates:
            fig.add_trace(go.Scatter(
                x=buy_dates,
                y=buy_values,
                mode='markers',
                name='매수',
                marker=dict(
                    symbol='triangle-up',
                    size=10,
                    color=CHART_COLORS["buy"],
                    line=dict(width=1, color='white'),
                ),
                text=buy_texts,
                hovertemplate='<b>매수</b><br>%{text}<extra></extra>',
                showlegend=False,
            ), row=1, col=1)

        if sell_dates:
            fig.add_trace(go.Scatter(
                x=sell_dates,
                y=sell_values,
                mode='markers',
                name='매도',
                marker=dict(
                    symbol='triangle-down',
                    size=10,
                    color=CHART_COLORS["sell"],
                    line=dict(width=1, color='white'),
                ),
                text=sell_texts,
                hovertemplate='<b>매도</b><br>%{text}<extra></extra>',
                showlegend=False,
            ), row=1, col=1)

    def _parse_trade(self, trade) -> Optional[tuple]:
        """Order 객체 또는 Dict에서 거래 정보 파싱"""
        from datetime import datetime

        if isinstance(trade, dict):
            # Dict 키 매핑
            trade_date = trade.get("time") or trade.get("datetime") or trade.get("date")

            # symbol: nested dict {'value': '005930'} 또는 문자열
            raw_symbol = trade.get("symbol", "")
            symbol = raw_symbol.get("value", str(raw_symbol)) if isinstance(raw_symbol, dict) else str(raw_symbol)

            # direction: Lean int (0=buy, 1=sell) 또는 문자열
            raw_dir = trade.get("direction") if trade.get("direction") is not None else trade.get("side", "")
            if isinstance(raw_dir, int):
                side = "buy" if raw_dir == 0 else "sell"
            else:
                side = str(raw_dir).lower()

            price = float(trade.get("price", 0))
            qty = int(float(trade.get("quantity", 0)))

            if isinstance(trade_date, str):
                for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%Y%m%d"):
                    try:
                        trade_date = datetime.strptime(trade_date, fmt)
                        break
                    except ValueError:
                        continue

            if side in ("buy", "매수", "long", "0"):
                side = "buy"
            elif side not in ("buy", "sell"):
                side = "sell"

            return (trade_date, symbol, side, price, qty) if trade_date else None

        # Order 객체
        try:
            return (
                trade.created_at,
                trade.symbol,
                trade.side.value,
                trade.average_price,
                trade.quantity,
            )
        except AttributeError:
            return None


class MonthlyReturnsHeatmap:
    """월별 수익률 히트맵"""

    def __init__(self, theme: "KISTheme" = None):
        from ..themes import KISTheme
        self.theme = theme or KISTheme()

    def render(self, result: "BacktestResult") -> str:
        """Plotly 히트맵 HTML 생성"""
        try:
            import plotly.graph_objects as go
        except ImportError:
            return "<p>Plotly가 필요합니다: pip install plotly</p>"

        if result.equity_curve is None:
            return '<div class="card"><p class="empty-state">자산 곡선 데이터 없음</p></div>'

        # 월별 수익률 계산
        monthly = result.equity_curve.resample('ME').last().pct_change()

        # 피벗 테이블 생성
        try:
            monthly_df = pd.DataFrame(monthly)
            monthly_df['year'] = monthly_df.index.year
            monthly_df['month'] = monthly_df.index.month
            monthly_df.columns = ['return', 'year', 'month']

            pivot = monthly_df.pivot(index='year', columns='month', values='return')
        except Exception:
            return '<div class="card"><p class="empty-state">월별 수익률 계산 실패</p></div>'

        # 12개월 전체로 리인덱스 (NaN으로 채움)
        pivot = pivot.reindex(columns=range(1, 13))

        month_labels = ['1월', '2월', '3월', '4월', '5월', '6월',
                        '7월', '8월', '9월', '10월', '11월', '12월']
        year_labels = [str(y) for y in pivot.index.tolist()]

        # z: NaN → None (Plotly 호환)
        z_data = []
        text_data = []
        for row in pivot.values:
            z_row = []
            t_row = []
            for v in row:
                if pd.notna(v):
                    z_row.append(round(v * 100, 2))
                    t_row.append(f"{v*100:.1f}%")
                else:
                    z_row.append(None)
                    t_row.append("")
            z_data.append(z_row)
            text_data.append(t_row)

        # 한국식 색상: 상승=빨강, 하락=파랑
        colorscale = [
            [0, "#3b82f6"],
            [0.5, "#ffffff"],
            [1, "#ef4444"],
        ]

        fig = go.Figure(data=go.Heatmap(
            z=z_data,
            x=month_labels,
            y=year_labels,
            colorscale=colorscale,
            zmid=0,
            text=text_data,
            texttemplate="%{text}",
            textfont={"size": 11},
            hoverongaps=False,
            showscale=True,
            colorbar=dict(title="수익률 (%)"),
        ))

        fig.update_layout(
            height=max(150, 60 * len(year_labels) + 80),
            margin=dict(l=60, r=20, t=10, b=30),
            xaxis=dict(type='category', title=""),
            yaxis=dict(type='category', title="", autorange='reversed'),
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(family="Pretendard, sans-serif", size=11),
        )

        chart_html = fig.to_html(include_plotlyjs=False, full_html=False)

        return f"""
        <div class="card">
            <div class="chart-header">
                <h3>월별 수익률</h3>
            </div>
            {chart_html}
        </div>
        """


class DrawdownChart:
    """낙폭 차트 (독립 사용 시)"""

    def __init__(self, theme: "KISTheme" = None):
        from ..themes import KISTheme
        self.theme = theme or KISTheme()

    def render(self, result: "BacktestResult") -> str:
        """Plotly 낙폭 차트 HTML 생성"""
        try:
            import plotly.graph_objects as go
        except ImportError:
            return "<p>Plotly가 필요합니다: pip install plotly</p>"

        if result.equity_curve is None:
            return '<div class="card"><p class="empty-state">자산 곡선 데이터 없음</p></div>'

        equity = result.equity_curve
        running_max = equity.cummax()
        drawdown = (equity - running_max) / running_max

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=[d.isoformat() for d in drawdown.index],
            y=(drawdown.values * 100).tolist(),
            name="낙폭",
            line=dict(color=CHART_COLORS["drawdown"], width=1),
            fill='tozeroy',
            fillcolor="rgba(239, 68, 68, 0.12)",
        ))

        fig.update_layout(
            height=200,
            margin=dict(l=60, r=20, t=10, b=30),
            xaxis=dict(gridcolor=CHART_COLORS["grid"]),
            yaxis=dict(
                title="낙폭 (%)",
                gridcolor=CHART_COLORS["grid"],
                ticksuffix="%",
            ),
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(family="Pretendard, sans-serif", size=11),
        )

        chart_html = fig.to_html(include_plotlyjs=False, full_html=False)

        return f"""
        <div class="card">
            <div class="chart-header">
                <h3>낙폭 (Drawdown)</h3>
            </div>
            {chart_html}
        </div>
        """
