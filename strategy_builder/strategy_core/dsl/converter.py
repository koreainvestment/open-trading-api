"""
BuilderState → DSL 변환

Visual Builder의 BuilderState(dict)를 DSL 문자열로 변환합니다.
strategy.py에 2벌 중복되어 있던 convert_indicator_to_function + format_condition을
하나로 통합한 모듈입니다.
"""

from typing import Any, Dict, List, Tuple


def convert_indicator_to_function(alias: str, output: str, indicators: List[Dict]) -> str:
    """지표 alias를 함수 호출 형태로 변환

    Args:
        alias: 지표 별칭 (예: 'sma_fast')
        output: 출력 필드 (예: 'value', 'signal', 'upper', 'lower')
        indicators: BuilderState의 indicators 배열

    Returns:
        DSL 함수 호출 문자열 (예: 'ma(5)')
    """
    ind_def = next((i for i in indicators if i.get('alias') == alias), None)
    if not ind_def:
        return alias

    ind_id = ind_def.get('indicatorId', '')
    params = ind_def.get('params', {})

    converter_map = {
        # ── 기존 21개 ──────────────────────────────────────────────
        'macd':          _convert_macd,
        'bollinger':     _convert_bollinger,
        'stochastic':    _convert_stochastic,
        'rsi':           lambda p, o: f"rsi({p.get('period', 14)})",
        'sma':           lambda p, o: f"ma({p.get('period', 20)})",
        'ema':           lambda p, o: f"ema({p.get('period', 20)})",
        'atr':           lambda p, o: f"atr({p.get('period', 14)})",
        'roc':           lambda p, o: f"roc({p.get('period', 10)})",
        'adx':           lambda p, o: f"adx({p.get('period', 14)})",
        'maximum':       lambda p, o: f"highest({p.get('period', 20)})",
        'minimum':       lambda p, o: f"lowest({p.get('period', 20)})",
        'williams_r':    lambda p, o: f"williams_r({p.get('period', 14)})",
        'cci':           lambda p, o: f"cci({p.get('period', 20)})",
        'obv':           lambda p, o: "obv()",
        'consecutive':   lambda p, o: f"consecutive({p.get('direction', 'up')})",
        'disparity':     lambda p, o: f"disparity({p.get('period', 20)})",
        'volatility_ind': lambda p, o: f"volatility_ind({p.get('period', 10)})",
        'change':        lambda p, o: "change",
        'ibs':           lambda p, o: "ibs",
        'returns':       lambda p, o: f"returns({p.get('period', 60)})",
        'std':           lambda p, o: f"std({p.get('period', 20)})",

        # ── 1-A. 단순 period 이동평균 (12개) ───────────────────────
        'dema':  lambda p, o: f"dema({p.get('period', 21)})",
        'tema':  lambda p, o: f"tema({p.get('period', 21)})",
        'hma':   lambda p, o: f"hma({p.get('period', 21)})",
        'kama':  lambda p, o: f"kama({p.get('period', 20)})",
        'lwma':  lambda p, o: f"lwma({p.get('period', 20)})",
        'trima': lambda p, o: f"trima({p.get('period', 20)})",
        'zlema': lambda p, o: f"zlema({p.get('period', 20)})",
        'wma':   lambda p, o: f"wma({p.get('period', 20)})",
        'frama': lambda p, o: f"frama({p.get('period', 20)})",
        'vidya': lambda p, o: f"vidya({p.get('period', 20)})",
        'cmo':   lambda p, o: f"cmo({p.get('period', 14)})",
        'trix':  lambda p, o: f"trix({p.get('period', 15)})",

        # ── 1-B. 복합 파라미터 지표 (15개) ────────────────────────
        'alma':       lambda p, o: f"alma({p.get('period', 20)},{p.get('sigma', 6.0)},{p.get('offset', 0.85)})",
        't3':         lambda p, o: f"t3({p.get('period', 20)},{p.get('volume_factor', 0.7)})",
        'cho':        lambda p, o: f"cho({p.get('fast', 3)},{p.get('slow', 10)})",
        'ultosc':     lambda p, o: f"ultosc({p.get('period1', 7)},{p.get('period2', 14)},{p.get('period3', 28)})",
        'dpo':        lambda p, o: f"dpo({p.get('period', 20)})",
        'adxr':       lambda p, o: f"adxr({p.get('period', 14)})",
        'chop':       lambda p, o: f"chop({p.get('period', 14)})",
        'supertrend': lambda p, o: f"supertrend({p.get('period', 10)},{p.get('multiplier', 3.0)})",
        'mass_index': lambda p, o: f"mass_index({p.get('ema_period', 9)})",
        'schaff':     lambda p, o: f"schaff({p.get('cycle', 23)},{p.get('fast', 10)},{p.get('slow', 50)})",
        'fisher':     lambda p, o: f"fisher_transform({p.get('period', 9)})",
        'cmf':        lambda p, o: f"cmf({p.get('period', 20)})",
        'mfi':        lambda p, o: f"mfi({p.get('period', 14)})",
        'force':      lambda p, o: f"force({p.get('period', 13)})",
        'natr':       lambda p, o: f"natr({p.get('period', 14)})",

        # ── 1-C. 파라미터 없는 지표 (10개) ───────────────────────
        'ao':      lambda p, o: "ao()",
        'kst':     lambda p, o: "kst()",
        'coppock': lambda p, o: "coppock()",
        'ad':      lambda p, o: "ad()",
        'adl':     lambda p, o: "adl()",
        'bop':     lambda p, o: "bop()",
        'logr':    lambda p, o: "logr()",

        # ── 1-D. 멀티 출력 지표 (12개) ────────────────────────────
        'vortex':    _convert_vortex,
        'keltner':   _convert_keltner,
        'donchian':  _convert_donchian,
        'accbands':  _convert_accbands,
        'ichimoku':  _convert_ichimoku,
        'aroon':     _convert_aroon,
        'tsi':       _convert_tsi,
        'kvo':       _convert_kvo,
        'ppo':       _convert_ppo,
        'sar':       _convert_sar,
        'stochrsi':  _convert_stochrsi,
        'regression': _convert_regression,

        # ── 1-E. 특수 케이스 (13개) ───────────────────────────────
        'momentum':  lambda p, o: f"momentum({p.get('period', 10)})",
        'apo':       lambda p, o: f"apo({p.get('fast', 12)},{p.get('slow', 26)})",
        'rvi':       lambda p, o: f"rvi_ind({p.get('period', 10)})",
        'vwap':      lambda p, o: "vwap()",
        'vwma':      lambda p, o: f"vwma({p.get('period', 20)})",
        'eom':       lambda p, o: f"eom({p.get('period', 14)})",
        'variance':  lambda p, o: f"variance({p.get('period', 20)})",
        'midpoint':  lambda p, o: f"midpoint({p.get('period', 14)})",
        'midprice':  lambda p, o: f"midprice({p.get('period', 14)})",
        'pivot':     lambda p, o: "pivot()",
        'augen':     lambda p, o: f"augen({p.get('period', 14)})",
        'beta':      lambda p, o: f"beta({p.get('period', 20)})",
        'alpha':     lambda p, o: f"alpha({p.get('period', 20)})",
    }

    converter = converter_map.get(ind_id)
    if converter:
        return converter(params, output)

    # 미등록 지표: 범용 변환
    param_str = ','.join(str(v) for v in params.values())
    return f"{ind_id}({param_str})" if param_str else ind_id


