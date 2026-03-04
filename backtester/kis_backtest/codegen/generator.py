"""Lean Code Generator - Schema Based.

StrategySchema → Lean Python 코드 변환.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from kis_backtest.core.schema import (
    CandlestickSchema,
    ConditionSchema,
    CompositeConditionSchema,
    IndicatorSchema,
    OperatorType,
    StrategySchema,
    PRICE_FIELDS,
)
from kis_backtest.core.strategy import StrategyDefinition
from kis_backtest.core.converters import from_definition
from kis_backtest.core.indicator import INDICATOR_REGISTRY, get_indicator_info
from kis_backtest.core.candlestick import CANDLESTICK_REGISTRY
from kis_backtest.codegen.validator import IndicatorValidator
from kis_backtest.strategies.base import BaseStrategy

logger = logging.getLogger(__name__)


@dataclass
class CodeGenConfig:
    """코드 생성 설정"""
    market: str = "krx"  # krx, us
    commission_rate: float = 0.00015  # 0.015%
    tax_rate: float = 0.002  # 0.2% (KRX 매도세)
    slippage: float = 0.0  # 슬리피지 (기본 0%)
    initial_capital: float = 100_000_000  # 1억원


class LeanCodeGenerator:
    """Lean 코드 생성기 - Schema Based
    
    StrategySchema를 읽어 Lean Python 알고리즘 코드를 생성합니다.
    
    Example:
        # StrategySchema 직접 사용
        schema = StrategySchema(...)
        generator = LeanCodeGenerator(schema)
        
        # StrategyDefinition도 자동 변환
        definition = StrategyRegistry.build("rsi_oversold")
        generator = LeanCodeGenerator(definition)
        
        code = generator.generate(
            symbols=["005930", "000660"],
            start_date="2024-01-01",
            end_date="2024-12-31",
        )
    """
    
    def __init__(
        self,
        strategy: Union[StrategySchema, StrategyDefinition, BaseStrategy],
        config: Optional[CodeGenConfig] = None,
    ):
        if strategy is None:
            raise ValueError("strategy cannot be None")

        # BaseStrategy 인스턴스 저장 (커스텀 로직용)
        self._base_strategy: Optional[BaseStrategy] = None

        # BaseStrategy → StrategyDefinition → StrategySchema
        if isinstance(strategy, BaseStrategy):
            self._base_strategy = strategy
            definition = strategy.build()
            self.schema = from_definition(definition)
            self._original_definition = definition
        # StrategyDefinition → StrategySchema 자동 변환
        elif isinstance(strategy, StrategyDefinition):
            self.schema = from_definition(strategy)
            self._original_definition = strategy
        else:
            self.schema = strategy
            self._original_definition = None

        if self.schema is None:
            raise ValueError("Failed to create strategy schema")

        self.config = config or CodeGenConfig()

        # 지표 맵 구축 (alias → IndicatorSchema)
        self._indicator_map = self.schema.collect_all_indicators()

        # 캔들스틱 맵 구축 (alias → CandlestickSchema)
        self._candlestick_map: Dict[str, CandlestickSchema] = {
            cs.alias or cs.id: cs for cs in self.schema.candlesticks
        }

        # 고유 지표 목록 (중복 제거)
        self._unique_indicators = self.schema.get_unique_indicators()

        # sanitization collision 감지: 서로 다른 alias가 같은 Python 식별자로 충돌할 경우 suffix 부여
        self._sanitized_alias_map: Dict[str, str] = self._build_sanitized_alias_map()

        self._validate_indicators()
    
    @staticmethod
    def _sanitize_var_name(name: str) -> str:
        """alias → 유효한 Python 식별자 변환.

        괄호·공백·특수문자를 _ 로 치환합니다.
        숫자로 시작하는 이름에는 ind_ prefix를 추가합니다.
        예: 'SMA(단기)' → 'SMA_단기', 'RSI (14)' → 'RSI_14', '2sma' → 'ind_2sma'
        """
        import re
        sanitized = re.sub(r'[^a-zA-Z0-9_\uAC00-\uD7A3]', '_', name)
        sanitized = re.sub(r'_+', '_', sanitized).strip('_')
        if not sanitized:
            return '_indicator'
        if sanitized[0].isdigit():
            sanitized = f'ind_{sanitized}'
        return sanitized

    def _build_sanitized_alias_map(self) -> Dict[str, str]:
        """alias → collision-free Python 식별자 매핑 구축.

        서로 다른 alias가 sanitization 후 같은 이름으로 충돌할 경우
        _2, _3 suffix를 붙여 고유성을 보장합니다.
        """
        seen_sanitized: Dict[str, str] = {}  # sanitized_name → original alias
        alias_map: Dict[str, str] = {}

        for alias in list(self._indicator_map.keys()) + list(self._candlestick_map.keys()):
            base = self._sanitize_var_name(alias)
            if base not in seen_sanitized:
                seen_sanitized[base] = alias
                alias_map[alias] = base
            else:
                # 충돌: suffix로 보정
                n = 2
                while f"{base}_{n}" in seen_sanitized:
                    n += 1
                resolved = f"{base}_{n}"
                seen_sanitized[resolved] = alias
                alias_map[alias] = resolved
                logger.warning(
                    f"alias sanitization 충돌: '{alias}' → '{resolved}' "
                    f"('{seen_sanitized[base]}'와 동일한 Python 식별자)"
                )

        return alias_map

    def _get_sanitized_alias(self, alias: str) -> str:
        """alias의 collision-free Python 식별자 반환."""
        return self._sanitized_alias_map.get(alias, self._sanitize_var_name(alias))

    def _validate_indicators(self) -> None:
        """지표 파라미터 검증 + 조건 alias 정합성 검증"""
        for indicator in self._unique_indicators:
            result = IndicatorValidator.validate(indicator.id, indicator.params)
            if not result.is_valid:
                result.raise_if_invalid()

            for warning in result.warnings:
                logger.warning(f"[{indicator.id}] {warning}")

        self._validate_condition_aliases()

    def _validate_condition_aliases(self) -> None:
        """조건에서 참조하는 indicator alias가 실제 indicators에 정의되어 있는지 검증.

        정의되지 않은 alias를 사용하면 런타임 KeyError가 발생하므로
        코드 생성 전에 명확한 오류 메시지를 제공합니다.

        예: indicators에 SMA(단기)/SMA(장기) 가 있는데 조건이 sma_1/sma_2를 참조하면 오류.
        """
        defined_aliases = set(self._indicator_map.keys()) | PRICE_FIELDS

        unknown: list[str] = []

        def collect(cond) -> None:
            if isinstance(cond, CompositeConditionSchema):
                for sub in cond.conditions:
                    collect(sub)
            elif isinstance(cond, ConditionSchema):
                if cond.indicator and cond.indicator not in defined_aliases:
                    unknown.append(f"indicator '{cond.indicator}'")
                if (
                    cond.compare_to
                    and isinstance(cond.compare_to, str)
                    and cond.compare_to not in defined_aliases
                ):
                    unknown.append(f"compare_to '{cond.compare_to}'")

        collect(self.schema.entry)
        collect(self.schema.exit)

        if unknown:
            defined_list = sorted(defined_aliases - PRICE_FIELDS)
            raise ValueError(
                f"조건에서 정의되지 않은 indicator alias 참조: {', '.join(set(unknown))}. "
                f"정의된 alias 목록: {defined_list}. "
                f"지표 alias를 변경했다면 조건에서 참조하는 alias도 함께 수정해야 합니다."
            )

    def _get_tradebar_indicator_aliases(self) -> tuple[List[str], List[str]]:
        """지표를 TradeBar 필요/불필요로 분류

        Returns:
            (tradebar_required, decimal_only) - 각각의 alias 리스트
        """
        tradebar_required = []
        decimal_only = []

        # 커스텀 지표는 .Update() 루프에서 제외 (정수/부동소수 카운터로 관리)
        # beta/alpha는 self.B()/self.A()로 등록 → Lean 프레임워크가 자동 업데이트
        custom_ids = {"consecutive", "disparity", "volatility_ind", "change", "returns", "beta", "alpha"}

        for ind in self._unique_indicators:
            if ind.id in custom_ids:
                continue
            info = get_indicator_info(ind.id)
            alias = ind.alias or ind.id
            if info and info.requires_tradebar:
                tradebar_required.append(alias)
            else:
                decimal_only.append(alias)

        return tradebar_required, decimal_only

    def _generate_custom_logic(self) -> tuple[str, str]:
        """커스텀 로직 코드 생성

        BaseStrategy.get_custom_lean_code()가 반환하는 커스텀 로직을 처리합니다.

        Returns:
            (custom_init, custom_logic) - Initialize용 코드와 OnData용 코드
        """
        if self._base_strategy is None:
            return "", ""

        custom_code = self._base_strategy.get_custom_lean_code()
        if custom_code is None:
            return "", ""

        # 커스텀 로직에 필요한 변수 초기화 코드 생성
        # 변수 패턴: self.variable_name[symbol] 형태
        custom_vars = set()

        # 일반적인 커스텀 변수 패턴 검색
        import re
        patterns = [
            r'self\.(\w+)\[symbol\]',  # self.var_name[symbol]
        ]

        for pattern in patterns:
            matches = re.findall(pattern, custom_code)
            custom_vars.update(matches)

        # 기본 변수 제외 (이미 초기화됨)
        excluded = {
            'indicators', 'candlesticks', 'prev_values',
            'entry_prices', 'high_prices', 'Portfolio', 'Securities'
        }
        custom_vars -= excluded

        # Initialize 코드 생성
        init_lines = []
        for var_name in sorted(custom_vars):
            init_lines.append(f"        self.{var_name} = {{}}")

        custom_init = "\n".join(init_lines)

        # OnData 코드 (들여쓰기 조정)
        # 이미 커스텀 코드에 적절한 들여쓰기가 포함되어 있음
        custom_logic = f'''
            # === 커스텀 로직 ==={custom_code}'''

        return custom_init, custom_logic

    def _generate_indicator_update_code(
        self,
        tradebar_indicators: List[str],
        decimal_indicators: List[str],
    ) -> str:
        """지표 업데이트 코드 생성

        TradeBar가 필요한 지표와 decimal-only 지표를 분리하여 업데이트합니다.

        Args:
            tradebar_indicators: TradeBar 업데이트가 필요한 지표 alias 목록
            decimal_indicators: decimal 업데이트 가능한 지표 alias 목록

        Returns:
            지표 업데이트 코드
        """
        lines = []

        # TradeBar가 필요한 지표가 있거나 캔들스틱이 있으면 TradeBar 생성
        needs_tradebar = bool(tradebar_indicators) or bool(self.schema.candlesticks)

        if needs_tradebar:
            lines.append('''            # TradeBar 생성 (TradeBar 필요 지표/캔들스틱용)
            trade_bar = TradeBar()
            trade_bar.Time = bar.Time
            trade_bar.Open = bar.Open
            trade_bar.High = bar.High
            trade_bar.Low = bar.Low
            trade_bar.Close = bar.Close
            trade_bar.Volume = bar.Volume''')

        # Decimal-only 지표 업데이트
        if decimal_indicators:
            decimal_aliases_str = str(decimal_indicators)
            lines.append(f'''
            # Decimal-only 지표 업데이트
            for alias in {decimal_aliases_str}:
                if alias in self.indicators[symbol]:
                    self.indicators[symbol][alias].Update(bar.Time, price)''')

        # TradeBar 필요 지표 업데이트
        if tradebar_indicators:
            tradebar_aliases_str = str(tradebar_indicators)
            lines.append(f'''
            # TradeBar 필요 지표 업데이트
            for alias in {tradebar_aliases_str}:
                if alias in self.indicators[symbol]:
                    self.indicators[symbol][alias].Update(trade_bar)''')

        return "\n".join(lines)
    
    def generate(
        self,
        symbols: List[str],
        start_date: str,
        end_date: str,
        initial_capital: Optional[float] = None,
    ) -> str:
        """Lean 코드 생성
        
        Args:
            symbols: 종목 코드 리스트
            start_date: 시작일 (YYYY-MM-DD)
            end_date: 종료일 (YYYY-MM-DD)
            initial_capital: 초기 자본 (None이면 config 사용)
        
        Returns:
            Lean Python 알고리즘 코드
        """
        capital = initial_capital or self.config.initial_capital
        
        # 코드 생성
        code_parts = [
            self._generate_header(),
            self._generate_data_class(),
            self._generate_fee_model(),
        ]
        
        # 슬리피지 모델 추가 (설정된 경우만)
        slippage_model = self._generate_slippage_model()
        if slippage_model:
            code_parts.append(slippage_model)
        
        code_parts.append(self._generate_algorithm(symbols, start_date, end_date, capital))
        
        code = "\n\n".join(code_parts)
        try:
            compile(code, "<lean_generated>", "exec")
        except SyntaxError as e:
            raise ValueError(f"생성된 Lean 코드 구문 오류 (line {e.lineno}): {e.msg}")
        return code
    
    def _generate_header(self) -> str:
        """파일 헤더 생성"""
        # 캔들스틱 패턴 import 생성
        candlestick_imports = ""
        if self.schema.candlesticks:
            # 사용되는 캔들스틱 클래스 수집
            lean_classes = set()
            for cs in self.schema.candlesticks:
                pattern_info = CANDLESTICK_REGISTRY.get(cs.id)
                if pattern_info:
                    lean_classes.add(pattern_info.lean_class)

            if lean_classes:
                classes_str = ", ".join(sorted(lean_classes))
                candlestick_imports = f"\nfrom QuantConnect.Indicators.CandlestickPatterns import {classes_str}"

        slippage_info = f"\n슬리피지: {self.config.slippage * 100:.2f}%" if self.config.slippage > 0 else ""
        return f'''"""자동 생성된 Lean 알고리즘
