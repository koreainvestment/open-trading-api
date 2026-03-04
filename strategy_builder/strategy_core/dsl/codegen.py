"""
전략 코드 생성기

파싱된 AST를 Python 전략 클래스 코드로 변환합니다.
"""

import logging
import os
from strategy_core.dsl.parser import (
    StrategyDefinition,
    Condition,
    CompositeCondition,
    Indicator,
    Value,
    ArithmeticExpr,
    Operator,
    LogicalOperator,
    ConditionType,
    parse_strategy,
)


class StrategyCodeGenerator:
    """전략 코드 생성기"""

    def __init__(self):
        self.indent = "    "  # 4 spaces

    def generate(self, strategy: StrategyDefinition) -> str:
        """
        StrategyDefinition을 Python 코드로 변환

        Args:
            strategy: 전략 정의

        Returns:
            Python 소스 코드 문자열
        """
        class_name = self._to_class_name(strategy.name)
        required_days = strategy.get_required_days()

        # 코드 조각들
        imports = self._generate_imports()
        class_def = self._generate_class(
            class_name=class_name,
            name_ko=strategy.name_ko,
            buy_condition=strategy.buy_condition,
            sell_condition=strategy.sell_condition,
            required_days=required_days,
            params=strategy.params,
        )

        return f"{imports}\n\n{class_def}"

    def _to_class_name(self, name: str) -> str:
        """snake_case를 PascalCase로 변환"""
        return "".join(word.capitalize() for word in name.split("_")) + "Strategy"

    def _generate_imports(self) -> str:
        """import 문 생성"""
        return '''"""
자동 생성된 전략 파일

이 파일은 strategy_builder에 의해 자동 생성되었습니다.
"""

from core import data_fetcher, indicators, candlestick
from core.signal import Action, Signal
from strategy.base_strategy import BaseStrategy'''

    def _generate_class(
        self,
        class_name: str,
        name_ko: str,
        buy_condition,
        sell_condition,
        required_days: int,
        params: dict,
    ) -> str:
        """클래스 정의 생성"""

        # 파라미터 추출
        param_list = self._extract_params(buy_condition, sell_condition, params)
        init_params = self._generate_init_params(param_list)
        init_body = self._generate_init_body(param_list)

        # 조건 코드 생성
        buy_code = self._generate_condition_code(buy_condition, "buy") if buy_condition else None
        sell_code = self._generate_condition_code(sell_condition, "sell") if sell_condition else None

        # 시그널 생성 로직
        signal_logic = self._generate_signal_logic(buy_condition, sell_condition, buy_code, sell_code)

        return f'''
class {class_name}(BaseStrategy):
    """
    {name_ko} 전략

    매수 조건: {buy_condition if buy_condition else '없음'}
    매도 조건: {sell_condition if sell_condition else '없음'}
    """

    def __init__(self{init_params}):
{init_body}

    @property
    def name(self) -> str:
        return "{name_ko}"

    @property
    def required_days(self) -> int:
        return {required_days}

    def generate_signal(self, stock_code: str, stock_name: str) -> Signal:
        """시그널 생성"""
        # 데이터 조회
        df = data_fetcher.get_daily_prices(stock_code, self.required_days)

        if df.empty or len(df) < self.required_days - 5:
            return Signal(
                stock_code=stock_code,
                stock_name=stock_name,
                action=Action.HOLD,
                strength=0.0,
                reason="데이터 부족"
            )

{signal_logic}
'''

    def _extract_params(self, buy_condition, sell_condition, extra_params: dict) -> dict:
        """조건에서 파라미터 추출"""
        params = {}

        def extract_from_node(node):
            if isinstance(node, Indicator):
                # 지표에서 파라미터 추출
                if node.params:
                    param_name = f"{node.name}_period"
                    if node.name in ["ma", "ema", "rsi", "disparity", "volatility"]:
                        params[param_name] = node.params[0]
                    elif node.name == "consecutive":
                        params["consecutive_days"] = 5  # 기본값
                    elif node.name in ["bb_upper", "bb_lower"]:
                        params["bb_period"] = node.params[0] if len(node.params) > 0 else 20
                        params["bb_std"] = node.params[1] if len(node.params) > 1 else 2
                    elif node.name == "macd":
                        params["macd_fast"] = node.params[0] if len(node.params) > 0 else 12
                        params["macd_slow"] = node.params[1] if len(node.params) > 1 else 26
                        params["macd_signal"] = node.params[2] if len(node.params) > 2 else 9

            elif isinstance(node, Value):
                pass  # 값은 하드코딩 또는 threshold로 처리

            elif isinstance(node, ArithmeticExpr):
                extract_from_node(node.left)
                extract_from_node(node.right)

            elif isinstance(node, Condition):
                extract_from_node(node.left)
                extract_from_node(node.right)
                # threshold 값 추출
                if isinstance(node.right, Value):
                    if node.operator in [Operator.LT, Operator.LTE]:
                        params["threshold_low"] = node.right.value
                    elif node.operator in [Operator.GT, Operator.GTE]:
                        params["threshold_high"] = node.right.value

            elif isinstance(node, CompositeCondition):
                extract_from_node(node.left)
                extract_from_node(node.right)

        if buy_condition:
            extract_from_node(buy_condition)
        if sell_condition:
            extract_from_node(sell_condition)

        # 추가 파라미터 병합
        params.update(extra_params or {})

        return params

    def _generate_init_params(self, params: dict) -> str:
        """__init__ 파라미터 문자열 생성"""
        if not params:
            return ""

        param_strs = []
        for name, default in params.items():
            if isinstance(default, str):
                param_strs.append(f'{name}: str = "{default}"')
            elif isinstance(default, float):
                param_strs.append(f"{name}: float = {default}")
            else:
                param_strs.append(f"{name}: int = {default}")

        return ", " + ", ".join(param_strs)

    def _generate_init_body(self, params: dict) -> str:
        """__init__ 본문 생성"""
        if not params:
            return f"{self.indent * 2}pass"

        lines = []
        for name in params:
            lines.append(f"{self.indent * 2}self.{name} = {name}")

        return "\n".join(lines)

    def _generate_condition_code(self, condition, prefix: str) -> str:
        """조건을 Python 코드로 변환"""
        return self._node_to_code(condition)

    def _node_to_code(self, node) -> str:
        """AST 노드를 Python 표현식으로 변환"""
        if isinstance(node, Indicator):
            return self._indicator_to_code(node)

        elif isinstance(node, Value):
            if node.is_percent:
                return str(node.value / 100)
            return str(node.value)

        elif isinstance(node, ArithmeticExpr):
            left = self._node_to_code(node.left)
            right = self._node_to_code(node.right)
            return f"({left} {node.operator.value} {right})"

        elif isinstance(node, Condition):
            return self._condition_to_code(node)

        elif isinstance(node, CompositeCondition):
            left = self._node_to_code(node.left)
            right = self._node_to_code(node.right)
            op = "and" if node.operator == LogicalOperator.AND else "or"
            return f"({left} {op} {right})"

        return str(node)

    def _indicator_to_code(self, indicator: Indicator) -> str:
        """지표를 Python 코드로 변환"""
        name = indicator.name
        params = indicator.params

        # 지표별 코드 매핑
        if name == "ma":
            period = params[0] if params else 20
            return f"indicators.calc_ma(df, {period}).iloc[-1]"

        elif name == "ema":
            period = params[0] if params else 20
            return f"indicators.calc_ema(df, {period}).iloc[-1]"

        elif name == "rsi":
            period = params[0] if params else 14
            return f"indicators.calc_rsi(df, {period}).iloc[-1]"

        elif name == "disparity":
            period = params[0] if params else 20
            return f"indicators.calc_disparity(df, {period}).iloc[-1]"

        elif name == "returns":
            period = params[0] if params else 1
            return f"indicators.calc_returns(df, {period}).iloc[-1] * 100"  # 퍼센트로

        elif name == "volatility":
            period = params[0] if params else 10
            return f"indicators.calc_volatility(df, {period}).iloc[-1]"

        elif name == "consecutive":
            direction = params[0] if params else "up"
            return f"indicators.calc_consecutive_days(df, '{direction}')"

        elif name == "change":
            return "indicators.calc_daily_change(df)"

        elif name == "close":
            return "indicators.get_latest_close(df)"

        elif name == "open":
            return "df['open'].iloc[-1]"

        elif name == "prev_close":
            return "indicators.get_prev_close(df)"

        elif name == "high":
            period = params[0] if params else 20
            return f"indicators.calc_high_since(df, {period})"

        elif name == "low":
            period = params[0] if params else 20
            return f"indicators.calc_low_since(df, {period})"

        elif name == "volume":
            return "df['volume'].iloc[-1]"

        elif name == "volume_ma":
            period = params[0] if params else 20
            return f"indicators.calc_volume_ma(df, {period}).iloc[-1]"

        elif name == "macd":
            fast = params[0] if len(params) > 0 else 12
            slow = params[1] if len(params) > 1 else 26
            signal = params[2] if len(params) > 2 else 9
            return f"indicators.calc_macd(df, {fast}, {slow}, {signal}).iloc[-1]"

        elif name == "macd_signal":
            fast = params[0] if len(params) > 0 else 12
            slow = params[1] if len(params) > 1 else 26
            signal = params[2] if len(params) > 2 else 9
            return f"indicators.calc_macd_signal(df, {fast}, {slow}, {signal}).iloc[-1]"

        elif name == "bb_upper":
            period = params[0] if len(params) > 0 else 20
            std = params[1] if len(params) > 1 else 2
            return f"indicators.calc_bb_upper(df, {period}, {std}).iloc[-1]"

        elif name == "bb_lower":
            period = params[0] if len(params) > 0 else 20
            std = params[1] if len(params) > 1 else 2
            return f"indicators.calc_bb_lower(df, {period}, {std}).iloc[-1]"

        elif name == "bb_middle":
            period = params[0] if params else 20
            return f"indicators.calc_bb_middle(df, {period}).iloc[-1]"

        elif name == "atr":
            period = params[0] if params else 14
            return f"indicators.calc_atr(df, {period}).iloc[-1]"

        elif name == "stoch_k":
            period = params[0] if params else 14
            return f"indicators.calc_stochastic_k(df, {period}).iloc[-1]"

        elif name == "stoch_d":
            period = params[0] if params else 14
            return f"indicators.calc_stochastic_d(df, {period}).iloc[-1]"

        elif name == "cci":
            period = params[0] if params else 20
            return f"indicators.calc_cci(df, {period}).iloc[-1]"

        elif name == "adx":
            period = params[0] if params else 14
            return f"indicators.calc_adx(df, {period}).iloc[-1]"

        elif name == "williams_r":
            period = params[0] if params else 14
            return f"indicators.calc_williams_r(df, {period}).iloc[-1]"

        elif name == "obv":
            return "indicators.calc_obv(df).iloc[-1]"

        elif name == "mfi":
            period = params[0] if params else 14
            return f"indicators.calc_mfi(df, {period}).iloc[-1]"

        elif name == "vwap":
            return "indicators.calc_vwap(df).iloc[-1]"

        elif name == "roc":
            period = params[0] if params else 10
            return f"indicators.calc_roc(df, {period}).iloc[-1]"

        elif name == "volatility_ind":
            period = params[0] if params else 10
            return f"indicators.calc_volatility(df, {period}).iloc[-1]"

        elif name == "ibs":
            return "indicators.calc_strong_close_ratio(df)"

        elif name == "maximum":
            period = params[0] if params else 20
            return f"indicators.calc_high_since(df, {period})"

        elif name == "minimum":
            period = params[0] if params else 20
            return f"indicators.calc_low_since(df, {period})"

        elif name in ("highest", "high_since"):
            period = params[0] if params else 20
            return f"indicators.calc_high_since(df, {period})"

        elif name in ("lowest", "low_since"):
            period = params[0] if params else 20
            return f"indicators.calc_low_since(df, {period})"

        elif name == "momentum":
            period = params[0] if params else 10
            return f"indicators.calc_momentum(df, {period}).iloc[-1]"

        elif name == "stochrsi":
            period = params[0] if params else 14
            return f"indicators.calc_stochrsi(df, {period}).iloc[-1]"

        elif name == "aroon_up":
            period = params[0] if params else 25
            return f"indicators.calc_aroon_up(df, {period}).iloc[-1]"

        elif name == "aroon_down":
            period = params[0] if params else 25
            return f"indicators.calc_aroon_down(df, {period}).iloc[-1]"

        elif name == "natr":
            period = params[0] if params else 14
            return f"indicators.calc_natr(df, {period}).iloc[-1]"

        elif name == "keltner_upper":
            period = params[0] if params else 20
            return f"indicators.calc_keltner_upper(df, {period}).iloc[-1]"

        elif name == "keltner_lower":
            period = params[0] if params else 20
            return f"indicators.calc_keltner_lower(df, {period}).iloc[-1]"

        elif name == "donchian_upper":
            period = params[0] if params else 20
            return f"indicators.calc_donchian_upper(df, {period}).iloc[-1]"

        elif name == "donchian_lower":
            period = params[0] if params else 20
            return f"indicators.calc_donchian_lower(df, {period}).iloc[-1]"

        elif name == "supertrend":
            period = params[0] if params else 10
            return f"indicators.calc_supertrend(df, {period}).iloc[-1]"

        elif name == "sar":
            return "indicators.calc_sar(df).iloc[-1]"

        elif name == "ichimoku_tenkan":
            period = params[0] if params else 9
            return f"indicators.calc_ichimoku_tenkan(df, {period}).iloc[-1]"

        elif name == "ichimoku_kijun":
            period = params[0] if params else 26
            return f"indicators.calc_ichimoku_kijun(df, {period}).iloc[-1]"

        elif name == "hma":
            period = params[0] if params else 20
            return f"indicators.calc_hma(df, {period}).iloc[-1]"

        elif name == "dema":
            period = params[0] if params else 20
            return f"indicators.calc_dema(df, {period}).iloc[-1]"

        elif name == "cmf":
            period = params[0] if params else 20
            return f"indicators.calc_cmf(df, {period}).iloc[-1]"

        elif name in ("tema", "kama", "alma", "lwma", "trima", "t3", "zlema",
                       "wma", "frama", "vidya"):
            period = params[0] if params else 20
            return f"indicators.calc_{name}(df, {period}).iloc[-1]"

        elif name in ("apo", "ppo"):
            return f"indicators.calc_{name}(df).iloc[-1]"

        elif name in ("cmo", "trix", "dpo", "adxr", "vortex_plus", "vortex_minus",
                       "chop", "mass_index", "schaff", "force", "vwma", "eom",
                       "variance", "accbands_upper", "accbands_lower",
                       "midpoint", "midprice", "regression_slope", "augen"):
            period = params[0] if params else 14
            return f"indicators.calc_{name}(df, {period}).iloc[-1]"

        elif name == "fisher_transform":
            period = params[0] if params else 9
            return f"indicators.calc_fisher(df, {period}).iloc[-1]"

        elif name == "rvi_ind":
            period = params[0] if params else 10
            return f"indicators.calc_rvi(df, {period}).iloc[-1]"

        elif name in ("ao", "cho", "kvo", "tsi", "kst", "coppock",
                       "ad", "adl", "logr", "bop", "pivot",
                       "ultosc"):
            return f"indicators.calc_{name}(df).iloc[-1]"

        else:
            from core.candlestick import PATTERN_DETECTORS
            if name in PATTERN_DETECTORS or name.rstrip("_0123456789") in PATTERN_DETECTORS:
                pattern_id = name.rstrip("_0123456789") if name not in PATTERN_DETECTORS else name
                return f"candlestick.detect_pattern(df, '{pattern_id}')"
            logging.warning(f"미지원 지표: {name} → 0으로 대체")
            return "0"

    def _condition_to_code(self, cond: Condition) -> str:
        """조건을 Python 코드로 변환"""
        left = self._node_to_code(cond.left)
        right = self._node_to_code(cond.right)

        # Crossover 처리 (전일/당일 비교 필요)
        if cond.operator == Operator.CROSSES_ABOVE:
            return self._generate_crossover_code(cond.left, cond.right, "above")

        elif cond.operator == Operator.CROSSES_BELOW:
            return self._generate_crossover_code(cond.left, cond.right, "below")

        elif cond.operator == Operator.BREAKS:
            # Breakout: 현재가 > N일 고가
            return f"({left} > {right})"

        else:
            # 일반 비교
            op_map = {
                Operator.GT: ">",
                Operator.LT: "<",
                Operator.GTE: ">=",
                Operator.LTE: "<=",
                Operator.EQ: "==",
                Operator.NEQ: "!=",
            }
            op = op_map.get(cond.operator, ">")
            return f"({left} {op} {right})"

    def _generate_crossover_code(self, left, right, direction: str) -> str:
        """크로스오버 조건 코드 생성 (Indicator, Value, ArithmeticExpr 지원)"""

        # 지표 시리즈 코드 생성 (인덱스 포함)
        def get_series_call(node, index: str = "") -> str:
            if isinstance(node, Value):
                # 상수값: 인덱스 불필요
                return node.to_code()
            elif isinstance(node, ArithmeticExpr):
                # 산술식: 각 부분을 재귀 처리
                left_code = get_series_call(node.left, index)
                right_code = get_series_call(node.right, index)
                return f"({left_code} {node.operator.value} {right_code})"
            elif isinstance(node, Indicator):
                name = node.name
                params = node.params

                # 가격 필드는 DataFrame 컬럼 직접 접근
                if name == "close":
                    return f"df['close']{index}"
                elif name == "open":
                    return f"df['open']{index}"
                elif name == "high":
                    return f"df['high']{index}"
                elif name == "low":
                    return f"df['low']{index}"
                elif name == "volume":
                    return f"df['volume']{index}"
                elif name == "prev_close":
                    return f"df['close']{index}"

                # 지표명 → calc 함수 매핑
                calc_map = {
                    "stoch_k": "calc_stochastic_k",
                    "stoch_d": "calc_stochastic_d",
                    "volatility_ind": "calc_volatility",
                    "ibs": "calc_strong_close_ratio",
                    "maximum": "calc_high_since",
                    "minimum": "calc_low_since",
                    "fisher_transform": "calc_fisher",
                    "rvi_ind": "calc_rvi",
                }
                calc_name = calc_map.get(name, f"calc_{name}")

                if name in ["macd", "macd_signal"]:
                    fast = params[0] if len(params) > 0 else 12
                    slow = params[1] if len(params) > 1 else 26
                    signal = params[2] if len(params) > 2 else 9
                    return f"indicators.{calc_name}(df, {fast}, {slow}, {signal}){index}"
                elif name in ["bb_upper", "bb_lower"]:
                    period = params[0] if len(params) > 0 else 20
                    std = params[1] if len(params) > 1 else 2
                    return f"indicators.{calc_name}(df, {period}, {std}){index}"
                elif name in ["obv", "vwap", "ibs", "change",
                              "ao", "cho", "kvo", "tsi", "kst", "coppock",
                              "ad", "adl", "logr", "bop", "pivot",
                              "ultosc"]:
                    return f"indicators.{calc_name}(df){index}"
                else:
                    period = params[0] if params else 20
                    return f"indicators.{calc_name}(df, {period}){index}"
            else:
                return str(node)

        left_prev = get_series_call(left, ".iloc[-2]")
        left_curr = get_series_call(left, ".iloc[-1]")
        right_prev = get_series_call(right, ".iloc[-2]")
        right_curr = get_series_call(right, ".iloc[-1]")

        if direction == "above":
            # 전일: left < right, 당일: left > right
            return f"""(
            {left_prev} < {right_prev} and
            {left_curr} > {right_curr}
        )"""
        else:
            # 전일: left > right, 당일: left < right
            return f"""(
            {left_prev} > {right_prev} and
            {left_curr} < {right_curr}
        )"""

    def _generate_signal_logic(self, buy_condition, sell_condition, buy_code: str, sell_code: str) -> str:
        """시그널 생성 로직 코드"""
        lines = []
        indent = self.indent * 2

        # 매수 조건 체크
        if buy_code:
            lines.append(f"{indent}# 매수 조건 체크")
            lines.append(f"{indent}buy_signal = {buy_code}")
            lines.append("")
            lines.append(f"{indent}if buy_signal:")
            lines.append(f"{indent}    return Signal(")
            lines.append(f"{indent}        stock_code=stock_code,")
            lines.append(f"{indent}        stock_name=stock_name,")
            lines.append(f"{indent}        action=Action.BUY,")
            lines.append(f"{indent}        strength=0.7,")
            lines.append(f'{indent}        reason="매수 조건 충족: {buy_condition}"')
            lines.append(f"{indent}    )")
            lines.append("")

        # 매도 조건 체크
        if sell_code:
            lines.append(f"{indent}# 매도 조건 체크")
            lines.append(f"{indent}sell_signal = {sell_code}")
            lines.append("")
            lines.append(f"{indent}if sell_signal:")
            lines.append(f"{indent}    return Signal(")
            lines.append(f"{indent}        stock_code=stock_code,")
            lines.append(f"{indent}        stock_name=stock_name,")
            lines.append(f"{indent}        action=Action.SELL,")
            lines.append(f"{indent}        strength=0.7,")
            lines.append(f'{indent}        reason="매도 조건 충족: {sell_condition}"')
            lines.append(f"{indent}    )")
            lines.append("")

        # 기본 HOLD
        lines.append(f"{indent}# 조건 미충족")
        lines.append(f"{indent}return Signal(")
        lines.append(f"{indent}    stock_code=stock_code,")
        lines.append(f"{indent}    stock_name=stock_name,")
        lines.append(f"{indent}    action=Action.HOLD,")
        lines.append(f"{indent}    strength=0.0,")
        lines.append(f'{indent}    reason="조건 미충족"')
        lines.append(f"{indent})")

        return "\n".join(lines)


