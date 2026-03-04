"""
Strategy 05: 이격도 (Disparity)

매수 조건: 이격도 < 90 (과매도)
매도 조건: 이격도 > 110 (과매수)
"""

from core import data_fetcher, indicators
from core.signal import Action, Signal
from strategy.base_strategy import BaseStrategy


class DisparityStrategy(BaseStrategy):
    """이격도 전략"""

    def __init__(
        self,
        period: int = 20,
        oversold_threshold: float = 90.0,
        overbought_threshold: float = 110.0
    ):
        """
        Args:
            period: 이동평균 기간 (기본: 20)
            oversold_threshold: 과매도 기준 (기본: 90)
            overbought_threshold: 과매수 기준 (기본: 110)
        """
        self.period = period
        self.oversold_threshold = oversold_threshold
        self.overbought_threshold = overbought_threshold

    @property
    def name(self) -> str:
        return "이격도"

    @property
    def required_days(self) -> int:
        return self.period + 10

    def generate_signal(self, stock_code: str, stock_name: str) -> Signal:
        """
        이격도 기반 시그널 생성
        """
        df = data_fetcher.get_daily_prices(stock_code, self.required_days)

        if df.empty or len(df) < self.period:
            return Signal(
                stock_code=stock_code,
                stock_name=stock_name,
                action=Action.HOLD,
                strength=0.0,
                reason="데이터 부족"
            )

        disparity = indicators.calc_disparity(df, self.period)
        current_disparity = disparity.iloc[-1]

        # 과매도
        if current_disparity < self.oversold_threshold:
            strength = min(1.0, (self.oversold_threshold - current_disparity) / 20 + 0.5)
            return Signal(
                stock_code=stock_code,
                stock_name=stock_name,
                action=Action.BUY,
                strength=strength,
                reason=f"이격도 {current_disparity:.1f} (과매도)"
            )

        # 과매수
        if current_disparity > self.overbought_threshold:
            strength = min(1.0, (current_disparity - self.overbought_threshold) / 20 + 0.5)
            return Signal(
                stock_code=stock_code,
                stock_name=stock_name,
                action=Action.SELL,
                strength=strength,
                reason=f"이격도 {current_disparity:.1f} (과매수)"
            )

        return Signal(
            stock_code=stock_code,
            stock_name=stock_name,
            action=Action.HOLD,
            strength=0.0,
            reason=f"이격도 {current_disparity:.1f} (중립)"
        )

