"""리포트 생성기

프론트엔드 UI 스타일의 standalone HTML 리포트 생성.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union

from ..models.result import BacktestResult
from .themes import KISTheme, BaseTheme
from .components import (
    PerformanceSummaryCard,
    EquityCurveChart,
    MonthlyReturnsHeatmap,
    DrawdownChart,
    TradesTable,
)

logger = logging.getLogger(__name__)


class KISReportGenerator:
    """HTML 리포트 생성기 (프론트엔드 UI 스타일)"""

    def __init__(
        self,
        theme: Optional[BaseTheme] = None,
        renderer: str = "plotly"
    ):
        self.theme = theme or KISTheme()
        self.renderer = renderer

        self.components: Dict[str, object] = {
            'summary': PerformanceSummaryCard(self.theme),
            'equity_curve': EquityCurveChart(self.theme),
            'monthly_heatmap': MonthlyReturnsHeatmap(self.theme),
            'drawdown': DrawdownChart(self.theme),
            'trades': TradesTable(self.theme),
        }

    def generate(
        self,
        result: BacktestResult,
        output_path: Union[str, Path],
        title: str = "백테스트 리포트",
        subtitle: Optional[str] = None,
        include_components: Optional[List[str]] = None,
        benchmark=None
    ) -> Path:
        """리포트 생성

        Args:
            result: 백테스트 결과
            output_path: 출력 파일 경로
            title: 리포트 제목
            subtitle: 부제목
            include_components: 포함할 컴포넌트 목록
            benchmark: 벤치마크 시계열

        Returns:
            생성된 파일 경로
        """
        output_path = Path(output_path)

        # 기본 컴포넌트 (drawdown은 equity_curve 서브차트로 통합)
        if include_components is None:
            include_components = ['summary', 'equity_curve', 'monthly_heatmap', 'trades']

        if subtitle is None:
            if result.start_date and result.end_date:
                subtitle = f"{result.start_date} ~ {result.end_date}"
            else:
                subtitle = datetime.now().strftime("%Y-%m-%d")

        # 각 컴포넌트 렌더링
        rendered_components = []
        for name in include_components:
            if name not in self.components:
                logger.warning(f"알 수 없는 컴포넌트: {name}")
                continue

            component = self.components[name]

            try:
                if name == 'equity_curve':
                    html = component.render(result, benchmark)
                elif name == 'trades':
                    # Order 객체가 있으면 사용, 없으면 trades Dict 사용
                    trades_data = result.orders if result.orders else result.trades
                    html = component.render(trades_data)
                else:
                    html = component.render(result)

                rendered_components.append(html)
            except Exception as e:
                logger.error(f"컴포넌트 렌더링 오류 ({name}): {e}")
                rendered_components.append(f"<p>렌더링 오류: {name}</p>")

        html = self._build_html(
            title=title,
            subtitle=subtitle,
            components=rendered_components
        )

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html, encoding='utf-8')
        logger.info(f"리포트 생성 완료: {output_path}")

        return output_path

    def _build_html(
        self,
        title: str,
        subtitle: str,
        components: List[str]
    ) -> str:
        """전체 HTML 빌드"""
        css = self._get_css()

        return f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="preconnect" href="https://cdn.jsdelivr.net">
    <link href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css" rel="stylesheet">
    <script src="https://cdn.plot.ly/plotly-3.3.1.min.js"></script>
    <style>
{css}
    </style>
</head>
<body>
    <div class="container">
        <header class="report-header">
            <h1>{title}</h1>
            <p class="subtitle">{subtitle}</p>
        </header>

        <main class="report-content">
            {''.join(components)}
        </main>

        <footer class="report-footer">
            <p>kis_backtest로 생성됨 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </footer>
    </div>
</body>
</html>"""

    def _get_css(self) -> str:
        """CSS 로드"""
        css_path = Path(__file__).parent / "assets" / "kis-report.css"

        if css_path.exists():
            return css_path.read_text(encoding='utf-8')
        else:
            logger.warning(f"CSS 파일을 찾을 수 없습니다: {css_path}")
            return self.theme.to_css_vars()

    def add_component(self, name: str, component: object) -> None:
        """커스텀 컴포넌트 추가"""
        self.components[name] = component
