"""
캔들스틱 패턴 탐지 모듈

OHLC DataFrame → 패턴 탐지 → +1(bullish) / -1(bearish) / 0(없음)

pandas 기반 직접 구현. 외부 의존성 없음.
"""

from typing import Optional

import pandas as pd


def _body(o, c):
    return abs(c - o)


def _upper_shadow(h, o, c):
    return h - max(o, c)


def _lower_shadow(o, c, l):
    return min(o, c) - l


def _range(h, l):
    return h - l


def _is_bullish(o, c):
    return c > o


def _is_bearish(o, c):
    return c < o


def detect_pattern(df: pd.DataFrame, pattern_id: str) -> int:
    """
    최근 캔들에서 패턴 탐지

    Args:
        df: OHLC DataFrame (open, high, low, close)
        pattern_id: 패턴 ID (예: "doji", "hammer")

    Returns:
        +1 (bullish), -1 (bearish), 0 (미감지)
    """
    if df.empty or len(df) < 5:
        return 0

    detector = PATTERN_DETECTORS.get(pattern_id)
    if detector is None:
        return 0

    try:
        return detector(df)
    except Exception:
        return 0


def _get_ohlc(df, idx=-1):
    return (
        float(df["open"].iloc[idx]),
        float(df["high"].iloc[idx]),
        float(df["low"].iloc[idx]),
        float(df["close"].iloc[idx]),
    )


def _avg_body(df, n=10):
    bodies = abs(df["close"].tail(n) - df["open"].tail(n))
    return float(bodies.mean()) if len(bodies) > 0 else 1.0


# =============================================================================
# Single Candle Patterns
# =============================================================================


def _doji(df):
    o, h, l, c = _get_ohlc(df)
    r = _range(h, l)
    if r == 0:
        return 0
    return 1 if _body(o, c) / r < 0.1 else 0


def _dragonfly_doji(df):
    o, h, l, c = _get_ohlc(df)
    r = _range(h, l)
    if r == 0:
        return 0
    if _body(o, c) / r < 0.1 and _lower_shadow(o, c, l) / r > 0.6 and _upper_shadow(h, o, c) / r < 0.1:
        return 1
    return 0


def _gravestone_doji(df):
    o, h, l, c = _get_ohlc(df)
    r = _range(h, l)
    if r == 0:
        return 0
    if _body(o, c) / r < 0.1 and _upper_shadow(h, o, c) / r > 0.6 and _lower_shadow(o, c, l) / r < 0.1:
        return -1
    return 0


def _long_legged_doji(df):
    o, h, l, c = _get_ohlc(df)
    r = _range(h, l)
    if r == 0:
        return 0
    if _body(o, c) / r < 0.1 and _upper_shadow(h, o, c) / r > 0.3 and _lower_shadow(o, c, l) / r > 0.3:
        return 1
    return 0


def _hammer(df):
    o, h, l, c = _get_ohlc(df)
    b = _body(o, c)
    r = _range(h, l)
    if r == 0 or b == 0:
        return 0
    ls = _lower_shadow(o, c, l)
    us = _upper_shadow(h, o, c)
    if ls >= 2 * b and us <= b * 0.3:
        return 1
    return 0


def _hanging_man(df):
    o, h, l, c = _get_ohlc(df)
    b = _body(o, c)
    r = _range(h, l)
    if r == 0 or b == 0:
        return 0
    ls = _lower_shadow(o, c, l)
    us = _upper_shadow(h, o, c)
    if ls >= 2 * b and us <= b * 0.3:
        return -1
    return 0


def _inverted_hammer(df):
    o, h, l, c = _get_ohlc(df)
    b = _body(o, c)
    if b == 0:
        return 0
    us = _upper_shadow(h, o, c)
    ls = _lower_shadow(o, c, l)
    if us >= 2 * b and ls <= b * 0.3:
        return 1
    return 0


