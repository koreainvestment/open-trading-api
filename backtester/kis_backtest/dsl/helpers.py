"""Indicator factory functions for DSL.

Provides convenient functions to create indicator instances.

Example:
    from kis_backtest.dsl import SMA, RSI, Price

    condition = (SMA(5) > SMA(20)) & (RSI(14) < 70)
"""

from kis_backtest.core.indicator import Indicator, BollingerBands, Price
from kis_backtest.core.candlestick import CandlestickPattern


# ============================================================
# 이동평균 계열 (Moving Averages) - 14개
# ============================================================

def SMA(period: int, alias: str = None) -> Indicator:
    """단순 이동평균 (Simple Moving Average)

    Args:
        period: 이동평균 기간
        alias: 지표 별칭

    Example:
        sma20 = SMA(20)
        condition = SMA(5) > SMA(20)  # 골든크로스 조건
    """
    return Indicator("sma", {"period": period}, alias=alias)


def EMA(period: int, alias: str = None) -> Indicator:
    """지수 이동평균 (Exponential Moving Average)

    Args:
        period: 이동평균 기간
        alias: 지표 별칭

    Example:
        ema12 = EMA(12)
        condition = EMA(12) > EMA(26)
    """
    return Indicator("ema", {"period": period}, alias=alias)


def DEMA(period: int = 21, alias: str = None) -> Indicator:
    """이중 지수 이동평균 (Double Exponential Moving Average)

    Args:
        period: 이동평균 기간 (기본값: 21)
        alias: 지표 별칭

    Example:
        dema = DEMA(21)
        condition = Price.close() > DEMA(21)
    """
    return Indicator("dema", {"period": period}, alias=alias)


def TEMA(period: int = 21, alias: str = None) -> Indicator:
    """삼중 지수 이동평균 (Triple Exponential Moving Average)

    Args:
        period: 이동평균 기간 (기본값: 21)
        alias: 지표 별칭

    Example:
        tema = TEMA(21)
        condition = Price.close() > TEMA(21)
    """
    return Indicator("tema", {"period": period}, alias=alias)


def HMA(period: int = 21, alias: str = None) -> Indicator:
    """헐 이동평균 (Hull Moving Average)

    노이즈를 줄이고 추세 전환을 빠르게 포착.

    Args:
        period: 이동평균 기간 (기본값: 21)
        alias: 지표 별칭

    Example:
        condition = Price.close() > HMA(21)
    """
    return Indicator("hma", {"period": period}, alias=alias)


def KAMA(period: int = 21, alias: str = None) -> Indicator:
    """카우프만 적응형 이동평균 (Kaufman Adaptive Moving Average)

    시장 상황에 따라 감도를 자동 조절.

    Args:
        period: 이동평균 기간 (기본값: 21)
        alias: 지표 별칭

    Example:
        condition = Price.close() > KAMA(21)
    """
    return Indicator("kama", {"period": period}, alias=alias)


def ALMA(
    period: int = 21,
    sigma: float = 6.0,
    offset: float = 0.85,
    alias: str = None
) -> Indicator:
    """아르노 르구 이동평균 (Arnaud Legoux Moving Average)

    가우시안 분포를 이용한 이동평균. 노이즈 감소와 지연 최소화.

    Args:
        period: 이동평균 기간 (기본값: 21)
        sigma: 가우시안 분포 표준편차 (기본값: 6.0)
        offset: 가우시안 분포 중심 (기본값: 0.85, 0~1)
        alias: 지표 별칭

    Example:
        condition = Price.close() > ALMA(21, 6.0, 0.85)
    """
    return Indicator(
        "alma",
        {"period": period, "sigma": sigma, "offset": offset},
        alias=alias
    )


def LWMA(period: int = 21, alias: str = None) -> Indicator:
    """선형 가중 이동평균 (Linear Weighted Moving Average)

    최근 가격에 더 높은 가중치 부여.

    Args:
        period: 이동평균 기간 (기본값: 21)
        alias: 지표 별칭

    Example:
        condition = Price.close() > LWMA(21)
    """
    return Indicator("lwma", {"period": period}, alias=alias)


def TRIMA(period: int = 21, alias: str = None) -> Indicator:
    """삼각 이동평균 (Triangular Moving Average)

    중앙 데이터에 더 높은 가중치 부여.

    Args:
        period: 이동평균 기간 (기본값: 21)
        alias: 지표 별칭

    Example:
        condition = Price.close() > TRIMA(21)
    """
    return Indicator("trima", {"period": period}, alias=alias)


def T3(period: int = 5, volume_factor: float = 0.7, alias: str = None) -> Indicator:
    """T3 이동평균 (T3 Moving Average)

    지수 이동평균을 여러 번 적용하여 부드러움과 빠른 반응 동시 달성.

    Args:
        period: 이동평균 기간 (기본값: 5)
        volume_factor: 볼륨 팩터 (기본값: 0.7, 0~1)
        alias: 지표 별칭

    Example:
        condition = Price.close() > T3(5, 0.7)
    """
    return Indicator(
        "t3",
        {"period": period, "volume_factor": volume_factor},
        alias=alias
    )


def ZLEMA(period: int = 21, alias: str = None) -> Indicator:
    """제로 래그 지수 이동평균 (Zero Lag Exponential Moving Average)

    지연을 최소화한 지수 이동평균.

    Args:
        period: 이동평균 기간 (기본값: 21)
        alias: 지표 별칭

    Example:
        condition = Price.close() > ZLEMA(21)
    """
    return Indicator("zlema", {"period": period}, alias=alias)


