"""
기술적 지표 계산 모듈

Applied Skills: skills/investment-strategy-framework.md
- 모든 지표는 pandas DataFrame/Series 기반
- 기간 부족 시 None 반환 (에러 발생 금지)
"""

from typing import Optional

import numpy as np
import pandas as pd


def calc_ma(df: pd.DataFrame, period: int, column: str = "close") -> pd.Series:
    """
    이동평균 계산

    Args:
        df: OHLCV DataFrame
        period: 기간
        column: 대상 컬럼 (기본: close)

    Returns:
        이동평균 Series (기간 부족 시 NaN 포함)
    """
    if df.empty or len(df) < period:
        return pd.Series(dtype=float)

    return df[column].rolling(window=period).mean()


def calc_std(df: pd.DataFrame, period: int, column: str = "close") -> pd.Series:
    """
    표준편차 계산

    Args:
        df: OHLCV DataFrame
        period: 기간
        column: 대상 컬럼

    Returns:
        표준편차 Series
    """
    if df.empty or len(df) < period:
        return pd.Series(dtype=float)

    return df[column].rolling(window=period).std()


def calc_returns(df: pd.DataFrame, period: int) -> pd.Series:
    """
    기간 수익률 계산

    Args:
        df: OHLCV DataFrame
        period: 기간 (일)

    Returns:
        수익률 Series (소수점, 예: 0.05 = 5%)
    """
    if df.empty or len(df) < period:
        return pd.Series(dtype=float)

    return df["close"].pct_change(periods=period)


def calc_disparity(df: pd.DataFrame, period: int = 20) -> pd.Series:
    """
    이격도 계산: 현재가 / 이동평균 * 100

    Args:
        df: OHLCV DataFrame
        period: 이동평균 기간

    Returns:
        이격도 Series
        - 100 초과: 과매수 구간
        - 100 미만: 과매도 구간
    """
    if df.empty or len(df) < period:
        return pd.Series(dtype=float)

    ma = calc_ma(df, period)
    return (df["close"] / ma) * 100


def calc_volatility(df: pd.DataFrame, period: int = 10) -> pd.Series:
    """
    변동성 계산 (일간 수익률의 표준편차)

    Args:
        df: OHLCV DataFrame
        period: 기간

    Returns:
        변동성 Series
    """
    if df.empty or len(df) < period + 1:
        return pd.Series(dtype=float)

    daily_returns = df["close"].pct_change()
    return daily_returns.rolling(window=period).std()


def calc_consecutive_days(df: pd.DataFrame, direction: str = "up") -> int:
    """
    연속 상승/하락 일수 계산

    Args:
        df: OHLCV DataFrame
        direction: "up" (상승) or "down" (하락)

    Returns:
        연속 일수 (정수)
    """
    if df.empty or len(df) < 2:
        return 0

    changes = df["close"].diff()

    if direction == "up":
        condition = changes > 0
    else:
        condition = changes < 0

    # 최근부터 역순으로 연속 카운트
    count = 0
    for i in range(len(condition) - 1, 0, -1):
        if condition.iloc[i]:
            count += 1
        else:
            break

    return count


def calc_daily_change(df: pd.DataFrame) -> Optional[float]:
    """
    전일 대비 등락률 계산

    Args:
        df: OHLCV DataFrame

    Returns:
        등락률 (%, 예: 5.0 = 5%)
        데이터 부족 시 None
    """
    if df.empty or len(df) < 2:
        return None

    prev_close = df["close"].iloc[-2]
    curr_close = df["close"].iloc[-1]

    if prev_close == 0:
        return None

    return (curr_close - prev_close) / prev_close * 100


def calc_strong_close_ratio(df: pd.DataFrame) -> Optional[float]:
    """
    강한 종가 비율 계산: 당일 봉에서 종가가 고가에 얼마나 가까운지

    계산식: (Close - Low) / (High - Low)

    Args:
        df: OHLCV DataFrame

    Returns:
        비율 (0.0 ~ 1.0)
        - 1.0에 가까움: 종가가 고가 근처 (강한 매수세)
        - 0.0에 가까움: 종가가 저가 근처 (강한 매도세)
        데이터 부족 시 None

    Note:
        장마감 후 확정된 일봉 데이터로 계산해야 정확함
    """
    if df.empty:
        return None

    high = df["high"].iloc[-1]
    low = df["low"].iloc[-1]
    close = df["close"].iloc[-1]

    # 고가 = 저가인 경우 (변동 없음)
    if high == low:
        return 0.5

    return (close - low) / (high - low)


def calc_high_since(df: pd.DataFrame, days: int) -> Optional[int]:
    """
    N일간 최고가 조회

    Args:
        df: OHLCV DataFrame
        days: 조회 기간

    Returns:
        최고가 (정수)
    """
    if df.empty or len(df) < days:
        return None

    return int(df["high"].tail(days).max())


def calc_low_since(df: pd.DataFrame, days: int) -> Optional[int]:
    """
    N일간 최저가 조회

    Args:
        df: OHLCV DataFrame
        days: 조회 기간

    Returns:
        최저가 (정수)
    """
    if df.empty or len(df) < days:
        return None

    return int(df["low"].tail(days).min())


def get_latest_close(df: pd.DataFrame) -> Optional[int]:
    """
    최근 종가 조회

    Args:
        df: OHLCV DataFrame

    Returns:
        종가 (정수)
    """
    if df.empty:
        return None

    return int(df["close"].iloc[-1])


def get_prev_close(df: pd.DataFrame) -> Optional[int]:
    """
    전일 종가 조회

    Args:
        df: OHLCV DataFrame

    Returns:
        전일 종가 (정수)
    """
    if df.empty or len(df) < 2:
        return None

    return int(df["close"].iloc[-2])


# =============================================================================
# 확장 지표 (Extended Indicators)
# =============================================================================


def calc_ema(df: pd.DataFrame, period: int, column: str = "close") -> pd.Series:
    """
    지수이동평균 (EMA) 계산

    Args:
        df: OHLCV DataFrame
        period: 기간
        column: 대상 컬럼 (기본: close)

    Returns:
        EMA Series
    """
    if df.empty or len(df) < period:
        return pd.Series(dtype=float)

    return df[column].ewm(span=period, adjust=False).mean()