def _shooting_star(df):
    o, h, l, c = _get_ohlc(df)
    b = _body(o, c)
    if b == 0:
        return 0
    us = _upper_shadow(h, o, c)
    ls = _lower_shadow(o, c, l)
    if us >= 2 * b and ls <= b * 0.3:
        return -1
    return 0


def _marubozu(df):
    o, h, l, c = _get_ohlc(df)
    r = _range(h, l)
    if r == 0:
        return 0
    us = _upper_shadow(h, o, c)
    ls = _lower_shadow(o, c, l)
    if us / r < 0.05 and ls / r < 0.05:
        return 1 if _is_bullish(o, c) else -1
    return 0


def _closing_marubozu(df):
    o, h, l, c = _get_ohlc(df)
    r = _range(h, l)
    if r == 0:
        return 0
    if _is_bullish(o, c) and _upper_shadow(h, o, c) / r < 0.05:
        return 1
    if _is_bearish(o, c) and _lower_shadow(o, c, l) / r < 0.05:
        return -1
    return 0


def _opening_marubozu(df):
    o, h, l, c = _get_ohlc(df)
    r = _range(h, l)
    if r == 0:
        return 0
    if _is_bullish(o, c) and _lower_shadow(o, c, l) / r < 0.05:
        return 1
    if _is_bearish(o, c) and _upper_shadow(h, o, c) / r < 0.05:
        return -1
    return 0


def _spinning_top(df):
    o, h, l, c = _get_ohlc(df)
    r = _range(h, l)
    if r == 0:
        return 0
    b = _body(o, c)
    if b / r < 0.3 and _upper_shadow(h, o, c) > b and _lower_shadow(o, c, l) > b:
        return 1
    return 0


def _belt_hold(df):
    o, h, l, c = _get_ohlc(df)
    avg = _avg_body(df)
    b = _body(o, c)
    if b > avg * 1.5:
        if _is_bullish(o, c) and _lower_shadow(o, c, l) < b * 0.05:
            return 1
        if _is_bearish(o, c) and _upper_shadow(h, o, c) < b * 0.05:
            return -1
    return 0


def _high_wave(df):
    o, h, l, c = _get_ohlc(df)
    r = _range(h, l)
    if r == 0:
        return 0
    b = _body(o, c)
    if b / r < 0.15 and _upper_shadow(h, o, c) / r > 0.3 and _lower_shadow(o, c, l) / r > 0.3:
        return 1
    return 0


def _rickshaw_man(df):
    return _long_legged_doji(df)


# =============================================================================
# Double Candle Patterns
# =============================================================================


def _engulfing(df):
    o1, h1, l1, c1 = _get_ohlc(df, -2)
    o2, h2, l2, c2 = _get_ohlc(df, -1)
    if _is_bearish(o1, c1) and _is_bullish(o2, c2) and o2 <= c1 and c2 >= o1:
        return 1
    if _is_bullish(o1, c1) and _is_bearish(o2, c2) and o2 >= c1 and c2 <= o1:
        return -1
    return 0


def _harami(df):
    o1, h1, l1, c1 = _get_ohlc(df, -2)
    o2, h2, l2, c2 = _get_ohlc(df, -1)
    b1 = _body(o1, c1)
    b2 = _body(o2, c2)
    if b1 > 0 and b2 < b1:
        if _is_bearish(o1, c1) and _is_bullish(o2, c2) and o2 >= c1 and c2 <= o1:
            return 1
        if _is_bullish(o1, c1) and _is_bearish(o2, c2) and o2 <= c1 and c2 >= o1:
            return -1
    return 0


def _harami_cross(df):
    o1, h1, l1, c1 = _get_ohlc(df, -2)
    o2, h2, l2, c2 = _get_ohlc(df, -1)
    b1 = _body(o1, c1)
    r2 = _range(h2, l2)
    if b1 > 0 and r2 > 0 and _body(o2, c2) / r2 < 0.1:
        if min(o2, c2) >= min(o1, c1) and max(o2, c2) <= max(o1, c1):
            return 1 if _is_bearish(o1, c1) else -1
    return 0


