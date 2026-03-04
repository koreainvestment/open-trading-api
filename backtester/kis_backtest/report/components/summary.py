"""성과 요약 카드 컴포넌트

프론트엔드 UI의 StatCard + MetricsGroup 레이아웃 미러링.
"""

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

if TYPE_CHECKING:
    from ...models.result import BacktestResult
    from ..themes import KISTheme


# SVG 아이콘 (인라인)
_ICONS = {
    "trending_up": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>',
    "percent": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="5" x2="5" y2="19"/><circle cx="6.5" cy="6.5" r="2.5"/><circle cx="17.5" cy="17.5" r="2.5"/></svg>',
    "trending_down": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 18 13.5 8.5 8.5 13.5 1 6"/><polyline points="17 18 23 18 23 12"/></svg>',
    "bar_chart": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="20" x2="12" y2="10"/><line x1="18" y1="20" x2="18" y2="4"/><line x1="6" y1="20" x2="6" y2="16"/></svg>',
    "shield": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
    "activity": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>',
    "zap": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>',
    "target": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>',
    "repeat": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="17 1 21 5 17 9"/><path d="M3 11V9a4 4 0 0 1 4-4h14"/><polyline points="7 23 3 19 7 15"/><path d="M21 13v2a4 4 0 0 1-4 4H3"/></svg>',
    "dollar": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>',
}


def _icon(name: str) -> str:
    return f'<span class="icon">{_ICONS.get(name, "")}</span>'


def _color_class(value: float) -> str:
    if value > 0:
        return "text-profit"
    elif value < 0:
        return "text-loss"
    return ""


def _fmt_pct(value: float) -> str:
    """0.0~1.0 범위 값을 퍼센트 문자열로."""
    return f"{value * 100:+.2f}%"


def _fmt_pct_unsigned(value: float) -> str:
    return f"{value * 100:.2f}%"


def _fmt_ratio(value: float) -> str:
    return f"{value:.2f}"


def _fmt_money(value: float) -> str:
    if abs(value) >= 1e8:
        return f"{value / 1e8:+,.1f}억원"
    if abs(value) >= 1e4:
        return f"{value / 1e4:+,.0f}만원"
    return f"{value:+,.0f}원"


class PerformanceSummaryCard:
    """성과 요약 카드

    상단 4개 StatCard + 하단 6개 MetricsGroup.
    """

    def __init__(self, theme: "KISTheme" = None):
        from ..themes import KISTheme
        self.theme = theme or KISTheme()

    def render(self, result: "BacktestResult") -> str:
        """HTML 렌더링"""
        ext = _get_extended_metrics(result)

        stat_cards = self._render_stat_cards(result, ext)
        metrics_groups = self._render_metrics_groups(result, ext)

        return f"""
        {stat_cards}
        {metrics_groups}
        """

    def _render_stat_cards(self, result: "BacktestResult", ext: Dict[str, Any]) -> str:
        """상단 4개 StatCard 렌더링"""
        ret_color = _color_class(result.total_return_pct)
        cagr_color = _color_class(result.cagr)
        dd_color = "text-loss" if result.max_drawdown > 0 else ""

        cards = [
            {
                "icon": "trending_up",
                "label": "총 수익률",
                "value": _fmt_pct(result.total_return_pct),
                "sub": _fmt_money(result.total_return),
                "color": ret_color,
            },
            {
                "icon": "percent",
                "label": "CAGR",
                "value": _fmt_pct(result.cagr),
                "sub": "연환산 수익률",
                "color": cagr_color,
            },
            {
                "icon": "trending_down",
                "label": "최대 낙폭",
                "value": f"-{_fmt_pct_unsigned(result.max_drawdown)}",
                "sub": ext.get("drawdown_recovery", ""),
                "color": dd_color,
            },
            {
                "icon": "bar_chart",
                "label": "샤프 비율",
                "value": _fmt_ratio(result.sharpe_ratio),
                "sub": "위험 조정 수익률",
                "color": "",
            },
        ]

        html_cards = ""
        for c in cards:
            html_cards += f"""
            <div class="stat-card">
                <div class="stat-label">{_icon(c['icon'])} {c['label']}</div>
                <div class="stat-value {c['color']}">{c['value']}</div>
                <div class="stat-sub">{c['sub']}</div>
            </div>
            """

        return f'<div class="stat-cards">{html_cards}</div>'

    def _render_metrics_groups(self, result: "BacktestResult", ext: Dict[str, Any]) -> str:
        """하단 6개 MetricsGroup 렌더링"""
        groups = [
            {
                "icon": "shield",
                "title": "위험 대비 성과",
                "rows": [
                    ("샤프 비율", _fmt_ratio(result.sharpe_ratio), True, ""),
                    ("소르티노 비율", _fmt_ratio(result.sortino_ratio), False, ""),
                    ("확률적 샤프", ext.get("probabilistic_sharpe", "-"), False, ""),
                ],
            },
            {
                "icon": "activity",
                "title": "시장 민감도",
                "rows": [
                    ("알파", ext.get("alpha", "-"), False, ""),
                    ("베타", ext.get("beta", "-"), False, ""),
                ],
            },
            {
                "icon": "bar_chart",
                "title": "변동성",
                "rows": [
                    ("연간 표준편차", ext.get("annual_std", "-"), False, ""),
                    ("연간 분산", ext.get("annual_variance", "-"), False, ""),
                ],
            },
            {
                "icon": "target",
                "title": "시장 대비 성과",
                "badge": "KOSPI기준",
                "rows": [
                    ("정보 비율", ext.get("information_ratio", "-"), False, ""),
                    ("추적 오차", ext.get("tracking_error", "-"), False, ""),
                    ("트레이너 비율", ext.get("treynor_ratio", "-"), False, ""),
                ],
            },
            {
                "icon": "repeat",
                "title": "매매 리포트",
                "rows": [
                    ("체결 거래", f"{len(result.trades or []):,}건", True, ""),
                    ("승률", _fmt_pct_unsigned(result.win_rate), False, _color_class(result.win_rate - 0.5)),
                    ("평균 수익", ext.get("avg_win", "-"), False, "text-profit" if ext.get("avg_win_raw", 0) > 0 else ""),
                    ("평균 손실", ext.get("avg_loss", "-"), False, "text-loss" if ext.get("avg_loss_raw", 0) < 0 else ""),
                    ("손익비", _fmt_ratio(result.profit_factor) if result.profit_factor else "-", False, ""),
                    ("기대값", ext.get("expectancy", "-"), False, ""),
                ],
            },
            {
                "icon": "dollar",
                "title": "운용 정보 및 비용",
                "rows": [
                    ("총 수수료", ext.get("total_fees", "-"), False, ""),
                    ("회전율", ext.get("turnover", "-"), False, ""),
                    ("낙폭 회복", ext.get("drawdown_recovery", "-"), False, ""),
                ],
            },
        ]

        html_groups = ""
        for g in groups:
            rows_html = ""
            for row in g["rows"]:
                label, value, bold, color = row
                bold_class = " bold" if bold else ""
                color_class = f" {color}" if color else ""
                rows_html += f"""
                <div class="metric-row">
                    <span class="label">{label}</span>
                    <span class="value{bold_class}{color_class}">{value}</span>
                </div>
                """

            badge_html = f'<span class="group-badge">{g["badge"]}</span>' if g.get("badge") else ""
            html_groups += f"""
            <div class="metrics-group">
                <div class="group-title">{_icon(g['icon'])} {g['title']}{badge_html}</div>
                {rows_html}
            </div>
            """

        return f'<div class="metrics-groups">{html_groups}</div>'


