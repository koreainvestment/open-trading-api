"""
Strategy 01: 골든크로스 (Golden Cross)

매수 조건: MA(5) > MA(20) 상향 돌파 (전일: MA5 < MA20, 당일: MA5 > MA20)
매도 조건: MA(5) < MA(20) 하향 돌파 (데드크로스)
"""

from core import data_fetcher, indicators
from core.signal import Action, Signal
from strategy.base_strategy import BaseStrategy


class GoldenCrossStrategy(BaseStrategy):
    """골든크로스 전략"""

    def __init__(self, short_period: int = 5, long_period: int = 20):
        """
        Args:
            short_period: 단기 이동평균 기간 (기본: 5)
            long_period: 장기 이동평균 기간 (기본: 20)
        """
        self.short_period = short_period
        self.long_period = long_period

    @property
    def name(self) -> str:
        return "골든크로스"

    @property
    def required_days(self) -> int:
        return self.long_period + 10

    def generate_signal(self, stock_code: str, stock_name: str) -> Signal:
        """
        골든크로스/데드크로스 시그널 생성
        """
        # 데이터 조회
        df = data_fetcher.get_daily_prices(stock_code, self.required_days)

        if df.empty or len(df) < self.long_period + 1:
            return Signal(
                stock_code=stock_code,
                stock_name=stock_name,
                action=Action.HOLD,
                strength=0.0,
                reason="데이터 부족"
            )

        # 이동평균 계산
        ma_short = indicators.calc_ma(df, self.short_period)
        ma_long = indicators.calc_ma(df, self.long_period)

        # 전일/당일 값
        prev_short = ma_short.iloc[-2]
        curr_short = ma_short.iloc[-1]
        prev_long = ma_long.iloc[-2]
        curr_long = ma_long.iloc[-1]

        # 골든크로스: 전일 단기 < 장기, 당일 단기 > 장기
        if prev_short < prev_long and curr_short > curr_long:
            return Signal(
                stock_code=stock_code,
                stock_name=stock_name,
                action=Action.BUY,
                strength=0.7,
                reason=f"골든크로스 발생 (MA{self.short_period} > MA{self.long_period})"
            )

        # 데드크로스: 전일 단기 > 장기, 당일 단기 < 장기
        if prev_short > prev_long and curr_short < curr_long:
            return Signal(
                stock_code=stock_code,
                stock_name=stock_name,
                action=Action.SELL,
                strength=0.7,
                reason=f"데드크로스 발생 (MA{self.short_period} < MA{self.long_period})"
            )

        return Signal(
            stock_code=stock_code,
            stock_name=stock_name,
            action=Action.HOLD,
            strength=0.0,
            reason="크로스 조건 미충족"
        )