# ── 기존 멀티 출력 헬퍼 ───────────────────────────────────────────

def _convert_macd(params: Dict, output: str) -> str:
    fast = params.get('fast', 12)
    slow = params.get('slow', 26)
    signal = params.get('signal', 9)
    if output == 'signal':
        return f"macd_signal({fast},{slow},{signal})"
    return f"macd({fast},{slow},{signal})"


def _convert_bollinger(params: Dict, output: str) -> str:
    period = params.get('period', 20)
    std = params.get('std', 2)
    if output == 'upper':
        return f"bb_upper({period},{std})"
    elif output == 'lower':
        return f"bb_lower({period},{std})"
    return f"bb_middle({period},{std})"


def _convert_stochastic(params: Dict, output: str) -> str:
    k_period = params.get('k_period', 14)
    if output == 'd':
        return f"stoch_d({k_period})"
    return f"stoch_k({k_period})"


# ── 신규 멀티 출력 헬퍼 ───────────────────────────────────────────

def _convert_vortex(params: Dict, output: str) -> str:
    period = params.get('period', 14)
    if output == 'plus_vi':
        return f"vortex_plus({period})"
    return f"vortex_minus({period})"


def _convert_keltner(params: Dict, output: str) -> str:
    period = params.get('period', 20)
    multiplier = params.get('multiplier', 2.0)
    if output == 'upper':
        return f"keltner_upper({period},{multiplier})"
    return f"keltner_lower({period},{multiplier})"


def _convert_donchian(params: Dict, output: str) -> str:
    period = params.get('period', 20)
    if output == 'upper':
        return f"donchian_upper({period})"
    return f"donchian_lower({period})"


def _convert_accbands(params: Dict, output: str) -> str:
    period = params.get('period', 20)
    if output == 'upper':
        return f"accbands_upper({period})"
    return f"accbands_lower({period})"