def calc_rsi(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    RSI (Relative Strength Index) 계산

    Args:
        df: OHLCV DataFrame
        period: 기간 (기본: 14)

    Returns:
        RSI Series (0~100)
        - 70 이상: 과매수
        - 30 이하: 과매도
    """
    if df.empty or len(df) < period + 1:
        return pd.Series(dtype=float)

    delta = df["close"].diff()

    gain = delta.where(delta > 0, 0.0)
    loss = (-delta).where(delta < 0, 0.0)

    avg_gain = gain.ewm(span=period, adjust=False).mean()
    avg_loss = loss.ewm(span=period, adjust=False).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi


def calc_macd(
    df: pd.DataFrame,
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9
) -> pd.Series:
    """
    MACD 라인 계산

    Args:
        df: OHLCV DataFrame
        fast_period: 단기 EMA 기간 (기본: 12)
        slow_period: 장기 EMA 기간 (기본: 26)
        signal_period: 시그널 EMA 기간 (기본: 9)

    Returns:
        MACD 라인 Series (fast EMA - slow EMA)
    """
    if df.empty or len(df) < slow_period:
        return pd.Series(dtype=float)

    fast_ema = calc_ema(df, fast_period)
    slow_ema = calc_ema(df, slow_period)

    return fast_ema - slow_ema


def calc_macd_signal(
    df: pd.DataFrame,
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9
) -> pd.Series:
    """
    MACD 시그널 라인 계산

    Args:
        df: OHLCV DataFrame
        fast_period: 단기 EMA 기간
        slow_period: 장기 EMA 기간
        signal_period: 시그널 EMA 기간

    Returns:
        시그널 라인 Series (MACD의 EMA)
    """
    macd = calc_macd(df, fast_period, slow_period, signal_period)

    if macd.empty:
        return pd.Series(dtype=float)

    return macd.ewm(span=signal_period, adjust=False).mean()


def calc_macd_histogram(
    df: pd.DataFrame,
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9
) -> pd.Series:
    """
    MACD 히스토그램 계산

    Args:
        df: OHLCV DataFrame
        fast_period: 단기 EMA 기간
        slow_period: 장기 EMA 기간
        signal_period: 시그널 EMA 기간

    Returns:
        MACD 히스토그램 Series (MACD - Signal)
    """
    macd = calc_macd(df, fast_period, slow_period, signal_period)
    signal = calc_macd_signal(df, fast_period, slow_period, signal_period)

    if macd.empty or signal.empty:
        return pd.Series(dtype=float)

    return macd - signal


def calc_bb_middle(df: pd.DataFrame, period: int = 20) -> pd.Series:
    """
    볼린저밴드 중심선 (SMA)

    Args:
        df: OHLCV DataFrame
        period: 기간 (기본: 20)

    Returns:
        중심선 Series
    """
    return calc_ma(df, period)


def calc_bb_upper(df: pd.DataFrame, period: int = 20, std_dev: float = 2.0) -> pd.Series:
    """
    볼린저밴드 상단선

    Args:
        df: OHLCV DataFrame
        period: 기간 (기본: 20)
        std_dev: 표준편차 배수 (기본: 2.0)

    Returns:
        상단선 Series
    """
    if df.empty or len(df) < period:
        return pd.Series(dtype=float)

    middle = calc_bb_middle(df, period)
    std = calc_std(df, period)

    return middle + (std * std_dev)


def calc_bb_lower(df: pd.DataFrame, period: int = 20, std_dev: float = 2.0) -> pd.Series:
    """
    볼린저밴드 하단선

    Args:
        df: OHLCV DataFrame
        period: 기간 (기본: 20)
        std_dev: 표준편차 배수 (기본: 2.0)

    Returns:
        하단선 Series
    """
    if df.empty or len(df) < period:
        return pd.Series(dtype=float)

    middle = calc_bb_middle(df, period)
    std = calc_std(df, period)

    return middle - (std * std_dev)


def calc_bb_width(df: pd.DataFrame, period: int = 20, std_dev: float = 2.0) -> pd.Series:
    """
    볼린저밴드 폭 (밴드 수축/확장 판단)

    Args:
        df: OHLCV DataFrame
        period: 기간 (기본: 20)
        std_dev: 표준편차 배수 (기본: 2.0)

    Returns:
        밴드 폭 Series (상단 - 하단)
    """
    upper = calc_bb_upper(df, period, std_dev)
    lower = calc_bb_lower(df, period, std_dev)

    if upper.empty or lower.empty:
        return pd.Series(dtype=float)

    return upper - lower


def calc_bb_percent(df: pd.DataFrame, period: int = 20, std_dev: float = 2.0) -> pd.Series:
    """
    볼린저밴드 %B (현재가 위치)

    Args:
        df: OHLCV DataFrame
        period: 기간 (기본: 20)
        std_dev: 표준편차 배수 (기본: 2.0)

    Returns:
        %B Series (0~1, 0이면 하단, 1이면 상단)
    """
    upper = calc_bb_upper(df, period, std_dev)
    lower = calc_bb_lower(df, period, std_dev)

    if upper.empty or lower.empty:
        return pd.Series(dtype=float)

    return (df["close"] - lower) / (upper - lower)


def calc_stochastic_k(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    스토캐스틱 %K 계산

    Args:
        df: OHLCV DataFrame
        period: 기간 (기본: 14)

    Returns:
        %K Series (0~100)
    """
    if df.empty or len(df) < period:
        return pd.Series(dtype=float)

    lowest_low = df["low"].rolling(window=period).min()
    highest_high = df["high"].rolling(window=period).max()

    k = ((df["close"] - lowest_low) / (highest_high - lowest_low)) * 100

    return k


def calc_stochastic_d(df: pd.DataFrame, k_period: int = 14, d_period: int = 3) -> pd.Series:
    """
    스토캐스틱 %D 계산 (%K의 이동평균)

    Args:
        df: OHLCV DataFrame
        k_period: %K 기간 (기본: 14)
        d_period: %D 기간 (기본: 3)

    Returns:
        %D Series
    """
    k = calc_stochastic_k(df, k_period)

    if k.empty:
        return pd.Series(dtype=float)

    return k.rolling(window=d_period).mean()


def calc_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    ATR (Average True Range) 계산

    Args:
        df: OHLCV DataFrame
        period: 기간 (기본: 14)

    Returns:
        ATR Series
    """
    if df.empty or len(df) < period + 1:
        return pd.Series(dtype=float)

    high = df["high"]
    low = df["low"]
    close = df["close"]

    # True Range 계산
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))

    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    # ATR = TR의 이동평균
    return tr.ewm(span=period, adjust=False).mean()


def calc_cci(df: pd.DataFrame, period: int = 20) -> pd.Series:
    """
    CCI (Commodity Channel Index) 계산

    Args:
        df: OHLCV DataFrame
        period: 기간 (기본: 20)

    Returns:
        CCI Series
        - +100 이상: 과매수
        - -100 이하: 과매도
    """
    if df.empty or len(df) < period:
        return pd.Series(dtype=float)

    # Typical Price
    tp = (df["high"] + df["low"] + df["close"]) / 3

    # SMA of TP
    tp_sma = tp.rolling(window=period).mean()

    # Mean Deviation
    mean_dev = tp.rolling(window=period).apply(lambda x: abs(x - x.mean()).mean(), raw=True)

    # CCI
    cci = (tp - tp_sma) / (0.015 * mean_dev)

    return cci


def calc_williams_r(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    윌리엄스 %R 계산

    Args:
        df: OHLCV DataFrame
        period: 기간 (기본: 14)

    Returns:
        %R Series (-100~0)
        - -20 이상: 과매수
        - -80 이하: 과매도
    """
    if df.empty or len(df) < period:
        return pd.Series(dtype=float)

    highest_high = df["high"].rolling(window=period).max()
    lowest_low = df["low"].rolling(window=period).min()

    wr = ((highest_high - df["close"]) / (highest_high - lowest_low)) * -100

    return wr


def calc_obv(df: pd.DataFrame) -> pd.Series:
    """
    OBV (On-Balance Volume) 계산

    Args:
        df: OHLCV DataFrame

    Returns:
        OBV Series
    """
    if df.empty or len(df) < 2:
        return pd.Series(dtype=float)

    obv = pd.Series(index=df.index, dtype=float)
    obv.iloc[0] = df["volume"].iloc[0]

    for i in range(1, len(df)):
        if df["close"].iloc[i] > df["close"].iloc[i - 1]:
            obv.iloc[i] = obv.iloc[i - 1] + df["volume"].iloc[i]
        elif df["close"].iloc[i] < df["close"].iloc[i - 1]:
            obv.iloc[i] = obv.iloc[i - 1] - df["volume"].iloc[i]
        else:
            obv.iloc[i] = obv.iloc[i - 1]

    return obv


def calc_volume_ma(df: pd.DataFrame, period: int = 20) -> pd.Series:
    """
    거래량 이동평균

    Args:
        df: OHLCV DataFrame
        period: 기간 (기본: 20)

    Returns:
        거래량 MA Series
    """
    if df.empty or len(df) < period:
        return pd.Series(dtype=float)

    return df["volume"].rolling(window=period).mean()


def calc_vwap(df: pd.DataFrame) -> pd.Series:
    """
    VWAP (Volume Weighted Average Price) 계산

    Args:
        df: OHLCV DataFrame

    Returns:
        VWAP Series
    """
    if df.empty:
        return pd.Series(dtype=float)

    tp = (df["high"] + df["low"] + df["close"]) / 3
    cumulative_tp_vol = (tp * df["volume"]).cumsum()
    cumulative_vol = df["volume"].cumsum()

    return cumulative_tp_vol / cumulative_vol


def calc_mfi(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    MFI (Money Flow Index) 계산 - 거래량 가중 RSI

    Args:
        df: OHLCV DataFrame
        period: 기간 (기본: 14)

    Returns:
        MFI Series (0~100)
        - 80 이상: 과매수
        - 20 이하: 과매도
    """
    if df.empty or len(df) < period + 1:
        return pd.Series(dtype=float)

    # Typical Price
    tp = (df["high"] + df["low"] + df["close"]) / 3

    # Raw Money Flow
    rmf = tp * df["volume"]

    # Money Flow Direction
    tp_diff = tp.diff()

    positive_mf = rmf.where(tp_diff > 0, 0.0)
    negative_mf = rmf.where(tp_diff < 0, 0.0)

    # Money Ratio
    positive_sum = positive_mf.rolling(window=period).sum()
    negative_sum = negative_mf.rolling(window=period).sum()

    mr = positive_sum / negative_sum

    # MFI
    mfi = 100 - (100 / (1 + mr))

    return mfi


def calc_adx(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    ADX (Average Directional Index) 계산 - 추세 강도

    Args:
        df: OHLCV DataFrame
        period: 기간 (기본: 14)

    Returns:
        ADX Series (0~100)
        - 25 이상: 추세 존재
        - 20 이하: 추세 없음 (횡보)
    """
    if df.empty or len(df) < period * 2:
        return pd.Series(dtype=float)

    high = df["high"]
    low = df["low"]
    close = df["close"]

    # +DM, -DM
    plus_dm = high.diff()
    minus_dm = -low.diff()

    plus_dm = plus_dm.where((plus_dm > minus_dm) & (plus_dm > 0), 0.0)
    minus_dm = minus_dm.where((minus_dm > plus_dm) & (minus_dm > 0), 0.0)

    # ATR
    atr = calc_atr(df, period)

    # +DI, -DI
    plus_di = 100 * (plus_dm.ewm(span=period, adjust=False).mean() / atr)
    minus_di = 100 * (minus_dm.ewm(span=period, adjust=False).mean() / atr)

    # DX
    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)

    # ADX = DX의 이동평균
    adx = dx.ewm(span=period, adjust=False).mean()

    return adx


def calc_roc(df: pd.DataFrame, period: int = 10) -> pd.Series:
    """
    ROC (Rate of Change) 계산 - 변화율

    Args:
        df: OHLCV DataFrame
        period: 기간 (기본: 10)

    Returns:
        ROC Series (%, 예: 5.0 = 5% 상승)
    """
    if df.empty or len(df) < period + 1:
        return pd.Series(dtype=float)

    return df["close"].pct_change(periods=period) * 100


# =============================================================================
# Phase 2 Tier 1 지표 (12개 추가)
# =============================================================================


def calc_momentum(df: pd.DataFrame, period: int = 10) -> pd.Series:
    """모멘텀 (현재가 - N일전 가격)"""
    if df.empty or len(df) < period + 1:
        return pd.Series(dtype=float)
    return df["close"] - df["close"].shift(period)


def calc_stochrsi(
    df: pd.DataFrame, rsi_period: int = 14, stoch_period: int = 14
) -> pd.Series:
    """스토캐스틱 RSI (%K)"""
    rsi = calc_rsi(df, rsi_period)
    if rsi.empty or len(rsi.dropna()) < stoch_period:
        return pd.Series(dtype=float)
    lowest_rsi = rsi.rolling(window=stoch_period).min()
    highest_rsi = rsi.rolling(window=stoch_period).max()
    return ((rsi - lowest_rsi) / (highest_rsi - lowest_rsi)) * 100


def calc_aroon_up(df: pd.DataFrame, period: int = 25) -> pd.Series:
    """아룬 업"""
    if df.empty or len(df) < period + 1:
        return pd.Series(dtype=float)
    result = pd.Series(index=df.index, dtype=float)
    for i in range(period, len(df)):
        window = df["high"].iloc[i - period : i + 1]
        days_since_high = period - window.values.argmax()
        result.iloc[i] = ((period - days_since_high) / period) * 100
    return result


def calc_aroon_down(df: pd.DataFrame, period: int = 25) -> pd.Series:
    """아룬 다운"""
    if df.empty or len(df) < period + 1:
        return pd.Series(dtype=float)
    result = pd.Series(index=df.index, dtype=float)
    for i in range(period, len(df)):
        window = df["low"].iloc[i - period : i + 1]
        days_since_low = period - window.values.argmin()
        result.iloc[i] = ((period - days_since_low) / period) * 100
    return result


def calc_natr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """정규화 ATR (ATR / Close * 100)"""
    atr = calc_atr(df, period)
    if atr.empty:
        return pd.Series(dtype=float)
    return (atr / df["close"]) * 100


def calc_keltner_upper(
    df: pd.DataFrame, ema_period: int = 20, atr_period: int = 10, multiplier: float = 2.0
) -> pd.Series:
    """켈트너 채널 상단"""
    ema = calc_ema(df, ema_period)
    atr = calc_atr(df, atr_period)
    if ema.empty or atr.empty:
        return pd.Series(dtype=float)
    return ema + (atr * multiplier)


def calc_keltner_lower(
    df: pd.DataFrame, ema_period: int = 20, atr_period: int = 10, multiplier: float = 2.0
) -> pd.Series:
    """켈트너 채널 하단"""
    ema = calc_ema(df, ema_period)
    atr = calc_atr(df, atr_period)
    if ema.empty or atr.empty:
        return pd.Series(dtype=float)
    return ema - (atr * multiplier)


def calc_donchian_upper(df: pd.DataFrame, period: int = 20) -> pd.Series:
    """돈치안 채널 상단 (N일 최고가)"""
    if df.empty or len(df) < period:
        return pd.Series(dtype=float)
    return df["high"].rolling(window=period).max()


def calc_donchian_lower(df: pd.DataFrame, period: int = 20) -> pd.Series:
    """돈치안 채널 하단 (N일 최저가)"""
    if df.empty or len(df) < period:
        return pd.Series(dtype=float)
    return df["low"].rolling(window=period).min()


def calc_supertrend(
    df: pd.DataFrame, period: int = 10, multiplier: float = 3.0
) -> pd.Series:
    """슈퍼트렌드 (1=상승추세, -1=하락추세)"""
    atr = calc_atr(df, period)
    if atr.empty:
        return pd.Series(dtype=float)

    hl2 = (df["high"] + df["low"]) / 2
    upper = hl2 + (multiplier * atr)
    lower = hl2 - (multiplier * atr)
    direction = pd.Series(1, index=df.index, dtype=float)

    for i in range(1, len(df)):
        if df["close"].iloc[i] > upper.iloc[i - 1]:
            direction.iloc[i] = 1
        elif df["close"].iloc[i] < lower.iloc[i - 1]:
            direction.iloc[i] = -1
        else:
            direction.iloc[i] = direction.iloc[i - 1]

    return direction


def calc_sar(
    df: pd.DataFrame, af_start: float = 0.02, af_max: float = 0.2
) -> pd.Series:
    """파라볼릭 SAR"""
    if df.empty or len(df) < 2:
        return pd.Series(dtype=float)

    high = df["high"].values
    low = df["low"].values
    sar = pd.Series(index=df.index, dtype=float)
    trend = 1
    ep = high[0]
    af = af_start
    sar.iloc[0] = low[0]

    for i in range(1, len(df)):
        sar.iloc[i] = sar.iloc[i - 1] + af * (ep - sar.iloc[i - 1])

        if trend == 1:
            if low[i] < sar.iloc[i]:
                trend = -1
                sar.iloc[i] = ep
                ep = low[i]
                af = af_start
            else:
                if high[i] > ep:
                    ep = high[i]
                    af = min(af + af_start, af_max)
        else:
            if high[i] > sar.iloc[i]:
                trend = 1
                sar.iloc[i] = ep
                ep = high[i]
                af = af_start
            else:
                if low[i] < ep:
                    ep = low[i]
                    af = min(af + af_start, af_max)

    return sar


def calc_ichimoku_tenkan(df: pd.DataFrame, period: int = 9) -> pd.Series:
    """이치모쿠 전환선 (Tenkan-sen)"""
    if df.empty or len(df) < period:
        return pd.Series(dtype=float)
    return (df["high"].rolling(window=period).max() + df["low"].rolling(window=period).min()) / 2


def calc_ichimoku_kijun(df: pd.DataFrame, period: int = 26) -> pd.Series:
    """이치모쿠 기준선 (Kijun-sen)"""
    if df.empty or len(df) < period:
        return pd.Series(dtype=float)
    return (df["high"].rolling(window=period).max() + df["low"].rolling(window=period).min()) / 2


def calc_hma(df: pd.DataFrame, period: int = 20) -> pd.Series:
    """헐 이동평균 (Hull Moving Average)"""
    if df.empty or len(df) < period:
        return pd.Series(dtype=float)
    import math
    half_period = int(period / 2)
    sqrt_period = int(math.sqrt(period))
    wma_half = df["close"].rolling(window=half_period).mean()
    wma_full = df["close"].rolling(window=period).mean()
    diff = 2 * wma_half - wma_full
    return diff.rolling(window=sqrt_period).mean()


def calc_dema(df: pd.DataFrame, period: int = 20) -> pd.Series:
    """이중 지수이동평균 (Double EMA)"""
    ema1 = calc_ema(df, period)
    if ema1.empty:
        return pd.Series(dtype=float)
    ema2_series = ema1.ewm(span=period, adjust=False).mean()
    return 2 * ema1 - ema2_series


def calc_cmf(df: pd.DataFrame, period: int = 20) -> pd.Series:
    """차이킨 머니 플로우 (Chaikin Money Flow)"""
    if df.empty or len(df) < period:
        return pd.Series(dtype=float)
    mfm = ((df["close"] - df["low"]) - (df["high"] - df["close"])) / (df["high"] - df["low"])
    mfm = mfm.fillna(0)
    mfv = mfm * df["volume"]
    return mfv.rolling(window=period).sum() / df["volume"].rolling(window=period).sum()


# ──────────────────────────────────────────────────────────────
# Tier 2 지표 (48개 추가)
# ──────────────────────────────────────────────────────────────

# ── 이동평균 (10개) ──────────────────────────────────────────

def calc_tema(df: pd.DataFrame, period: int = 20) -> pd.Series:
    """삼중 EMA (Triple EMA)"""
    ema1 = calc_ema(df, period)
    if ema1.empty:
        return pd.Series(dtype=float)
    ema2 = ema1.ewm(span=period, adjust=False).mean()
    ema3 = ema2.ewm(span=period, adjust=False).mean()
    return 3 * ema1 - 3 * ema2 + ema3


def calc_kama(df: pd.DataFrame, period: int = 20) -> pd.Series:
    """카우프만 적응형 이동평균 (Kaufman Adaptive MA)"""
    if df.empty or len(df) < period:
        return pd.Series(dtype=float)
    close = df["close"]
    direction = (close - close.shift(period)).abs()
    volatility = close.diff().abs().rolling(window=period).sum()
    er = direction / volatility.replace(0, np.nan)
    fast_sc, slow_sc = 2 / 3, 2 / 31
    sc = (er * (fast_sc - slow_sc) + slow_sc) ** 2
    kama = pd.Series(np.nan, index=close.index)
    kama.iloc[period - 1] = close.iloc[period - 1]
    for i in range(period, len(close)):
        kama.iloc[i] = kama.iloc[i - 1] + sc.iloc[i] * (close.iloc[i] - kama.iloc[i - 1])
    return kama


def calc_alma(df: pd.DataFrame, period: int = 20, sigma: float = 6.0, offset: float = 0.85) -> pd.Series:
    """아르노 르구 이동평균 (Arnaud Legoux MA)"""
    if df.empty or len(df) < period:
        return pd.Series(dtype=float)
    close = df["close"]
    m = offset * (period - 1)
    s = period / sigma
    w = np.exp(-((np.arange(period) - m) ** 2) / (2 * s * s))
    w /= w.sum()
    return close.rolling(window=period).apply(lambda x: np.dot(x, w), raw=True)


def calc_lwma(df: pd.DataFrame, period: int = 20) -> pd.Series:
    """선형 가중 이동평균 (Linear Weighted MA)"""
    if df.empty or len(df) < period:
        return pd.Series(dtype=float)
    weights = np.arange(1, period + 1, dtype=float)
    return df["close"].rolling(window=period).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True)