def _piercing(df):
    o1, h1, l1, c1 = _get_ohlc(df, -2)
    o2, h2, l2, c2 = _get_ohlc(df, -1)
    mid1 = (o1 + c1) / 2
    if _is_bearish(o1, c1) and _is_bullish(o2, c2) and o2 < c1 and c2 > mid1 and c2 < o1:
        return 1
    return 0


def _dark_cloud_cover(df):
    o1, h1, l1, c1 = _get_ohlc(df, -2)
    o2, h2, l2, c2 = _get_ohlc(df, -1)
    mid1 = (o1 + c1) / 2
    if _is_bullish(o1, c1) and _is_bearish(o2, c2) and o2 > c1 and c2 < mid1 and c2 > o1:
        return -1
    return 0


def _counterattack(df):
    o1, h1, l1, c1 = _get_ohlc(df, -2)
    o2, h2, l2, c2 = _get_ohlc(df, -1)
    avg = _avg_body(df)
    tol = avg * 0.05
    if _is_bearish(o1, c1) and _is_bullish(o2, c2) and abs(c2 - c1) < tol:
        return 1
    if _is_bullish(o1, c1) and _is_bearish(o2, c2) and abs(c2 - c1) < tol:
        return -1
    return 0


def _tweezer_top(df):
    o1, h1, l1, c1 = _get_ohlc(df, -2)
    o2, h2, l2, c2 = _get_ohlc(df, -1)
    tol = _avg_body(df) * 0.05
    if abs(h1 - h2) < tol and _is_bullish(o1, c1) and _is_bearish(o2, c2):
        return -1
    return 0


def _tweezer_bottom(df):
    o1, h1, l1, c1 = _get_ohlc(df, -2)
    o2, h2, l2, c2 = _get_ohlc(df, -1)
    tol = _avg_body(df) * 0.05
    if abs(l1 - l2) < tol and _is_bearish(o1, c1) and _is_bullish(o2, c2):
        return 1
    return 0


def _on_neck(df):
    o1, h1, l1, c1 = _get_ohlc(df, -2)
    o2, h2, l2, c2 = _get_ohlc(df, -1)
    tol = _avg_body(df) * 0.05
    if _is_bearish(o1, c1) and _is_bullish(o2, c2) and abs(c2 - l1) < tol:
        return -1
    return 0


def _in_neck(df):
    o1, h1, l1, c1 = _get_ohlc(df, -2)
    o2, h2, l2, c2 = _get_ohlc(df, -1)
    tol = _avg_body(df) * 0.05
    if _is_bearish(o1, c1) and _is_bullish(o2, c2) and abs(c2 - c1) < tol:
        return -1
    return 0


def _thrusting(df):
    o1, h1, l1, c1 = _get_ohlc(df, -2)
    o2, h2, l2, c2 = _get_ohlc(df, -1)
    mid1 = (o1 + c1) / 2
    if _is_bearish(o1, c1) and _is_bullish(o2, c2) and c2 > c1 and c2 < mid1:
        return -1
    return 0


def _separating_lines(df):
    o1, h1, l1, c1 = _get_ohlc(df, -2)
    o2, h2, l2, c2 = _get_ohlc(df, -1)
    tol = _avg_body(df) * 0.05
    if _is_bearish(o1, c1) and _is_bullish(o2, c2) and abs(o1 - o2) < tol:
        return 1
    if _is_bullish(o1, c1) and _is_bearish(o2, c2) and abs(o1 - o2) < tol:
        return -1
    return 0


def _meeting_lines(df):
    o1, h1, l1, c1 = _get_ohlc(df, -2)
    o2, h2, l2, c2 = _get_ohlc(df, -1)
    tol = _avg_body(df) * 0.05
    if _is_bearish(o1, c1) and _is_bullish(o2, c2) and abs(c1 - c2) < tol:
        return 1
    if _is_bullish(o1, c1) and _is_bearish(o2, c2) and abs(c1 - c2) < tol:
        return -1
    return 0