def WMA(period: int = 21, alias: str = None) -> Indicator:
    """와일더 이동평균 (Wilder Moving Average)

    J. Welles Wilder가 개발한 이동평균. RSI, ATR 등의 기초.

    Args:
        period: 이동평균 기간 (기본값: 21)
        alias: 지표 별칭

    Example:
        condition = Price.close() > WMA(21)
    """
    return Indicator("wma", {"period": period}, alias=alias)


def FRAMA(period: int = 21, alias: str = None) -> Indicator:
    """프랙탈 적응형 이동평균 (Fractal Adaptive Moving Average)

    시장의 프랙탈 차원에 따라 감도 조절.

    Args:
        period: 이동평균 기간 (기본값: 21)
        alias: 지표 별칭

    Example:
        condition = Price.close() > FRAMA(21)
    """
    return Indicator("frama", {"period": period}, alias=alias)


def VIDYA(period: int = 21, alias: str = None) -> Indicator:
    """VIDYA 이동평균 (Variable Index Dynamic Average)

    Chande Momentum에 기반한 적응형 이동평균.

    Args:
        period: 이동평균 기간 (기본값: 21)
        alias: 지표 별칭

    Example:
        condition = Price.close() > VIDYA(21)
    """
    return Indicator("vidya", {"period": period}, alias=alias)


# ============================================================
# 오실레이터 계열 (Oscillators) - 20개
# ============================================================

def RSI(period: int = 14, alias: str = None) -> Indicator:
    """상대강도지수 (Relative Strength Index)

    Args:
        period: RSI 계산 기간 (기본값: 14)
        alias: 지표 별칭

    Example:
        condition = RSI(14) < 30  # 과매도 조건
    """
    return Indicator("rsi", {"period": period}, alias=alias)


def STOCH(
    k_period: int = 14,
    d_period: int = 3,
    output: str = "k",
    alias: str = None
) -> Indicator:
    """스토캐스틱 (Stochastic Oscillator)

    Args:
        k_period: %K 기간 (기본값: 14)
        d_period: %D 기간 (기본값: 3)
        output: 출력값 ("k" 또는 "d")
        alias: 지표 별칭

    Example:
        stoch_k = STOCH(14, 3, output="k")
        stoch_d = STOCH(14, 3, output="d")
        condition = stoch_k.crosses_above(stoch_d)
    """
    return Indicator(
        "stochastic",
        {"k_period": k_period, "d_period": d_period},
        output=output,
        alias=alias
    )


def STOCHRSI(
    rsi_period: int = 14,
    stoch_period: int = 14,
    k_period: int = 3,
    d_period: int = 3,
    output: str = "k",
    alias: str = None
) -> Indicator:
    """스토캐스틱 RSI (Stochastic RSI)

    RSI에 스토캐스틱 공식을 적용한 지표.

    Args:
        rsi_period: RSI 기간 (기본값: 14)
        stoch_period: 스토캐스틱 기간 (기본값: 14)
        k_period: %K 기간 (기본값: 3)
        d_period: %D 기간 (기본값: 3)
        output: 출력값 ("k" 또는 "d")
        alias: 지표 별칭

    Example:
        stochrsi_k = STOCHRSI(output="k")
        stochrsi_d = STOCHRSI(output="d")
        condition = stochrsi_k.crosses_above(stochrsi_d)
    """
    return Indicator(
        "stochrsi",
        {
            "rsi_period": rsi_period,
            "stoch_period": stoch_period,
            "k_period": k_period,
            "d_period": d_period,
        },
        output=output,
        alias=alias
    )


def MACD(
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
    output: str = "value",
    alias: str = None
) -> Indicator:
    """MACD (Moving Average Convergence Divergence)

    Args:
        fast: 빠른 EMA 기간 (기본값: 12)
        slow: 느린 EMA 기간 (기본값: 26)
        signal: 시그널 EMA 기간 (기본값: 9)
        output: 출력값 ("value", "signal", "histogram")
        alias: 지표 별칭

    Example:
        macd = MACD()
        macd_signal = MACD(output="signal")
        condition = macd.crosses_above(macd_signal)
    """
    return Indicator(
        "macd",
        {"fast": fast, "slow": slow, "signal": signal},
        output=output,
        alias=alias
    )


def CCI(period: int = 20, alias: str = None) -> Indicator:
    """상품채널지수 (Commodity Channel Index)

    Args:
        period: CCI 계산 기간 (기본값: 20)
        alias: 지표 별칭

    Example:
        condition = CCI(20) < -100  # 과매도
    """
    return Indicator("cci", {"period": period}, alias=alias)


def WILLIAMS_R(period: int = 14, alias: str = None) -> Indicator:
    """윌리엄스 %R (Williams Percent R)

    과매수/과매도 판단 지표. -100~0 범위.

    Args:
        period: 계산 기간 (기본값: 14)
        alias: 지표 별칭

    Example:
        condition = WILLIAMS_R(14) < -80  # 과매도
    """
    return Indicator("williams_r", {"period": period}, alias=alias)


def MOMENTUM(period: int = 10, alias: str = None) -> Indicator:
    """모멘텀 (Momentum Percent)

    Args:
        period: 모멘텀 계산 기간 (기본값: 10)
        alias: 지표 별칭

    Example:
        condition = MOMENTUM(10) > 0
    """
    return Indicator("momentum", {"period": period}, alias=alias)