def calc_trima(df: pd.DataFrame, period: int = 20) -> pd.Series:
    """삼각 이동평균 (Triangular MA) — SMA의 SMA"""
    if df.empty or len(df) < period:
        return pd.Series(dtype=float)
    half = (period + 1) // 2
    sma1 = df["close"].rolling(window=half).mean()
    return sma1.rolling(window=half).mean()


def calc_t3(df: pd.DataFrame, period: int = 20, volume_factor: float = 0.7) -> pd.Series:
    """T3 이동평균 (Tillson T3)"""
    if df.empty or len(df) < period:
        return pd.Series(dtype=float)
    close = df["close"]
    v = volume_factor
    c1 = -(v ** 3)
    c2 = 3 * v * v + 3 * v * v * v
    c3 = -6 * v * v - 3 * v - 3 * v * v * v
    c4 = 1 + 3 * v + v * v * v + 3 * v * v
    e1 = close.ewm(span=period, adjust=False).mean()
    e2 = e1.ewm(span=period, adjust=False).mean()
    e3 = e2.ewm(span=period, adjust=False).mean()
    e4 = e3.ewm(span=period, adjust=False).mean()
    e5 = e4.ewm(span=period, adjust=False).mean()
    e6 = e5.ewm(span=period, adjust=False).mean()
    return c1 * e6 + c2 * e5 + c3 * e4 + c4 * e3


