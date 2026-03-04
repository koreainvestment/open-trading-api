"""Indicator definitions and registry.

Defines all supported technical indicators with their Lean class mappings.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union

from kis_backtest.core.condition import Condition, CompositeCondition


@dataclass
class Indicator:
    """기술적 지표
    
    비교 연산자를 오버로딩하여 직관적인 조건 생성 가능.
    
    Attributes:
        id: 지표 식별자 (sma, ema, rsi, macd, ...)
        params: 지표 파라미터
        alias: 별칭 (자동 생성 가능)
        output: 출력값 (macd의 경우 signal, histogram 등)
    
    Example:
        sma_fast = SMA(5)
        sma_slow = SMA(20)
        condition = sma_fast > sma_slow  # Condition 객체 반환
    """
    id: str
    params: Dict[str, Any] = field(default_factory=dict)
    alias: Optional[str] = None
    output: str = "value"
    
    def __post_init__(self) -> None:
        if self.alias is None:
            # 자동 alias 생성: sma_20, rsi_14 등
            param_str = "_".join(str(v) for v in self.params.values())
            self.alias = f"{self.id}_{param_str}" if param_str else self.id
    
    # 비교 연산자 오버로딩
    def __gt__(self, other: Union[Indicator, float, int]) -> Condition:
        """Greater than (>)"""
        return Condition("greater_than", self, other)
    
    def __lt__(self, other: Union[Indicator, float, int]) -> Condition:
        """Less than (<)"""
        return Condition("less_than", self, other)
    
    def __ge__(self, other: Union[Indicator, float, int]) -> Condition:
        """Greater or equal (>=)"""
        return Condition("greater_equal", self, other)
    
    def __le__(self, other: Union[Indicator, float, int]) -> Condition:
        """Less or equal (<=)"""
        return Condition("less_equal", self, other)
    
    def __mul__(self, other: Union[float, int]) -> "ScaledIndicator":
        """곱셈 연산 (Indicator * float)
        
        Example:
            ma * 0.9  # MA의 90%
        """
        return ScaledIndicator(self, other, "mul")
    
    def __rmul__(self, other: Union[float, int]) -> "ScaledIndicator":
        """역방향 곱셈 연산 (float * Indicator)"""
        return ScaledIndicator(self, other, "mul")

    def __add__(self, other: Union[float, int]) -> "ScaledIndicator":
        """덧셈 연산 (Indicator + float)"""
        return ScaledIndicator(self, other, "add")

    def __radd__(self, other: Union[float, int]) -> "ScaledIndicator":
        """역방향 덧셈 연산 (float + Indicator)"""
        return ScaledIndicator(self, other, "add")

    def __sub__(self, other: Union[float, int]) -> "ScaledIndicator":
        """뺄셈 연산 (Indicator - float)"""
        return ScaledIndicator(self, other, "sub")
    
    def crosses_above(self, other: Union[Indicator, float]) -> Condition:
        """상향 돌파 (Cross Above)
        
        Example:
            SMA(5).crosses_above(SMA(20))  # 골든크로스
        """
        return Condition("cross_above", self, other)
    
    def crosses_below(self, other: Union[Indicator, float]) -> Condition:
        """하향 돌파 (Cross Below)
        
        Example:
            SMA(5).crosses_below(SMA(20))  # 데드크로스
        """
        return Condition("cross_below", self, other)
    
    def between(self, low: float, high: float) -> CompositeCondition:
        """범위 내 (Between)
        
        Example:
            RSI(14).between(30, 70)  # RSI가 30~70 사이
        """
        return (self >= low) & (self <= high)
    
    def to_dict(self) -> Dict[str, Any]:
        """선언적 정의로 변환"""
        return {
            "id": self.id,
            "alias": self.alias,
            "params": self.params,
            "output": self.output,
        }


@dataclass
class ScaledIndicator:
    """스케일된 지표 (Indicator * scalar, + offset 등)
    
    MA * 0.9, MA + 1000 등의 연산 결과를 표현합니다.
    
    Attributes:
        indicator: 원본 지표
        scalar: 스케일/오프셋 값
        operation: 연산 종류 ("mul", "div", "add", "sub")
    """
    indicator: Indicator
    scalar: Union[float, int]
    operation: str = "mul"
    
    def __gt__(self, other: Union[Indicator, "ScaledIndicator", float, int]) -> Condition:
        """Greater than (>)"""
        return Condition("greater_than", other, self)
    
    def __lt__(self, other: Union[Indicator, "ScaledIndicator", float, int]) -> Condition:
        """Less than (<)"""
        return Condition("less_than", other, self)
    
    def __ge__(self, other: Union[Indicator, "ScaledIndicator", float, int]) -> Condition:
        """Greater or equal (>=)"""
        return Condition("greater_equal", other, self)
    
    def __le__(self, other: Union[Indicator, "ScaledIndicator", float, int]) -> Condition:
        """Less or equal (<=)"""
        return Condition("less_equal", other, self)
    
    def to_dict(self) -> Dict[str, Any]:
        """선언적 정의로 변환"""
        return {
            "type": "scaled_indicator",
            "indicator": self.indicator.to_dict(),
            "scalar": self.scalar,
            "operation": self.operation,
        }


# ============================================================
# Indicator Registry - Lean 클래스 매핑
# ============================================================

@dataclass(frozen=True)
class IndicatorInfo:
    """지표 메타데이터

    Attributes:
        id: 지표 식별자
        name: 지표 이름
        lean_class: Lean 클래스명
        params: 파라미터 목록
        value_template: 값 접근 템플릿
        outputs: 다중 출력 템플릿
        init_template: 초기화 템플릿
        description: 설명
        requires_tradebar: TradeBar 업데이트 필요 여부
            True인 경우 Update(TradeBar)만 지원
            False인 경우 Update(DateTime, decimal) 가능
    """
    id: str
    name: str
    lean_class: str
    params: List[str]
    value_template: Optional[str]
    outputs: Dict[str, str] = field(default_factory=dict)
    init_template: str = ""
    description: str = ""
    requires_tradebar: bool = False


INDICATOR_REGISTRY: Dict[str, IndicatorInfo] = {
    # ============================================================
    # 이동평균 계열 (Moving Averages) - 14개
    # ============================================================
    "sma": IndicatorInfo(
        id="sma",
        name="Simple Moving Average",
        lean_class="SimpleMovingAverage",
        params=["period"],
        value_template="{name}.Current.Value",
        init_template="{name} = SimpleMovingAverage({period})",
        description="단순 이동평균",
    ),
    "ema": IndicatorInfo(
        id="ema",
        name="Exponential Moving Average",
        lean_class="ExponentialMovingAverage",
        params=["period"],
        value_template="{name}.Current.Value",
        init_template="{name} = ExponentialMovingAverage({period})",
        description="지수 이동평균",
    ),
    "dema": IndicatorInfo(
        id="dema",
        name="Double Exponential Moving Average",
        lean_class="DoubleExponentialMovingAverage",
        params=["period"],
        value_template="{name}.Current.Value",
        init_template="{name} = DoubleExponentialMovingAverage({period})",
        description="이중 지수 이동평균",
    ),
    "tema": IndicatorInfo(
        id="tema",
        name="Triple Exponential Moving Average",
        lean_class="TripleExponentialMovingAverage",
        params=["period"],
        value_template="{name}.Current.Value",
        init_template="{name} = TripleExponentialMovingAverage({period})",
        description="삼중 지수 이동평균",
    ),
    "hma": IndicatorInfo(
        id="hma",
        name="Hull Moving Average",
        lean_class="HullMovingAverage",
        params=["period"],
        value_template="{name}.Current.Value",
        init_template="{name} = HullMovingAverage({period})",
        description="헐 이동평균 (노이즈 감소)",
    ),
    "kama": IndicatorInfo(
        id="kama",
        name="Kaufman Adaptive Moving Average",
        lean_class="KaufmanAdaptiveMovingAverage",
        params=["period"],
        value_template="{name}.Current.Value",
        init_template="{name} = KaufmanAdaptiveMovingAverage({period})",
        description="카우프만 적응형 이동평균",
    ),
    "alma": IndicatorInfo(
        id="alma",
        name="Arnaud Legoux Moving Average",
        lean_class="ArnaudLegouxMovingAverage",
        params=["period", "sigma", "offset"],
        value_template="{name}.Current.Value",
        init_template="{name} = ArnaudLegouxMovingAverage({period}, int({sigma}), {offset})",
        description="아르노 르구 이동평균",
    ),
    "lwma": IndicatorInfo(
        id="lwma",
        name="Linear Weighted Moving Average",
        lean_class="LinearWeightedMovingAverage",
        params=["period"],
        value_template="{name}.Current.Value",
        init_template="{name} = LinearWeightedMovingAverage({period})",
        description="선형 가중 이동평균",
    ),
    "trima": IndicatorInfo(
        id="trima",
        name="Triangular Moving Average",
        lean_class="TriangularMovingAverage",
        params=["period"],
        value_template="{name}.Current.Value",
        init_template="{name} = TriangularMovingAverage({period})",
        description="삼각 이동평균",
    ),
    "t3": IndicatorInfo(
        id="t3",
        name="T3 Moving Average",
        lean_class="T3MovingAverage",
        params=["period", "volume_factor"],
        value_template="{name}.Current.Value",
        init_template="{name} = T3MovingAverage({period}, {volume_factor})",
        description="T3 이동평균",
    ),
    "zlema": IndicatorInfo(
        id="zlema",
        name="Zero Lag Exponential Moving Average",
        lean_class="ZeroLagExponentialMovingAverage",
        params=["period"],
        value_template="{name}.Current.Value",
        init_template="{name} = ZeroLagExponentialMovingAverage({period})",
        description="제로 래그 지수 이동평균",
    ),
    "wma": IndicatorInfo(
        id="wma",
        name="Wilder Moving Average",
        lean_class="WilderMovingAverage",
        params=["period"],
        value_template="{name}.Current.Value",
        init_template="{name} = WilderMovingAverage({period})",
        description="와일더 이동평균",
    ),
    "frama": IndicatorInfo(
        id="frama",
        name="Fractal Adaptive Moving Average",
        lean_class="FractalAdaptiveMovingAverage",
        params=["period"],
        value_template="{name}.Current.Value",
        init_template="{name} = FractalAdaptiveMovingAverage({period})",
        description="프랙탈 적응형 이동평균",
        requires_tradebar=True,
    ),
    "vidya": IndicatorInfo(
        id="vidya",
        name="Variable Index Dynamic Average",
        lean_class="VariableIndexDynamicAverage",
        params=["period"],
        value_template="{name}.Current.Value",
        init_template="{name} = VariableIndexDynamicAverage({period})",
        description="VIDYA 이동평균",
    ),
    
    # ============================================================
    # 오실레이터 계열 (Oscillators) - 20개
    # ============================================================
    "rsi": IndicatorInfo(
        id="rsi",
        name="Relative Strength Index",
        lean_class="RelativeStrengthIndex",
        params=["period"],
        value_template="{name}.Current.Value",
        init_template="{name} = RelativeStrengthIndex({period}, MovingAverageType.Wilders)",
        description="상대강도지수",
    ),
    "stochastic": IndicatorInfo(
        id="stochastic",
        name="Stochastic Oscillator",
        lean_class="Stochastic",
        params=["k_period", "d_period"],
        value_template=None,
        outputs={
            "k": "{name}.StochK.Current.Value",
            "d": "{name}.StochD.Current.Value",
        },
        init_template="{name} = Stochastic({k_period}, 1, {d_period})",
        description="스토캐스틱",
        requires_tradebar=True,
    ),
    "stochrsi": IndicatorInfo(
        id="stochrsi",
        name="Stochastic RSI",
        lean_class="StochasticRelativeStrengthIndex",
        params=["rsi_period", "stoch_period", "k_period", "d_period"],
        value_template=None,
        outputs={
            "k": "{name}.K.Current.Value",
            "d": "{name}.D.Current.Value",
        },
        init_template="{name} = StochasticRelativeStrengthIndex({rsi_period}, {stoch_period}, {k_period}, {d_period})",
        description="스토캐스틱 RSI",
    ),
    "macd": IndicatorInfo(
        id="macd",
        name="MACD",
        lean_class="MovingAverageConvergenceDivergence",
        params=["fast", "slow", "signal"],
        value_template="{name}.Current.Value",
        outputs={
            "value": "{name}.Current.Value",
            "signal": "{name}.Signal.Current.Value",
            "histogram": "{name}.Histogram.Current.Value",
        },
        init_template="{name} = MovingAverageConvergenceDivergence({fast}, {slow}, {signal}, MovingAverageType.Exponential)",
        description="MACD",
    ),
    "cci": IndicatorInfo(
        id="cci",
        name="Commodity Channel Index",
        lean_class="CommodityChannelIndex",
        params=["period"],
        value_template="{name}.Current.Value",
        init_template="{name} = CommodityChannelIndex({period}, MovingAverageType.Simple)",
        description="상품채널지수",
        requires_tradebar=True,
    ),
    "williams_r": IndicatorInfo(
        id="williams_r",
        name="Williams %R",
        lean_class="WilliamsPercentR",
        params=["period"],
        value_template="{name}.Current.Value",
        init_template="{name} = WilliamsPercentR({period})",
        description="윌리엄스 %R",
        requires_tradebar=True,
    ),
    "momentum": IndicatorInfo(
        id="momentum",
        name="Momentum Percent",
        lean_class="MomentumPercent",
        params=["period"],
        value_template="{name}.Current.Value",
        init_template="{name} = MomentumPercent({period})",
        description="모멘텀",
    ),
    "roc": IndicatorInfo(
        id="roc",
        name="Rate of Change Percent",
        lean_class="RateOfChangePercent",
        params=["period"],
        value_template="{name}.Current.Value",
        init_template="{name} = RateOfChangePercent({period})",
        description="변화율",
    ),
    "apo": IndicatorInfo(
        id="apo",
        name="Absolute Price Oscillator",
        lean_class="AbsolutePriceOscillator",
        params=["fast", "slow"],
        value_template="{name}.Current.Value",
        init_template="{name} = AbsolutePriceOscillator({fast}, {slow}, MovingAverageType.Exponential)",
        description="절대 가격 오실레이터",
    ),
    "ppo": IndicatorInfo(
        id="ppo",
        name="Percentage Price Oscillator",
        lean_class="PercentagePriceOscillator",
        params=["fast", "slow"],
        value_template="{name}.Current.Value",
        outputs={
            "value": "{name}.Current.Value",
            "signal": "{name}.Signal.Current.Value",
            "histogram": "{name}.Histogram.Current.Value",
        },
        init_template="{name} = PercentagePriceOscillator({fast}, {slow}, MovingAverageType.Exponential)",
        description="백분율 가격 오실레이터",
    ),
    "aroon": IndicatorInfo(
        id="aroon",
        name="Aroon Oscillator",
        lean_class="AroonOscillator",
        params=["up_period", "down_period"],
        value_template="{name}.Current.Value",
        outputs={
            "value": "{name}.Current.Value",
            "aroon_up": "{name}.AroonUp.Current.Value",
            "aroon_down": "{name}.AroonDown.Current.Value",
        },
        init_template="{name} = AroonOscillator({up_period}, {down_period})",
        description="아룬 오실레이터",
        requires_tradebar=True,
    ),
    "cmo": IndicatorInfo(
        id="cmo",
        name="Chande Momentum Oscillator",
        lean_class="ChandeMomentumOscillator",
        params=["period"],
        value_template="{name}.Current.Value",
        init_template="{name} = ChandeMomentumOscillator({period})",
        description="챈드 모멘텀 오실레이터",
    ),
    "ao": IndicatorInfo(
        id="ao",
        name="Awesome Oscillator",
        lean_class="AwesomeOscillator",
        params=["fast", "slow"],
        value_template="{name}.Current.Value",
        init_template="{name} = AwesomeOscillator({fast}, {slow}, MovingAverageType.Simple)",
        description="오썸 오실레이터",
        requires_tradebar=True,
    ),
    "cho": IndicatorInfo(
        id="cho",
        name="Chaikin Oscillator",
        lean_class="ChaikinOscillator",
        params=["fast", "slow"],
        value_template="{name}.Current.Value",
        init_template="{name} = ChaikinOscillator({fast}, {slow})",
        description="채킨 오실레이터",
        requires_tradebar=True,
    ),
    "ultosc": IndicatorInfo(
        id="ultosc",
        name="Ultimate Oscillator",
        lean_class="UltimateOscillator",
        params=["period1", "period2", "period3"],
        value_template="{name}.Current.Value",
        init_template="{name} = UltimateOscillator({period1}, {period2}, {period3})",
        description="궁극 오실레이터",
        requires_tradebar=True,
    ),
    "trix": IndicatorInfo(
        id="trix",
        name="TRIX",
        lean_class="Trix",
        params=["period"],
        value_template="{name}.Current.Value",
        init_template="{name} = Trix({period})",
        description="TRIX 오실레이터",
    ),
    "tsi": IndicatorInfo(
        id="tsi",
        name="True Strength Index",
        lean_class="TrueStrengthIndex",
        params=["long_period", "short_period", "signal_period"],
        value_template="{name}.Current.Value",
        outputs={
            "value": "{name}.Current.Value",
            "signal": "{name}.Signal.Current.Value",
        },
        init_template="{name} = TrueStrengthIndex({long_period}, {short_period}, {signal_period})",
        description="참 강도 지수",
    ),
    "rvi": IndicatorInfo(
        id="rvi",
        name="Relative Vigor Index",
        lean_class="RelativeVigorIndex",
        params=["period"],
        value_template="{name}.Current.Value",
        init_template='{name} = RelativeVigorIndex("{name}", {period}, MovingAverageType.Simple)',
        description="상대 활력 지수",
        requires_tradebar=True,
    ),
    "dpo": IndicatorInfo(
        id="dpo",
        name="Detrended Price Oscillator",
        lean_class="DetrendedPriceOscillator",
        params=["period"],
        value_template="{name}.Current.Value",
        init_template="{name} = DetrendedPriceOscillator({period})",
        description="추세 제거 가격 오실레이터",
    ),
    "kvo": IndicatorInfo(
        id="kvo",
        name="Klinger Volume Oscillator",
        lean_class="KlingerVolumeOscillator",
        params=["fast", "slow", "signal"],
        value_template="{name}.Current.Value",
        outputs={
            "value": "{name}.Current.Value",
            "signal": "{name}.Signal.Current.Value",
        },
        init_template="{name} = KlingerVolumeOscillator({fast}, {slow}, {signal})",
        description="클링거 거래량 오실레이터",
        requires_tradebar=True,
    ),
    
    # ============================================================
    # 추세 지표 (Trend) - 12개
    # ============================================================
    "adx": IndicatorInfo(
        id="adx",
        name="Average Directional Index",
        lean_class="AverageDirectionalIndex",
        params=["period"],
        value_template="{name}.Current.Value",
        outputs={
            "value": "{name}.Current.Value",
            "plus_di": "{name}.PositiveDirectionalIndex.Current.Value",
            "minus_di": "{name}.NegativeDirectionalIndex.Current.Value",
        },
        init_template="{name} = AverageDirectionalIndex({period})",
        description="평균방향지수",
        requires_tradebar=True,
    ),
    "adxr": IndicatorInfo(
        id="adxr",
        name="Average Directional Movement Rating",
        lean_class="AverageDirectionalMovementIndexRating",
        params=["period"],
        value_template="{name}.Current.Value",
        init_template="{name} = AverageDirectionalMovementIndexRating({period})",
        description="평균방향운동등급",
        requires_tradebar=True,
    ),
    "ichimoku": IndicatorInfo(
        id="ichimoku",
        name="Ichimoku Kinko Hyo",
        lean_class="IchimokuKinkoHyo",
        params=["tenkan", "kijun", "senkou_b"],
        value_template=None,
        outputs={
            "tenkan": "{name}.Tenkan.Current.Value",
            "kijun": "{name}.Kijun.Current.Value",
            "senkou_a": "{name}.SenkouA.Current.Value",
            "senkou_b": "{name}.SenkouB.Current.Value",
            "chikou": "{name}.Chikou.Current.Value",
        },
        init_template="{name} = IchimokuKinkoHyo({tenkan}, {kijun}, {kijun}, {senkou_b}, {kijun})",
        description="일목균형표",
        requires_tradebar=True,
    ),
    "sar": IndicatorInfo(
        id="sar",
        name="Parabolic SAR",
        lean_class="ParabolicStopAndReverse",
        params=["af_start", "af_step", "af_max"],
        value_template="{name}.Current.Value",
        init_template="{name} = ParabolicStopAndReverse({af_start}, {af_step}, {af_max})",
        description="파라볼릭 SAR",
        requires_tradebar=True,
    ),
    "vortex": IndicatorInfo(
        id="vortex",
        name="Vortex Indicator",
        lean_class="Vortex",
        params=["period"],
        value_template=None,
        outputs={
            "plus_vi": "{name}.PlusVortex.Current.Value",
            "minus_vi": "{name}.MinusVortex.Current.Value",
        },
        init_template="{name} = Vortex({period})",
        description="볼텍스 지표",
        requires_tradebar=True,
    ),
    "chop": IndicatorInfo(
        id="chop",
        name="Choppiness Index",
        lean_class="ChoppinessIndex",
        params=["period"],
        value_template="{name}.Current.Value",
        init_template="{name} = ChoppinessIndex({period})",
        description="혼잡 지수",
        requires_tradebar=True,
    ),
    "kst": IndicatorInfo(
        id="kst",
        name="Know Sure Thing",
        lean_class="KnowSureThing",
        params=["roc1", "roc2", "roc3", "roc4"],
        value_template="{name}.Current.Value",
        outputs={
            "value": "{name}.Current.Value",
            "signal": "{name}.Signal.Current.Value",
        },
        init_template="{name} = KnowSureThing({roc1}, {roc2}, {roc3}, {roc4}, 10, 13, 15, 20, 9)",
        description="KST 지표 (Python.NET은 C# 기본값 미지원 → SMA/signal 기본값 명시)",
    ),
    "coppock": IndicatorInfo(
        id="coppock",
        name="Coppock Curve",
        lean_class="CoppockCurve",
        params=["short_roc", "long_roc", "wma"],
        value_template="{name}.Current.Value",
        init_template="{name} = CoppockCurve({short_roc}, {long_roc}, {wma})",
        description="코폭 곡선",
    ),
    "supertrend": IndicatorInfo(
        id="supertrend",
        name="SuperTrend",
        lean_class="SuperTrend",
        params=["period", "multiplier"],
        value_template="{name}.Current.Value",
        init_template="{name} = SuperTrend({period}, {multiplier})",
        description="슈퍼트렌드",
        requires_tradebar=True,
    ),
    "mass_index": IndicatorInfo(
        id="mass_index",
        name="Mass Index",
        lean_class="MassIndex",
        params=["ema_period", "sum_period"],
        value_template="{name}.Current.Value",
        init_template="{name} = MassIndex({ema_period}, {sum_period})",
        description="매스 인덱스",
        requires_tradebar=True,
    ),
    "schaff": IndicatorInfo(
        id="schaff",
        name="Schaff Trend Cycle",
        lean_class="SchaffTrendCycle",
        params=["cycle", "fast", "slow"],
        value_template="{name}.Current.Value",
        init_template="{name} = SchaffTrendCycle({cycle}, {fast}, {slow})",
        description="샤프 추세 사이클",
    ),
    "fisher": IndicatorInfo(
        id="fisher",
        name="Fisher Transform",
        lean_class="FisherTransform",
        params=["period"],
        value_template="{name}.Current.Value",
        init_template="{name} = FisherTransform({period})",
        description="피셔 변환",
        requires_tradebar=True,
    ),
    
    # ============================================================
    # 거래량 지표 (Volume) - 12개
    # ============================================================
    "obv": IndicatorInfo(
        id="obv",
        name="On Balance Volume",
        lean_class="OnBalanceVolume",
        params=[],
        value_template="{name}.Current.Value",
        init_template="{name} = OnBalanceVolume()",
        description="OBV",
        requires_tradebar=True,
    ),
    "ad": IndicatorInfo(
        id="ad",
        name="Accumulation/Distribution",
        lean_class="AccumulationDistribution",
        params=[],
        value_template="{name}.Current.Value",
        init_template="{name} = AccumulationDistribution()",
        description="누적/분산",
        requires_tradebar=True,
    ),
    "adl": IndicatorInfo(
        id="adl",
        name="Accumulation/Distribution Line",
        lean_class="AccumulationDistribution",
        params=[],
        value_template="{name}.Current.Value",
        init_template="{name} = AccumulationDistribution()",
        description="누적/분산 라인 (AccumulationDistribution 별칭)",
        requires_tradebar=True,
    ),
    "cmf": IndicatorInfo(
        id="cmf",
        name="Chaikin Money Flow",
        lean_class="ChaikinMoneyFlow",
        params=["period"],
        value_template="{name}.Current.Value",
        init_template="{name} = ChaikinMoneyFlow({period})",
        description="채킨 머니플로우",
        requires_tradebar=True,
    ),
    "mfi": IndicatorInfo(
        id="mfi",
        name="Money Flow Index",
        lean_class="MoneyFlowIndex",
        params=["period"],
        value_template="{name}.Current.Value",
        init_template="{name} = MoneyFlowIndex({period})",
        description="자금흐름지수",
        requires_tradebar=True,
    ),
    "force": IndicatorInfo(
        id="force",
        name="Force Index",
        lean_class="ForceIndex",
        params=["period"],
        value_template="{name}.Current.Value",
        init_template="{name} = ForceIndex({period})",
        description="포스 인덱스",
        requires_tradebar=True,
    ),
    "vwap": IndicatorInfo(
        id="vwap",
        name="Volume Weighted Average Price",
        lean_class="VolumeWeightedAveragePriceIndicator",
        params=["period"],
        value_template="{name}.Current.Value",
        init_template="{name} = VolumeWeightedAveragePriceIndicator({period})",
        description="거래량 가중 평균가",
        requires_tradebar=True,
    ),
    "vwma": IndicatorInfo(
        id="vwma",
        name="Volume Weighted Moving Average",
        lean_class="VolumeWeightedMovingAverage",
        params=["period"],
        value_template="{name}.Current.Value",
        init_template="{name} = VolumeWeightedMovingAverage({period})",
        description="거래량 가중 이동평균",
        requires_tradebar=True,
    ),
    "eom": IndicatorInfo(
        id="eom",
        name="Ease of Movement",
        lean_class="EaseOfMovementValue",
        params=["period", "scale"],
        value_template="{name}.Current.Value",
        init_template="{name} = EaseOfMovementValue({period}, {scale})",
        description="움직임의 용이성",
        requires_tradebar=True,
    ),
    
    # ============================================================
    # 변동성 지표 (Volatility) - 10개
    # ============================================================
    "atr": IndicatorInfo(
        id="atr",
        name="Average True Range",
        lean_class="AverageTrueRange",
        params=["period"],
        value_template="{name}.Current.Value",
        init_template="{name} = AverageTrueRange({period}, MovingAverageType.Simple)",
        description="평균진폭",
        requires_tradebar=True,
    ),
    "natr": IndicatorInfo(
        id="natr",
        name="Normalized Average True Range",
        lean_class="NormalizedAverageTrueRange",
        params=["period"],
        value_template="{name}.Current.Value",
        init_template="{name} = NormalizedAverageTrueRange({period})",
        description="정규화 ATR",
        requires_tradebar=True,
    ),
    "bollinger": IndicatorInfo(
        id="bollinger",
        name="Bollinger Bands",
        lean_class="BollingerBands",
        params=["period", "std"],
        value_template=None,
        outputs={
            "upper": "{name}.UpperBand.Current.Value",
            "middle": "{name}.MiddleBand.Current.Value",
            "lower": "{name}.LowerBand.Current.Value",
        },
        init_template="{name} = BollingerBands({period}, {std}, MovingAverageType.Simple)",
        description="볼린저 밴드",
    ),
    "keltner": IndicatorInfo(
        id="keltner",
        name="Keltner Channels",
        lean_class="KeltnerChannels",
        params=["period", "multiplier"],
        value_template=None,
        outputs={
            "upper": "{name}.UpperBand.Current.Value",
            "middle": "{name}.MiddleBand.Current.Value",
            "lower": "{name}.LowerBand.Current.Value",
        },
        init_template="{name} = KeltnerChannels({period}, {multiplier}, MovingAverageType.Simple)",
        description="켈트너 채널",
        requires_tradebar=True,
    ),
    "donchian": IndicatorInfo(
        id="donchian",
        name="Donchian Channel",
        lean_class="DonchianChannel",
        params=["period"],
        value_template=None,
        outputs={
            "upper": "{name}.UpperBand.Current.Value",
            "lower": "{name}.LowerBand.Current.Value",
        },
        init_template="{name} = DonchianChannel({period})",
        description="돈치안 채널",
        requires_tradebar=True,
    ),
    "std": IndicatorInfo(
        id="std",
        name="Standard Deviation",
        lean_class="StandardDeviation",
        params=["period"],
        value_template="{name}.Current.Value",
        init_template="{name} = StandardDeviation({period})",
        description="표준편차",
    ),
    "variance": IndicatorInfo(
        id="variance",
        name="Variance",
        lean_class="Variance",
        params=["period"],
        value_template="{name}.Current.Value",
        init_template="{name} = Variance({period})",
        description="분산",
    ),
    "accbands": IndicatorInfo(
        id="accbands",
        name="Acceleration Bands",
        lean_class="AccelerationBands",
        params=["period", "width"],
        value_template=None,
        outputs={
            "upper": "{name}.UpperBand.Current.Value",
            "middle": "{name}.MiddleBand.Current.Value",
            "lower": "{name}.LowerBand.Current.Value",
        },
        init_template="{name} = AccelerationBands({period}, {width})",
        description="가속 밴드",
        requires_tradebar=True,
    ),
    "beta": IndicatorInfo(
        id="beta",
        name="Beta",
        lean_class="Beta",
        params=["period"],
        value_template="{name}.Current.Value",
        init_template="{name} = Beta({period})",
        description="베타",
    ),
    "alpha": IndicatorInfo(
        id="alpha",
        name="Alpha",
        lean_class="Alpha",
        params=["period"],
        value_template="{name}.Current.Value",
        init_template="{name} = Alpha({period})",
        description="알파",
    ),
    
    # ============================================================
    # 기타 지표 (Misc) - 10개
    # ============================================================
    "maximum": IndicatorInfo(
        id="maximum",
        name="Maximum",
        lean_class="Maximum",
        params=["period"],
        value_template="{name}.Current.Value",
        init_template="{name} = Maximum({period})",
        description="기간 내 최고가",
    ),
    "minimum": IndicatorInfo(
        id="minimum",
        name="Minimum",
        lean_class="Minimum",
        params=["period"],
        value_template="{name}.Current.Value",
        init_template="{name} = Minimum({period})",
        description="기간 내 최저가",
    ),
    "midpoint": IndicatorInfo(
        id="midpoint",
        name="Mid Point",
        lean_class="MidPoint",
        params=["period"],
        value_template="{name}.Current.Value",
        init_template="{name} = MidPoint({period})",
        description="중간값",
    ),
    "midprice": IndicatorInfo(
        id="midprice",
        name="Mid Price",
        lean_class="MidPrice",
        params=["period"],
        value_template="{name}.Current.Value",
        init_template="{name} = MidPrice({period})",
        description="중간가격",
        requires_tradebar=True,
    ),
    "logr": IndicatorInfo(
        id="logr",
        name="Log Return",
        lean_class="LogReturn",
        params=["period"],
        value_template="{name}.Current.Value",
        init_template="{name} = LogReturn({period})",
        description="로그 수익률",
    ),
    "ibs": IndicatorInfo(
        id="ibs",
        name="Internal Bar Strength",
        lean_class="InternalBarStrength",
        params=[],
        value_template="{name}.Current.Value",
        init_template="{name} = InternalBarStrength()",
        description="내부 바 강도",
        requires_tradebar=True,
    ),
    "bop": IndicatorInfo(
        id="bop",
        name="Balance of Power",
        lean_class="BalanceOfPower",
        params=[],
        value_template="{name}.Current.Value",
        init_template="{name} = BalanceOfPower()",
        description="힘의 균형",
        requires_tradebar=True,
    ),
    "regression": IndicatorInfo(
        id="regression",
        name="Linear Regression",
        lean_class="LeastSquaresMovingAverage",
        params=["period"],
        value_template="{name}.Current.Value",
        outputs={
            "value": "{name}.Current.Value",
            "slope": "{name}.Slope.Current.Value",
            "intercept": "{name}.Intercept.Current.Value",
        },
        init_template="{name} = LeastSquaresMovingAverage({period})",
        description="선형 회귀",
    ),
    "pivot": IndicatorInfo(
        id="pivot",
        name="Pivot Points",
        lean_class="PivotPointsHighLow",
        params=["left_bars", "right_bars"],
        value_template=None,
        outputs={
            "high": "{name}.High.Current.Value",
            "low": "{name}.Low.Current.Value",
        },
        init_template="{name} = PivotPointsHighLow({left_bars}, {right_bars})",
        description="피봇 포인트",
        requires_tradebar=True,
    ),
    "augen": IndicatorInfo(
        id="augen",
        name="Augen Price Spike",
        lean_class="AugenPriceSpike",
        params=["period"],
        value_template="{name}.Current.Value",
        init_template="{name} = AugenPriceSpike({period})",
        description="오겐 가격 스파이크",
    ),
    # ============================================================
    # 커스텀 지표 (Custom Indicators)
    # ============================================================
    "consecutive": IndicatorInfo(
        id="consecutive",
        name="Consecutive Days",
        lean_class="ConsecutiveDays",  # 커스텀 구현 필요
        params=["direction"],
        value_template="{name}",
        init_template="{name} = 0  # Consecutive {direction} counter",
        description="연속 상승/하락 일수 (커스텀 지표)",
    ),
    "disparity": IndicatorInfo(
        id="disparity",
        name="Disparity Index",
        lean_class="",
        params=["period"],
        value_template="{name}",
        init_template="{name}_sma = SimpleMovingAverage({period})",
        description="이격도 (현재가 / SMA * 100)",
    ),
    "volatility_ind": IndicatorInfo(
        id="volatility_ind",
        name="Volatility",
        lean_class="",
        params=["period"],
        value_template="{name}",
        init_template="{name}_std = StandardDeviation({period})",
        description="변동성 (일간 수익률의 표준편차)",
    ),
    "change": IndicatorInfo(
        id="change",
        name="Daily Change",
        lean_class="",
        params=[],
        value_template="{name}",
        init_template="{name} = 0",
        description="전일대비 등락률 (%)",
    ),
    "returns": IndicatorInfo(
        id="returns",
        name="Returns",
        lean_class="",
        params=["period"],
        value_template="{name}",
        init_template="{name}_roc = RateOfChangePercent({period})",
        description="N일 수익률",
    ),
}


def get_indicator_info(indicator_id: str) -> Optional[IndicatorInfo]:
    """지표 정보 조회"""
    return INDICATOR_REGISTRY.get(indicator_id)


def list_indicators() -> List[Dict[str, Any]]:
    """모든 지표 목록"""
    return [
        {
            "id": info.id,
            "name": info.name,
            "params": info.params,
            "description": info.description,
            "has_multiple_outputs": bool(info.outputs),
        }
        for info in INDICATOR_REGISTRY.values()
    ]


# ============================================================
# Price 클래스 (가격 데이터)
# ============================================================

class Price:
    """가격 데이터
    
    현재가, 고가, 저가, 시가에 접근.
    
    Example:
        condition = Price.close() > SMA(20)  # 현재가가 20일 이평선 위
    """
    @staticmethod
    def close() -> Indicator:
        """종가 (Close)"""
        return Indicator("price", {}, alias="close", output="close")
    
    @staticmethod
    def high() -> Indicator:
        """고가 (High)"""
        return Indicator("price", {}, alias="high", output="high")
    
    @staticmethod
    def low() -> Indicator:
        """저가 (Low)"""
        return Indicator("price", {}, alias="low", output="low")
    
    @staticmethod
    def open() -> Indicator:
        """시가 (Open)"""
        return Indicator("price", {}, alias="open", output="open")
    
    @staticmethod
    def volume() -> Indicator:
        """거래량 (Volume)"""
        return Indicator("volume", {}, alias="volume", output="value")


# ============================================================
# Bollinger Bands 클래스 (다중 출력)
# ============================================================

class BollingerBands:
    """볼린저 밴드 (다중 출력)
    
    상단, 중단, 하단 밴드에 각각 접근 가능.
    
    Example:
        bb = BB(20, 2.0)
        buy_condition = Price.close() < bb.lower
        sell_condition = Price.close() > bb.upper
    """
    def __init__(self, period: int = 20, std: float = 2.0):
        self.period = period
        self.std = std
    
    @property
    def _base_alias(self) -> str:
        """공통 alias (멀티 아웃풋 지표는 같은 alias 사용)"""
        return f"bb_{self.period}"
    
    @property
    def upper(self) -> Indicator:
        """상단 밴드"""
        return Indicator(
            "bollinger",
            {"period": self.period, "std": self.std},
            alias=self._base_alias,
            output="upper"
        )
    
    @property
    def middle(self) -> Indicator:
        """중간 밴드 (SMA)"""
        return Indicator(
            "bollinger",
            {"period": self.period, "std": self.std},
            alias=self._base_alias,
            output="middle"
        )
    
    @property
    def lower(self) -> Indicator:
        """하단 밴드"""
        return Indicator(
            "bollinger",
            {"period": self.period, "std": self.std},
            alias=self._base_alias,
            output="lower"
        )