def ROC(period: int = 10, alias: str = None) -> Indicator:
    """변화율 (Rate of Change Percent)

    Args:
        period: ROC 계산 기간 (기본값: 10)
        alias: 지표 별칭

    Example:
        condition = ROC(10) > 5  # 10일간 5% 이상 상승
    """
    return Indicator("roc", {"period": period}, alias=alias)


def APO(fast: int = 12, slow: int = 26, alias: str = None) -> Indicator:
    """절대 가격 오실레이터 (Absolute Price Oscillator)

    두 EMA의 차이를 절대값으로 표시.

    Args:
        fast: 빠른 EMA 기간 (기본값: 12)
        slow: 느린 EMA 기간 (기본값: 26)
        alias: 지표 별칭

    Example:
        condition = APO(12, 26) > 0
    """
    return Indicator("apo", {"fast": fast, "slow": slow}, alias=alias)


def PPO(
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
    output: str = "value",
    alias: str = None
) -> Indicator:
    """백분율 가격 오실레이터 (Percentage Price Oscillator)

    MACD와 유사하나 백분율로 표시.

    Args:
        fast: 빠른 EMA 기간 (기본값: 12)
        slow: 느린 EMA 기간 (기본값: 26)
        signal: 시그널 EMA 기간 (기본값: 9)
        output: 출력값 ("value", "signal", "histogram")
        alias: 지표 별칭

    Example:
        ppo = PPO()
        ppo_signal = PPO(output="signal")
        condition = ppo.crosses_above(ppo_signal)
    """
    return Indicator(
        "ppo",
        {"fast": fast, "slow": slow, "signal": signal},
        output=output,
        alias=alias
    )


def AROON(
    up_period: int = 25,
    down_period: int = 25,
    output: str = "value",
    alias: str = None
) -> Indicator:
    """아룬 오실레이터 (Aroon Oscillator)

    추세의 강도와 방향 측정.

    Args:
        up_period: 상승 기간 (기본값: 25)
        down_period: 하락 기간 (기본값: 25)
        output: 출력값 ("value", "aroon_up", "aroon_down")
        alias: 지표 별칭

    Example:
        aroon = AROON(25, 25)
        aroon_up = AROON(25, 25, output="aroon_up")
        condition = aroon > 50  # 상승 추세
    """
    return Indicator(
        "aroon",
        {"up_period": up_period, "down_period": down_period},
        output=output,
        alias=alias
    )


def CMO(period: int = 14, alias: str = None) -> Indicator:
    """챈드 모멘텀 오실레이터 (Chande Momentum Oscillator)

    -100~+100 범위의 모멘텀 지표.

    Args:
        period: 계산 기간 (기본값: 14)
        alias: 지표 별칭

    Example:
        condition = CMO(14) > 50  # 강한 상승 모멘텀
    """
    return Indicator("cmo", {"period": period}, alias=alias)


def AO(fast: int = 5, slow: int = 34, alias: str = None) -> Indicator:
    """오썸 오실레이터 (Awesome Oscillator)

    Bill Williams의 시장 모멘텀 지표.

    Args:
        fast: 빠른 SMA 기간 (기본값: 5)
        slow: 느린 SMA 기간 (기본값: 34)
        alias: 지표 별칭

    Example:
        condition = AO() > 0  # 상승 모멘텀
    """
    return Indicator("ao", {"fast": fast, "slow": slow}, alias=alias)


def CHO(fast: int = 3, slow: int = 10, alias: str = None) -> Indicator:
    """채킨 오실레이터 (Chaikin Oscillator)

    ADL의 MACD. 매집/분산 추세 측정.

    Args:
        fast: 빠른 EMA 기간 (기본값: 3)
        slow: 느린 EMA 기간 (기본값: 10)
        alias: 지표 별칭

    Example:
        condition = CHO() > 0  # 매집 추세
    """
    return Indicator("cho", {"fast": fast, "slow": slow}, alias=alias)


def ULTOSC(
    period1: int = 7,
    period2: int = 14,
    period3: int = 28,
    alias: str = None
) -> Indicator:
    """궁극 오실레이터 (Ultimate Oscillator)

    세 가지 기간을 결합한 모멘텀 오실레이터.

    Args:
        period1: 단기 기간 (기본값: 7)
        period2: 중기 기간 (기본값: 14)
        period3: 장기 기간 (기본값: 28)
        alias: 지표 별칭

    Example:
        condition = ULTOSC() < 30  # 과매도
    """
    return Indicator(
        "ultosc",
        {"period1": period1, "period2": period2, "period3": period3},
        alias=alias
    )


def TRIX(period: int = 15, alias: str = None) -> Indicator:
    """TRIX 오실레이터 (Triple Exponential Average ROC)

    삼중 EMA의 변화율.

    Args:
        period: 계산 기간 (기본값: 15)
        alias: 지표 별칭

    Example:
        condition = TRIX(15) > 0  # 상승 추세
    """
    return Indicator("trix", {"period": period}, alias=alias)


def TSI(
    long_period: int = 25,
    short_period: int = 13,
    signal_period: int = 7,
    output: str = "value",
    alias: str = None
) -> Indicator:
    """참 강도 지수 (True Strength Index)

    이중 평활 모멘텀 오실레이터.

    Args:
        long_period: 장기 기간 (기본값: 25)
        short_period: 단기 기간 (기본값: 13)
        signal_period: 시그널 기간 (기본값: 7)
        output: 출력값 ("value", "signal")
        alias: 지표 별칭

    Example:
        tsi = TSI()
        tsi_signal = TSI(output="signal")
        condition = tsi.crosses_above(tsi_signal)
    """
    return Indicator(
        "tsi",
        {
            "long_period": long_period,
            "short_period": short_period,
            "signal_period": signal_period,
        },
        output=output,
        alias=alias
    )


