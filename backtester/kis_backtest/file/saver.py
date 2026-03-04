"""Strategy File Saver.

StrategyDefinition을 .kis.yaml 파일로 저장합니다.
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Union

import yaml

from kis_backtest.file.schema import KisStrategyFile
from kis_backtest.core.strategy import StrategyDefinition

logger = logging.getLogger(__name__)


class StrategyFileSaver:
    """전략 파일 저장기
    
    StrategyDefinition 또는 KisStrategyFile을 .kis.yaml 파일로 저장합니다.
    
    Example:
        # StrategyDefinition에서 저장
        saver = StrategyFileSaver()
        saver.save_definition(definition, "my_strategy.kis.yaml")
        
        # KisStrategyFile에서 저장
        saver.save(strategy_file, "my_strategy.kis.yaml")
        
        # 문자열로 변환
        yaml_str = saver.to_yaml_string(definition)
    """
    
    @staticmethod
    def save(
        strategy_file: KisStrategyFile,
        path: Union[str, Path],
        update_timestamp: bool = True,
    ) -> Path:
        """KisStrategyFile을 YAML 파일로 저장
        
        Args:
            strategy_file: 저장할 전략 파일
            path: 저장 경로
            update_timestamp: True이면 updated_at 갱신
        
        Returns:
            저장된 파일 경로
        """
        path = Path(path)
        
        # .kis.yaml 확장자 보장
        if not path.name.endswith(".kis.yaml"):
            if path.suffix in (".yaml", ".yml"):
                path = path.with_suffix(".kis.yaml")
            else:
                path = Path(str(path) + ".kis.yaml")
        
        # 딕셔너리로 변환 (원본 mutation 방지)
        data = strategy_file.model_dump(exclude_none=True)

        # 타임스탬프 갱신 (딕셔너리에서만 수정, 원본 객체 보존)
        if update_timestamp:
            now_iso = datetime.now().isoformat()
            data.setdefault("metadata", {})
            data["metadata"]["updated_at"] = now_iso
            if not data["metadata"].get("created_at"):
                data["metadata"]["created_at"] = now_iso
        else:
            # datetime을 ISO 문자열로 변환
            if data.get("metadata", {}).get("created_at"):
                created = strategy_file.metadata.created_at
                if created:
                    data["metadata"]["created_at"] = created.isoformat()
            if data.get("metadata", {}).get("updated_at"):
                updated = strategy_file.metadata.updated_at
                if updated:
                    data["metadata"]["updated_at"] = updated.isoformat()
        
        # 부모 디렉토리 생성
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # YAML로 저장
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(
                data,
                f,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False,
                indent=2,
            )
        
        logger.info(f"Strategy saved to {path}")
        return path
    
    @staticmethod
    def save_definition(
        definition: StrategyDefinition,
        path: Union[str, Path],
        author: str = "user",
        tags: list[str] = None,
    ) -> Path:
        """StrategyDefinition을 YAML 파일로 저장
        
        Args:
            definition: 저장할 전략 정의
            path: 저장 경로
            author: 작성자
            tags: 태그 목록
        
        Returns:
            저장된 파일 경로
        """
        # KisStrategyFile로 변환 (새 객체이므로 mutation OK)
        strategy_file = KisStrategyFile.from_strategy_definition(definition)

        # 메타데이터가 다르면 새 객체로 교체
        metadata_updates = {}
        if author != strategy_file.metadata.author:
            metadata_updates["author"] = author
        if tags:
            metadata_updates["tags"] = tags
        if metadata_updates:
            strategy_file = strategy_file.model_copy(
                update={"metadata": strategy_file.metadata.model_copy(update=metadata_updates)}
            )

        return StrategyFileSaver.save(strategy_file, path)
    
    @staticmethod
    def to_yaml_string(
        obj: Union[StrategyDefinition, KisStrategyFile]
    ) -> str:
        """YAML 문자열로 변환
        
        Args:
            obj: StrategyDefinition 또는 KisStrategyFile
        
        Returns:
            YAML 문자열
        """
        if isinstance(obj, StrategyDefinition):
            strategy_file = KisStrategyFile.from_strategy_definition(obj)
        else:
            strategy_file = obj
        
        data = strategy_file.model_dump(exclude_none=True)
        
        # datetime을 ISO 문자열로 변환
        if data.get("metadata", {}).get("created_at"):
            if strategy_file.metadata.created_at:
                data["metadata"]["created_at"] = strategy_file.metadata.created_at.isoformat()
        if data.get("metadata", {}).get("updated_at"):
            if strategy_file.metadata.updated_at:
                data["metadata"]["updated_at"] = strategy_file.metadata.updated_at.isoformat()
        
        return yaml.dump(
            data,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
            indent=2,
        )
