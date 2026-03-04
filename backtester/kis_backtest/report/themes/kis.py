"""한국투자증권 테마

api_v1/static/css/variables.css 기반.
KIS 블루(#245BEE) 브랜드 컬러 및 한국식 상승/하락 색상 적용.
"""

from dataclasses import dataclass
from .base import BaseTheme


@dataclass
class KISTheme(BaseTheme):
    """한국투자증권 디자인 테마

    api_v1/static/css/variables.css에서 가져온 스타일.

    특징:
    - 브랜드 컬러: KIS 블루 (#245BEE) — 프론트엔드 통일
    - 한국식 상승/하락: 빨강(상승), 파랑(하락)
    - 폰트: Pretendard
    """

    # ===== 브랜드 컬러 (KIS 블루) =====
    PRIMARY: str = "#245BEE"
    PRIMARY_DARK: str = "#1A47B8"
    PRIMARY_LIGHT: str = "#4A7AFF"
    
    # ===== 한국식 상승/하락 색상 =====
    # 한국 주식시장: 상승=빨강, 하락=파랑 (글로벌과 반대)
    POSITIVE: str = "#E31837"      # 상승: 빨강
    NEGATIVE: str = "#2563EB"      # 하락: 파랑
    NEUTRAL: str = "#8E8E93"       # 보합: 회색
    
    # ===== 차트 전용 색상 =====
    # 차트에서는 녹색/빨강을 더 뚜렷하게
    CHART_UP: str = "#16A34A"      # 차트 상승 (녹색 사용 가능)
    CHART_DOWN: str = "#DC2626"    # 차트 하락
    CHART_LINE: str = "#245BEE"    # 메인 라인
    CHART_AREA: str = "rgba(36, 91, 238, 0.1)"  # 영역 채우기
    
    # ===== 배경 =====
    BG_PRIMARY: str = "#FFFFFF"
    BG_SECONDARY: str = "#F8F9FA"
    BG_TERTIARY: str = "#F1F3F5"
    BG_CARD: str = "#FFFFFF"
    
    # ===== 텍스트 =====
    TEXT_PRIMARY: str = "#1A1A1A"
    TEXT_SECONDARY: str = "#555555"
    TEXT_MUTED: str = "#888888"
    TEXT_INVERSE: str = "#FFFFFF"
    
    # ===== 보더 =====
    BORDER: str = "#E5E7EB"
    BORDER_HOVER: str = "#D1D5DB"
    BORDER_FOCUS: str = "#245BEE"
    GRID: str = "#E0E0E0"
    
    # ===== 차트 컬러 팔레트 =====
    CHART_COLORS: tuple = (
        "#245BEE",  # Primary Blue
        "#2563EB",  # Blue-600
        "#16A34A",  # Green
        "#F59E0B",  # Yellow
        "#9C27B0",  # Purple
        "#00ACC1",  # Cyan
    )
    
    # ===== 시맨틱 컬러 (차트 외) =====
    SUCCESS: str = "#16A34A"
    SUCCESS_DIM: str = "rgba(22, 163, 74, 0.1)"
    DANGER: str = "#DC2626"
    DANGER_DIM: str = "rgba(220, 38, 38, 0.1)"
    WARNING: str = "#F59E0B"
    WARNING_DIM: str = "rgba(245, 158, 11, 0.1)"
    INFO: str = "#2563EB"
    INFO_DIM: str = "rgba(37, 99, 235, 0.1)"
    
    # ===== 타이포그래피 =====
    FONT_FAMILY: str = "'Pretendard', -apple-system, BlinkMacSystemFont, 'Noto Sans KR', sans-serif"
    FONT_MONO: str = "'JetBrains Mono', 'Fira Code', monospace"
    
    def to_css_vars(self) -> str:
        """CSS 변수로 변환 (한투 확장)"""
        base_css = super().to_css_vars()
        
        # 한투 전용 변수 추가
        kis_css = f"""
    /* KIS 전용 */
    --color-chart-up: {self.CHART_UP};
    --color-chart-down: {self.CHART_DOWN};
    --color-chart-line: {self.CHART_LINE};
    --color-chart-area: {self.CHART_AREA};
    
    --color-success: {self.SUCCESS};
    --color-success-dim: {self.SUCCESS_DIM};
    --color-danger: {self.DANGER};
    --color-danger-dim: {self.DANGER_DIM};
    --color-warning: {self.WARNING};
    --color-warning-dim: {self.WARNING_DIM};
    --color-info: {self.INFO};
    --color-info-dim: {self.INFO_DIM};
    
    --color-border-hover: {self.BORDER_HOVER};
    --color-border-focus: {self.BORDER_FOCUS};
"""
        
        # base_css의 닫는 괄호 전에 삽입
        return base_css.rstrip().rstrip("}") + kis_css + "\n}"
    
    def get_plotly_template(self) -> dict:
        """Plotly 차트 템플릿 생성"""
        return {
            "layout": {
                "font": {"family": self.FONT_FAMILY.split(",")[0].strip("'")},
                "paper_bgcolor": self.BG_PRIMARY,
                "plot_bgcolor": self.BG_PRIMARY,
                "colorway": list(self.CHART_COLORS),
                "xaxis": {
                    "gridcolor": self.GRID,
                    "linecolor": self.BORDER,
                },
                "yaxis": {
                    "gridcolor": self.GRID,
                    "linecolor": self.BORDER,
                },
                "title": {
                    "font": {"color": self.TEXT_PRIMARY, "size": 18}
                },
                "legend": {
                    "font": {"color": self.TEXT_SECONDARY}
                }
            }
        }
