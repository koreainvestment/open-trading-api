"""Indicator Parameter Validator.

Lean에서 지표가 정확히 동작하도록 파라미터를 검증합니다.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from kis_backtest.core.indicator import INDICATOR_REGISTRY, IndicatorInfo
from kis_backtest.core.candlestick import CANDLESTICK_REGISTRY


@dataclass
class ValidationError:
    """검증 에러"""
    indicator_id: str
    param_name: str
    message: str
    expected: Any = None
    actual: Any = None


@dataclass
class ValidationResult:
    """검증 결과"""
    is_valid: bool
    errors: List[ValidationError]
    warnings: List[str]
    
    def raise_if_invalid(self) -> None:
        """에러가 있으면 예외 발생"""
        if not self.is_valid:
            error_msgs = [
                f"{e.indicator_id}.{e.param_name}: {e.message}"
                for e in self.errors
            ]
            raise ValueError(f"지표 파라미터 검증 실패:\n" + "\n".join(error_msgs))


class IndicatorValidator:
    """지표 파라미터 검증기
    
    Lean 호환성을 위한 파라미터 검증:
    1. 필수 파라미터 존재 여부
    2. 파라미터 타입 검증
    3. 파라미터 값 범위 검증
    """
    
    # 파라미터별 검증 규칙
    PARAM_RULES: Dict[str, Dict[str, Any]] = {
        "period": {
            "type": int,
            "min": 1,
            "max": 1000,
            "description": "기간 (1~1000)",
        },
        "fast": {
            "type": int,
            "min": 1,
            "max": 500,
            "description": "빠른 기간 (1~500)",
        },
        "slow": {
            "type": int,
            "min": 1,
            "max": 500,
            "description": "느린 기간 (1~500)",
        },
        "signal": {
            "type": int,
            "min": 1,
            "max": 100,
            "description": "시그널 기간 (1~100)",
        },
        "k_period": {
            "type": int,
            "min": 1,
            "max": 100,
            "description": "%K 기간 (1~100)",
        },
        "d_period": {
            "type": int,
            "min": 1,
            "max": 100,
            "description": "%D 기간 (1~100)",
        },
        "std": {
            "type": float,
            "min": 0.1,
            "max": 10.0,
            "description": "표준편차 배수 (0.1~10.0)",
        },
        "multiplier": {
            "type": float,
            "min": 0.1,
            "max": 10.0,
            "description": "배수 (0.1~10.0)",
        },
        "direction": {
            "type": str,
            "allowed": ["up", "down"],
            "description": "방향 (up 또는 down)",
        },
    }
    
    # Lean 특수 규칙 (2026-01-30 테스트 결과 반영)
    LEAN_SPECIAL_RULES: Dict[str, Dict[str, Any]] = {
        "aroon": {
            # AroonOscillator(upPeriod, downPeriod) - 두 파라미터 필요
            "params": ["up_period", "down_period"],
            "init_template": "AroonOscillator({up_period}, {down_period})",
            "warning": "AroonOscillator는 up_period와 down_period 두 파라미터가 필요합니다.",
        },
        "stochastic": {
            # Stochastic(k_period, slowing, d_period)
            "params": ["k_period", "d_period"],
            "init_template": "Stochastic({k_period}, 1, {d_period})",
            "warning": "Stochastic은 slowing=1이 기본값입니다.",
        },
        "ichimoku": {
            # IchimokuKinkoHyo(tenkan, kijun, senkou_a, senkou_b, chikou)
            "params": ["tenkan", "kijun", "senkou_b"],
            "init_template": "IchimokuKinkoHyo({tenkan}, {kijun}, {kijun}, {senkou_b}, {kijun})",
            "warning": "Ichimoku는 5개 파라미터가 필요하며, senkou_a=kijun, chikou=kijun로 기본 설정됩니다.",
        },
        "supertrend": {
            # SuperTrend(period, multiplier, MovingAverageType)
            "params": ["period", "multiplier"],
            "init_template": "SuperTrend({period}, {multiplier}, MovingAverageType.Wilders)",
            "warning": "SuperTrend은 MovingAverageType.Wilders를 사용합니다.",
        },
        "consecutive": {
            # 커스텀 지표 - 연속 상승/하락 일수
            "params": ["direction"],
            "init_template": "0",  # 단순 카운터로 초기화
            "warning": "consecutive는 커스텀 로직이 필요합니다. direction='up' 또는 'down'.",
            "is_custom": True,
        },
        "disparity": {
            "params": ["period"],
            "init_template": "SimpleMovingAverage({period})",
            "warning": "disparity는 SMA 기반 커스텀 계산입니다.",
            "is_custom": True,
        },
        "volatility_ind": {
            "params": ["period"],
            "init_template": "StandardDeviation({period})",
            "warning": "volatility_ind는 일간 수익률 기반 커스텀 계산입니다.",
            "is_custom": True,
        },
        "change": {
            "params": [],
            "init_template": "0",
            "warning": "change는 전일대비 등락률 커스텀 계산입니다.",
            "is_custom": True,
        },
        "returns": {
            "params": ["period"],
            "init_template": "RateOfChangePercent({period})",
            "warning": "returns는 RateOfChangePercent 기반입니다.",
            "is_custom": True,
        },
    }
    
    @classmethod
    def validate(
        cls,
        indicator_id: str,
        params: Dict[str, Any],
    ) -> ValidationResult:
        """지표 파라미터 검증
        
        Args:
            indicator_id: 지표 ID
            params: 파라미터 딕셔너리
        
        Returns:
            ValidationResult
        """
        errors: List[ValidationError] = []
        warnings: List[str] = []
        
        # 1. 지표 존재 확인
        indicator_info = INDICATOR_REGISTRY.get(indicator_id)
        is_candlestick = indicator_id in CANDLESTICK_REGISTRY

        if indicator_info is None and not is_candlestick:
            # 지원하지 않는 지표
            errors.append(ValidationError(
                indicator_id=indicator_id,
                param_name="",
                message=f"지원하지 않는 지표입니다. 지원 지표: {list(INDICATOR_REGISTRY.keys())}",
            ))
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings)

        # 캔들스틱 패턴은 파라미터 없이 유효
        if is_candlestick:
            return ValidationResult(is_valid=True, errors=[], warnings=[])
        
        # 2. 필수 파라미터 확인
        required_params = indicator_info.params
        for param_name in required_params:
            if param_name not in params:
                errors.append(ValidationError(
                    indicator_id=indicator_id,
                    param_name=param_name,
                    message=f"필수 파라미터 '{param_name}'이(가) 없습니다.",
                ))
        
        # 3. 파라미터 타입 및 범위 검증
        for param_name, param_value in params.items():
            if param_name in cls.PARAM_RULES:
                rule = cls.PARAM_RULES[param_name]
                
                # 타입 검증
                expected_type = rule["type"]
                if not isinstance(param_value, (expected_type, int if expected_type == float else type(None))):
                    errors.append(ValidationError(
                        indicator_id=indicator_id,
                        param_name=param_name,
                        message=f"타입 오류: {expected_type.__name__} 예상, {type(param_value).__name__} 받음",
                        expected=expected_type.__name__,
                        actual=type(param_value).__name__,
                    ))
                    continue
                
                # 범위 검증
                min_val = rule.get("min")
                max_val = rule.get("max")
                
                if min_val is not None and param_value < min_val:
                    errors.append(ValidationError(
                        indicator_id=indicator_id,
                        param_name=param_name,
                        message=f"값이 너무 작습니다. 최소: {min_val}",
                        expected=f">= {min_val}",
                        actual=param_value,
                    ))
                
                if max_val is not None and param_value > max_val:
                    errors.append(ValidationError(
                        indicator_id=indicator_id,
                        param_name=param_name,
                        message=f"값이 너무 큽니다. 최대: {max_val}",
                        expected=f"<= {max_val}",
                        actual=param_value,
                    ))
                
                # 허용값 검증 (string 타입용)
                allowed = rule.get("allowed")
                if allowed is not None and param_value not in allowed:
                    errors.append(ValidationError(
                        indicator_id=indicator_id,
                        param_name=param_name,
                        message=f"허용되지 않는 값: {param_value}. 허용값: {allowed}",
                        expected=str(allowed),
                        actual=param_value,
                    ))
        
        # 4. Lean 특수 규칙 경고
        if indicator_id in cls.LEAN_SPECIAL_RULES:
            rule = cls.LEAN_SPECIAL_RULES[indicator_id]
            if "warning" in rule:
                warnings.append(rule["warning"])
        
        # 5. MACD fast < slow 검증
        if indicator_id == "macd":
            fast = params.get("fast", 12)
            slow = params.get("slow", 26)
            if fast >= slow:
                errors.append(ValidationError(
                    indicator_id=indicator_id,
                    param_name="fast",
                    message=f"fast({fast})는 slow({slow})보다 작아야 합니다.",
                    expected=f"fast < slow",
                    actual=f"fast={fast}, slow={slow}",
                ))
        
        is_valid = len(errors) == 0
        return ValidationResult(is_valid=is_valid, errors=errors, warnings=warnings)
    
    @classmethod
    def get_lean_init_code(
        cls,
        indicator_id: str,
        params: Dict[str, Any],
        name: str = "indicator",
    ) -> Tuple[str, int]:
        """Lean 초기화 코드 생성
        
        Args:
            indicator_id: 지표 ID
            params: 파라미터
            name: 변수명
        
        Returns:
            (초기화 코드, warmup 기간)
        """
        # 검증
        result = cls.validate(indicator_id, params)
        result.raise_if_invalid()
        
        # 특수 규칙 확인
        if indicator_id in cls.LEAN_SPECIAL_RULES:
            rule = cls.LEAN_SPECIAL_RULES[indicator_id]
            template = rule["init_template"]
            init_code = f"{name} = {template.format(**params)}"
        else:
            # 기본 템플릿 사용
            indicator_info = INDICATOR_REGISTRY[indicator_id]
            init_code = indicator_info.init_template.format(name=name, **params)
        
        # Warmup 기간 계산
        warmup = cls._calculate_warmup(indicator_id, params)
        
        return init_code, warmup
    
    @classmethod
    def _calculate_warmup(cls, indicator_id: str, params: Dict[str, Any]) -> int:
        """Warmup 기간 계산"""
        if indicator_id in ["sma", "ema", "rsi", "atr", "cci", "momentum", "roc", "williams_r", "maximum", "minimum", "donchian"]:
            return params.get("period", 14) + 1
        elif indicator_id == "macd":
            return params.get("slow", 26) + params.get("signal", 9)
        elif indicator_id == "bollinger":
            return params.get("period", 20) + 1
        elif indicator_id == "stochastic":
            return params.get("k_period", 14) + params.get("d_period", 3)
        elif indicator_id == "adx":
            return params.get("period", 14) * 2
        elif indicator_id == "supertrend":
            return params.get("period", 10) + 1
        elif indicator_id == "keltner":
            return params.get("period", 20) + 1
        elif indicator_id == "aroon":
            return max(params.get("up_period", 25), params.get("down_period", 25)) + 1
        elif indicator_id == "ichimoku":
            return params.get("senkou_b", 52) + params.get("kijun", 26)
        elif indicator_id == "consecutive":
            return 2  # 연속 카운터는 최소 2일 필요
        else:
            return 30  # 기본값

    @classmethod
    def validate_output(cls, indicator_id: str, output: str) -> bool:
        """지표의 output 필드 존재 여부 확인

        Args:
            indicator_id: 지표 ID
            output: 출력 필드명 (value, signal, upper, lower, ...)

        Returns:
            True if output is valid for the indicator
        """
        indicator_info = INDICATOR_REGISTRY.get(indicator_id)
        if indicator_info is None:
            return False

        # 기본 output은 "value"
        if output == "value":
            return True

        # 멀티 아웃풋 지표인 경우 outputs 딕셔너리 확인
        if indicator_info.outputs:
            return output in indicator_info.outputs

        return False

    @classmethod
    def requires_tradebar(cls, indicator_id: str) -> bool:
        """지표가 TradeBar 업데이트를 필요로 하는지 확인

        Args:
            indicator_id: 지표 ID

        Returns:
            True if indicator requires TradeBar.Update() instead of Update(DateTime, decimal)
        """
        indicator_info = INDICATOR_REGISTRY.get(indicator_id)
        if indicator_info is None:
            return False

        return indicator_info.requires_tradebar

    @classmethod
    def get_candlestick_init_code(
        cls,
        pattern_id: str,
        alias: str,
    ) -> Tuple[str, int]:
        """캔들스틱 패턴 초기화 코드 생성

        Args:
            pattern_id: 패턴 ID (marubozu, doji, engulfing, ...)
            alias: 변수명

        Returns:
            (초기화 코드, warmup 기간)

        Note:
            캔들스틱 패턴은 Lean의 CandlestickPatterns 네임스페이스를 사용합니다.
            패턴은 TradeBar로 업데이트하며, Current.Value로 신호를 읽습니다.
            - +1: 상승 신호 (bullish)
            - -1: 하락 신호 (bearish)
            - 0: 신호 없음
        """
        pattern_info = CANDLESTICK_REGISTRY.get(pattern_id)
        if pattern_info is None:
            raise ValueError(f"Unknown candlestick pattern: {pattern_id}")

        if pattern_info.lean_unsupported:
            raise ValueError(
                f"캔들스틱 패턴 '{pattern_id}' ({pattern_info.lean_class})은(는) "
                f"현재 Lean 버전에서 지원하지 않습니다. "
                f"{pattern_info.description}"
            )

        lean_class = pattern_info.lean_class
        candle_count = pattern_info.candle_count

        # Lean 초기화 코드 생성
        # CandlestickPatterns.ClassName()은 QCAlgorithm 헬퍼 메서드 (symbol 필요)
        # ClassName()은 직접 클래스 생성자 (이름만 필요)
        # 직접 클래스 생성자 사용 (from QuantConnect.Indicators.CandlestickPatterns import ClassName)
        init_code = f'{alias} = {lean_class}("{alias}")'

        # Warmup: 캔들 수 + 여유분
        warmup = candle_count + 5

        return init_code, warmup