def RVI(period: int = 10, alias: str = None) -> Indicator:
    """상대 활력 지수 (Relative Vigor Index)

    종가가 고가에 가까울수록 상승 추세.

    Args:
        period: 계산 기간 (기본값: 10)
        alias: 지표 별칭

    Example:
        condition = RVI(10) > 0  # 상승 추세
    """
    return Indicator("rvi", {"period": period}, alias=alias)


def DPO(period: int = 21, alias: str = None) -> Indicator:
    """추세 제거 가격 오실레이터 (Detrended Price Oscillator)

    장기 추세를 제거하여 단기 사이클 분석.

    Args:
        period: 계산 기간 (기본값: 21)
        alias: 지표 별칭

    Example:
        condition = DPO(21) > 0  # 단기 상승
    """
    return Indicator("dpo", {"period": period}, alias=alias)


def KVO(
    fast: int = 34,
    slow: int = 55,
    signal: int = 13,
    output: str = "value",
    alias: str = None
) -> Indicator:
    """클링거 거래량 오실레이터 (Klinger Volume Oscillator)

    거래량 기반 추세 지표.

    Args:
        fast: 빠른 EMA 기간 (기본값: 34)
        slow: 느린 EMA 기간 (기본값: 55)
        signal: 시그널 EMA 기간 (기본값: 13)
        output: 출력값 ("value", "signal")
        alias: 지표 별칭

    Example:
        kvo = KVO()
        kvo_signal = KVO(output="signal")
        condition = kvo.crosses_above(kvo_signal)
    """
    return Indicator(
        "kvo",
        {"fast": fast, "slow": slow, "signal": signal},
        output=output,
        alias=alias
    )


# ============================================================
# 추세 지표 (Trend) - 12개
# ============================================================

def ADX(period: int = 14, output: str = "value", alias: str = None) -> Indicator:
    """평균방향지수 (Average Directional Index)

    추세의 강도 측정 (방향 무관).

    Args:
        period: ADX 계산 기간 (기본값: 14)
        output: 출력값 ("value", "plus_di", "minus_di")
        alias: 지표 별칭

    Example:
        condition = ADX(14) > 25  # 강한 추세
    """
    return Indicator("adx", {"period": period}, output=output, alias=alias)


def ADXR(period: int = 14, alias: str = None) -> Indicator:
    """평균방향운동등급 (Average Directional Movement Index Rating)

    ADX의 평균. 추세 강도의 지연 확인.

    Args:
        period: 계산 기간 (기본값: 14)
        alias: 지표 별칭

    Example:
        condition = ADXR(14) > 25  # 강한 추세 확인
    """
    return Indicator("adxr", {"period": period}, alias=alias)


def SAR(
    af_start: float = 0.02,
    af_step: float = 0.02,
    af_max: float = 0.2,
    alias: str = None
) -> Indicator:
    """파라볼릭 SAR (Parabolic Stop and Reverse)

    추세 추종 및 손절 지점 설정.

    Args:
        af_start: 가속 팩터 시작값 (기본값: 0.02)
        af_step: 가속 팩터 증분 (기본값: 0.02)
        af_max: 가속 팩터 최대값 (기본값: 0.2)
        alias: 지표 별칭

    Example:
        condition = Price.close() > SAR()  # 상승 추세
    """
    return Indicator(
        "sar",
        {"af_start": af_start, "af_step": af_step, "af_max": af_max},
        alias=alias
    )


def CHOP(period: int = 14, alias: str = None) -> Indicator:
    """혼잡 지수 (Choppiness Index)

    시장이 추세인지 횡보인지 판단. 0~100 범위.

    Args:
        period: 계산 기간 (기본값: 14)
        alias: 지표 별칭

    Example:
        condition = CHOP(14) < 38.2  # 강한 추세
    """
    return Indicator("chop", {"period": period}, alias=alias)


def COPPOCK(
    short_roc: int = 11,
    long_roc: int = 14,
    wma: int = 10,
    alias: str = None
) -> Indicator:
    """코폭 곡선 (Coppock Curve)

    장기 매수 신호 생성.

    Args:
        short_roc: 단기 ROC 기간 (기본값: 11)
        long_roc: 장기 ROC 기간 (기본값: 14)
        wma: WMA 기간 (기본값: 10)
        alias: 지표 별칭

    Example:
        condition = COPPOCK().crosses_above(0)  # 매수 신호
    """
    return Indicator(
        "coppock",
        {"short_roc": short_roc, "long_roc": long_roc, "wma": wma},
        alias=alias
    )


def SUPERTREND(period: int = 10, multiplier: float = 3.0, alias: str = None) -> Indicator:
    """슈퍼트렌드 (SuperTrend)

    ATR 기반 추세 추종 지표.

    Args:
        period: ATR 기간 (기본값: 10)
        multiplier: ATR 배수 (기본값: 3.0)
        alias: 지표 별칭

    Example:
        condition = Price.close() > SUPERTREND()  # 상승 추세
    """
    return Indicator(
        "supertrend",
        {"period": period, "multiplier": multiplier},
        alias=alias
    )


def MASS_INDEX(ema_period: int = 9, sum_period: int = 25, alias: str = None) -> Indicator:
    """매스 인덱스 (Mass Index)

    가격 변동폭 분석으로 추세 반전 감지.

    Args:
        ema_period: EMA 기간 (기본값: 9)
        sum_period: 합산 기간 (기본값: 25)
        alias: 지표 별칭

    Example:
        condition = MASS_INDEX() > 27  # 반전 신호
    """
    return Indicator(
        "mass_index",
        {"ema_period": ema_period, "sum_period": sum_period},
        alias=alias
    )