def _get_extended_metrics(result: "BacktestResult") -> Dict[str, Any]:
    """raw_statistics에서 확장 지표를 추출."""
    stats = result.raw_statistics or {}
    ext: Dict[str, Any] = {}

    def _parse(key: str, default: float = 0.0) -> float:
        val = stats.get(key)
        if val is None:
            return default
        if isinstance(val, (int, float)):
            return float(val)
        if isinstance(val, str):
            cleaned = val.replace("%", "").replace("$", "").replace(",", "").strip()
            try:
                return float(cleaned) if cleaned else default
            except ValueError:
                return default
        return default

    # Alpha / Beta
    alpha = _parse("Alpha")
    beta = _parse("Beta")
    ext["alpha"] = f"{alpha:.3f}" if alpha != 0 else "-"
    ext["beta"] = f"{beta:.3f}" if beta != 0 else "-"

    # Volatility
    annual_std = _parse("Annual Standard Deviation")
    annual_var = _parse("Annual Variance")
    ext["annual_std"] = f"{annual_std:.4f}" if annual_std != 0 else "-"
    ext["annual_variance"] = f"{annual_var:.4f}" if annual_var != 0 else "-"

    # Benchmark
    info_ratio = _parse("Information Ratio")
    tracking_err = _parse("Tracking Error")
    treynor = _parse("Treynor Ratio")
    ext["information_ratio"] = f"{info_ratio:.3f}" if info_ratio != 0 else "-"
    ext["tracking_error"] = f"{tracking_err:.4f}" if tracking_err != 0 else "-"
    ext["treynor_ratio"] = f"{treynor:.3f}" if treynor != 0 else "-"

    # Probabilistic Sharpe
    prob_sharpe = _parse("Probabilistic Sharpe Ratio")
    ext["probabilistic_sharpe"] = f"{prob_sharpe:.1f}%" if prob_sharpe != 0 else "-"

    # Trade stats
    win_rate = result.win_rate
    loss_rate = 1.0 - win_rate if win_rate > 0 else 0.0

    avg_win = result.average_win
    avg_loss = result.average_loss
    ext["avg_win_raw"] = avg_win
    ext["avg_loss_raw"] = avg_loss
    ext["avg_win"] = f"{avg_win:+.2f}%" if avg_win != 0 else "-"
    ext["avg_loss"] = f"{avg_loss:+.2f}%" if avg_loss != 0 else "-"

    # Expectancy
    if result.win_rate > 0 and (avg_win != 0 or avg_loss != 0):
        expectancy = (win_rate * avg_win) + (loss_rate * avg_loss)
        ext["expectancy"] = f"{expectancy:+.2f}%"
    else:
        ext["expectancy"] = "-"

    # Fees / Turnover
    total_fees = _parse("Total Fees")
    ext["total_fees"] = f"₩{total_fees:,.0f}" if total_fees != 0 else "-"

    # Drawdown recovery
    dr = _parse("Drawdown Recovery")
    ext["drawdown_recovery"] = f"{int(dr)}일" if dr else "-"

    # Turnover
    tu = _parse("Portfolio Turnover")
    ext["turnover"] = f"{tu:.1f}%" if tu else "-"

    return ext