def generate_strategy_file(
    name: str,
    name_ko: str,
    buy_condition: str = None,
    sell_condition: str = None,
    params: dict = None,
    output_dir: str = "strategy"
) -> str:
    """
    전략 파일 생성

    Args:
        name: 전략 영문명 (snake_case)
        name_ko: 전략 한글명
        buy_condition: 매수 조건 DSL
        sell_condition: 매도 조건 DSL
        params: 추가 파라미터
        output_dir: 출력 디렉토리

    Returns:
        생성된 파일 경로
    """
    # 전략 파싱
    strategy = parse_strategy(name, name_ko, buy_condition, sell_condition, params)

    # 코드 생성
    generator = StrategyCodeGenerator()
    code = generator.generate(strategy)

    # 파일 저장
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, f"strategy_{name}.py")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(code)

    return file_path


# 테스트
if __name__ == "__main__":
    # 테스트: 골든크로스
    strategy = parse_strategy(
        name="golden_cross_test",
        name_ko="골든크로스 테스트",
        buy_condition="ma(5) crosses_above ma(20)",
        sell_condition="ma(5) crosses_below ma(20)"
    )

    generator = StrategyCodeGenerator()
    code = generator.generate(strategy)
    print("=" * 60)
    print("골든크로스 전략")
    print("=" * 60)
    print(code)

    # 테스트: RSI
    strategy2 = parse_strategy(
        name="rsi_oversold",
        name_ko="RSI 과매도",
        buy_condition="rsi(14) < 30",
        sell_condition="rsi(14) > 70"
    )

    code2 = generator.generate(strategy2)
    print("\n" + "=" * 60)
    print("RSI 과매도 전략")
    print("=" * 60)
    print(code2)

    # 테스트: 복합 조건
    strategy3 = parse_strategy(
        name="trend_momentum",
        name_ko="추세+모멘텀",
        buy_condition="close > ma(60) AND change > 0",
        sell_condition="close < ma(60) AND change < 0"
    )

    code3 = generator.generate(strategy3)
    print("\n" + "=" * 60)
    print("추세+모멘텀 전략")
    print("=" * 60)
    print(code3)
