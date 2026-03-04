"""Candlestick Pattern definitions and registry.

Lean 캔들스틱 패턴 지원.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from kis_backtest.core.condition import Condition


@dataclass
class CandlestickPattern:
    """캔들스틱 패턴
    
    비교 연산자를 오버로딩하여 조건 생성 가능.
    
    Attributes:
        id: 패턴 식별자 (doji, engulfing, hammer, ...)
        alias: 별칭
    
    Example:
        doji = Doji()
        condition = doji.is_bullish()  # 상승 시그널
    """
    id: str
    alias: Optional[str] = None
    
    def __post_init__(self) -> None:
        if self.alias is None:
            self.alias = self.id
    
    def is_bullish(self) -> Condition:
        """상승 패턴 감지 (value > 0)"""
        return Condition("pattern_bullish", self, 0)
    
    def is_bearish(self) -> Condition:
        """하락 패턴 감지 (value < 0)"""
        return Condition("pattern_bearish", self, 0)
    
    def is_detected(self) -> Condition:
        """패턴 감지 (value != 0)"""
        return Condition("pattern_detected", self, 0)
    
    def to_dict(self) -> Dict[str, Any]:
        """선언적 정의로 변환"""
        return {
            "type": "candlestick",
            "id": self.id,
            "alias": self.alias,
        }


# ============================================================
# Candlestick Pattern Registry - Lean 클래스 매핑
# ============================================================

@dataclass(frozen=True)
class PatternInfo:
    """패턴 메타데이터"""
    id: str
    name: str
    lean_class: str
    candle_count: int  # 1=단일, 2=이중, 3=삼중
    description: str = ""
    lean_unsupported: bool = False  # True이면 현재 Lean 버전에서 미지원


CANDLESTICK_REGISTRY: Dict[str, PatternInfo] = {
    # ============================================================
    # 단일 캔들 패턴 (Single Candle) - 15개
    # ============================================================
    "doji": PatternInfo(
        id="doji",
        name="Doji (도지)",
        lean_class="Doji",
        candle_count=1,
        description="시가와 종가가 거의 같음 - 우유부단",
    ),
    "dragonfly_doji": PatternInfo(
        id="dragonfly_doji",
        name="Dragonfly Doji (잠자리형 도지)",
        lean_class="DragonflyDoji",
        candle_count=1,
        description="긴 아래꼬리, 몸통 상단 - 하락 후 상승 반전",
    ),
    "gravestone_doji": PatternInfo(
        id="gravestone_doji",
        name="Gravestone Doji (비석형 도지)",
        lean_class="GravestoneDoji",
        candle_count=1,
        description="긴 위꼬리, 몸통 하단 - 상승 후 하락 반전",
    ),
    "long_legged_doji": PatternInfo(
        id="long_legged_doji",
        name="Long Legged Doji (긴다리 도지)",
        lean_class="LongLeggedDoji",
        candle_count=1,
        description="긴 양쪽 꼬리, 중간 몸통 - 극심한 우유부단",
    ),
    "hammer": PatternInfo(
        id="hammer",
        name="Hammer (망치형)",
        lean_class="Hammer",
        candle_count=1,
        description="긴 아래꼬리, 짧은 몸통 상단 - 하락 후 상승 반전",
    ),
    "hanging_man": PatternInfo(
        id="hanging_man",
        name="Hanging Man (교수형)",
        lean_class="HangingMan",
        candle_count=1,
        description="Hammer와 동일 형태, 상승 추세 후 - 하락 반전",
    ),
    "inverted_hammer": PatternInfo(
        id="inverted_hammer",
        name="Inverted Hammer (역망치형)",
        lean_class="InvertedHammer",
        candle_count=1,
        description="긴 위꼬리, 짧은 몸통 하단 - 하락 후 상승 반전",
    ),
    "shooting_star": PatternInfo(
        id="shooting_star",
        name="Shooting Star (유성형)",
        lean_class="ShootingStar",
        candle_count=1,
        description="Inverted Hammer와 동일 형태, 상승 추세 후 - 하락 반전",
    ),
    "marubozu": PatternInfo(
        id="marubozu",
        name="Marubozu (장대봉)",
        lean_class="Marubozu",
        candle_count=1,
        description="꼬리 없는 긴 몸통 - 강한 추세",
    ),
    "closing_marubozu": PatternInfo(
        id="closing_marubozu",
        name="Closing Marubozu (종가 장대봉)",
        lean_class="ClosingMarubozu",
        candle_count=1,
        description="종가 방향에 꼬리 없음 - 강한 추세 지속",
    ),
    "opening_marubozu": PatternInfo(
        id="opening_marubozu",
        name="Opening Marubozu (시가 장대봉)",
        lean_class="OpeningMarubozu",
        candle_count=1,
        description="시가 방향에 꼬리 없음 - 강한 시작",
        lean_unsupported=True,
    ),
    "spinning_top": PatternInfo(
        id="spinning_top",
        name="Spinning Top (팽이형)",
        lean_class="SpinningTop",
        candle_count=1,
        description="작은 몸통, 양쪽 꼬리 - 우유부단",
    ),
    "belt_hold": PatternInfo(
        id="belt_hold",
        name="Belt Hold (띠 잡기)",
        lean_class="BeltHold",
        candle_count=1,
        description="장대 양봉/음봉, 시가가 저가/고가 - 반전 가능성",
    ),
    "high_wave": PatternInfo(
        id="high_wave",
        name="High Wave (큰 파도)",
        lean_class="HighWaveCandle",
        candle_count=1,
        description="매우 긴 위아래 꼬리 - 극도의 우유부단",
    ),
    "rickshaw_man": PatternInfo(
        id="rickshaw_man",
        name="Rickshaw Man (인력거꾼)",
        lean_class="RickshawMan",
        candle_count=1,
        description="중앙에 도지, 긴 양쪽 꼬리 - 우유부단",
    ),
    
    # ============================================================
    # 이중 캔들 패턴 (Double Candle) - 20개
    # ============================================================
    "engulfing": PatternInfo(
        id="engulfing",
        name="Engulfing (장악형)",
        lean_class="Engulfing",
        candle_count=2,
        description="두 번째 캔들이 첫 번째를 완전히 감쌈 - 강한 반전",
    ),
    "harami": PatternInfo(
        id="harami",
        name="Harami (잉태형)",
        lean_class="Harami",
        candle_count=2,
        description="두 번째 캔들이 첫 번째 안에 들어감 - 반전 가능성",
    ),
    "harami_cross": PatternInfo(
        id="harami_cross",
        name="Harami Cross (잉태 십자형)",
        lean_class="HaramiCross",
        candle_count=2,
        description="Harami + 두 번째가 Doji - 강한 반전",
    ),
    "piercing": PatternInfo(
        id="piercing",
        name="Piercing (관통형)",
        lean_class="Piercing",
        candle_count=2,
        description="하락 후 갭다운, 전일 중간 이상 회복 - 상승 반전",
    ),
    "dark_cloud_cover": PatternInfo(
        id="dark_cloud_cover",
        name="Dark Cloud Cover (먹구름형)",
        lean_class="DarkCloudCover",
        candle_count=2,
        description="상승 후 갭업, 전일 중간 이하 하락 - 하락 반전",
    ),
    "counterattack": PatternInfo(
        id="counterattack",
        name="Counterattack (반격형)",
        lean_class="Counterattack",
        candle_count=2,
        description="전일과 동일한 종가로 마감 - 반전 가능성",
    ),
    "tweezer_top": PatternInfo(
        id="tweezer_top",
        name="Tweezer Top (족집게 천장)",
        lean_class="TweezerTop",
        candle_count=2,
        description="동일 고가 두 캔들 - 하락 반전",
        lean_unsupported=True,
    ),
    "tweezer_bottom": PatternInfo(
        id="tweezer_bottom",
        name="Tweezer Bottom (족집게 바닥)",
        lean_class="TweezerBottom",
        candle_count=2,
        description="동일 저가 두 캔들 - 상승 반전",
        lean_unsupported=True,
    ),
    "on_neck": PatternInfo(
        id="on_neck",
        name="On Neck (목 위)",
        lean_class="OnNeck",
        candle_count=2,
        description="하락 지속 패턴",
    ),
    "in_neck": PatternInfo(
        id="in_neck",
        name="In Neck (목 안)",
        lean_class="InNeck",
        candle_count=2,
        description="하락 지속 패턴 (약간 침투)",
    ),
    "thrusting": PatternInfo(
        id="thrusting",
        name="Thrusting (밀어붙이기)",
        lean_class="Thrusting",
        candle_count=2,
        description="하락 지속 패턴 (중간까지 침투)",
    ),
    "separating_lines": PatternInfo(
        id="separating_lines",
        name="Separating Lines (분리선)",
        lean_class="SeparatingLines",
        candle_count=2,
        description="동일 시가, 반대 방향 - 추세 지속",
    ),
    "meeting_lines": PatternInfo(
        id="meeting_lines",
        name="Meeting Lines (만남선)",
        lean_class="MeetingLines",
        candle_count=2,
        description="동일 종가, 반대 방향 - 반전",
        lean_unsupported=True,
    ),
    "kicking": PatternInfo(
        id="kicking",
        name="Kicking (킥킹)",
        lean_class="Kicking",
        candle_count=2,
        description="갭을 동반한 강한 반전",
    ),
    "kicking_by_length": PatternInfo(
        id="kicking_by_length",
        name="Kicking By Length",
        lean_class="KickingByLength",
        candle_count=2,
        description="길이 기준 킥킹 패턴",
    ),
    "matching_low": PatternInfo(
        id="matching_low",
        name="Matching Low (일치 저가)",
        lean_class="MatchingLow",
        candle_count=2,
        description="동일 저가 - 지지 확인",
    ),
    "matching_high": PatternInfo(
        id="matching_high",
        name="Matching High (일치 고가)",
        lean_class="MatchingHigh",
        candle_count=2,
        description="동일 고가 - 저항 확인",
        lean_unsupported=True,
    ),
    "gap_side_by_side_white": PatternInfo(
        id="gap_side_by_side_white",
        name="Gap Side By Side White",
        lean_class="GapSideBySideWhite",
        candle_count=2,
        description="갭 후 나란한 양봉 - 추세 지속",
    ),
    "homing_pigeon": PatternInfo(
        id="homing_pigeon",
        name="Homing Pigeon (귀소비둘기)",
        lean_class="HomingPigeon",
        candle_count=2,
        description="두 번째 음봉이 첫 번째 안에 - 상승 반전",
    ),
    "dojistar": PatternInfo(
        id="dojistar",
        name="Doji Star (도지별)",
        lean_class="DojiStar",
        candle_count=2,
        description="갭 후 도지 - 반전 가능성",
    ),
    
    # ============================================================
    # 삼중 캔들 패턴 (Triple Candle) - 25개
    # ============================================================
    "morning_star": PatternInfo(
        id="morning_star",
        name="Morning Star (샛별형)",
        lean_class="MorningStar",
        candle_count=3,
        description="하락-갭다운-상승 패턴 - 강한 상승 반전",
    ),
    "morning_doji_star": PatternInfo(
        id="morning_doji_star",
        name="Morning Doji Star (샛별 도지)",
        lean_class="MorningDojiStar",
        candle_count=3,
        description="샛별형 + 도지 - 더 강한 상승 반전",
    ),
    "evening_star": PatternInfo(
        id="evening_star",
        name="Evening Star (저녁별형)",
        lean_class="EveningStar",
        candle_count=3,
        description="상승-갭업-하락 패턴 - 강한 하락 반전",
    ),
    "evening_doji_star": PatternInfo(
        id="evening_doji_star",
        name="Evening Doji Star (저녁별 도지)",
        lean_class="EveningDojiStar",
        candle_count=3,
        description="저녁별형 + 도지 - 더 강한 하락 반전",
    ),
    "three_white_soldiers": PatternInfo(
        id="three_white_soldiers",
        name="Three White Soldiers (적삼병)",
        lean_class="ThreeWhiteSoldiers",
        candle_count=3,
        description="3연속 강한 양봉 - 강한 상승 추세",
    ),
    "three_black_crows": PatternInfo(
        id="three_black_crows",
        name="Three Black Crows (흑삼병)",
        lean_class="ThreeBlackCrows",
        candle_count=3,
        description="3연속 강한 음봉 - 강한 하락 추세",
    ),
    "three_inside": PatternInfo(
        id="three_inside",
        name="Three Inside (삼내형)",
        lean_class="ThreeInside",
        candle_count=3,
        description="Harami + 확인 캔들 - 확정된 반전",
    ),
    "three_outside": PatternInfo(
        id="three_outside",
        name="Three Outside (삼외형)",
        lean_class="ThreeOutside",
        candle_count=3,
        description="Engulfing + 확인 캔들 - 확정된 반전",
    ),
    "abandoned_baby": PatternInfo(
        id="abandoned_baby",
        name="Abandoned Baby (버려진 아기)",
        lean_class="AbandonedBaby",
        candle_count=3,
        description="갭-Doji-갭 패턴 - 희귀하지만 강한 반전",
    ),
    "three_stars_in_south": PatternInfo(
        id="three_stars_in_south",
        name="Three Stars in South (남쪽 삼성)",
        lean_class="ThreeStarsInSouth",
        candle_count=3,
        description="점점 작아지는 음봉 - 상승 반전",
    ),
    "advance_block": PatternInfo(
        id="advance_block",
        name="Advance Block (진행 차단)",
        lean_class="AdvanceBlock",
        candle_count=3,
        description="약해지는 양봉 3개 - 상승 약화",
    ),
    "stalled_pattern": PatternInfo(
        id="stalled_pattern",
        name="Stalled Pattern (정체)",
        lean_class="StalledPattern",
        candle_count=3,
        description="상승 후 정체 - 반전 경고",
    ),
    "deliberation": PatternInfo(
        id="deliberation",
        name="Deliberation (숙고)",
        lean_class="Deliberation",
        candle_count=3,
        description="상승 후 작은 캔들 - 반전 경고",
        lean_unsupported=True,
    ),
    "tasuki_gap": PatternInfo(
        id="tasuki_gap",
        name="Tasuki Gap (타스키 갭)",
        lean_class="TasukiGap",
        candle_count=3,
        description="갭 후 부분 채움 - 추세 지속",
    ),
    "upside_gap_two_crows": PatternInfo(
        id="upside_gap_two_crows",
        name="Upside Gap Two Crows",
        lean_class="UpsideGapTwoCrows",
        candle_count=3,
        description="갭업 후 두 음봉 - 하락 반전",
    ),
    "downside_tasuki_gap": PatternInfo(
        id="downside_tasuki_gap",
        name="Downside Tasuki Gap",
        lean_class="DownsideTasukiGap",
        candle_count=3,
        description="하락 갭 후 부분 채움 - 하락 지속 (Lean 미지원: tasuki_gap 사용 권장)",
        lean_unsupported=True,
    ),
    "upside_tasuki_gap": PatternInfo(
        id="upside_tasuki_gap",
        name="Upside Tasuki Gap",
        lean_class="UpsideTasukiGap",
        candle_count=3,
        description="상승 갭 후 부분 채움 - 상승 지속 (Lean 미지원: tasuki_gap 사용 권장)",
        lean_unsupported=True,
    ),
    "side_by_side_white_lines": PatternInfo(
        id="side_by_side_white_lines",
        name="Side By Side White Lines",
        lean_class="SideBySideWhiteLines",
        candle_count=3,
        description="나란한 양봉 - 추세 지속",
        lean_unsupported=True,
    ),
    "stick_sandwich": PatternInfo(
        id="stick_sandwich",
        name="Stick Sandwich (막대 샌드위치)",
        lean_class="StickSandwich",
        candle_count=3,
        description="동일 종가 음봉 사이 양봉 - 지지 확인",
    ),
    "three_line_strike": PatternInfo(
        id="three_line_strike",
        name="Three Line Strike (삼선 타격)",
        lean_class="ThreeLineStrike",
        candle_count=4,
        description="3캔들 추세 + 반대 장악 - 강한 반전",
    ),
    "two_crows": PatternInfo(
        id="two_crows",
        name="Two Crows (두 까마귀)",
        lean_class="TwoCrows",
        candle_count=3,
        description="갭업 후 두 음봉 - 하락 반전",
    ),
    "unique_three_river": PatternInfo(
        id="unique_three_river",
        name="Unique Three River",
        lean_class="UniqueThreeRiver",
        candle_count=3,
        description="독특한 3일 패턴 - 상승 반전",
    ),
    "concealing_baby_swallow": PatternInfo(
        id="concealing_baby_swallow",
        name="Concealing Baby Swallow",
        lean_class="ConcealedBabySwallow",
        candle_count=4,
        description="희귀한 상승 반전 패턴",
    ),
    
    # ============================================================
    # 5일+ 패턴 (Complex) - 5개
    # ============================================================
    "breakaway": PatternInfo(
        id="breakaway",
        name="Breakaway (이탈형)",
        lean_class="Breakaway",
        candle_count=5,
        description="5일 패턴 - 추세 전환",
    ),
    "mat_hold": PatternInfo(
        id="mat_hold",
        name="Mat Hold (매트 홀드)",
        lean_class="MatHold",
        candle_count=5,
        description="5일 지속 패턴 - 추세 지속",
    ),
    "rising_three_methods": PatternInfo(
        id="rising_three_methods",
        name="Rising Three Methods",
        lean_class="RiseFallThreeMethods",
        candle_count=5,
        description="상승 후 3일 조정 후 상승 - 상승 지속 (Lean: RiseFallThreeMethods, +1=상승)",
    ),
    "falling_three_methods": PatternInfo(
        id="falling_three_methods",
        name="Falling Three Methods",
        lean_class="RiseFallThreeMethods",
        candle_count=5,
        description="하락 후 3일 반등 후 하락 - 하락 지속 (Lean: RiseFallThreeMethods, -1=하락)",
    ),
    "ladder_bottom": PatternInfo(
        id="ladder_bottom",
        name="Ladder Bottom (사다리 바닥)",
        lean_class="LadderBottom",
        candle_count=5,
        description="5일 바닥 패턴 - 상승 반전",
    ),
    "tristar": PatternInfo(
        id="tristar",
        name="Tri-Star (트라이스타)",
        lean_class="Tristar",
        candle_count=3,
        description="세 개의 도지 - 강한 반전 신호",
    ),
    "identical_three_crows": PatternInfo(
        id="identical_three_crows",
        name="Identical Three Crows (동일 삼흑병)",
        lean_class="IdenticalThreeCrows",
        candle_count=3,
        description="동일 종가 3연속 음봉 - 강한 하락",
    ),
    "up_down_gap_three_methods": PatternInfo(
        id="up_down_gap_three_methods",
        name="Up/Down Gap Three Methods",
        lean_class="UpDownGapThreeMethods",
        candle_count=3,
        description="갭 후 삼법 패턴 - 추세 지속",
    ),
}