def SCHAFF(cycle: int = 10, fast: int = 23, slow: int = 50, alias: str = None) -> Indicator:
    """샤프 추세 사이클 (Schaff Trend Cycle)

    MACD와 스토캐스틱 결합.

    Args:
        cycle: 사이클 기간 (기본값: 10)
        fast: 빠른 기간 (기본값: 23)
        slow: 느린 기간 (기본값: 50)
        alias: 지표 별칭

    Example:
        condition = SCHAFF() < 25  # 과매도
    """
    return Indicator(
        "schaff",
        {"cycle": cycle, "fast": fast, "slow": slow},
        alias=alias
    )


def FISHER(period: int = 10, alias: str = None) -> Indicator:
    """피셔 변환 (Fisher Transform)

    가격을 정규 분포로 변환.

    Args:
        period: 계산 기간 (기본값: 10)
        alias: 지표 별칭

    Example:
        condition = FISHER(10).crosses_above(0)  # 매수 신호
    """
    return Indicator("fisher", {"period": period}, alias=alias)


def KST(
    roc1: int = 10,
    roc2: int = 15,
    roc3: int = 20,
    roc4: int = 30,
    output: str = "value",
    alias: str = None
) -> Indicator:
    """KST 지표 (Know Sure Thing)

    네 가지 ROC의 가중 합.

    Args:
        roc1: 첫 번째 ROC 기간 (기본값: 10)
        roc2: 두 번째 ROC 기간 (기본값: 15)
        roc3: 세 번째 ROC 기간 (기본값: 20)
        roc4: 네 번째 ROC 기간 (기본값: 30)
        output: 출력값 ("value", "signal")
        alias: 지표 별칭

    Example:
        kst = KST()
        kst_signal = KST(output="signal")
        condition = kst.crosses_above(kst_signal)
    """
    return Indicator(
        "kst",
        {"roc1": roc1, "roc2": roc2, "roc3": roc3, "roc4": roc4},
        output=output,
        alias=alias
    )


def VORTEX(period: int = 14, output: str = "plus_vi", alias: str = None) -> Indicator:
    """볼텍스 지표 (Vortex Indicator)

    추세 방향과 강도 측정.

    Args:
        period: 계산 기간 (기본값: 14)
        output: 출력값 ("plus_vi", "minus_vi")
        alias: 지표 별칭

    Example:
        vi_plus = VORTEX(14, output="plus_vi")
        vi_minus = VORTEX(14, output="minus_vi")
        condition = vi_plus > vi_minus  # 상승 추세
    """
    return Indicator("vortex", {"period": period}, output=output, alias=alias)


# ============================================================
# 거래량 지표 (Volume) - 12개
# ============================================================

def OBV(alias: str = None) -> Indicator:
    """OBV (On Balance Volume)

    거래량 누적 지표.

    Args:
        alias: 지표 별칭

    Example:
        condition = OBV() > SMA(20)  # OBV가 이평선 위
    """
    return Indicator("obv", {}, alias=alias)


def AD(alias: str = None) -> Indicator:
    """누적/분산 (Accumulation/Distribution)

    가격과 거래량의 관계 분석.

    Args:
        alias: 지표 별칭

    Example:
        condition = AD() > 0  # 매집 추세
    """
    return Indicator("ad", {}, alias=alias)


def ADL(alias: str = None) -> Indicator:
    """누적/분산 라인 (Accumulation/Distribution Line)

    AD의 누적선.

    Args:
        alias: 지표 별칭

    Example:
        # ADL 상승 추세 확인
    """
    return Indicator("adl", {}, alias=alias)


def CMF(period: int = 20, alias: str = None) -> Indicator:
    """채킨 머니플로우 (Chaikin Money Flow)

    일정 기간 동안의 매수/매도 압력 측정.

    Args:
        period: 계산 기간 (기본값: 20)
        alias: 지표 별칭

    Example:
        condition = CMF(20) > 0  # 매수 압력
    """
    return Indicator("cmf", {"period": period}, alias=alias)


def MFI(period: int = 14, alias: str = None) -> Indicator:
    """자금흐름지수 (Money Flow Index)

    거래량 가중 RSI. 0~100 범위.

    Args:
        period: 계산 기간 (기본값: 14)
        alias: 지표 별칭

    Example:
        condition = MFI(14) < 20  # 과매도
    """
    return Indicator("mfi", {"period": period}, alias=alias)


def FORCE(period: int = 13, alias: str = None) -> Indicator:
    """포스 인덱스 (Force Index)

    가격 변화와 거래량의 곱.

    Args:
        period: EMA 기간 (기본값: 13)
        alias: 지표 별칭

    Example:
        condition = FORCE(13) > 0  # 매수 압력
    """
    return Indicator("force", {"period": period}, alias=alias)


def VWAP(period: int = 14, alias: str = None) -> Indicator:
    """VWAP (Volume Weighted Average Price)

    거래량 가중 평균 가격.

    Args:
        period: 계산 기간 (기본값: 14)
        alias: 지표 별칭

    Example:
        condition = Price.close() > VWAP()  # 가격이 VWAP 위
    """
    return Indicator("vwap", {"period": period}, alias=alias)


def VWMA(period: int = 21, alias: str = None) -> Indicator:
    """거래량 가중 이동평균 (Volume Weighted Moving Average)

    Args:
        period: 이동평균 기간 (기본값: 21)
        alias: 지표 별칭

    Example:
        condition = Price.close() > VWMA(21)
    """
    return Indicator("vwma", {"period": period}, alias=alias)