전략: {self.schema.name}
ID: {self.schema.id}
생성일: {datetime.now().isoformat()}
수수료율: {self.config.commission_rate * 100:.4f}%
거래세율: {self.config.tax_rate * 100:.2f}%{slippage_info}
"""

from AlgorithmImports import *
from datetime import datetime, timedelta{candlestick_imports}'''
    
    def _generate_data_class(self) -> str:
        """커스텀 데이터 클래스 생성"""
        if self.config.market == "us":
            return self._generate_us_data_class()
        return self._generate_krx_data_class()
    
    def _generate_krx_data_class(self) -> str:
        """KRX 커스텀 데이터 클래스 (주식 + 지수)"""
        return '''
class KRXEquity(PythonData):
    """한국 주식 커스텀 데이터"""

    def GetSource(self, config, date, isLive):
        symbol = config.Symbol.Value.lower()
        source = f"/Data/equity/krx/daily/{symbol}.csv"
        return SubscriptionDataSource(source, SubscriptionTransportMedium.LocalFile, FileFormat.Csv)

    def Reader(self, config, line, date, isLive):
        if not line.strip():
            return None

        data = KRXEquity()
        data.Symbol = config.Symbol

        try:
            cols = line.split(",")
            data.Time = datetime.strptime(cols[0], "%Y%m%d")
            data.Value = float(cols[4])
            data["Open"] = float(cols[1])
            data["High"] = float(cols[2])
            data["Low"] = float(cols[3])
            data["Close"] = float(cols[4])
            data["Volume"] = int(cols[5])
        except Exception:
            return None

        return data


class KRXIndex(PythonData):
    """한국 지수 커스텀 데이터 (KOSPI 벤치마크용)"""

    def GetSource(self, config, date, isLive):
        symbol = config.Symbol.Value.lower()
        source = f"/Data/index/krx/daily/{symbol}.csv"
        return SubscriptionDataSource(source, SubscriptionTransportMedium.LocalFile, FileFormat.Csv)

    def Reader(self, config, line, date, isLive):
        if not line.strip():
            return None

        data = KRXIndex()
        data.Symbol = config.Symbol

        try:
            cols = line.split(",")
            data.Time = datetime.strptime(cols[0], "%Y%m%d")
            data.Value = float(cols[4])  # 종가
            data["Open"] = float(cols[1])
            data["High"] = float(cols[2])
            data["Low"] = float(cols[3])
            data["Close"] = float(cols[4])
            data["Volume"] = int(cols[5]) if len(cols) > 5 and cols[5] else 0
        except Exception:
            return None

        return data'''
    
    def _generate_us_data_class(self) -> str:
        """US 커스텀 데이터 클래스"""
        return '''
class USEquity(PythonData):
    """미국 주식 커스텀 데이터"""
    
    def GetSource(self, config, date, isLive):
        symbol = config.Symbol.Value.lower()
        source = f"/Data/equity/usa/daily/{symbol}.csv"
        return SubscriptionDataSource(source, SubscriptionTransportMedium.LocalFile, FileFormat.Csv)
    
    def Reader(self, config, line, date, isLive):
        if not line.strip():
            return None
        
        data = USEquity()
        data.Symbol = config.Symbol
        
        try:
            cols = line.split(",")
            data.Time = datetime.strptime(cols[0], "%Y%m%d")
            data.Value = float(cols[4])
            data["Open"] = float(cols[1])
            data["High"] = float(cols[2])
            data["Low"] = float(cols[3])
            data["Close"] = float(cols[4])
            data["Volume"] = int(cols[5])
        except Exception:
            return None
        
        return data'''
    
    def _generate_fee_model(self) -> str:
        """수수료 모델 생성"""
        return f'''
class CustomFeeModel(FeeModel):
    """수수료 모델: 매수 {self.config.commission_rate * 100:.4f}%, 매도 {self.config.commission_rate * 100:.4f}% + 세금 {self.config.tax_rate * 100:.2f}%"""
    
    def GetOrderFee(self, parameters):
        value = abs(parameters.Order.GetValue(parameters.Security))
        if parameters.Order.Direction == OrderDirection.Buy:
            fee = value * {self.config.commission_rate}
        else:
            fee = value * ({self.config.commission_rate} + {self.config.tax_rate})
        return OrderFee(CashAmount(fee, "USD"))'''
    
    def _generate_slippage_model(self) -> str:
        """슬리피지 모델 생성 - KRX 호가 단위 기반 KRXSlippageModel"""
        if self.config.slippage <= 0:
            return ""
        return f'''class KRXSlippageModel:
    """한국 주식 호가 단위 기반 슬리피지 모델

    매수: (종가 + raw_slip) → 올림(ceiling) → 상위 유효 틱
    매도: (종가 - raw_slip) → 내림(floor)  → 하위 유효 틱
    """

    SLIP_RATE = {self.config.slippage}

    def _tick(self, price):
        if price < 1000: return 1
        elif price < 5000: return 5
        elif price < 10000: return 10
        elif price < 50000: return 50
        elif price < 100000: return 100
        elif price < 500000: return 500
        else: return 1000

    def GetSlippageApproximation(self, asset, order):
        price = int(round(float(asset.Price)))
        if price <= 0:
            return 0.0
        tick = self._tick(price)
        raw = int(round(price * self.SLIP_RATE))
        if int(order.Direction) == 0:  # Buy: 올림
            target = ((price + raw + tick - 1) // tick) * tick
        else:                           # Sell: 내림
            target = ((price - raw) // tick) * tick
        return float(abs(target - price))
'''
    
    def _generate_algorithm(
        self,
        symbols: List[str],
        start_date: str,
        end_date: str,
        capital: float,
    ) -> str:
        """Algorithm 클래스 생성"""
        data_class = "USEquity" if self.config.market == "us" else "KRXEquity"
        symbols_str = ",".join(symbols)

        # 지표 초기화 코드 생성 (중복 제거됨)
        indicator_init, warmup = self._generate_indicator_init()

        # 캔들스틱 초기화 코드 생성
        candlestick_init, cs_warmup = self._generate_candlestick_init()
        warmup = max(warmup, cs_warmup)

        # 지표값 가져오기 코드 생성
        indicator_values = self._generate_indicator_values()

        # 캔들스틱값 가져오기 코드 생성
        candlestick_values = self._generate_candlestick_values()

        # 이전값 업데이트 코드 생성
        prev_update = self._generate_prev_update()

        # 진입/청산 조건 생성 (스키마 기반)
        entry_condition = self._generate_condition(self.schema.entry, "entry")
        exit_condition = self._generate_condition(self.schema.exit, "exit")

        # 리스크 관리 코드 생성
        risk_init, risk_check, risk_update = self._generate_risk_management()

        # 날짜 파싱
        start_parts = start_date.split("-")
        end_parts = end_date.split("-")
        strategy_name = self.schema.name or self.schema.id
        
        # 캔들스틱 딕셔너리 초기화 (캔들스틱이 있는 경우만)
        candlestick_dict_init = ""
        candlestick_update = ""
        candlestick_ready_check = ""
        if self.schema.candlesticks:
            candlestick_dict_init = "            self.candlesticks[symbol] = {}"
            candlestick_update = '''
            for pattern in self.candlesticks[symbol].values():
                pattern.Update(trade_bar)'''
            candlestick_ready_check = " and all(p.IsReady for p in self.candlesticks[symbol].values())"

        # TradeBar 필요 지표와 decimal-only 지표 분류
        tradebar_indicators, decimal_indicators = self._get_tradebar_indicator_aliases()

        # 지표 업데이트 코드 생성
        indicator_update_code = self._generate_indicator_update_code(
            tradebar_indicators, decimal_indicators
        )

        # 커스텀 로직 코드 생성
        custom_init, custom_logic = self._generate_custom_logic()

        # 벤치마크 설정 (KRX만 해당)
        benchmark_setup = ""
        if self.config.market == "krx":
            benchmark_setup = """
        # KOSPI 벤치마크 설정 (Alpha/Beta 계산용)
        self.kospi_symbol = None
        try:
            kospi = self.AddData(KRXIndex, "kospi", Resolution.Daily).Symbol
            self.SetBenchmark(kospi)
            self.kospi_symbol = kospi
        except Exception:
            self.Debug("KOSPI 벤치마크 설정 실패 - 기본값 사용")