def calc_zlema(df: pd.DataFrame, period: int = 20) -> pd.Series:
    """제로 래그 EMA (Zero Lag EMA)"""
    if df.empty or len(df) < period:
        return pd.Series(dtype=float)
    lag = (period - 1) // 2
    adjusted = 2 * df["close"] - df["close"].shift(lag)
    return adjusted.ewm(span=period, adjust=False).mean()


def calc_wma(df: pd.DataFrame, period: int = 20) -> pd.Series:
    """가중 이동평균 (Weighted MA) — Wilder 방식"""
    if df.empty or len(df) < period:
        return pd.Series(dtype=float)
    return df["close"].ewm(alpha=1.0 / period, adjust=False).mean()


def calc_frama(df: pd.DataFrame, period: int = 20) -> pd.Series:
    """프랙탈 적응형 이동평균 (Fractal Adaptive MA) — 근사 구현"""
    if df.empty or len(df) < period:
        return pd.Series(dtype=float)
    close = df["close"]
    half = period // 2
    h1 = close.rolling(half).max()
    l1 = close.rolling(half).min()
    h2 = close.shift(half).rolling(half).max()
    l2 = close.shift(half).rolling(half).min()
    h_all = close.rolling(period).max()
    l_all = close.rolling(period).min()
    n1 = (h1 - l1) / half
    n2 = (h2 - l2) / half
    n3 = (h_all - l_all) / period
    d = (np.log(n1 + n2) - np.log(n3)) / np.log(2)
    alpha = np.exp(-4.6 * (d - 1)).clip(0.01, 1.0)
    frama = pd.Series(np.nan, index=close.index)
    start = period - 1
    frama.iloc[start] = close.iloc[start]
    for i in range(start + 1, len(close)):
        a = alpha.iloc[i] if not np.isnan(alpha.iloc[i]) else 0.5
        frama.iloc[i] = a * close.iloc[i] + (1 - a) * frama.iloc[i - 1]
    return frama