def EOM(period: int = 14, scale: int = 1000000000, alias: str = None) -> Indicator:
    """움직임의 용이성 (Ease of Movement)

    가격 변화와 거래량의 관계.

    Args:
        period: 계산 기간 (기본값: 14)
        scale: 스케일 팩터 (기본값: 1000000000)
        alias: 지표 별칭

    Example:
        condition = EOM() > 0  # 쉬운 상승
    """
    return Indicator("eom", {"period": period, "scale": scale}, alias=alias)



# ============================================================
# 변동성 지표 (Volatility) - 10개
# ============================================================

def ATR(period: int = 14, alias: str = None) -> Indicator:
    """평균진폭 (Average True Range)

    Args:
        period: ATR 계산 기간 (기본값: 14)
        alias: 지표 별칭

    Example:
        atr = ATR(14)
    """
    return Indicator("atr", {"period": period}, alias=alias)


def NATR(period: int = 14, alias: str = None) -> Indicator:
    """정규화 ATR (Normalized Average True Range)

    ATR을 종가로 나눠 백분율로 표시.

    Args:
        period: 계산 기간 (기본값: 14)
        alias: 지표 별칭

    Example:
        condition = NATR(14) > 5  # 변동성 5% 이상
    """
    return Indicator("natr", {"period": period}, alias=alias)


def BB(period: int = 20, std: float = 2.0) -> BollingerBands:
    """볼린저 밴드 (Bollinger Bands)

    Args:
        period: 이동평균 기간 (기본값: 20)
        std: 표준편차 배수 (기본값: 2.0)

    Example:
        bb = BB(20, 2.0)
        condition = Price.close() < bb.lower  # 하단 돌파
    """
    return BollingerBands(period, std)


def STD(period: int = 21, alias: str = None) -> Indicator:
    """표준편차 (Standard Deviation)

    Args:
        period: 계산 기간 (기본값: 21)
        alias: 지표 별칭

    Example:
        # 변동성 측정
    """
    return Indicator("std", {"period": period}, alias=alias)


def VARIANCE(period: int = 21, alias: str = None) -> Indicator:
    """분산 (Variance)

    Args:
        period: 계산 기간 (기본값: 21)
        alias: 지표 별칭

    Example:
        # 변동성 측정
    """
    return Indicator("variance", {"period": period}, alias=alias)


def BETA(period: int = 21, alias: str = None) -> Indicator:
    """베타 (Beta)

    벤치마크 대비 변동성.

    Args:
        period: 계산 기간 (기본값: 21)
        alias: 지표 별칭

    Example:
        condition = BETA() > 1.0  # 시장보다 변동성 큼
    """
    return Indicator("beta", {"period": period}, alias=alias)


def ALPHA(period: int = 21, alias: str = None) -> Indicator:
    """알파 (Alpha)

    벤치마크 대비 초과 수익.

    Args:
        period: 계산 기간 (기본값: 21)
        alias: 지표 별칭

    Example:
        condition = ALPHA() > 0  # 양의 알파
    """
    return Indicator("alpha", {"period": period}, alias=alias)


# ============================================================
# 기타 지표 (Misc) - 10개
# ============================================================

def MAXIMUM(period: int = 252, alias: str = None) -> Indicator:
    """기간 내 최고가 (52주 신고가 등)

    Args:
        period: 기간 (252 = 약 1년)
        alias: 지표 별칭

    Example:
        condition = Price.close() > MAXIMUM(252)  # 52주 신고가 돌파
    """
    return Indicator("maximum", {"period": period}, alias=alias)


def MINIMUM(period: int = 252, alias: str = None) -> Indicator:
    """기간 내 최저가

    Args:
        period: 기간 (252 = 약 1년)
        alias: 지표 별칭

    Example:
        condition = Price.close() < MINIMUM(252)  # 52주 신저가 돌파
    """
    return Indicator("minimum", {"period": period}, alias=alias)


def MIDPOINT(period: int = 14, alias: str = None) -> Indicator:
    """중간값 (Mid Point)

    기간 내 최고/최저의 중간값.

    Args:
        period: 계산 기간 (기본값: 14)
        alias: 지표 별칭

    Example:
        condition = Price.close() > MIDPOINT(14)
    """
    return Indicator("midpoint", {"period": period}, alias=alias)


def MIDPRICE(period: int = 14, alias: str = None) -> Indicator:
    """중간가격 (Mid Price)

    고가와 저가의 중간값.

    Args:
        period: 계산 기간 (기본값: 14)
        alias: 지표 별칭

    Example:
        condition = Price.close() > MIDPRICE(14)
    """
    return Indicator("midprice", {"period": period}, alias=alias)


def LOGR(period: int = 1, alias: str = None) -> Indicator:
    """로그 수익률 (Log Return)

    Args:
        period: 계산 기간 (기본값: 1)
        alias: 지표 별칭

    Example:
        # 로그 수익률 분석
    """
    return Indicator("logr", {"period": period}, alias=alias)


def IBS(alias: str = None) -> Indicator:
    """내부 바 강도 (Internal Bar Strength)

    (종가 - 저가) / (고가 - 저가). 0~1 범위.

    Args:
        alias: 지표 별칭

    Example:
        condition = IBS() < 0.2  # 약세 신호
    """
    return Indicator("ibs", {}, alias=alias)


