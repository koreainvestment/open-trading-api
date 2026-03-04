"""Risk Management settings.

Defines stop loss, take profit, trailing stop configurations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class RiskManagement:
    """리스크 관리 설정
    
    손절, 익절, 트레일링 스탑 등 리스크 관리 옵션.
    
    Attributes:
        stop_loss_pct: 손절 비율 (%)
        take_profit_pct: 익절 비율 (%)
        trailing_stop_pct: 트레일링 스탑 비율 (%)
        max_position_pct: 최대 포지션 비중 (0.0 ~ 1.0)
    
    Example:
        risk = RiskManagement(
            stop_loss_pct=5.0,      # 5% 손절
            take_profit_pct=10.0,   # 10% 익절
            trailing_stop_pct=3.0,  # 3% 트레일링 스탑
        )
    """
    stop_loss_pct: Optional[float] = None
    take_profit_pct: Optional[float] = None
    trailing_stop_pct: Optional[float] = None
    max_position_pct: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """선언적 정의로 변환"""
        return {
            "stop_loss": {
                "enabled": self.stop_loss_pct is not None,
                "percent": self.stop_loss_pct or 0,
            },
            "take_profit": {
                "enabled": self.take_profit_pct is not None,
                "percent": self.take_profit_pct or 0,
            },
            "trailing_stop": {
                "enabled": self.trailing_stop_pct is not None,
                "percent": self.trailing_stop_pct or 0,
            },
            "max_position_pct": self.max_position_pct,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> RiskManagement:
        """딕셔너리에서 생성"""
        stop_loss = data.get("stop_loss", {})
        take_profit = data.get("take_profit", {})
        trailing_stop = data.get("trailing_stop", {})
        
        return cls(
            stop_loss_pct=stop_loss.get("percent") if stop_loss.get("enabled") else None,
            take_profit_pct=take_profit.get("percent") if take_profit.get("enabled") else None,
            trailing_stop_pct=trailing_stop.get("percent") if trailing_stop.get("enabled") else None,
            max_position_pct=data.get("max_position_pct", 1.0),
        )
    
    def is_empty(self) -> bool:
        """리스크 관리 설정이 없는지 확인"""
        return (
            self.stop_loss_pct is None
            and self.take_profit_pct is None
            and self.trailing_stop_pct is None
        )