def calc_vidya(df: pd.DataFrame, period: int = 20) -> pd.Series:
    """가변 인덱스 동적 평균 (Variable Index Dynamic Average)"""
    if df.empty or len(df) < period:
        return pd.Series(dtype=float)
    close = df["close"]
    cmo_abs = calc_cmo(df, period).abs() / 100
    sc = 2 / (period + 1)
    vidya = pd.Series(np.nan, index=close.index)
    vidya.iloc[period - 1] = close.iloc[period - 1]
    for i in range(period, len(close)):
        k = sc * cmo_abs.iloc[i] if not np.isnan(cmo_abs.iloc[i]) else 0
        vidya.iloc[i] = k * close.iloc[i] + (1 - k) * vidya.iloc[i - 1]
    return vidya


# ── 오실레이터 (11개) ───────────────────────────────────────

def calc_apo(df: pd.DataFrame, fast: int = 12, slow: int = 26) -> pd.Series:
    """절대 가격 오실레이터 (Absolute Price Oscillator)"""
    if df.empty or len(df) < slow:
        return pd.Series(dtype=float)
    ema_fast = df["close"].ewm(span=fast, adjust=False).mean()
    ema_slow = df["close"].ewm(span=slow, adjust=False).mean()
    return ema_fast - ema_slow


