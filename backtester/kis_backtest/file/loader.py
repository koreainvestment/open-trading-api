"""Strategy File Loader.

.kis.yaml 파일을 로드하고 검증합니다.

"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional, Union

import yaml

from kis_backtest.file.schema import KisStrategyFile
from kis_backtest.core.strategy import StrategyDefinition

if TYPE_CHECKING:
    from kis_backtest.core.schema import StrategySchema

logger = logging.getLogger(__name__)

# 가격 예약어 (지표가 아닌 가격 데이터)
PRICE_FIELDS = frozenset({"close", "open", "high", "low", "volume", "price"})


class StrategyFileLoader:
    """전략 파일 로더
    
    .kis.yaml 파일을 로드하여 KisStrategyFile 또는 StrategyDefinition으로 변환합니다.
    
    Example:
        # 파일에서 로드
        loader = StrategyFileLoader()
        strategy_file = loader.load("my_strategy.kis.yaml")
        
        # StrategyDefinition으로 변환
        definition = strategy_file.to_strategy_definition()
        
        # 또는 직접 로드
        definition = loader.load_as_definition("my_strategy.kis.yaml")
    """
    
    @staticmethod
    def load(path: Union[str, Path]) -> KisStrategyFile:
        """YAML 파일 로드
        
        Args:
            path: 파일 경로 (.kis.yaml)
        
        Returns:
            KisStrategyFile 객체
        
        Raises:
            FileNotFoundError: 파일이 없는 경우
            ValueError: YAML 파싱 또는 검증 실패
        """
        path = Path(path)
        
        if not path.exists():
            raise FileNotFoundError(f"Strategy file not found: {path}")
        
        if not path.suffix.endswith(".yaml") and not path.suffix.endswith(".yml"):
            logger.warning(f"File extension is not .yaml or .yml: {path}")
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML format: {e}")
        
        if not data:
            raise ValueError(f"Empty strategy file: {path}")
        
        try:
            return KisStrategyFile.model_validate(data)
        except Exception as e:
            raise ValueError(f"Invalid strategy file format: {e}")
    
    @staticmethod
    def load_as_definition(path: Union[str, Path]) -> StrategyDefinition:
        """YAML 파일을 StrategyDefinition으로 로드
        
        Args:
            path: 파일 경로
        
        Returns:
            StrategyDefinition 객체
        """
        strategy_file = StrategyFileLoader.load(path)
        return strategy_file.to_strategy_definition()
    
    @staticmethod
    def load_as_schema(path: Union[str, Path]) -> "StrategySchema":
        """YAML 파일을 StrategySchema로 로드 (권장)
        
        Args:
            path: 파일 경로
        
        Returns:
            StrategySchema 객체
        """
        from kis_backtest.core.converters import from_yaml_file
        strategy_file = StrategyFileLoader.load(path)
        return from_yaml_file(strategy_file)
    
    @staticmethod
    def load_schema_from_string(content: str) -> "StrategySchema":
        """YAML 문자열에서 StrategySchema 로드 (권장)

        Args:
            content: YAML 문자열

        Returns:
            StrategySchema 객체
        """
        from kis_backtest.core.converters import from_yaml_file
        strategy_file = StrategyFileLoader.load_from_string(content)
        return from_yaml_file(strategy_file)

    @staticmethod
    def load_schema_with_params(
        path_or_content: Union[str, Path],
        param_overrides: Optional[Dict[str, Any]] = None,
    ) -> "StrategySchema":
        """YAML → StrategySchema (param 오버라이드 포함)

        파일 경로 또는 YAML 문자열에서 StrategySchema를 로드하고,
        $param_name 참조를 param_overrides 값으로 치환합니다.

        Args:
            path_or_content: 파일 경로 또는 YAML 문자열
            param_overrides: 파라미터 오버라이드 값 (선택)

        Returns:
            StrategySchema 객체

        Example:
            # 파일에서 로드
            schema = StrategyFileLoader.load_schema_with_params(
                "my_strategy.kis.yaml",
                param_overrides={"period": 21, "oversold": 25}
            )

            # 문자열에서 로드
            schema = StrategyFileLoader.load_schema_with_params(
                yaml_content,
                param_overrides={"period": 21}
            )
        """
        from kis_backtest.core.converters import from_yaml_file

        # 파일 경로 vs 문자열 판별
        if isinstance(path_or_content, Path):
            strategy_file = StrategyFileLoader.load(path_or_content)
        elif isinstance(path_or_content, str):
            # 파일 경로인지 YAML 문자열인지 판별
            # version: 으로 시작하면 YAML 문자열로 간주
            if path_or_content.strip().startswith("version"):
                strategy_file = StrategyFileLoader.load_from_string(path_or_content)
            else:
                # 파일 경로로 시도
                path = Path(path_or_content)
                try:
                    path_exists = path.exists()
                except OSError:
                    # 경로가 너무 길면 YAML 문자열로 간주
                    path_exists = False
                if path_exists:
                    strategy_file = StrategyFileLoader.load(path)
                else:
                    # 파일이 없으면 YAML 문자열로 간주
                    strategy_file = StrategyFileLoader.load_from_string(path_or_content)
        else:
            raise ValueError(f"Invalid path_or_content type: {type(path_or_content)}")

        return from_yaml_file(strategy_file, param_overrides=param_overrides)
    
    @staticmethod
    def load_from_string(content: str) -> KisStrategyFile:
        """YAML 문자열에서 로드
        
        Args:
            content: YAML 문자열
        
        Returns:
            KisStrategyFile 객체
        """
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML format: {e}")
        
        if not data:
            raise ValueError("Empty strategy content")
        
        try:
            return KisStrategyFile.model_validate(data)
        except Exception as e:
            raise ValueError(f"Invalid strategy format: {e}")
    
    @staticmethod
    def _validate_strategy_file(strategy_file: KisStrategyFile) -> list[str]:
        """KisStrategyFile 객체 공통 검증 로직."""
        errors = []

        if not strategy_file.strategy.indicators:
            errors.append("No indicators defined")

        if not strategy_file.strategy.entry.conditions:
            errors.append("No entry conditions defined")

        if not strategy_file.strategy.exit.conditions:
            errors.append("No exit conditions defined")

        indicator_aliases = {
            ind.alias or ind.id for ind in strategy_file.strategy.indicators
        }
        valid_aliases = indicator_aliases | PRICE_FIELDS

        for cond in strategy_file.strategy.entry.conditions:
            if cond.indicator and cond.indicator not in valid_aliases:
                errors.append(f"Unknown indicator alias in entry: {cond.indicator}")
            if isinstance(cond.compare_to, str) and cond.compare_to not in valid_aliases:
                errors.append(f"Unknown compare_to alias in entry: {cond.compare_to}")

        for cond in strategy_file.strategy.exit.conditions:
            if cond.indicator and cond.indicator not in valid_aliases:
                errors.append(f"Unknown indicator alias in exit: {cond.indicator}")
            if isinstance(cond.compare_to, str) and cond.compare_to not in valid_aliases:
                errors.append(f"Unknown compare_to alias in exit: {cond.compare_to}")

        return errors

    @staticmethod
    def validate(path: Union[str, Path]) -> list[str]:
        """전략 파일 검증

        Args:
            path: 파일 경로

        Returns:
            오류 메시지 목록 (빈 리스트면 유효)
        """
        try:
            strategy_file = StrategyFileLoader.load(path)
        except (FileNotFoundError, ValueError) as e:
            return [str(e)]

        return StrategyFileLoader._validate_strategy_file(strategy_file)

    @staticmethod
    def validate_content(content: str) -> list[str]:
        """YAML 문자열 검증.

        Args:
            content: .kis.yaml 포맷 문자열

        Returns:
            오류 메시지 목록 (빈 리스트면 유효)
        """
        try:
            strategy_file = StrategyFileLoader.load_from_string(content)
        except ValueError as e:
            return [str(e)]

        return StrategyFileLoader._validate_strategy_file(strategy_file)
