"""기본 테마
"""

from dataclasses import dataclass
from typing import List


@dataclass
class BaseTheme:
    """기본 테마 (추상)
    
    서브클래스에서 오버라이드하여 커스텀 테마 생성 가능.
    """
    
    # ===== 브랜드 컬러 =====
    PRIMARY: str = "#007AFF"
    PRIMARY_DARK: str = "#005BB5"
    PRIMARY_LIGHT: str = "#4DA3FF"
    
    # ===== 시맨틱 컬러 =====
    # 글로벌 표준: 상승=녹색, 하락=빨강
    POSITIVE: str = "#16A34A"
    NEGATIVE: str = "#DC2626"
    NEUTRAL: str = "#8E8E93"
    
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
    
    # ===== 보더/그리드 =====
    BORDER: str = "#E5E7EB"
    GRID: str = "#E0E0E0"
    
    # ===== 차트 컬러 팔레트 =====
    CHART_COLORS: tuple = (
        "#007AFF",
        "#16A34A",
        "#F59E0B",
        "#9C27B0",
        "#00ACC1",
        "#E91E63",
    )
    
    # ===== 타이포그래피 =====
    FONT_FAMILY: str = "'Pretendard', -apple-system, BlinkMacSystemFont, 'Noto Sans KR', sans-serif"
    FONT_MONO: str = "'JetBrains Mono', 'Fira Code', monospace"
    
    # 폰트 사이즈
    FONT_SIZE_XS: str = "0.6875rem"
    FONT_SIZE_SM: str = "0.8125rem"
    FONT_SIZE_BASE: str = "0.875rem"
    FONT_SIZE_LG: str = "1rem"
    FONT_SIZE_XL: str = "1.125rem"
    FONT_SIZE_2XL: str = "1.25rem"
    FONT_SIZE_3XL: str = "1.5rem"
    FONT_SIZE_4XL: str = "2rem"
    
    # ===== 간격 =====
    SPACING_XS: str = "0.25rem"
    SPACING_SM: str = "0.5rem"
    SPACING_MD: str = "0.75rem"
    SPACING_LG: str = "1rem"
    SPACING_XL: str = "1.5rem"
    SPACING_2XL: str = "2rem"
    
    # ===== 반경 =====
    RADIUS_SM: str = "4px"
    RADIUS_MD: str = "6px"
    RADIUS_LG: str = "8px"
    RADIUS_XL: str = "12px"
    
    # ===== 그림자 =====
    SHADOW_SM: str = "0 1px 2px rgba(0, 0, 0, 0.05)"
    SHADOW_MD: str = "0 4px 6px rgba(0, 0, 0, 0.07)"
    SHADOW_LG: str = "0 10px 15px rgba(0, 0, 0, 0.1)"
    SHADOW_CARD: str = "0 2px 8px rgba(0, 0, 0, 0.08)"
    
    def to_css_vars(self) -> str:
        """CSS 변수로 변환"""
        return f"""
:root {{
    /* Colors */
    --color-primary: {self.PRIMARY};
    --color-primary-dark: {self.PRIMARY_DARK};
    --color-primary-light: {self.PRIMARY_LIGHT};
    
    --color-positive: {self.POSITIVE};
    --color-negative: {self.NEGATIVE};
    --color-neutral: {self.NEUTRAL};
    
    --color-bg-primary: {self.BG_PRIMARY};
    --color-bg-secondary: {self.BG_SECONDARY};
    --color-bg-tertiary: {self.BG_TERTIARY};
    --color-bg-card: {self.BG_CARD};
    
    --color-text-primary: {self.TEXT_PRIMARY};
    --color-text-secondary: {self.TEXT_SECONDARY};
    --color-text-muted: {self.TEXT_MUTED};
    --color-text-inverse: {self.TEXT_INVERSE};
    
    --color-border: {self.BORDER};
    --color-grid: {self.GRID};
    
    /* Typography */
    --font-family: {self.FONT_FAMILY};
    --font-mono: {self.FONT_MONO};
    
    --font-size-xs: {self.FONT_SIZE_XS};
    --font-size-sm: {self.FONT_SIZE_SM};
    --font-size-base: {self.FONT_SIZE_BASE};
    --font-size-lg: {self.FONT_SIZE_LG};
    --font-size-xl: {self.FONT_SIZE_XL};
    --font-size-2xl: {self.FONT_SIZE_2XL};
    --font-size-3xl: {self.FONT_SIZE_3XL};
    --font-size-4xl: {self.FONT_SIZE_4XL};
    
    /* Spacing */
    --spacing-xs: {self.SPACING_XS};
    --spacing-sm: {self.SPACING_SM};
    --spacing-md: {self.SPACING_MD};
    --spacing-lg: {self.SPACING_LG};
    --spacing-xl: {self.SPACING_XL};
    --spacing-2xl: {self.SPACING_2XL};
    
    /* Border Radius */
    --radius-sm: {self.RADIUS_SM};
    --radius-md: {self.RADIUS_MD};
    --radius-lg: {self.RADIUS_LG};
    --radius-xl: {self.RADIUS_XL};
    
    /* Shadows */
    --shadow-sm: {self.SHADOW_SM};
    --shadow-md: {self.SHADOW_MD};
    --shadow-lg: {self.SHADOW_LG};
    --shadow-card: {self.SHADOW_CARD};
}}
"""