def calc_ppo(df: pd.DataFrame, fast: int = 12, slow: int = 26) -> pd.Series:
    """백분율 가격 오실레이터 (Percentage Price Oscillator)"""
    if df.empty or len(df) < slow:
        return pd.Series(dtype=float)
    ema_fast = df["close"].ewm(span=fast, adjust=False).mean()
    ema_slow = df["close"].ewm(span=slow, adjust=False).mean()
    return ((ema_fast - ema_slow) / ema_slow) * 100


def calc_cmo(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """샹데 모멘텀 오실레이터 (Chande Momentum Oscillator)"""
    if df.empty or len(df) < period:
        return pd.Series(dtype=float)
    diff = df["close"].diff()
    gain = diff.clip(lower=0).rolling(window=period).sum()
    loss = (-diff.clip(upper=0)).rolling(window=period).sum()
    return ((gain - loss) / (gain + loss).replace(0, np.nan)) * 100


def calc_ao(df: pd.DataFrame) -> pd.Series:
    """어썸 오실레이터 (Awesome Oscillator)"""
    if df.empty or len(df) < 34:
        return pd.Series(dtype=float)
    hl2 = (df["high"] + df["low"]) / 2
    return hl2.rolling(window=5).mean() - hl2.rolling(window=34).mean()


def calc_cho(df: pd.DataFrame, fast: int = 3, slow: int = 10) -> pd.Series:
    """차이킨 오실레이터 (Chaikin Oscillator) — ADL의 EMA 차이"""
    if df.empty or len(df) < slow:
        return pd.Series(dtype=float)
    adl = calc_adl(df)
    if adl.empty:
        return pd.Series(dtype=float)
    return adl.ewm(span=fast, adjust=False).mean() - adl.ewm(span=slow, adjust=False).mean()


def calc_ultosc(df: pd.DataFrame, p1: int = 7, p2: int = 14, p3: int = 28) -> pd.Series:
    """궁극 오실레이터 (Ultimate Oscillator)"""
    if df.empty or len(df) < p3:
        return pd.Series(dtype=float)
    prev_close = df["close"].shift(1)
    tl = pd.concat([df["low"], prev_close], axis=1).min(axis=1)
    bp = df["close"] - tl
    tr = pd.concat([df["high"], prev_close], axis=1).max(axis=1) - tl
    avg1 = bp.rolling(p1).sum() / tr.rolling(p1).sum()
    avg2 = bp.rolling(p2).sum() / tr.rolling(p2).sum()
    avg3 = bp.rolling(p3).sum() / tr.rolling(p3).sum()
    return 100 * (4 * avg1 + 2 * avg2 + avg3) / 7


def calc_trix(df: pd.DataFrame, period: int = 15) -> pd.Series:
    """TRIX — 삼중 EMA의 ROC"""
    if df.empty or len(df) < period:
        return pd.Series(dtype=float)
    e1 = df["close"].ewm(span=period, adjust=False).mean()
    e2 = e1.ewm(span=period, adjust=False).mean()
    e3 = e2.ewm(span=period, adjust=False).mean()
    return e3.pct_change() * 100


def calc_tsi(df: pd.DataFrame, long: int = 25, short: int = 13) -> pd.Series:
    """참강도지수 (True Strength Index)"""
    if df.empty or len(df) < long:
        return pd.Series(dtype=float)
    diff = df["close"].diff()
    smooth1 = diff.ewm(span=long, adjust=False).mean().ewm(span=short, adjust=False).mean()
    smooth2 = diff.abs().ewm(span=long, adjust=False).mean().ewm(span=short, adjust=False).mean()
    return (smooth1 / smooth2.replace(0, np.nan)) * 100


def calc_rvi(df: pd.DataFrame, period: int = 10) -> pd.Series:
    """상대활력지수 (Relative Vigor Index)"""
    if df.empty or len(df) < period + 3:
        return pd.Series(dtype=float)
    co = df["close"] - df["open"]
    hl = df["high"] - df["low"]
    num = (co + 2 * co.shift(1) + 2 * co.shift(2) + co.shift(3)) / 6
    den = (hl + 2 * hl.shift(1) + 2 * hl.shift(2) + hl.shift(3)) / 6
    return num.rolling(window=period).mean() / den.rolling(window=period).mean().replace(0, np.nan)


def calc_dpo(df: pd.DataFrame, period: int = 20) -> pd.Series:
    """가격추세제거 오실레이터 (Detrended Price Oscillator)"""
    if df.empty or len(df) < period:
        return pd.Series(dtype=float)
    shift = period // 2 + 1
    return df["close"] - df["close"].rolling(window=period).mean().shift(shift)


def calc_kvo(df: pd.DataFrame, fast: int = 34, slow: int = 55) -> pd.Series:
    """클링거 볼륨 오실레이터 (Klinger Volume Oscillator)"""
    if df.empty or len(df) < slow:
        return pd.Series(dtype=float)
    hlc = df["high"] + df["low"] + df["close"]
    trend = np.where(hlc > hlc.shift(1), 1, -1)
    dm = df["high"] - df["low"]
    cm = pd.Series(np.nan, index=df.index, dtype=float)
    cm.iloc[0] = dm.iloc[0]
    for i in range(1, len(df)):
        cm.iloc[i] = cm.iloc[i - 1] + dm.iloc[i] if trend[i] == trend[i - 1] else dm.iloc[i - 1] + dm.iloc[i]
    vf = df["volume"] * abs(2 * dm / cm.replace(0, np.nan) - 1) * trend * 100
    return vf.ewm(span=fast, adjust=False).mean() - vf.ewm(span=slow, adjust=False).mean()


# ── 추세 (9개) ──────────────────────────────────────────────

def calc_adxr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """ADXR — ADX의 이동평균"""
    adx = calc_adx(df, period)
    if adx.empty:
        return pd.Series(dtype=float)
    return (adx + adx.shift(period)) / 2


def calc_vortex_plus(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """Vortex Indicator +"""
    if df.empty or len(df) < period + 1:
        return pd.Series(dtype=float)
    vm_plus = (df["high"] - df["low"].shift(1)).abs()
    tr = pd.concat([df["high"] - df["low"],
                    (df["high"] - df["close"].shift(1)).abs(),
                    (df["low"] - df["close"].shift(1)).abs()], axis=1).max(axis=1)
    return vm_plus.rolling(period).sum() / tr.rolling(period).sum()


def calc_vortex_minus(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """Vortex Indicator -"""
    if df.empty or len(df) < period + 1:
        return pd.Series(dtype=float)
    vm_minus = (df["low"] - df["high"].shift(1)).abs()
    tr = pd.concat([df["high"] - df["low"],
                    (df["high"] - df["close"].shift(1)).abs(),
                    (df["low"] - df["close"].shift(1)).abs()], axis=1).max(axis=1)
    return vm_minus.rolling(period).sum() / tr.rolling(period).sum()


def calc_chop(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """Choppiness Index"""
    if df.empty or len(df) < period:
        return pd.Series(dtype=float)
    atr = calc_atr(df, 1)
    if atr.empty:
        return pd.Series(dtype=float)
    atr_sum = atr.rolling(period).sum()
    high_max = df["high"].rolling(period).max()
    low_min = df["low"].rolling(period).min()
    return 100 * np.log10(atr_sum / (high_max - low_min).replace(0, np.nan)) / np.log10(period)


def calc_kst(df: pd.DataFrame) -> pd.Series:
    """KST 오실레이터 (Know Sure Thing)"""
    if df.empty or len(df) < 30:
        return pd.Series(dtype=float)
    roc1 = df["close"].pct_change(10) * 100
    roc2 = df["close"].pct_change(15) * 100
    roc3 = df["close"].pct_change(20) * 100
    roc4 = df["close"].pct_change(30) * 100
    return (roc1.rolling(10).mean() * 1 +
            roc2.rolling(10).mean() * 2 +
            roc3.rolling(10).mean() * 3 +
            roc4.rolling(15).mean() * 4)


def calc_coppock(df: pd.DataFrame) -> pd.Series:
    """코폭 커브 (Coppock Curve)"""
    if df.empty or len(df) < 14:
        return pd.Series(dtype=float)
    roc14 = df["close"].pct_change(14) * 100
    roc11 = df["close"].pct_change(11) * 100
    return (roc14 + roc11).ewm(span=10, adjust=False).mean()


def calc_mass_index(df: pd.DataFrame, period: int = 25) -> pd.Series:
    """Mass Index"""
    if df.empty or len(df) < period:
        return pd.Series(dtype=float)
    hl = df["high"] - df["low"]
    ema1 = hl.ewm(span=9, adjust=False).mean()
    ema2 = ema1.ewm(span=9, adjust=False).mean()
    ratio = ema1 / ema2.replace(0, np.nan)
    return ratio.rolling(window=period).sum()


def calc_schaff(df: pd.DataFrame, period: int = 23, fast: int = 10, slow: int = 50) -> pd.Series:
    """Schaff Trend Cycle"""
    if df.empty or len(df) < slow:
        return pd.Series(dtype=float)
    close = df["close"]
    macd_line = close.ewm(span=fast, adjust=False).mean() - close.ewm(span=slow, adjust=False).mean()
    ll = macd_line.rolling(period).min()
    hh = macd_line.rolling(period).max()
    stoch1 = ((macd_line - ll) / (hh - ll).replace(0, np.nan)) * 100
    pf = stoch1.ewm(com=1, adjust=False).mean()
    ll2 = pf.rolling(period).min()
    hh2 = pf.rolling(period).max()
    stoch2 = ((pf - ll2) / (hh2 - ll2).replace(0, np.nan)) * 100
    return stoch2.ewm(com=1, adjust=False).mean()


def calc_fisher(df: pd.DataFrame, period: int = 9) -> pd.Series:
    """Fisher Transform"""
    if df.empty or len(df) < period:
        return pd.Series(dtype=float)
    hl2 = (df["high"] + df["low"]) / 2
    highest = hl2.rolling(period).max()
    lowest = hl2.rolling(period).min()
    val = 2 * ((hl2 - lowest) / (highest - lowest).replace(0, np.nan)) - 1
    val = val.clip(-0.999, 0.999)
    fisher = pd.Series(0.0, index=df.index)
    for i in range(period, len(df)):
        fisher.iloc[i] = 0.5 * np.log((1 + val.iloc[i]) / (1 - val.iloc[i])) * 0.5 + fisher.iloc[i - 1] * 0.5
    return fisher


# ── 거래량 (8개) ────────────────────────────────────────────

def calc_ad(df: pd.DataFrame) -> pd.Series:
    """축적/분배 (Accumulation/Distribution) — 단일 바"""
    if df.empty:
        return pd.Series(dtype=float)
    hl = (df["high"] - df["low"]).replace(0, np.nan)
    mfm = ((df["close"] - df["low"]) - (df["high"] - df["close"])) / hl
    return mfm.fillna(0) * df["volume"]


def calc_adl(df: pd.DataFrame) -> pd.Series:
    """축적/분배선 (A/D Line) — AD의 누적합"""
    ad = calc_ad(df)
    if ad.empty:
        return pd.Series(dtype=float)
    return ad.cumsum()


def calc_force(df: pd.DataFrame, period: int = 13) -> pd.Series:
    """Force Index"""
    if df.empty or len(df) < period:
        return pd.Series(dtype=float)
    fi = df["close"].diff() * df["volume"]
    return fi.ewm(span=period, adjust=False).mean()


def calc_vwma(df: pd.DataFrame, period: int = 20) -> pd.Series:
    """거래량 가중 이동평균 (Volume Weighted MA)"""
    if df.empty or len(df) < period:
        return pd.Series(dtype=float)
    pv = df["close"] * df["volume"]
    return pv.rolling(window=period).sum() / df["volume"].rolling(window=period).sum()


def calc_eom(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """이동 용이성 (Ease of Movement)"""
    if df.empty or len(df) < period:
        return pd.Series(dtype=float)
    dm = ((df["high"] + df["low"]) / 2) - ((df["high"].shift(1) + df["low"].shift(1)) / 2)
    br = df["volume"] / (df["high"] - df["low"]).replace(0, np.nan)
    return (dm / br).rolling(window=period).mean()



# ── 변동성 (5개) ────────────────────────────────────────────

def calc_variance(df: pd.DataFrame, period: int = 20) -> pd.Series:
    """분산 (Variance)"""
    if df.empty or len(df) < period:
        return pd.Series(dtype=float)
    return df["close"].rolling(window=period).var()


def calc_accbands_upper(df: pd.DataFrame, period: int = 20) -> pd.Series:
    """가속밴드 상단 (Acceleration Bands Upper)"""
    if df.empty or len(df) < period:
        return pd.Series(dtype=float)
    factor = df["high"] * (1 + 2 * ((df["high"] - df["low"]) / (df["high"] + df["low"]).replace(0, np.nan)))
    return factor.rolling(window=period).mean()


def calc_accbands_lower(df: pd.DataFrame, period: int = 20) -> pd.Series:
    """가속밴드 하단 (Acceleration Bands Lower)"""
    if df.empty or len(df) < period:
        return pd.Series(dtype=float)
    factor = df["low"] * (1 - 2 * ((df["high"] - df["low"]) / (df["high"] + df["low"]).replace(0, np.nan)))
    return factor.rolling(window=period).mean()


def calc_beta(df: pd.DataFrame, benchmark: pd.Series, period: int = 20) -> pd.Series:
    """베타 (Beta) — 벤치마크 대비"""
    if df.empty or len(df) < period or len(benchmark) < period:
        return pd.Series(dtype=float)
    stock_ret = df["close"].pct_change()
    bench_ret = benchmark.pct_change()
    covar = stock_ret.rolling(period).cov(bench_ret)
    var = bench_ret.rolling(period).var()
    return covar / var.replace(0, np.nan)


def calc_alpha(df: pd.DataFrame, benchmark: pd.Series, period: int = 20) -> pd.Series:
    """알파 (Alpha) — 벤치마크 대비"""
    if df.empty or len(df) < period or len(benchmark) < period:
        return pd.Series(dtype=float)
    beta = calc_beta(df, benchmark, period)
    stock_ret = df["close"].pct_change().rolling(period).mean()
    bench_ret = benchmark.pct_change().rolling(period).mean()
    return stock_ret - beta * bench_ret


# ── 기타 (8개) ──────────────────────────────────────────────

def calc_midpoint(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """중간점 — 기간 내 (최고+최저)/2"""
    if df.empty or len(df) < period:
        return pd.Series(dtype=float)
    return (df["close"].rolling(period).max() + df["close"].rolling(period).min()) / 2


def calc_midprice(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """중간가격 — 기간 내 (high_max + low_min)/2"""
    if df.empty or len(df) < period:
        return pd.Series(dtype=float)
    return (df["high"].rolling(period).max() + df["low"].rolling(period).min()) / 2


def calc_logr(df: pd.DataFrame) -> pd.Series:
    """로그 수익률"""
    if df.empty:
        return pd.Series(dtype=float)
    return np.log(df["close"] / df["close"].shift(1))


def calc_bop(df: pd.DataFrame) -> pd.Series:
    """매수/매도 파워 (Balance of Power)"""
    if df.empty:
        return pd.Series(dtype=float)
    return (df["close"] - df["open"]) / (df["high"] - df["low"]).replace(0, np.nan)


def calc_regression_slope(df: pd.DataFrame, period: int = 20) -> pd.Series:
    """회귀 기울기 (Linear Regression Slope)"""
    if df.empty or len(df) < period:
        return pd.Series(dtype=float)
    x = np.arange(period, dtype=float)
    x_mean = x.mean()
    x_var = ((x - x_mean) ** 2).sum()
    def _slope(y):
        return np.sum((x - x_mean) * (y - y.mean())) / x_var
    return df["close"].rolling(window=period).apply(_slope, raw=True)


def calc_regression_intercept(df: pd.DataFrame, period: int = 20) -> pd.Series:
    """회귀 절편 (Linear Regression Intercept)"""
    if df.empty or len(df) < period:
        return pd.Series(dtype=float)
    x = np.arange(period, dtype=float)
    x_mean = x.mean()
    x_var = ((x - x_mean) ** 2).sum()
    def _intercept(y):
        slope = np.sum((x - x_mean) * (y - y.mean())) / x_var
        return y.mean() - slope * x_mean
    return df["close"].rolling(window=period).apply(_intercept, raw=True)


def calc_pivot(df: pd.DataFrame) -> pd.Series:
    """피봇 포인트 (Pivot Point)"""
    if df.empty:
        return pd.Series(dtype=float)
    return (df["high"] + df["low"] + df["close"]) / 3


def calc_augen(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """오겐 가격 스파이크 (Augen Price Spike)"""
    if df.empty or len(df) < period:
        return pd.Series(dtype=float)
    log_ret = np.log(df["close"] / df["close"].shift(1))
    return log_ret / log_ret.rolling(window=period).std().replace(0, np.nan)