def _kicking(df):
    o1, h1, l1, c1 = _get_ohlc(df, -2)
    o2, h2, l2, c2 = _get_ohlc(df, -1)
    r1, r2 = _range(h1, l1), _range(h2, l2)
    if r1 == 0 or r2 == 0:
        return 0
    m1 = _body(o1, c1) / r1 > 0.9
    m2 = _body(o2, c2) / r2 > 0.9
    if m1 and m2 and _is_bearish(o1, c1) and _is_bullish(o2, c2) and o2 > o1:
        return 1
    if m1 and m2 and _is_bullish(o1, c1) and _is_bearish(o2, c2) and o2 < o1:
        return -1
    return 0


def _matching_low(df):
    o1, h1, l1, c1 = _get_ohlc(df, -2)
    o2, h2, l2, c2 = _get_ohlc(df, -1)
    tol = _avg_body(df) * 0.03
    if _is_bearish(o1, c1) and _is_bearish(o2, c2) and abs(c1 - c2) < tol:
        return 1
    return 0


def _matching_high(df):
    o1, h1, l1, c1 = _get_ohlc(df, -2)
    o2, h2, l2, c2 = _get_ohlc(df, -1)
    tol = _avg_body(df) * 0.03
    if _is_bullish(o1, c1) and _is_bullish(o2, c2) and abs(c1 - c2) < tol:
        return -1
    return 0


def _gap_side_by_side_white(df):
    o1, _, _, c1 = _get_ohlc(df, -2)
    o2, _, _, c2 = _get_ohlc(df, -1)
    tol = _avg_body(df) * 0.1
    if _is_bullish(o1, c1) and _is_bullish(o2, c2) and abs(o1 - o2) < tol:
        return 1
    return 0


def _homing_pigeon(df):
    o1, h1, l1, c1 = _get_ohlc(df, -2)
    o2, h2, l2, c2 = _get_ohlc(df, -1)
    if _is_bearish(o1, c1) and _is_bearish(o2, c2):
        if o2 < o1 and c2 > c1 and _body(o2, c2) < _body(o1, c1):
            return 1
    return 0


def _dojistar(df):
    o1, h1, l1, c1 = _get_ohlc(df, -2)
    o2, h2, l2, c2 = _get_ohlc(df, -1)
    r2 = _range(h2, l2)
    if r2 > 0 and _body(o2, c2) / r2 < 0.1:
        if _is_bullish(o1, c1) and o2 > c1:
            return -1
        if _is_bearish(o1, c1) and o2 < c1:
            return 1
    return 0


def _kicking_by_length(df):
    return _kicking(df)


# =============================================================================
# Triple+ Candle Patterns
# =============================================================================


def _morning_star(df):
    o1, h1, l1, c1 = _get_ohlc(df, -3)
    o2, h2, l2, c2 = _get_ohlc(df, -2)
    o3, h3, l3, c3 = _get_ohlc(df, -1)
    if _is_bearish(o1, c1) and _body(o2, c2) < _body(o1, c1) * 0.3 and _is_bullish(o3, c3) and c3 > (o1 + c1) / 2:
        return 1
    return 0


def _morning_doji_star(df):
    o1, h1, l1, c1 = _get_ohlc(df, -3)
    o2, h2, l2, c2 = _get_ohlc(df, -2)
    o3, h3, l3, c3 = _get_ohlc(df, -1)
    r2 = _range(h2, l2)
    if _is_bearish(o1, c1) and r2 > 0 and _body(o2, c2) / r2 < 0.1 and _is_bullish(o3, c3) and c3 > (o1 + c1) / 2:
        return 1
    return 0


def _evening_star(df):
    o1, h1, l1, c1 = _get_ohlc(df, -3)
    o2, h2, l2, c2 = _get_ohlc(df, -2)
    o3, h3, l3, c3 = _get_ohlc(df, -1)
    if _is_bullish(o1, c1) and _body(o2, c2) < _body(o1, c1) * 0.3 and _is_bearish(o3, c3) and c3 < (o1 + c1) / 2:
        return -1
    return 0