"""

        return f'''
class Algorithm(QCAlgorithm):
    """{self.schema.name}

    {self.schema.description}
    """

    def Initialize(self):
        self.SetStartDate({start_parts[0]}, {start_parts[1].lstrip("0")}, {start_parts[2].lstrip("0")})
        self.SetEndDate({end_parts[0]}, {end_parts[1].lstrip("0")}, {end_parts[2].lstrip("0")})
        self.SetCash({int(capital)}){benchmark_setup}

        self.strategy_name = "{strategy_name}"
        self.symbols = []
        self.indicators = {{}}
        self.candlesticks = {{}}
        self.prev_values = {{}}
{custom_init}
{risk_init}

        for symbol_str in "{symbols_str}".split(","):
            symbol = self.AddData({data_class}, symbol_str, Resolution.Daily).Symbol
            self.symbols.append(symbol)
            self.indicators[symbol] = {{}}
{candlestick_dict_init}
            self.prev_values[symbol] = {{}}

{indicator_init}
{candlestick_init}

        self.SetWarmUp({warmup}, Resolution.Daily)

        for symbol in self.symbols:
            self.Securities[symbol].SetFeeModel(CustomFeeModel()){"""
            self.Securities[symbol].SetSlippageModel(KRXSlippageModel())""" if self.config.slippage > 0 else ""}

    def OnData(self, data):
        if self.IsWarmingUp:
            return

        for symbol in self.symbols:
            if not data.ContainsKey(symbol):
                continue

            bar = data[symbol]
            price = bar.Close

            # 커스텀 데이터 시가평가를 위해 현재 가격 명시적 설정
            self.Securities[symbol].SetMarketPrice(bar)

            # 지표 업데이트
{indicator_update_code}
{candlestick_update}

            # 지표 준비 확인
            if not all(getattr(ind, 'IsReady', True) for ind in self.indicators[symbol].values()){candlestick_ready_check}:
                continue

            # 지표값 가져오기
{indicator_values}
{candlestick_values}

            holdings = self.Portfolio[symbol].Quantity
{custom_logic}

            # === 진입 조건 ===
{entry_condition}

            if entry_signal and holdings == 0:
                weight = 1.0 / len(self.symbols)
                self.SetHoldings(symbol, weight, tag=f"ENTRY: {{self.strategy_name}}")
                self.Debug(f"{{self.Time}} BUY {{symbol}} | {{self.strategy_name}}")
{risk_update}

            # === 청산 조건 ===
{exit_condition}
{risk_check}

            if exit_signal and holdings > 0:
                self.Liquidate(symbol, tag=f"EXIT: {{self.strategy_name}}")
                self.Debug(f"{{self.Time}} SELL {{symbol}} | {{self.strategy_name}}")

            # === 이전값 업데이트 ===
{prev_update}'''
    
    def _generate_indicator_init(self) -> tuple:
        """지표 초기화 코드 생성 (중복 제거)

        멀티 아웃풋 지표(MACD, Bollinger)는 한 번만 초기화합니다.
        """
        lines = []
        max_warmup = 30
        initialized_aliases = set()

        for indicator in self._unique_indicators:
            # alias 기준으로 중복 제거 (같은 alias면 이미 초기화됨)
            alias = indicator.alias or indicator.id
            if alias in initialized_aliases:
                continue
            initialized_aliases.add(alias)

            # 커스텀 지표 처리
            if indicator.id == "consecutive":
                alias = indicator.alias or indicator.id
                lines.append(f"            self.indicators[symbol]['{alias}'] = 0  # consecutive counter")
                max_warmup = max(max_warmup, 2)
                continue

            if indicator.id == "disparity":
                alias = indicator.alias or indicator.id
                period = indicator.params.get("period", 20)
                lines.append(f"            self.indicators[symbol]['{alias}_sma'] = self.SMA(symbol, {period})")
                max_warmup = max(max_warmup, period + 5)
                continue

            if indicator.id == "volatility_ind":
                alias = indicator.alias or indicator.id
                period = indicator.params.get("period", 10)
                lines.append(f"            self.indicators[symbol]['{alias}_returns'] = []  # daily returns buffer")
                lines.append(f"            self.indicators[symbol]['{alias}_period'] = {period}")
                max_warmup = max(max_warmup, period + 5)
                continue

            if indicator.id == "change":
                alias = indicator.alias or indicator.id
                lines.append(f"            self.indicators[symbol]['{alias}'] = 0  # daily change %")
                max_warmup = max(max_warmup, 2)
                continue

            if indicator.id == "returns":
                alias = indicator.alias or indicator.id
                period = indicator.params.get("period", 10)
                lines.append(f"            self.indicators[symbol]['{alias}_roc'] = self.ROCP(symbol, {period})")
                max_warmup = max(max_warmup, period + 5)
                continue

            if indicator.id == "beta":
                alias = indicator.alias or indicator.id
                period = indicator.params.get("period", 20)
                lines.append(f"            if self.kospi_symbol is not None:")
                lines.append(f"                self.indicators[symbol]['{alias}'] = self.B(symbol, self.kospi_symbol, {period})")
                lines.append(f"            else:")
                lines.append(f"                self.indicators[symbol]['{alias}'] = SimpleMovingAverage(1)  # kospi 없을 때 더미")
                max_warmup = max(max_warmup, period + 5)
                continue

            if indicator.id == "alpha":
                alias = indicator.alias or indicator.id
                period = indicator.params.get("period", 20)
                lines.append(f"            if self.kospi_symbol is not None:")
                lines.append(f"                self.indicators[symbol]['{alias}'] = self.A(symbol, self.kospi_symbol, {period})")
                lines.append(f"            else:")
                lines.append(f"                self.indicators[symbol]['{alias}'] = SimpleMovingAverage(1)  # kospi 없을 때 더미")
                max_warmup = max(max_warmup, period + 5)
                continue

            init_code, warmup = IndicatorValidator.get_lean_init_code(
                indicator.id, indicator.params, alias
            )

            # 주석에 표시 이름(name) 우선, 없으면 alias 사용
            display = indicator.name or alias
            params_str = ", ".join(f"{k}={v}" for k, v in indicator.params.items())
            lines.append(
                f"            # {display}: {indicator.id}({params_str})\n"
                f"            self.indicators[symbol]['{alias}'] = {init_code.split(' = ', 1)[1]}"
            )
            max_warmup = max(max_warmup, warmup)

        return "\n".join(lines), max_warmup

    def _generate_candlestick_init(self) -> tuple:
        """캔들스틱 초기화 코드 생성

        Returns:
            (초기화 코드, warmup 기간)
        """
        if not self.schema.candlesticks:
            return "", 5

        lines = []
        max_warmup = 5

        for cs in self.schema.candlesticks:
            init_code, warmup = IndicatorValidator.get_candlestick_init_code(
                cs.id, cs.alias or cs.id
            )

            alias = cs.alias or cs.id
            # init_code는 "alias = CandlestickPatterns.Xxx()" 형태
            lean_init = init_code.split(" = ", 1)[1]
            lines.append(f"            self.candlesticks[symbol]['{alias}'] = {lean_init}")
            max_warmup = max(max_warmup, warmup)

        return "\n".join(lines), max_warmup

    def _generate_candlestick_values(self) -> str:
        """캔들스틱값 가져오기 코드 생성

        캔들스틱 패턴은 Current.Value로 신호를 반환합니다:
        - +1: 상승 신호 (bullish)
        - -1: 하락 신호 (bearish)
        - 0: 신호 없음
        """
        if not self.schema.candlesticks:
            return ""

        lines = []
        for cs in self.schema.candlesticks:
            alias = cs.alias or cs.id
            lines.append(f"            {alias}_signal = self.candlesticks[symbol]['{alias}'].Current.Value")

        return "\n".join(lines)
    
    def _collect_all_indicator_outputs(self) -> List[tuple]:
        """조건에서 사용되는 모든 지표+output 조합 수집
        
        Returns:
            List of (alias, output) tuples
        """
        outputs = set()
        
        # 지표 목록에서 수집
        for ind in self.schema.indicators:
            if ind.id not in PRICE_FIELDS:
                outputs.add((ind.alias or ind.id, ind.output or "value"))
        
        # 조건에서 수집
        def collect_from_condition(cond):
            if isinstance(cond, CompositeConditionSchema):
                for sub in cond.conditions:
                    collect_from_condition(sub)
            elif isinstance(cond, ConditionSchema):
                # 왼쪽 지표
                if cond.indicator and cond.indicator not in PRICE_FIELDS:
                    outputs.add((cond.indicator, cond.indicator_output or "value"))
                # 오른쪽 지표
                if cond.compare_to and cond.compare_to not in PRICE_FIELDS:
                    outputs.add((cond.compare_to, cond.compare_output or "value"))
        
        collect_from_condition(self.schema.entry)
        collect_from_condition(self.schema.exit)
        
        return list(outputs)
    
    def _generate_indicator_values(self) -> str:
        """지표값 가져오기 코드 생성
        
        조건에서 사용되는 모든 지표+output 조합을 생성합니다.
        """
        lines = []
        generated_values = set()
        
        # 커스텀 지표 업데이트 로직
        custom_ids = {"consecutive", "disparity", "volatility_ind", "change", "returns"}
        custom_indicators = [ind for ind in self.schema.indicators if ind.id in custom_ids]

        if custom_indicators:
            lines.append("            prev_price = self.prev_values[symbol].get('price', price)")

        for ind in custom_indicators:
            alias = ind.alias or ind.id

            if ind.id == "consecutive":
                lines.append(f"            # consecutive 카운터 업데이트")
                direction = ind.params.get("direction", "up")
                if direction == "up":
                    lines.append(f"            if price > prev_price:")
                    lines.append(f"                self.indicators[symbol]['{alias}'] += 1")
                    lines.append(f"            else:")
                    lines.append(f"                self.indicators[symbol]['{alias}'] = 0")
                else:
                    lines.append(f"            if price < prev_price:")
                    lines.append(f"                self.indicators[symbol]['{alias}'] += 1")
                    lines.append(f"            else:")
                    lines.append(f"                self.indicators[symbol]['{alias}'] = 0")

            elif ind.id == "disparity":
                lines.append(f"            # disparity 이격도 계산")
                lines.append(f"            {alias}_sma_val = self.indicators[symbol]['{alias}_sma'].Current.Value")
                lines.append(f"            self.indicators[symbol]['{alias}'] = (price / {alias}_sma_val * 100) if {alias}_sma_val > 0 else 100")

            elif ind.id == "volatility_ind":
                period = ind.params.get("period", 10)
                lines.append(f"            # volatility_ind 변동성 계산")
                lines.append(f"            if prev_price > 0:")
                lines.append(f"                daily_ret = (price - prev_price) / prev_price")
                lines.append(f"                self.indicators[symbol]['{alias}_returns'].append(daily_ret)")
                lines.append(f"                buf = self.indicators[symbol]['{alias}_returns']")
                lines.append(f"                if len(buf) > {period}: buf.pop(0)")
                lines.append(f"                if len(buf) >= 2:")
                lines.append(f"                    import statistics")
                lines.append(f"                    self.indicators[symbol]['{alias}'] = statistics.stdev(buf)")
                lines.append(f"                else:")
                lines.append(f"                    self.indicators[symbol]['{alias}'] = 0")
                lines.append(f"            else:")
                lines.append(f"                self.indicators[symbol]['{alias}'] = 0")

            elif ind.id == "change":
                lines.append(f"            # change 전일대비 등락률 계산")
                lines.append(f"            self.indicators[symbol]['{alias}'] = ((price - prev_price) / prev_price * 100) if prev_price > 0 else 0")

            elif ind.id == "returns":
                lines.append(f"            # returns N일 수익률 계산")
                lines.append(f"            {alias}_roc_val = self.indicators[symbol]['{alias}_roc'].Current.Value")
                lines.append(f"            self.indicators[symbol]['{alias}'] = {alias}_roc_val * 100")

        if custom_indicators:
            lines.append("")
        
        # 조건에서 사용되는 모든 지표+output 조합 수집
        all_outputs = self._collect_all_indicator_outputs()
        
        for alias, output in all_outputs:
            # 변수명: alias + output (예: macd_value, macd_signal)
            # alias에 괄호 등 특수문자가 있을 수 있으므로 Python 식별자로 정규화
            raw_var = f"{alias}_{output}" if output != "value" else alias
            var_name = self._sanitize_var_name(raw_var)

            # 이미 생성된 변수 건너뛰기
            if var_name in generated_values:
                continue
            generated_values.add(var_name)

            # alias로 지표 ID 찾기
            ind_schema = self._indicator_map.get(alias)
            if ind_schema is None:
                # 지표 맵에 없으면 alias를 ID로 사용
                indicator_id = alias
            else:
                indicator_id = ind_schema.id

            # 커스텀 지표는 저장된 값 직접 사용
            if indicator_id in ("consecutive", "disparity", "volatility_ind", "change", "returns"):
                lines.append(f"            {var_name} = self.indicators[symbol]['{alias}']")
                continue

            # 지표 정보 가져오기
            indicator_info = get_indicator_info(indicator_id)
            if indicator_info is None:
                lines.append(f"            {var_name} = self.indicators[symbol]['{alias}'].Current.Value")
                continue

            # 출력값 템플릿
            if indicator_info.outputs and output in indicator_info.outputs:
                value_template = indicator_info.outputs[output]
            elif indicator_info.value_template:
                value_template = indicator_info.value_template
            else:
                value_template = "{name}.Current.Value"

            value_code = value_template.replace("{name}", f"self.indicators[symbol]['{alias}']")
            lines.append(f"            {var_name} = {value_code}")
        
        return "\n".join(lines)
    
    def _generate_prev_update(self) -> str:
        """이전값 업데이트 코드 생성
        
        조건에서 사용되는 모든 지표+output 조합에 대해 이전값 업데이트.
        """
        lines = ["            self.prev_values[symbol]['price'] = price"]
        generated_values = set()
        
        # 조건에서 사용되는 모든 지표+output 조합 수집
        all_outputs = self._collect_all_indicator_outputs()
        
        for alias, output in all_outputs:
            raw_var = f"{alias}_{output}" if output != "value" else alias
            var_name = self._sanitize_var_name(raw_var)

            if var_name in generated_values:
                continue
            generated_values.add(var_name)

            lines.append(f"            self.prev_values[symbol]['{var_name}'] = {var_name}")

        return "\n".join(lines)
    
    def _generate_condition(
        self,
        condition: Union[ConditionSchema, CompositeConditionSchema],
        name: str,
    ) -> str:
        """조건 코드 생성 - 스키마 기반
        
        ConditionSchema/CompositeConditionSchema를 직접 사용합니다.
        """
        if isinstance(condition, CompositeConditionSchema):
            return self._generate_composite_condition(condition, name)
        
        # 단일 조건
        return self._generate_single_condition(condition, name)
    
    def _generate_single_condition(self, cond: ConditionSchema, name: str) -> str:
        """단일 조건 코드 생성"""
        # 캔들스틱 조건 처리
        if cond.is_candlestick_condition():
            return self._generate_candlestick_condition(cond, name)

        if cond.operator == OperatorType.CROSS_ABOVE:
            return self._generate_cross_above(cond, name)
        elif cond.operator == OperatorType.CROSS_BELOW:
            return self._generate_cross_below(cond, name)
        else:
            return self._generate_comparison(cond, name)

    def _generate_candlestick_condition(self, cond: ConditionSchema, name: str) -> str:
        """캔들스틱 조건 코드 생성

        캔들스틱 신호:
        - bullish: signal > 0 (상승 패턴)
        - bearish: signal < 0 (하락 패턴)
        - detected: signal != 0 (패턴 감지됨)
        """
        alias = cond.candlestick
        signal_type = cond.signal or "detected"

        signal_var = f"{alias}_signal"

        if signal_type == "bullish":
            return f"            {name}_signal = {signal_var} > 0  # 캔들스틱 상승 신호"
        elif signal_type == "bearish":
            return f"            {name}_signal = {signal_var} < 0  # 캔들스틱 하락 신호"
        else:  # detected
            return f"            {name}_signal = {signal_var} != 0  # 캔들스틱 패턴 감지"
    
    def _generate_cross_above(self, cond: ConditionSchema, name: str) -> str:
        """상향 돌파 조건 - 스키마 기반"""
        left_code, left_var = self._get_indicator_code(cond.indicator, cond.indicator_output)
        
        if cond.value is not None:
            # 숫자와 비교 (예: RSI crosses_above 30)
            threshold = cond.value
            return f'''            # {name}: 상향 돌파 ({cond.indicator} crosses above {threshold})
            prev_{left_var} = self.prev_values[symbol].get('{left_var}', 0)
            {name}_signal = prev_{left_var} <= {threshold} and {left_code} > {threshold}'''
        else:
            # 지표끼리 비교
            right_code, right_var = self._get_indicator_code(cond.compare_to, cond.compare_output)
            return f'''            # {name}: 상향 돌파 ({cond.indicator} crosses above {cond.compare_to})
            prev_{left_var} = self.prev_values[symbol].get('{left_var}', 0)
            prev_{right_var} = self.prev_values[symbol].get('{right_var}', 0)
            {name}_signal = prev_{left_var} <= prev_{right_var} and {left_code} > {right_code}'''
    
    def _generate_cross_below(self, cond: ConditionSchema, name: str) -> str:
        """하향 돌파 조건 - 스키마 기반"""
        left_code, left_var = self._get_indicator_code(cond.indicator, cond.indicator_output)
        
        if cond.value is not None:
            threshold = cond.value
            return f'''            # {name}: 하향 돌파 ({cond.indicator} crosses below {threshold})
            prev_{left_var} = self.prev_values[symbol].get('{left_var}', 0)
            {name}_signal = prev_{left_var} >= {threshold} and {left_code} < {threshold}'''
        else:
            right_code, right_var = self._get_indicator_code(cond.compare_to, cond.compare_output)
            return f'''            # {name}: 하향 돌파 ({cond.indicator} crosses below {cond.compare_to})
            prev_{left_var} = self.prev_values[symbol].get('{left_var}', 0)
            prev_{right_var} = self.prev_values[symbol].get('{right_var}', 0)
            {name}_signal = prev_{left_var} >= prev_{right_var} and {left_code} < {right_code}'''
    
    def _generate_comparison(self, cond: ConditionSchema, name: str) -> str:
        """비교 조건 - 스키마 기반 (ScaledIndicator 지원)"""
        left_code, _ = self._get_indicator_code(cond.indicator, cond.indicator_output)
        
        if cond.value is not None:
            right_code = str(cond.value)
        elif cond.compare_to is not None:
            right_code, _ = self._get_indicator_code(cond.compare_to, cond.compare_output)
            
            if cond.compare_scalar is not None:
                op = cond.compare_operation or "mul"
                if op == "mul":
                    right_code = f"({right_code} * {cond.compare_scalar})"
                elif op == "div":
                    right_code = f"({right_code} / {cond.compare_scalar})"
                elif op == "add":
                    right_code = f"({right_code} + {cond.compare_scalar})"
                elif op == "sub":
                    right_code = f"({right_code} - {cond.compare_scalar})"
        else:
            right_code = "0"
        
        op_map = {
            OperatorType.GREATER_THAN: ">",
            OperatorType.LESS_THAN: "<",
            OperatorType.GREATER_EQUAL: ">=",
            OperatorType.LESS_EQUAL: "<=",
            OperatorType.EQUAL: "==",
            OperatorType.NOT_EQUAL: "!=",
            OperatorType.BREAKS: ">",
        }
        op = op_map.get(cond.operator, ">")
        
        return f"            {name}_signal = {left_code} {op} {right_code}"
    
    def _generate_composite_condition(
        self,
        cond: CompositeConditionSchema,
        name: str,
    ) -> str:
        """복합 조건 - 스키마 기반"""
        if not cond.conditions:
            return f"            {name}_signal = True"
        
        lines = []
        sub_signals = []
        
        for i, sub_cond in enumerate(cond.conditions):
            sub_name = f"{name}_sub_{i}"
            lines.append(self._generate_condition(sub_cond, sub_name))
            sub_signals.append(f"{sub_name}_signal")
        
        logic_op = " and " if cond.logic == "AND" else " or "
        combined = logic_op.join(sub_signals)
        lines.append(f"            {name}_signal = {combined}")
        
        return "\n".join(lines)
    
    def _get_indicator_code(
        self,
        alias: Optional[str],
        output: str = "value",
    ) -> tuple[str, str]:
        """지표 alias와 output으로 Lean 코드 생성
        
        Returns:
            (code, var_name) - Lean 코드와 변수명
        
        Examples:
            ("close", "value") → ("price", "price")
            ("macd", "value") → ("macd_value", "macd")
            ("macd", "signal") → ("macd_signal", "macd_signal")
            ("bb", "lower") → ("bb_lower", "bb_lower")
        """
        if alias is None:
            return "price", "price"
        
        # 가격 필드 처리
        if alias in PRICE_FIELDS or alias == "price":
            if alias == "close" or alias == "price":
                return "price", "price"
            elif alias == "open":
                return "bar.Open", "open"
            elif alias == "high":
                return "bar.High", "high"
            elif alias == "low":
                return "bar.Low", "low"
            elif alias == "volume":
                return "bar.Volume", "volume"
        
        # 지표 처리 - output 고려
        # alias에 괄호 등 특수문자가 있을 수 있으므로 Python 식별자로 정규화
        raw_var = f"{alias}_{output}" if output != "value" else alias
        var_name = self._sanitize_var_name(raw_var)

        return var_name, var_name
    
    def _generate_risk_management(self) -> tuple:
        """리스크 관리 코드 생성"""
        risk = self.schema.risk
        if risk is None:
            return "", "", ""
        
        init_lines = []
        check_lines = []
        update_lines = []
        
        if risk.stop_loss_pct is not None:
            sl_pct = risk.stop_loss_pct
            init_lines.append("        self.entry_prices = {}")
            update_lines.append("                self.entry_prices[symbol] = price")
            check_lines.append(f'''
            # 손절 체크 ({sl_pct}%)
            if symbol in self.entry_prices and holdings > 0:
                loss_pct = (price - self.entry_prices[symbol]) / self.entry_prices[symbol] * 100
                if loss_pct <= -{sl_pct}:
                    exit_signal = True''')
        
        if risk.take_profit_pct is not None:
            tp_pct = risk.take_profit_pct
            if "self.entry_prices = {}" not in init_lines:
                init_lines.append("        self.entry_prices = {}")
            if "self.entry_prices[symbol] = price" not in update_lines:
                update_lines.append("                self.entry_prices[symbol] = price")
            check_lines.append(f'''
            # 익절 체크 ({tp_pct}%)
            if symbol in self.entry_prices and holdings > 0:
                profit_pct = (price - self.entry_prices[symbol]) / self.entry_prices[symbol] * 100
                if profit_pct >= {tp_pct}:
                    exit_signal = True''')
        
        if risk.trailing_stop_pct is not None:
            ts_pct = risk.trailing_stop_pct
            init_lines.append("        self.high_prices = {}")
            update_lines.append("                self.high_prices[symbol] = price")
            check_lines.append(f'''
            # 트레일링 스탑 체크 ({ts_pct}%)
            if symbol in self.high_prices and holdings > 0:
                self.high_prices[symbol] = max(self.high_prices[symbol], price)
                drawdown_pct = (price - self.high_prices[symbol]) / self.high_prices[symbol] * 100
                if drawdown_pct <= -{ts_pct}:
                    exit_signal = True''')
        
        init_str = "\n".join(init_lines) if init_lines else ""
        check_str = "".join(check_lines) if check_lines else ""
        update_str = "\n".join(update_lines) if update_lines else ""
        
        return init_str, check_str, update_str
    
    def save(self, output_path: Path) -> None:
        """코드를 파일로 저장
        
        Args:
            output_path: 저장 경로
        """
        raise NotImplementedError("Use generate() with symbols, start_date, end_date parameters")
