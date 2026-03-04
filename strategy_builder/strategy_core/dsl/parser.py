"""
전략 DSL 파서

조건식을 파싱하여 AST(Abstract Syntax Tree)로 변환합니다.

지원 문법:
- Crossover: ma(5) crosses_above ma(20)
- Threshold: disparity(20) < 90, rsi(14) < 30
- Breakout: close breaks high(250)
- Pattern: consecutive(up) >= 5
- Composite: close > ma(60) AND change > 0
- Arithmetic: volume > volume_ma(20) * 1.5
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Union, Optional


class ConditionType(Enum):
    """조건 유형"""
    CROSSOVER = "crossover"
    THRESHOLD = "threshold"
    BREAKOUT = "breakout"
    PATTERN = "pattern"
    COMPOSITE = "composite"


class Operator(Enum):
    """비교 연산자"""
    GT = ">"
    LT = "<"
    GTE = ">="
    LTE = "<="
    EQ = "=="
    NEQ = "!="
    CROSSES_ABOVE = "crosses_above"
    CROSSES_BELOW = "crosses_below"
    BREAKS = "breaks"


class LogicalOperator(Enum):
    """논리 연산자"""
    AND = "AND"
    OR = "OR"


class ArithmeticOperator(Enum):
    """산술 연산자"""
    ADD = "+"
    SUB = "-"
    MUL = "*"
    DIV = "/"


@dataclass
class Indicator:
    """지표 노드"""
    name: str
    params: list = field(default_factory=list)

    def __str__(self) -> str:
        if self.params:
            params_str = ", ".join(str(p) for p in self.params)
            return f"{self.name}({params_str})"
        return self.name

    def to_code(self) -> str:
        """Python 코드로 변환"""
        indicator_map = {
            "ma": "indicators.calc_ma(df, {period})",
            "ema": "indicators.calc_ema(df, {period})",
            "std": "indicators.calc_std(df, {period})",
            "returns": "indicators.calc_returns(df, {period})",
            "disparity": "indicators.calc_disparity(df, {period})",
            "volatility": "indicators.calc_volatility(df, {period})",
            "consecutive": "indicators.calc_consecutive_days(df, '{direction}')",
            "change": "indicators.calc_daily_change(df)",
            "high": "indicators.calc_high_since(df, {period})",
            "low": "indicators.calc_low_since(df, {period})",
            "close": "indicators.get_latest_close(df)",
            "prev_close": "indicators.get_prev_close(df)",
            "rsi": "indicators.calc_rsi(df, {period})",
            "macd": "indicators.calc_macd(df, {fast}, {slow}, {signal})",
            "macd_signal": "indicators.calc_macd_signal(df, {fast}, {slow}, {signal})",
            "macd_hist": "indicators.calc_macd_histogram(df, {fast}, {slow}, {signal})",
            "bb_upper": "indicators.calc_bb_upper(df, {period}, {std})",
            "bb_lower": "indicators.calc_bb_lower(df, {period}, {std})",
            "bb_middle": "indicators.calc_bb_middle(df, {period})",
            "volume": "df['volume'].iloc[-1]",
            "volume_ma": "indicators.calc_volume_ma(df, {period})",
            "atr": "indicators.calc_atr(df, {period})",
            "stoch_k": "indicators.calc_stochastic_k(df, {period})",
            "stoch_d": "indicators.calc_stochastic_d(df, {period})",
            "cci": "indicators.calc_cci(df, {period})",
            "adx": "indicators.calc_adx(df, {period})",
            "williams_r": "indicators.calc_williams_r(df, {period})",
            "obv": "indicators.calc_obv(df)",
            "mfi": "indicators.calc_mfi(df, {period})",
            "vwap": "indicators.calc_vwap(df)",
            "highest": "indicators.calc_high_since(df, {period})",
            "lowest": "indicators.calc_low_since(df, {period})",
            "roc": "indicators.calc_roc(df, {period})",
            "volatility_ind": "indicators.calc_volatility(df, {period})",
            "ibs": "indicators.calc_strong_close_ratio(df)",
            "maximum": "indicators.calc_high_since(df, {period})",
            "minimum": "indicators.calc_low_since(df, {period})",
            "momentum": "indicators.calc_momentum(df, {period})",
            "stochrsi": "indicators.calc_stochrsi(df, {period})",
            "aroon_up": "indicators.calc_aroon_up(df, {period})",
            "aroon_down": "indicators.calc_aroon_down(df, {period})",
            "natr": "indicators.calc_natr(df, {period})",
            "keltner_upper": "indicators.calc_keltner_upper(df, {period})",
            "keltner_lower": "indicators.calc_keltner_lower(df, {period})",
            "donchian_upper": "indicators.calc_donchian_upper(df, {period})",
            "donchian_lower": "indicators.calc_donchian_lower(df, {period})",
            "supertrend": "indicators.calc_supertrend(df, {period})",
            "sar": "indicators.calc_sar(df)",
            "ichimoku_tenkan": "indicators.calc_ichimoku_tenkan(df, {period})",
            "ichimoku_kijun": "indicators.calc_ichimoku_kijun(df, {period})",
            "hma": "indicators.calc_hma(df, {period})",
            "dema": "indicators.calc_dema(df, {period})",
            "cmf": "indicators.calc_cmf(df, {period})",
            "tema": "indicators.calc_tema(df, {period})",
            "kama": "indicators.calc_kama(df, {period})",
            "alma": "indicators.calc_alma(df, {period})",
            "lwma": "indicators.calc_lwma(df, {period})",
            "trima": "indicators.calc_trima(df, {period})",
            "t3": "indicators.calc_t3(df, {period})",
            "zlema": "indicators.calc_zlema(df, {period})",
            "wma": "indicators.calc_wma(df, {period})",
            "frama": "indicators.calc_frama(df, {period})",
            "vidya": "indicators.calc_vidya(df, {period})",
            "apo": "indicators.calc_apo(df)",
            "ppo": "indicators.calc_ppo(df)",
            "cmo": "indicators.calc_cmo(df, {period})",
            "ao": "indicators.calc_ao(df)",
            "cho": "indicators.calc_cho(df)",
            "ultosc": "indicators.calc_ultosc(df)",
            "trix": "indicators.calc_trix(df, {period})",
            "tsi": "indicators.calc_tsi(df)",
            "rvi_ind": "indicators.calc_rvi(df, {period})",
            "dpo": "indicators.calc_dpo(df, {period})",
            "kvo": "indicators.calc_kvo(df)",
            "adxr": "indicators.calc_adxr(df, {period})",
            "vortex_plus": "indicators.calc_vortex_plus(df, {period})",
            "vortex_minus": "indicators.calc_vortex_minus(df, {period})",
            "chop": "indicators.calc_chop(df, {period})",
            "kst": "indicators.calc_kst(df)",
            "coppock": "indicators.calc_coppock(df)",
            "mass_index": "indicators.calc_mass_index(df, {period})",
            "schaff": "indicators.calc_schaff(df, {period})",
            "fisher_transform": "indicators.calc_fisher(df, {period})",
            "ad": "indicators.calc_ad(df)",
            "adl": "indicators.calc_adl(df)",
            "force": "indicators.calc_force(df, {period})",
            "vwma": "indicators.calc_vwma(df, {period})",
            "eom": "indicators.calc_eom(df, {period})",
            "variance": "indicators.calc_variance(df, {period})",
            "accbands_upper": "indicators.calc_accbands_upper(df, {period})",
            "accbands_lower": "indicators.calc_accbands_lower(df, {period})",
            "midpoint": "indicators.calc_midpoint(df, {period})",
            "midprice": "indicators.calc_midprice(df, {period})",
            "logr": "indicators.calc_logr(df)",
            "bop": "indicators.calc_bop(df)",
            "regression_slope": "indicators.calc_regression_slope(df, {period})",
            "pivot": "indicators.calc_pivot(df)",
            "augen": "indicators.calc_augen(df, {period})",
        }

        template = indicator_map.get(self.name)
        if not template:
            raise ValueError(f"Unknown indicator: {self.name}")

        # 파라미터 매핑
        period_indicators = [
            "ma", "ema", "std", "disparity", "volatility", "high", "low",
            "rsi", "volume_ma", "atr", "bb_middle",
            "stoch_k", "stoch_d", "cci", "adx", "williams_r", "mfi",
            "highest", "lowest", "roc", "volatility_ind", "maximum", "minimum",
            "momentum", "stochrsi", "aroon_up", "aroon_down", "natr",
            "keltner_upper", "keltner_lower", "donchian_upper", "donchian_lower",
            "supertrend", "ichimoku_tenkan", "ichimoku_kijun", "hma", "dema", "cmf",
            "tema", "kama", "alma", "lwma", "trima", "t3", "zlema", "wma", "frama", "vidya",
            "cmo", "trix", "rvi_ind", "dpo", "adxr", "vortex_plus", "vortex_minus",
            "chop", "mass_index", "schaff", "fisher_transform", "force", "vwma", "eom",
            "variance", "accbands_upper", "accbands_lower", "midpoint", "midprice",
            "regression_slope", "augen",
        ]
        if self.name in period_indicators:
            return template.format(period=self.params[0] if self.params else 20)
        elif self.name == "returns":
            return template.format(period=self.params[0] if self.params else 1)
        elif self.name == "consecutive":
            return template.format(direction=self.params[0] if self.params else "up")
        elif self.name == "macd":
            fast = self.params[0] if len(self.params) > 0 else 12
            slow = self.params[1] if len(self.params) > 1 else 26
            signal = self.params[2] if len(self.params) > 2 else 9
            return template.format(fast=fast, slow=slow, signal=signal)
        elif self.name in ["macd_signal", "macd_hist"]:
            fast = self.params[0] if len(self.params) > 0 else 12
            slow = self.params[1] if len(self.params) > 1 else 26
            signal = self.params[2] if len(self.params) > 2 else 9
            return template.format(fast=fast, slow=slow, signal=signal)
        elif self.name in ["bb_upper", "bb_lower"]:
            period = self.params[0] if len(self.params) > 0 else 20
            std = self.params[1] if len(self.params) > 1 else 2
            return template.format(period=period, std=std)
        else:
            return template


@dataclass
class Value:
    """값 노드 (숫자 또는 퍼센트)"""
    value: float
    is_percent: bool = False

    def __str__(self) -> str:
        if self.is_percent:
            return f"{self.value}%"
        return str(self.value)

    def to_code(self) -> str:
        if self.is_percent:
            return str(self.value / 100)  # 퍼센트를 소수로 변환
        return str(self.value)


@dataclass
class ArithmeticExpr:
    """산술 표현식 노드"""
    left: Union[Indicator, Value, "ArithmeticExpr"]
    operator: ArithmeticOperator
    right: Union[Indicator, Value, "ArithmeticExpr"]

    def __str__(self) -> str:
        return f"{self.left} {self.operator.value} {self.right}"

    def to_code(self) -> str:
        left_code = self.left.to_code() if hasattr(self.left, 'to_code') else str(self.left)
        right_code = self.right.to_code() if hasattr(self.right, 'to_code') else str(self.right)
        return f"({left_code} {self.operator.value} {right_code})"


@dataclass
class Condition:
    """단일 조건 노드"""
    left: Union[Indicator, Value, ArithmeticExpr]
    operator: Operator
    right: Union[Indicator, Value, ArithmeticExpr]
    condition_type: ConditionType = ConditionType.THRESHOLD

    def __str__(self) -> str:
        op_str = self.operator.value
        return f"{self.left} {op_str} {self.right}"

    def get_required_days(self) -> int:
        """필요한 과거 데이터 일수 계산"""
        days = 10  # 기본값

        def extract_period(node):
            if isinstance(node, Indicator):
                # MACD: slow_period + signal_period 필요
                if node.name in ["macd", "macd_signal"]:
                    slow = node.params[1] if len(node.params) > 1 else 26
                    signal = node.params[2] if len(node.params) > 2 else 9
                    return slow + signal
                elif node.params and isinstance(node.params[0], (int, float)):
                    return int(node.params[0])
            elif isinstance(node, ArithmeticExpr):
                return max(extract_period(node.left), extract_period(node.right))
            return 0

        days = max(days, extract_period(self.left) + 10, extract_period(self.right) + 10)
        return days


@dataclass
class CompositeCondition:
    """복합 조건 노드 (AND/OR)"""
    left: Union[Condition, "CompositeCondition"]
    operator: LogicalOperator
    right: Union[Condition, "CompositeCondition"]

    def __str__(self) -> str:
        return f"({self.left} {self.operator.value} {self.right})"

    def get_required_days(self) -> int:
        left_days = self.left.get_required_days() if hasattr(self.left, 'get_required_days') else 10
        right_days = self.right.get_required_days() if hasattr(self.right, 'get_required_days') else 10
        return max(left_days, right_days)


# 타입 별칭
ConditionNode = Union[Condition, CompositeCondition]
ExpressionNode = Union[Indicator, Value, ArithmeticExpr]


class StrategyDSLParser:
    """전략 DSL 파서"""

    # 토큰 패턴
    TOKEN_PATTERNS = [
        ("LPAREN", r"\("),
        ("RPAREN", r"\)"),
        ("COMMA", r","),
        ("PERCENT", r"%"),
        ("CROSSES_ABOVE", r"crosses_above"),
        ("CROSSES_BELOW", r"crosses_below"),
        ("BREAKS", r"breaks"),
        ("AND", r"(?:AND|and)\b"),
        ("OR", r"(?:OR|or)\b"),
        ("GTE", r">="),
        ("LTE", r"<="),
        ("NEQ", r"!="),
        ("EQ", r"=="),
        ("GT", r">"),
        ("LT", r"<"),
        ("MUL", r"\*"),
        ("DIV", r"/"),
        ("ADD", r"\+"),
        ("SUB", r"-"),
        ("NUMBER", r"-?\d+\.?\d*"),
        ("IDENTIFIER", r"[a-zA-Z_][a-zA-Z0-9_]*"),
        ("WHITESPACE", r"\s+"),
    ]

    def __init__(self):
        self.tokens = []
        self.pos = 0

    def tokenize(self, text: str) -> list:
        """문자열을 토큰으로 분리"""
        tokens = []
        pos = 0

        while pos < len(text):
            match = None
            for token_type, pattern in self.TOKEN_PATTERNS:
                regex = re.compile(pattern)
                match = regex.match(text, pos)
                if match:
                    if token_type != "WHITESPACE":
                        tokens.append((token_type, match.group()))
                    pos = match.end()
                    break

            if not match:
                raise SyntaxError(f"Unexpected character at position {pos}: {text[pos]}")

        return tokens

    def parse(self, text: str) -> ConditionNode:
        """DSL 문자열을 AST로 파싱"""
        self.tokens = self.tokenize(text)
        self.pos = 0
        return self._parse_or_expression()

    def _current_token(self) -> Optional[tuple]:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def _consume(self, expected_type: str = None) -> tuple:
        token = self._current_token()
        if token is None:
            raise SyntaxError("Unexpected end of input")
        if expected_type and token[0] != expected_type:
            raise SyntaxError(f"Expected {expected_type}, got {token[0]}")
        self.pos += 1
        return token

    def _peek(self, offset: int = 0) -> Optional[tuple]:
        pos = self.pos + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return None

    def _parse_or_expression(self) -> ConditionNode:
        """OR 표현식 파싱"""
        left = self._parse_and_expression()

        while self._current_token() and self._current_token()[0] == "OR":
            self._consume("OR")
            right = self._parse_and_expression()
            left = CompositeCondition(left, LogicalOperator.OR, right)

        return left

    def _parse_and_expression(self) -> ConditionNode:
        """AND 표현식 파싱"""
        left = self._parse_condition()

        while self._current_token() and self._current_token()[0] == "AND":
            self._consume("AND")
            right = self._parse_condition()
            left = CompositeCondition(left, LogicalOperator.AND, right)

        return left

    def _parse_condition(self) -> Condition:
        """단일 조건 파싱"""
        left = self._parse_arithmetic()

        token = self._current_token()
        if not token:
            raise SyntaxError("Expected operator")

        # 연산자 파싱
        operator = None
        condition_type = ConditionType.THRESHOLD

        if token[0] == "CROSSES_ABOVE":
            self._consume()
            operator = Operator.CROSSES_ABOVE
            condition_type = ConditionType.CROSSOVER
        elif token[0] == "CROSSES_BELOW":
            self._consume()
            operator = Operator.CROSSES_BELOW
            condition_type = ConditionType.CROSSOVER
        elif token[0] == "BREAKS":
            self._consume()
            operator = Operator.BREAKS
            condition_type = ConditionType.BREAKOUT
        elif token[0] == "GTE":
            self._consume()
            operator = Operator.GTE
        elif token[0] == "LTE":
            self._consume()
            operator = Operator.LTE
        elif token[0] == "GT":
            self._consume()
            operator = Operator.GT
        elif token[0] == "LT":
            self._consume()
            operator = Operator.LT
        elif token[0] == "EQ":
            self._consume()
            operator = Operator.EQ
        elif token[0] == "NEQ":
            self._consume()
            operator = Operator.NEQ
        else:
            raise SyntaxError(f"Expected operator, got {token[0]}")

        right = self._parse_arithmetic()

        # consecutive는 패턴 타입
        if isinstance(left, Indicator) and left.name == "consecutive":
            condition_type = ConditionType.PATTERN

        return Condition(left, operator, right, condition_type)

    def _parse_arithmetic(self) -> ExpressionNode:
        """산술 표현식 파싱 (*, /)"""
        left = self._parse_term()

        while self._current_token() and self._current_token()[0] in ["MUL", "DIV"]:
            op_token = self._consume()
            op = ArithmeticOperator.MUL if op_token[0] == "MUL" else ArithmeticOperator.DIV
            right = self._parse_term()
            left = ArithmeticExpr(left, op, right)

        return left

    def _parse_term(self) -> ExpressionNode:
        """항 파싱 (+, -)"""
        left = self._parse_factor()

        while self._current_token() and self._current_token()[0] in ["ADD", "SUB"]:
            op_token = self._consume()
            op = ArithmeticOperator.ADD if op_token[0] == "ADD" else ArithmeticOperator.SUB
            right = self._parse_factor()
            left = ArithmeticExpr(left, op, right)

        return left

    def _parse_factor(self) -> ExpressionNode:
        """인자 파싱 (지표, 값, 또는 단항 마이너스)"""
        token = self._current_token()

        if token[0] == "SUB":
            # 단항 마이너스: -20, -3.5 등
            self._consume("SUB")
            next_token = self._current_token()
            if next_token and next_token[0] == "NUMBER":
                val = self._parse_value()
                return Value(-val.value, val.is_percent)
            else:
                raise SyntaxError(f"Expected number after '-', got {next_token}")
        elif token[0] == "NUMBER":
            return self._parse_value()
        elif token[0] == "IDENTIFIER":
            return self._parse_indicator()
        elif token[0] == "LPAREN":
            self._consume("LPAREN")
            expr = self._parse_arithmetic()
            self._consume("RPAREN")
            return expr
        else:
            raise SyntaxError(f"Unexpected token: {token}")

    def _parse_indicator(self) -> Indicator:
        """지표 파싱"""
        name_token = self._consume("IDENTIFIER")
        name = name_token[1]
        params = []

        # 함수 호출 형태인지 확인
        if self._current_token() and self._current_token()[0] == "LPAREN":
            self._consume("LPAREN")

            # 파라미터 파싱
            while True:
                token = self._current_token()
                if token[0] == "RPAREN":
                    break

                if token[0] == "NUMBER":
                    num_token = self._consume("NUMBER")
                    params.append(float(num_token[1]) if "." in num_token[1] else int(num_token[1]))
                elif token[0] == "IDENTIFIER":
                    id_token = self._consume("IDENTIFIER")
                    params.append(id_token[1])

                # 콤마 처리
                if self._current_token() and self._current_token()[0] == "COMMA":
                    self._consume("COMMA")
                else:
                    break

            self._consume("RPAREN")

        return Indicator(name, params)

    def _parse_value(self) -> Value:
        """값 파싱"""
        num_token = self._consume("NUMBER")
        value = float(num_token[1]) if "." in num_token[1] else int(num_token[1])

        is_percent = False
        if self._current_token() and self._current_token()[0] == "PERCENT":
            self._consume("PERCENT")
            is_percent = True

        return Value(value, is_percent)


@dataclass
class StrategyDefinition:
    """전략 정의"""
    name: str
    name_ko: str
    buy_condition: Optional[ConditionNode] = None
    sell_condition: Optional[ConditionNode] = None
    params: dict = field(default_factory=dict)

    def get_required_days(self) -> int:
        """필요한 과거 데이터 일수"""
        days = 10
        if self.buy_condition:
            days = max(days, self.buy_condition.get_required_days())
        if self.sell_condition:
            days = max(days, self.sell_condition.get_required_days())
        return days

    def get_condition_type(self) -> ConditionType:
        """주요 조건 유형 판단"""
        if self.buy_condition:
            if isinstance(self.buy_condition, Condition):
                return self.buy_condition.condition_type
            elif isinstance(self.buy_condition, CompositeCondition):
                return ConditionType.COMPOSITE
        return ConditionType.THRESHOLD


def parse_strategy(
    name: str,
    name_ko: str,
    buy_condition: str = None,
    sell_condition: str = None,
    params: dict = None
) -> StrategyDefinition:
    """
    전략 문자열을 파싱하여 StrategyDefinition 생성

    Args:
        name: 전략 영문명 (snake_case)
        name_ko: 전략 한글명
        buy_condition: 매수 조건 DSL 문자열
        sell_condition: 매도 조건 DSL 문자열
        params: 추가 파라미터

    Returns:
        StrategyDefinition

    Example:
        >>> strategy = parse_strategy(
        ...     name="golden_cross",
        ...     name_ko="골든크로스",
        ...     buy_condition="ma(5) crosses_above ma(20)",
        ...     sell_condition="ma(5) crosses_below ma(20)"
        ... )
    """
    parser = StrategyDSLParser()

    buy_ast = parser.parse(buy_condition) if buy_condition else None
    sell_ast = parser.parse(sell_condition) if sell_condition else None

    return StrategyDefinition(
        name=name,
        name_ko=name_ko,
        buy_condition=buy_ast,
        sell_condition=sell_ast,
        params=params or {}
    )


# 테스트
if __name__ == "__main__":
    parser = StrategyDSLParser()

    # 테스트 케이스
    test_cases = [
        # Crossover
        "ma(5) crosses_above ma(20)",
        "ma(5) crosses_below ma(20)",

        # Threshold
        "disparity(20) < 90",
        "rsi(14) < 30",
        "returns(60) > 30%",

        # Breakout
        "close breaks high(250)",

        # Pattern
        "consecutive(up) >= 5",

        # Composite
        "close > ma(60) AND change > 0",
        "rsi(14) < 30 OR disparity(20) < 85",

        # Arithmetic
        "volume > volume_ma(20) * 1.5",
        "close < bb_lower(20, 2)",
    ]

    print("DSL Parser Test\n" + "=" * 50)

    for test in test_cases:
        try:
            ast = parser.parse(test)
            print(f"Input:  {test}")
            print(f"AST:    {ast}")
            print(f"Days:   {ast.get_required_days()}")
            print()
        except Exception as e:
            print(f"Input:  {test}")
            print(f"Error:  {e}")
            print()
