"""DSL (Domain Specific Language) for strategy building.

Provides fluent API for creating strategies without code.
"""

from kis_backtest.dsl.builder import RuleBuilder, StrategyRule
from kis_backtest.dsl.helpers import (
    # ============================================================
    # 이동평균 (14개)
    # ============================================================
    SMA,
    EMA,
    DEMA,
    TEMA,
    HMA,
    KAMA,
    ALMA,
    LWMA,
    TRIMA,
    T3,
    ZLEMA,
    WMA,
    FRAMA,
    VIDYA,

    # ============================================================
    # 오실레이터 (20개)
    # ============================================================
    RSI,
    STOCH,
    Stochastic,
    STOCHRSI,
    MACD,
    CCI,
    WILLIAMS_R,
    MOMENTUM,
    ROC,
    APO,
    PPO,
    AROON,
    CMO,
    AO,
    CHO,
    ULTOSC,
    TRIX,
    TSI,
    RVI,
    DPO,
    KVO,

    # ============================================================
    # 추세 지표 (12개)
    # ============================================================
    ADX,
    ADXR,
    SAR,
    CHOP,
    COPPOCK,
    SUPERTREND,
    MASS_INDEX,
    SCHAFF,
    FISHER,
    KST,
    VORTEX,

    # ============================================================
    # 거래량 (12개)
    # ============================================================
    OBV,
    AD,
    ADL,
    CMF,
    MFI,
    FORCE,
    VWAP,
    VWMA,
    EOM,

    # ============================================================
    # 변동성 (10개)
    # ============================================================
    ATR,
    NATR,
    BB,
    STD,
    VARIANCE,
    BETA,
    ALPHA,

    # ============================================================
    # 기타 (10개)
    # ============================================================
    MAXIMUM,
    Maximum,
    MINIMUM,
    Minimum,
    MIDPOINT,
    MIDPRICE,
    LOGR,
    IBS,
    BOP,
    REGRESSION,
    PIVOT,
    AUGEN,

    # ============================================================
    # 멀티 아웃풋 클래스 (5개)
    # ============================================================
    BollingerBands,
    IchimokuCloud,
    KeltnerChannels,
    DonchianChannel,
    AccelerationBands,

    # ============================================================
    # Price 클래스
    # ============================================================
    Price,

    # ============================================================
    # Candlestick Patterns (19개)
    # ============================================================
    Doji,
    DragonflyDoji,
    GravestoneDoji,
    Hammer,
    HangingMan,
    InvertedHammer,
    ShootingStar,
    Marubozu,
    SpinningTop,
    BeltHold,
    Engulfing,
    Harami,
    HaramiCross,
    Piercing,
    DarkCloudCover,
    MorningStar,
    EveningStar,
    ThreeWhiteSoldiers,
    ThreeBlackCrows,
)

__all__ = [
    # Builder
    "RuleBuilder",
    "StrategyRule",

    # ============================================================
    # 이동평균 (14개)
    # ============================================================
    "SMA",
    "EMA",
    "DEMA",
    "TEMA",
    "HMA",
    "KAMA",
    "ALMA",
    "LWMA",
    "TRIMA",
    "T3",
    "ZLEMA",
    "WMA",
    "FRAMA",
    "VIDYA",

    # ============================================================
    # 오실레이터 (20개)
    # ============================================================
    "RSI",
    "STOCH",
    "Stochastic",
    "STOCHRSI",
    "MACD",
    "CCI",
    "WILLIAMS_R",
    "MOMENTUM",
    "ROC",
    "APO",
    "PPO",
    "AROON",
    "CMO",
    "AO",
    "CHO",
    "ULTOSC",
    "TRIX",
    "TSI",
    "RVI",
    "DPO",
    "KVO",

    # ============================================================
    # 추세 지표 (12개)
    # ============================================================
    "ADX",
    "ADXR",
    "SAR",
    "CHOP",
    "COPPOCK",
    "SUPERTREND",
    "MASS_INDEX",
    "SCHAFF",
    "FISHER",
    "KST",
    "VORTEX",

    # ============================================================
    # 거래량 (12개)
    # ============================================================
    "OBV",
    "AD",
    "ADL",
    "CMF",
    "MFI",
    "FORCE",
    "VWAP",
    "VWMA",
    "EOM",

    # ============================================================
    # 변동성 (10개)
    # ============================================================
    "ATR",
    "NATR",
    "BB",
    "STD",
    "VARIANCE",
    "BETA",
    "ALPHA",

    # ============================================================
    # 기타 (10개)
    # ============================================================
    "MAXIMUM",
    "Maximum",
    "MINIMUM",
    "Minimum",
    "MIDPOINT",
    "MIDPRICE",
    "LOGR",
    "IBS",
    "BOP",
    "REGRESSION",
    "PIVOT",
    "AUGEN",

    # ============================================================
    # 멀티 아웃풋 클래스 (5개)
    # ============================================================
    "BollingerBands",
    "IchimokuCloud",
    "KeltnerChannels",
    "DonchianChannel",
    "AccelerationBands",

    # ============================================================
    # Price 클래스
    # ============================================================
    "Price",

    # ============================================================
    # Candlestick Patterns (19개)
    # ============================================================
    "Doji",
    "DragonflyDoji",
    "GravestoneDoji",
    "Hammer",
    "HangingMan",
    "InvertedHammer",
    "ShootingStar",
    "Marubozu",
    "SpinningTop",
    "BeltHold",
    "Engulfing",
    "Harami",
    "HaramiCross",
    "Piercing",
    "DarkCloudCover",
    "MorningStar",
    "EveningStar",
    "ThreeWhiteSoldiers",
    "ThreeBlackCrows",
]