def _evening_doji_star(df):
    o1, h1, l1, c1 = _get_ohlc(df, -3)
    o2, h2, l2, c2 = _get_ohlc(df, -2)
    o3, h3, l3, c3 = _get_ohlc(df, -1)
    r2 = _range(h2, l2)
    if _is_bullish(o1, c1) and r2 > 0 and _body(o2, c2) / r2 < 0.1 and _is_bearish(o3, c3) and c3 < (o1 + c1) / 2:
        return -1
    return 0


def _three_white_soldiers(df):
    results = []
    for i in [-3, -2, -1]:
        o, h, l, c = _get_ohlc(df, i)
        results.append((o, h, l, c))
    for i in range(3):
        if not _is_bullish(results[i][0], results[i][3]):
            return 0
    if results[1][3] > results[0][3] and results[2][3] > results[1][3]:
        return 1
    return 0


def _three_black_crows(df):
    results = []
    for i in [-3, -2, -1]:
        o, h, l, c = _get_ohlc(df, i)
        results.append((o, h, l, c))
    for i in range(3):
        if not _is_bearish(results[i][0], results[i][3]):
            return 0
    if results[1][3] < results[0][3] and results[2][3] < results[1][3]:
        return -1
    return 0


def _three_inside(df):
    h = _harami(pd.DataFrame({
        "open": df["open"].iloc[-3:-1], "high": df["high"].iloc[-3:-1],
        "low": df["low"].iloc[-3:-1], "close": df["close"].iloc[-3:-1],
    }).reset_index(drop=True))
    if h == 0:
        return 0
    o3, _, _, c3 = _get_ohlc(df, -1)
    _, _, _, c1 = _get_ohlc(df, -3)
    if h == 1 and c3 > c1:
        return 1
    if h == -1 and c3 < c1:
        return -1
    return 0


def _three_outside(df):
    e = _engulfing(pd.DataFrame({
        "open": df["open"].iloc[-3:-1], "high": df["high"].iloc[-3:-1],
        "low": df["low"].iloc[-3:-1], "close": df["close"].iloc[-3:-1],
    }).reset_index(drop=True))
    if e == 0:
        return 0
    _, _, _, c2 = _get_ohlc(df, -2)
    _, _, _, c3 = _get_ohlc(df, -1)
    if e == 1 and c3 > c2:
        return 1
    if e == -1 and c3 < c2:
        return -1
    return 0


def _abandoned_baby(df):
    o1, h1, l1, c1 = _get_ohlc(df, -3)
    o2, h2, l2, c2 = _get_ohlc(df, -2)
    o3, h3, l3, c3 = _get_ohlc(df, -1)
    r2 = _range(h2, l2)
    if r2 == 0:
        return 0
    is_doji = _body(o2, c2) / r2 < 0.1
    if _is_bearish(o1, c1) and is_doji and h2 < l1 and l2 < l3 and _is_bullish(o3, c3):
        return 1
    if _is_bullish(o1, c1) and is_doji and l2 > h1 and h2 > h3 and _is_bearish(o3, c3):
        return -1
    return 0


def _simple_triple(df, direction):
    """Simplified triple pattern stub for less common patterns"""
    o1, _, _, c1 = _get_ohlc(df, -3)
    o2, _, _, c2 = _get_ohlc(df, -2)
    o3, _, _, c3 = _get_ohlc(df, -1)
    if direction == "bullish":
        if _is_bearish(o1, c1) and _is_bearish(o2, c2) and _is_bullish(o3, c3) and c3 > c1:
            return 1
    else:
        if _is_bullish(o1, c1) and _is_bullish(o2, c2) and _is_bearish(o3, c3) and c3 < c1:
            return -1
    return 0


