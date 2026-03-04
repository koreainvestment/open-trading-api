"""Parameter Resolver for $param_name bindings.

$param_name 참조를 실제 값으로 치환하는 유틸리티 클래스.

Usage:
    params = {
        "period": {"default": 14, "min": 2, "max": 100},
        "threshold": {"default": 30, "min": 0, "max": 50}
    }

    # 단일 값 치환
    value = ParamResolver.resolve("$period", params)  # → 14

    # 딕셔너리 치환
    indicator_params = {"period": "$period"}
    resolved = ParamResolver.resolve(indicator_params, params)  # → {"period": 14}

    # 오버라이드 적용
    resolved = ParamResolver.resolve("$period", params, {"period": 21})  # → 21
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Union


class ParamResolver:
    """$param_name 참조를 실제 값으로 치환하는 유틸리티 클래스."""

    # $param_name 패턴 (전체 문자열이 $로 시작하는 파라미터 참조인 경우)
    PATTERN = re.compile(r'^\$([a-zA-Z_][a-zA-Z0-9_]*)$')

    @classmethod
    def resolve(
        cls,
        value: Any,
        params: Dict[str, Union[Dict[str, Any], Any]],
        overrides: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """단일 값 또는 구조 전체의 $param_name 참조를 치환.

        Args:
            value: 치환할 값 (문자열, 딕셔너리, 리스트, 또는 기본값)
            params: 파라미터 정의 딕셔너리
                    {"period": {"default": 14, ...}} 또는 {"period": 14}
            overrides: 오버라이드 값 딕셔너리 (선택)

        Returns:
            치환된 값

        Raises:
            ValueError: 알 수 없는 파라미터 참조

        Example:
            >>> params = {"period": {"default": 14}}
            >>> ParamResolver.resolve("$period", params)
            14
            >>> ParamResolver.resolve("$period", params, {"period": 21})
            21
        """
        overrides = overrides or {}

        if isinstance(value, str):
            match = cls.PATTERN.match(value)
            if match:
                name = match.group(1)
                # 오버라이드 우선
                if name in overrides:
                    return overrides[name]
                # params에서 조회
                if name in params:
                    param_def = params[name]
                    # 딕셔너리 형태 {"default": ..., "min": ...}
                    if isinstance(param_def, dict):
                        return param_def.get("default")
                    # 직접 값
                    return param_def
                raise ValueError(f"Unknown param reference: ${name}")
            # $로 시작하지 않는 일반 문자열
            return value

        if isinstance(value, dict):
            return {k: cls.resolve(v, params, overrides) for k, v in value.items()}

        if isinstance(value, list):
            return [cls.resolve(v, params, overrides) for v in value]

        # 숫자, None 등 기본 타입은 그대로 반환
        return value

    @classmethod
    def resolve_indicators(
        cls,
        indicators: List[Dict[str, Any]],
        params: Dict[str, Union[Dict[str, Any], Any]],
        overrides: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """모든 indicator params의 $param_name 참조를 치환.

        Args:
            indicators: 지표 정의 리스트
            params: 파라미터 정의 딕셔너리
            overrides: 오버라이드 값 딕셔너리 (선택)

        Returns:
            치환된 지표 정의 리스트

        Example:
            >>> indicators = [{"id": "rsi", "params": {"period": "$period"}}]
            >>> params = {"period": {"default": 14}}
            >>> ParamResolver.resolve_indicators(indicators, params)
            [{"id": "rsi", "params": {"period": 14}}]
        """
        result = []
        for ind in indicators:
            new_ind = dict(ind)
            if "params" in ind:
                new_ind["params"] = cls.resolve(ind["params"], params, overrides)
            result.append(new_ind)
        return result

    @classmethod
    def resolve_conditions(
        cls,
        conditions: List[Dict[str, Any]],
        params: Dict[str, Union[Dict[str, Any], Any]],
        overrides: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """조건의 value 필드 등에서 $param_name 참조를 치환.

        Args:
            conditions: 조건 정의 리스트
            params: 파라미터 정의 딕셔너리
            overrides: 오버라이드 값 딕셔너리 (선택)

        Returns:
            치환된 조건 정의 리스트

        Example:
            >>> conditions = [{"indicator": "rsi", "operator": "cross_above", "value": "$oversold"}]
            >>> params = {"oversold": {"default": 30}}
            >>> ParamResolver.resolve_conditions(conditions, params)
            [{"indicator": "rsi", "operator": "cross_above", "value": 30}]
        """
        result = []
        for cond in conditions:
            new_cond = dict(cond)
            # value 필드 치환
            if "value" in cond and cond["value"] is not None:
                new_cond["value"] = cls.resolve(cond["value"], params, overrides)
            # compare_to 필드도 치환 (지표 alias 또는 숫자)
            if "compare_to" in cond and cond["compare_to"] is not None:
                resolved = cls.resolve(cond["compare_to"], params, overrides)
                new_cond["compare_to"] = resolved
            result.append(new_cond)
        return result

    @classmethod
    def extract_param_refs(cls, value: Any) -> List[str]:
        """값에서 모든 $param_name 참조를 추출.

        Args:
            value: 검사할 값

        Returns:
            파라미터 이름 리스트 ($ 제외)

        Example:
            >>> ParamResolver.extract_param_refs({"a": "$foo", "b": "$bar"})
            ["foo", "bar"]
        """
        refs = []

        if isinstance(value, str):
            match = cls.PATTERN.match(value)
            if match:
                refs.append(match.group(1))
        elif isinstance(value, dict):
            for v in value.values():
                refs.extend(cls.extract_param_refs(v))
        elif isinstance(value, list):
            for v in value:
                refs.extend(cls.extract_param_refs(v))

        return refs

    @classmethod
    def validate_refs(
        cls,
        value: Any,
        params: Dict[str, Any],
        context: str = "",
    ) -> List[str]:
        """값의 모든 $param_name 참조가 유효한지 검증.

        Args:
            value: 검사할 값
            params: 파라미터 정의 딕셔너리
            context: 에러 메시지용 컨텍스트

        Returns:
            에러 메시지 리스트 (빈 리스트면 유효)

        Example:
            >>> params = {"period": {"default": 14}}
            >>> ParamResolver.validate_refs("$unknown", params)
            ["Unknown param reference: $unknown"]
        """
        errors = []
        available = set(params.keys())

        def check(v: Any, ctx: str) -> None:
            if isinstance(v, str):
                match = cls.PATTERN.match(v)
                if match:
                    name = match.group(1)
                    if name not in available:
                        err_ctx = f"{ctx}: " if ctx else ""
                        errors.append(f"{err_ctx}Unknown param reference: ${name}")
            elif isinstance(v, dict):
                for k, sub_v in v.items():
                    check(sub_v, f"{ctx}.{k}" if ctx else k)
            elif isinstance(v, list):
                for i, sub_v in enumerate(v):
                    check(sub_v, f"{ctx}[{i}]" if ctx else f"[{i}]")

        check(value, context)
        return errors