def BOP(alias: str = None) -> Indicator:
    """힘의 균형 (Balance of Power)

    매수/매도 세력 균형.

    Args:
        alias: 지표 별칭

    Example:
        condition = BOP() > 0  # 매수 우세
    """
    return Indicator("bop", {}, alias=alias)


def REGRESSION(period: int = 14, output: str = "value", alias: str = None) -> Indicator:
    """선형 회귀 (Linear Regression / Least Squares Moving Average)

    Args:
        period: 계산 기간 (기본값: 14)
        output: 출력값 ("value", "slope", "intercept")
        alias: 지표 별칭

    Example:
        reg = REGRESSION(14)
        slope = REGRESSION(14, output="slope")
        condition = slope > 0  # 상승 추세
    """
    return Indicator("regression", {"period": period}, output=output, alias=alias)


def PIVOT(left_bars: int = 4, right_bars: int = 2, output: str = "high", alias: str = None) -> Indicator:
    """피봇 포인트 (Pivot Points High/Low)

    지지/저항선 식별.

    Args:
        left_bars: 왼쪽 바 수 (기본값: 4)
        right_bars: 오른쪽 바 수 (기본값: 2)
        output: 출력값 ("high", "low")
        alias: 지표 별칭

    Example:
        pivot_high = PIVOT(4, 2, output="high")
        pivot_low = PIVOT(4, 2, output="low")
    """
    return Indicator(
        "pivot",
        {"left_bars": left_bars, "right_bars": right_bars},
        output=output,
        alias=alias
    )


def AUGEN(period: int = 3, alias: str = None) -> Indicator:
    """오겐 가격 스파이크 (Augen Price Spike)

    가격 급등/급락 감지.

    Args:
        period: 계산 기간 (기본값: 3)
        alias: 지표 별칭

    Example:
        condition = AUGEN() > 2  # 급등 신호
    """
    return Indicator("augen", {"period": period}, alias=alias)


# ============================================================
# 멀티 아웃풋 클래스
# ============================================================

class IchimokuCloud:
    """일목균형표 (Ichimoku Kinko Hyo)

    5개 구성요소: 전환선, 기준선, 선행스팬A, 선행스팬B, 후행스팬

    Example:
        ichimoku = IchimokuCloud()
        condition = ichimoku.tenkan.crosses_above(ichimoku.kijun)  # 매수 신호
    """
    def __init__(self, tenkan: int = 9, kijun: int = 26, senkou_b: int = 52):
        self.tenkan_period = tenkan
        self.kijun_period = kijun
        self.senkou_b_period = senkou_b

    @property
    def _base_alias(self) -> str:
        """공통 alias (멀티 아웃풋 지표는 같은 alias 사용)"""
        return f"ichimoku_{self.tenkan_period}_{self.kijun_period}"

    @property
    def tenkan(self) -> Indicator:
        """전환선 (Tenkan-sen) - 단기 추세"""
        return Indicator(
            "ichimoku",
            {
                "tenkan": self.tenkan_period,
                "kijun": self.kijun_period,
                "senkou_b": self.senkou_b_period,
            },
            alias=self._base_alias,
            output="tenkan"
        )

    @property
    def kijun(self) -> Indicator:
        """기준선 (Kijun-sen) - 중기 추세"""
        return Indicator(
            "ichimoku",
            {
                "tenkan": self.tenkan_period,
                "kijun": self.kijun_period,
                "senkou_b": self.senkou_b_period,
            },
            alias=self._base_alias,
            output="kijun"
        )

    @property
    def senkou_a(self) -> Indicator:
        """선행스팬 A (Senkou Span A) - 구름 상단"""
        return Indicator(
            "ichimoku",
            {
                "tenkan": self.tenkan_period,
                "kijun": self.kijun_period,
                "senkou_b": self.senkou_b_period,
            },
            alias=self._base_alias,
            output="senkou_a"
        )

    @property
    def senkou_b(self) -> Indicator:
        """선행스팬 B (Senkou Span B) - 구름 하단"""
        return Indicator(
            "ichimoku",
            {
                "tenkan": self.tenkan_period,
                "kijun": self.kijun_period,
                "senkou_b": self.senkou_b_period,
            },
            alias=self._base_alias,
            output="senkou_b"
        )

    @property
    def chikou(self) -> Indicator:
        """후행스팬 (Chikou Span) - 26일 전 종가"""
        return Indicator(
            "ichimoku",
            {
                "tenkan": self.tenkan_period,
                "kijun": self.kijun_period,
                "senkou_b": self.senkou_b_period,
            },
            alias=self._base_alias,
            output="chikou"
        )


class KeltnerChannels:
    """켈트너 채널 (Keltner Channels)

    EMA 중심선과 ATR 기반 상하단 밴드.

    Example:
        keltner = KeltnerChannels()
        condition = Price.close() < keltner.lower  # 하단 돌파
    """
    def __init__(self, period: int = 20, multiplier: float = 2.0):
        self.period = period
        self.multiplier = multiplier

    @property
    def _base_alias(self) -> str:
        """공통 alias"""
        return f"keltner_{self.period}"

    @property
    def upper(self) -> Indicator:
        """상단 밴드"""
        return Indicator(
            "keltner",
            {"period": self.period, "multiplier": self.multiplier},
            alias=self._base_alias,
            output="upper"
        )

    @property
    def middle(self) -> Indicator:
        """중간 밴드 (EMA)"""
        return Indicator(
            "keltner",
            {"period": self.period, "multiplier": self.multiplier},
            alias=self._base_alias,
            output="middle"
        )

    @property
    def lower(self) -> Indicator:
        """하단 밴드"""
        return Indicator(
            "keltner",
            {"period": self.period, "multiplier": self.multiplier},
            alias=self._base_alias,
            output="lower"
        )