def _three_stars_in_south(df): return _simple_triple(df, "bullish")
def _advance_block(df): return _simple_triple(df, "bearish")
def _stalled_pattern(df): return _simple_triple(df, "bearish")
def _deliberation(df): return _simple_triple(df, "bearish")


def _tasuki_gap(df):
    o1, _, _, c1 = _get_ohlc(df, -3)
    o2, _, _, c2 = _get_ohlc(df, -2)
    o3, _, _, c3 = _get_ohlc(df, -1)
    if _is_bullish(o1, c1) and _is_bullish(o2, c2) and o2 > c1 and _is_bearish(o3, c3):
        return 1
    if _is_bearish(o1, c1) and _is_bearish(o2, c2) and o2 < c1 and _is_bullish(o3, c3):
        return -1
    return 0


def _upside_gap_two_crows(df):
    o1, _, _, c1 = _get_ohlc(df, -3)
    o2, _, _, c2 = _get_ohlc(df, -2)
    o3, _, _, c3 = _get_ohlc(df, -1)
    if _is_bullish(o1, c1) and _is_bearish(o2, c2) and o2 > c1 and _is_bearish(o3, c3) and o3 > o2 and c3 < c2:
        return -1
    return 0


def _three_line_strike(df):
    if len(df) < 4:
        return 0
    candles = [_get_ohlc(df, i) for i in [-4, -3, -2, -1]]
    bears = all(_is_bearish(c[0], c[3]) for c in candles[:3])
    if bears and candles[1][3] < candles[0][3] and candles[2][3] < candles[1][3]:
        if _is_bullish(candles[3][0], candles[3][3]) and candles[3][3] > candles[0][0]:
            return 1
    bulls = all(_is_bullish(c[0], c[3]) for c in candles[:3])
    if bulls and candles[1][3] > candles[0][3] and candles[2][3] > candles[1][3]:
        if _is_bearish(candles[3][0], candles[3][3]) and candles[3][3] < candles[0][0]:
            return -1
    return 0


def _unique_three_river(df): return _simple_triple(df, "bullish")
def _breakaway(df): return _simple_triple(df, "bullish")
def _mat_hold(df): return _simple_triple(df, "bullish")
def _rising_three_methods(df): return _simple_triple(df, "bullish")
def _falling_three_methods(df): return _simple_triple(df, "bearish")
def _ladder_bottom(df): return _simple_triple(df, "bullish")
def _concealing_baby_swallow(df): return _simple_triple(df, "bullish")


def _stick_sandwich(df):
    o1, _, _, c1 = _get_ohlc(df, -3)
    o2, _, _, c2 = _get_ohlc(df, -2)
    o3, _, _, c3 = _get_ohlc(df, -1)
    tol = _avg_body(df) * 0.03
    if _is_bearish(o1, c1) and _is_bullish(o2, c2) and _is_bearish(o3, c3) and abs(c1 - c3) < tol:
        return 1
    return 0


def _tristar(df):
    for i in [-3, -2, -1]:
        o, h, l, c = _get_ohlc(df, i)
        r = _range(h, l)
        if r == 0 or _body(o, c) / r >= 0.1:
            return 0
    _, _, l2, _ = _get_ohlc(df, -2)
    _, _, l1, _ = _get_ohlc(df, -3)
    _, _, l3, _ = _get_ohlc(df, -1)
    if l2 < l1 and l2 < l3:
        return 1
    _, h2, _, _ = _get_ohlc(df, -2)
    _, h1, _, _ = _get_ohlc(df, -3)
    _, h3, _, _ = _get_ohlc(df, -1)
    if h2 > h1 and h2 > h3:
        return -1
    return 0


def _identical_three_crows(df):
    results = [_get_ohlc(df, i) for i in [-3, -2, -1]]
    for o, h, l, c in results:
        if not _is_bearish(o, c):
            return 0
    tol = _avg_body(df) * 0.03
    if abs(results[1][0] - results[0][3]) < tol and abs(results[2][0] - results[1][3]) < tol:
        return -1
    return 0


