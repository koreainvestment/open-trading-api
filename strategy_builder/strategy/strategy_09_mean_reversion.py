"""
Strategy 09: 평균회귀 (Mean Reversion)

매수 조건: N일 평균 대비 -M% 이하
매도 조건: N일 평균 대비 +M% 이상
"""

from core import data_fetcher, indicators
from core.signal import Action, Signal
from strategy.base_strategy import BaseStrategy


class MeanReversionStrategy(BaseStrategy):
    """평균회귀 전략"""

    def __init__(
        self,
        period: int = 5,
        buy_threshold: float = -3.0,
        sell_threshold: float = 3.0
    ):
        """
        Args:
            period: 이동평균 기간 (기본: 5일)
            buy_threshold: 매수 이탈 기준 (%, 기본: -3%)
            sell_threshold: 매도 이탈 기준 (%, 기본: +3%)
        """
        self.period = period
        self.buy_threshold = buy_threshold
        self.sell_threshold = sell_threshold

    @property
    def name(self) -> str:
        return "평균회귀"

    @property
    def required_days(self) -> int:
        return self.period + 5

    def generate_signal(self, stock_code: str, stock_name: str) -> Signal:
        """
        평균회귀 시그널 생성
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

        ma = indicators.calc_ma(df, self.period)
        current_close = indicators.get_latest_close(df)
        ma_value = ma.iloc[-1]

        if current_close is None or ma_value == 0:
            return Signal(
                stock_code=stock_code,
                stock_name=stock_name,
                action=Action.HOLD,
                strength=0.0,
                reason="지표 계산 실패"
            )

        deviation = (current_close - ma_value) / ma_value * 100

        # 매수: 평균 대비 하락
        if deviation <= self.buy_threshold:
            strength = min(1.0, 0.5 + abs(deviation) / 10)
            return Signal(
                stock_code=stock_code,
                stock_name=stock_name,
                action=Action.BUY,
                strength=strength,
                reason=f"평균 대비 {deviation:.1f}% 이탈 (매수)"
            )

        # 매도: 평균 대비 상승
        if deviation >= self.sell_threshold:
            strength = min(1.0, 0.5 + deviation / 10)
            return Signal(
                stock_code=stock_code,
                stock_name=stock_name,
                action=Action.SELL,
                strength=strength,
                reason=f"평균 대비 +{deviation:.1f}% 이탈 (매도)"
            )

        return Signal(
            stock_code=stock_code,
            stock_name=stock_name,
            action=Action.HOLD,
            strength=0.0,
            reason=f"평균 대비 {deviation:.1f}% (중립)"
        )

