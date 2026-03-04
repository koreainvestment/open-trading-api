"""
Strategy 10: 추세 필터 (Trend Filter)

매수 조건: 종가 > MA(60) AND 전일 대비 상승
매도 조건: 종가 < MA(60) AND 전일 대비 하락
"""

from core import data_fetcher, indicators
from core.signal import Action, Signal
from strategy.base_strategy import BaseStrategy


class TrendFilterStrategy(BaseStrategy):
    """추세 필터 전략"""

    def __init__(self, ma_period: int = 60):
        """
        Args:
            ma_period: 추세 판단 이동평균 기간 (기본: 60일)
        """
        self.ma_period = ma_period

    @property
    def name(self) -> str:
        return "추세 필터"

    @property
    def required_days(self) -> int:
        return self.ma_period + 10

    def generate_signal(self, stock_code: str, stock_name: str) -> Signal:
        """
        추세 필터 시그널 생성
        """
        df = data_fetcher.get_daily_prices(stock_code, self.required_days)

        if df.empty or len(df) < self.ma_period:
            return Signal(
                stock_code=stock_code,
                stock_name=stock_name,
                action=Action.HOLD,
                strength=0.0,
                reason="데이터 부족"
            )

        ma = indicators.calc_ma(df, self.ma_period)
        current_close = indicators.get_latest_close(df)
        prev_close = indicators.get_prev_close(df)
        ma_value = ma.iloc[-1]

        if current_close is None or prev_close is None:
            return Signal(
                stock_code=stock_code,
                stock_name=stock_name,
                action=Action.HOLD,
                strength=0.0,
                reason="지표 계산 실패"
            )

        above_ma = current_close > ma_value
        daily_up = current_close > prev_close

        # 매수: MA 위 + 상승
        if above_ma and daily_up:
            return Signal(
                stock_code=stock_code,
                stock_name=stock_name,
                action=Action.BUY,
                strength=0.65,
                reason=f"추세 상승: MA{self.ma_period}({ma_value:,.0f}) 위 + 상승"
            )

        # 매도: MA 아래 + 하락
        if not above_ma and not daily_up:
            return Signal(
                stock_code=stock_code,
                stock_name=stock_name,
                action=Action.SELL,
                strength=0.65,
                reason=f"추세 하락: MA{self.ma_period}({ma_value:,.0f}) 아래 + 하락"
            )

        return Signal(
            stock_code=stock_code,
            stock_name=stock_name,
            action=Action.HOLD,
            strength=0.0,
            reason="추세 조건 미충족"
        )