def _two_crows(df):
    o1, _, _, c1 = _get_ohlc(df, -3)
    o2, _, _, c2 = _get_ohlc(df, -2)
    o3, _, _, c3 = _get_ohlc(df, -1)
    if _is_bullish(o1, c1) and _is_bearish(o2, c2) and o2 > c1 and _is_bearish(o3, c3) and c3 < c1:
        return -1
    return 0


def _up_down_gap_three_methods(df): return _tasuki_gap(df)
def _downside_tasuki_gap(df): return _tasuki_gap(df) if _tasuki_gap(df) == -1 else 0
def _upside_tasuki_gap(df): return _tasuki_gap(df) if _tasuki_gap(df) == 1 else 0
def _side_by_side_white_lines(df): return _gap_side_by_side_white(df)


# =============================================================================
# Pattern Registry
# =============================================================================

PATTERN_DETECTORS = {
    # Single (15)
    "doji": _doji,
    "dragonfly_doji": _dragonfly_doji,
    "gravestone_doji": _gravestone_doji,
    "long_legged_doji": _long_legged_doji,
    "hammer": _hammer,
    "hanging_man": _hanging_man,
    "inverted_hammer": _inverted_hammer,
    "shooting_star": _shooting_star,
    "marubozu": _marubozu,
    "closing_marubozu": _closing_marubozu,
    "opening_marubozu": _opening_marubozu,
    "spinning_top": _spinning_top,
    "belt_hold": _belt_hold,
    "high_wave": _high_wave,
    "rickshaw_man": _rickshaw_man,
    # Double (20)
    "engulfing": _engulfing,
    "harami": _harami,
    "harami_cross": _harami_cross,
    "piercing": _piercing,
    "dark_cloud_cover": _dark_cloud_cover,
    "counterattack": _counterattack,
    "tweezer_top": _tweezer_top,
    "tweezer_bottom": _tweezer_bottom,
    "on_neck": _on_neck,
    "in_neck": _in_neck,
    "thrusting": _thrusting,
    "separating_lines": _separating_lines,
    "meeting_lines": _meeting_lines,
    "kicking": _kicking,
    "kicking_by_length": _kicking_by_length,
    "matching_low": _matching_low,
    "matching_high": _matching_high,
    "gap_side_by_side_white": _gap_side_by_side_white,
    "homing_pigeon": _homing_pigeon,
    "dojistar": _dojistar,
    # Triple+ (30)
    "morning_star": _morning_star,
    "morning_doji_star": _morning_doji_star,
    "evening_star": _evening_star,
    "evening_doji_star": _evening_doji_star,
    "three_white_soldiers": _three_white_soldiers,
    "three_black_crows": _three_black_crows,
    "three_inside": _three_inside,
    "three_outside": _three_outside,
    "abandoned_baby": _abandoned_baby,
    "three_stars_in_south": _three_stars_in_south,
    "advance_block": _advance_block,
    "stalled_pattern": _stalled_pattern,
    "deliberation": _deliberation,
    "tasuki_gap": _tasuki_gap,
    "upside_gap_two_crows": _upside_gap_two_crows,
    "three_line_strike": _three_line_strike,
    "unique_three_river": _unique_three_river,
    "breakaway": _breakaway,
    "mat_hold": _mat_hold,
    "rising_three_methods": _rising_three_methods,
    "falling_three_methods": _falling_three_methods,
    "ladder_bottom": _ladder_bottom,
    "concealing_baby_swallow": _concealing_baby_swallow,
    "stick_sandwich": _stick_sandwich,
    "tristar": _tristar,
    "identical_three_crows": _identical_three_crows,
    "two_crows": _two_crows,
    "up_down_gap_three_methods": _up_down_gap_three_methods,
    "downside_tasuki_gap": _downside_tasuki_gap,
    "upside_tasuki_gap": _upside_tasuki_gap,
    "side_by_side_white_lines": _side_by_side_white_lines,
}
