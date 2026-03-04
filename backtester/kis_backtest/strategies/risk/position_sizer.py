"""포지션 사이징 모듈

다양한 포지션 사이징 방법을 Lean 코드로 변환.
"""

from enum import Enum
from typing import Any, Dict


class SizingMethod(str, Enum):
    """포지션 사이징 방법"""
    EQUAL_WEIGHT = "equal_weight"      # 동일 비중
    ATR_BASED = "atr_based"            # ATR 기반 변동성 조절
    KELLY = "kelly"                    # 켈리 공식
    INVERSE_VOLATILITY = "inverse_volatility"  # 변동성 역비례
    FIXED_FRACTION = "fixed_fraction"  # 고정 비율


class PositionSizer:
    """포지션 사이징 코드 생성기
    
    사용 예:
        sizer = PositionSizer(
            method=SizingMethod.ATR_BASED,
            params={"risk_per_trade": 0.02, "atr_multiplier": 2.0}
        )
        
        init_code = sizer.generate_init()
        sizing_code = sizer.generate_sizing()
    """
    
    def __init__(
        self,
        method: SizingMethod = SizingMethod.EQUAL_WEIGHT,
        params: Dict[str, Any] = None,
    ):
        self.method = method
        self.params = params or {}
    
    def generate_init(self) -> str:
        """Initialize() 내부 초기화 코드 생성"""
        if self.method == SizingMethod.EQUAL_WEIGHT:
            return ""
        
        elif self.method == SizingMethod.ATR_BASED:
            return """
        # ATR 기반 포지션 사이징
        self.atr_indicators = {}
        for symbol in self.symbols:
            atr = AverageTrueRange(14, MovingAverageType.Simple)
            self.RegisterIndicator(symbol, atr, Resolution.Daily)
            self.atr_indicators[symbol] = atr
"""
        
        elif self.method == SizingMethod.INVERSE_VOLATILITY:
            return """
        # 변동성 역비례 포지션 사이징
        self.volatility_windows = {}
        for symbol in self.symbols:
            self.volatility_windows[symbol] = RollingWindow[float](20)
"""
        
        elif self.method == SizingMethod.FIXED_FRACTION:
            fraction = self.params.get("fraction", 0.1)
            return f"""
        # 고정 비율 포지션 사이징
        self.fixed_fraction = {fraction}
"""
        
        else:
            return ""
    
    def generate_sizing(self) -> str:
        """포지션 사이즈 계산 코드 생성"""
        if self.method == SizingMethod.EQUAL_WEIGHT:
            return "weight = 1.0 / len(self.symbols)"
        
        elif self.method == SizingMethod.ATR_BASED:
            risk_per_trade = self.params.get("risk_per_trade", 0.02)
            atr_mult = self.params.get("atr_multiplier", 2.0)
            return f'''# ATR 기반 사이징
            atr = self.atr_indicators[symbol]
            if atr.IsReady and atr.Current.Value > 0:
                # 리스크 금액 = 자본금 * 거래당 리스크
                risk_amount = self.Portfolio.TotalPortfolioValue * {risk_per_trade}
                # 1주당 리스크 = ATR * 배수
                per_share_risk = atr.Current.Value * {atr_mult}
                # 주문 수량 = 리스크 금액 / 1주당 리스크
                target_shares = int(risk_amount / per_share_risk)
                weight = (target_shares * price) / self.Portfolio.TotalPortfolioValue
                weight = min(weight, 1.0 / len(self.symbols))  # 최대 동일 비중
            else:
                weight = 1.0 / len(self.symbols)'''
        
        elif self.method == SizingMethod.INVERSE_VOLATILITY:
            lookback = self.params.get("lookback", 20)
            return f'''# 변동성 역비례 사이징
            if len(self.volatility_windows[symbol]) >= {lookback}:
                prices = [self.volatility_windows[symbol][i] for i in range({lookback})]
                mean = sum(prices) / len(prices)
                if mean > 0:
                    variance = sum((p - mean) ** 2 for p in prices) / len(prices)
                    std = variance ** 0.5
                    volatility = std / mean  # 변동성 비율
                    
                    # 모든 종목의 역변동성 합계 계산
                    inv_vol_sum = 0
                    for s in self.symbols:
                        if len(self.volatility_windows[s]) >= {lookback}:
                            s_prices = [self.volatility_windows[s][i] for i in range({lookback})]
                            s_mean = sum(s_prices) / len(s_prices)
                            if s_mean > 0:
                                s_var = sum((p - s_mean) ** 2 for p in s_prices) / len(s_prices)
                                s_std = s_var ** 0.5
                                inv_vol_sum += 1 / (s_std / s_mean + 0.001)
                    
                    weight = (1 / (volatility + 0.001)) / max(inv_vol_sum, 1)
                else:
                    weight = 1.0 / len(self.symbols)
            else:
                weight = 1.0 / len(self.symbols)'''
        
        elif self.method == SizingMethod.KELLY:
            # 단순화된 켈리 (실제 계산은 승률/손익비 필요)
            return '''# 켈리 공식 (단순화)
            # 실제 구현 시 과거 거래 데이터 필요
            win_rate = 0.5  # 예상 승률
            win_loss_ratio = 1.5  # 예상 손익비
            kelly_fraction = win_rate - (1 - win_rate) / win_loss_ratio
            kelly_fraction = max(0, min(kelly_fraction, 0.25))  # 0~25% 제한
            weight = kelly_fraction'''
        
        elif self.method == SizingMethod.FIXED_FRACTION:
            return "weight = self.fixed_fraction"
        
        else:
            return "weight = 1.0 / len(self.symbols)"
    
    def generate_update(self) -> str:
        """OnData() 내부 업데이트 코드 생성"""
        if self.method == SizingMethod.INVERSE_VOLATILITY:
            return "            self.volatility_windows[symbol].Add(price)"
        return ""