class DonchianChannel:
    """돈치안 채널 (Donchian Channel)

    기간 내 최고가/최저가 기반 채널.

    Example:
        donchian = DonchianChannel()
        condition = Price.close() > donchian.upper  # 상단 돌파
    """
    def __init__(self, period: int = 20):
        self.period = period

    @property
    def _base_alias(self) -> str:
        """공통 alias"""
        return f"donchian_{self.period}"

    @property
    def upper(self) -> Indicator:
        """상단 (기간 내 최고가)"""
        return Indicator(
            "donchian",
            {"period": self.period},
            alias=self._base_alias,
            output="upper"
        )

    @property
    def lower(self) -> Indicator:
        """하단 (기간 내 최저가)"""
        return Indicator(
            "donchian",
            {"period": self.period},
            alias=self._base_alias,
            output="lower"
        )


class AccelerationBands:
    """가속 밴드 (Acceleration Bands)

    SMA 중심선과 변동성 기반 상하단 밴드.

    Example:
        accbands = AccelerationBands()
        condition = Price.close() < accbands.lower  # 하단 돌파
    """
    def __init__(self, period: int = 20, width: float = 4.0):
        self.period = period
        self.width = width

    @property
    def _base_alias(self) -> str:
        """공통 alias"""
        return f"accbands_{self.period}"

    @property
    def upper(self) -> Indicator:
        """상단 밴드"""
        return Indicator(
            "accbands",
            {"period": self.period, "width": self.width},
            alias=self._base_alias,
            output="upper"
        )

    @property
    def middle(self) -> Indicator:
        """중간 밴드 (SMA)"""
        return Indicator(
            "accbands",
            {"period": self.period, "width": self.width},
            alias=self._base_alias,
            output="middle"
        )

    @property
    def lower(self) -> Indicator:
        """하단 밴드"""
        return Indicator(
            "accbands",
            {"period": self.period, "width": self.width},
            alias=self._base_alias,
            output="lower"
        )


# ============================================================
# Aliases for compatibility
# ============================================================

Stochastic = STOCH  # 프리셋 전략에서 사용
Maximum = MAXIMUM  # Maximum(252) 형태 지원
Minimum = MINIMUM  # Minimum(252) 형태 지원


# ============================================================
# Candlestick Pattern Factory Functions
# ============================================================

def Doji() -> CandlestickPattern:
    """도지 패턴 - 시가와 종가가 거의 같음"""
    return CandlestickPattern("doji")


def DragonflyDoji() -> CandlestickPattern:
    """잠자리형 도지 - 긴 아래꼬리, 상승 반전"""
    return CandlestickPattern("dragonfly_doji")


def GravestoneDoji() -> CandlestickPattern:
    """비석형 도지 - 긴 위꼬리, 하락 반전"""
    return CandlestickPattern("gravestone_doji")


def Hammer() -> CandlestickPattern:
    """망치형 - 하락 후 상승 반전"""
    return CandlestickPattern("hammer")


def HangingMan() -> CandlestickPattern:
    """교수형 - 상승 후 하락 반전"""
    return CandlestickPattern("hanging_man")


def InvertedHammer() -> CandlestickPattern:
    """역망치형 - 하락 후 상승 반전"""
    return CandlestickPattern("inverted_hammer")


def ShootingStar() -> CandlestickPattern:
    """유성형 - 상승 후 하락 반전"""
    return CandlestickPattern("shooting_star")


def Marubozu() -> CandlestickPattern:
    """장대봉 - 강한 추세"""
    return CandlestickPattern("marubozu")


def SpinningTop() -> CandlestickPattern:
    """팽이형 - 우유부단"""
    return CandlestickPattern("spinning_top")


def BeltHold() -> CandlestickPattern:
    """띠 잡기 - 반전 가능성"""
    return CandlestickPattern("belt_hold")


def Engulfing() -> CandlestickPattern:
    """장악형 - 강한 반전"""
    return CandlestickPattern("engulfing")


def Harami() -> CandlestickPattern:
    """잉태형 - 반전 가능성"""
    return CandlestickPattern("harami")


def HaramiCross() -> CandlestickPattern:
    """잉태 십자형 - 강한 반전"""
    return CandlestickPattern("harami_cross")


def Piercing() -> CandlestickPattern:
    """관통형 - 상승 반전"""
    return CandlestickPattern("piercing")


def DarkCloudCover() -> CandlestickPattern:
    """먹구름형 - 하락 반전"""
    return CandlestickPattern("dark_cloud_cover")


def MorningStar() -> CandlestickPattern:
    """샛별형 - 강한 상승 반전"""
    return CandlestickPattern("morning_star")


def EveningStar() -> CandlestickPattern:
    """저녁별형 - 강한 하락 반전"""
    return CandlestickPattern("evening_star")


def ThreeWhiteSoldiers() -> CandlestickPattern:
    """적삼병 - 강한 상승 추세"""
    return CandlestickPattern("three_white_soldiers")


def ThreeBlackCrows() -> CandlestickPattern:
    """흑삼병 - 강한 하락 추세"""
    return CandlestickPattern("three_black_crows")


# Re-export Price from indicator module
__all__ = [
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
    "Stochastic",  # alias
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
    "PVT",
    "NVI",
    "PVI",

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
    "Maximum",  # alias
    "MINIMUM",
    "Minimum",  # alias
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
    # Candlestick Patterns
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