def _convert_ichimoku(params: Dict, output: str) -> str:
    if output == 'tenkan':
        return f"ichimoku_tenkan({params.get('tenkan', 9)})"
    return f"ichimoku_kijun({params.get('kijun', 26)})"


def _convert_aroon(params: Dict, output: str) -> str:
    period = params.get('up_period', params.get('period', 25))
    if output in ('aroon_up', 'up'):
        return f"aroon_up({period})"
    return f"aroon_down({period})"


def _convert_tsi(params: Dict, output: str) -> str:
    long_period = params.get('long_period', 25)
    short_period = params.get('short_period', 13)
    if output == 'signal':
        return f"tsi_signal({long_period},{short_period})"
    return f"tsi({long_period},{short_period})"


def _convert_kvo(params: Dict, output: str) -> str:
    fast = params.get('fast', 34)
    slow = params.get('slow', 55)
    if output == 'signal':
        return f"kvo_signal({fast},{slow})"
    return f"kvo({fast},{slow})"


def _convert_ppo(params: Dict, output: str) -> str:
    fast = params.get('fast', 12)
    slow = params.get('slow', 26)
    if output == 'signal':
        return f"ppo_signal({fast},{slow})"
    return f"ppo({fast},{slow})"


def _convert_sar(_params: Dict, _output: str) -> str:
    # parser.py의 sar는 파라미터 없이 calc_sar(df) 호출
    return "sar()"


def _convert_stochrsi(params: Dict, _output: str) -> str:
    # parser.py는 stochrsi 단일 값만 지원 (k/d 구분 없음)
    period = params.get('rsi_period', params.get('period', 14))
    return f"stochrsi({period})"


def _convert_regression(params: Dict, _output: str) -> str:
    period = params.get('period', 20)
    # parser.py에는 regression_slope만 지원
    return f"regression_slope({period})"


def _format_operand(operand: Dict, indicators: List[Dict]) -> str:
    """피연산자(left/right)를 DSL 문자열로 변환"""
    op_type = operand.get('type', '')

    if op_type == 'indicator':
        alias = operand.get('indicatorAlias', '')
        output = operand.get('indicatorOutput', 'value')
        return convert_indicator_to_function(alias, output, indicators)
    elif op_type == 'price':
        return operand.get('priceField', 'close')
    elif op_type == 'value':
        return str(operand.get('value', 0))

    return '0'


# 연산자 매핑: BuilderState operator → DSL operator
_OPERATOR_MAP = {
    'greater_than': '>',
    'less_than': '<',
    'greater_equal': '>=',
    'less_equal': '<=',
    'cross_above': 'crosses_above',
    'cross_below': 'crosses_below',
    'equals': '==',
}


def format_condition(conditions: List[Dict], logic: str, indicators: List[Dict]) -> str:
    """BuilderState 조건 배열을 DSL 문자열로 변환

    Args:
        conditions: BuilderState의 conditions 배열
        logic: 'AND' 또는 'OR'
        indicators: BuilderState의 indicators 배열

    Returns:
        DSL 조건 문자열 (예: 'ma(5) crosses_above ma(20)')
    """
    if not conditions:
        return ""

    cond_strings = []
    for c in conditions:
        # 캔들스틱 조건
        if c.get('isCandlestick') and c.get('candlestickAlias'):
            signal_map = {'bullish': ' > 0', 'bearish': ' < 0', 'detected': ' != 0'}
            cond_strings.append(
                f"{c['candlestickAlias']}{signal_map.get(c.get('candlestickSignal', 'detected'), ' != 0')}"
            )
            continue

        left = c.get('left', {})
        right = c.get('right', {})

        left_str = _format_operand(left, indicators)
        right_str = _format_operand(right, indicators)

        op = _OPERATOR_MAP.get(c.get('operator', '>'), c.get('operator', '>'))
        cond_strings.append(f"{left_str} {op} {right_str}")

    connector = ' and ' if logic == 'AND' else ' or '
    return connector.join(cond_strings)


def builder_state_to_dsl(builder_state: Dict[str, Any]) -> Tuple[str, str]:
    """BuilderState를 매수/매도 DSL 문자열로 변환

    Args:
        builder_state: Visual Builder의 전체 상태 dict

    Returns:
        (buy_condition, sell_condition) 튜플
    """
    entry = builder_state.get('entry', {})
    exit_cond = builder_state.get('exit', {})
    indicators = builder_state.get('indicators', [])

    buy_condition = format_condition(
        entry.get('conditions', []),
        entry.get('logic', 'AND'),
        indicators,
    )
    sell_condition = format_condition(
        exit_cond.get('conditions', []),
        exit_cond.get('logic', 'OR'),
        indicators,
    )

    return buy_condition, sell_condition
