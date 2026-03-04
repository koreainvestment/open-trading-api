"""
Strategy 07: 강한 종가 (Strong Close)

매수 조건: 당일 종가가 당일 고가의 N% 이상 위치
매도 조건: 없음

Note:
    장마감 후(15:30 이후) 실행 권장
    - 장중에는 고가/저가/종가가 확정되지 않아 신호가 부정확할 수 있음
"""

from core import data_fetcher, indicators
from core.signal import Action, Signal
from strategy.base_strategy import BaseStrategy


class StrongCloseStrategy(BaseStrategy):
    """강한 종가 전략 (장마감 후 실행 권장)"""

    def __init__(self, min_close_ratio: float = 0.8):
        """
        Args:
            min_close_ratio: 최소 종가 위치 비율 (0~1, 기본: 0.8 = 80%)
                - 0.8 = 종가가 (고가-저가) 범위의 상위 80% 이상에 위치
        """
        self.min_close_ratio = min_close_ratio

    @property
    def name(self) -> str:
        return "강한 종가"

    @property
    def required_days(self) -> int:
        return 5

    def generate_signal(self, stock_code: str, stock_name: str) -> Signal:
        """
        강한 종가 시그널 생성

        당일 봉에서 종가가 고가에 가까울수록 매수세가 강했음을 의미
        """
        df = data_fetcher.get_daily_prices(stock_code, self.required_days)

        if df.empty or len(df) < 1:
            return Signal(
                stock_code=stock_code,
                stock_name=stock_name,
                action=Action.HOLD,
                strength=0.0,
                reason="데이터 부족"
            )

        close_ratio = indicators.calc_strong_close_ratio(df)

        if close_ratio is None:
            return Signal(
                stock_code=stock_code,
                stock_name=stock_name,
                action=Action.HOLD,
                strength=0.0,
                reason="지표 계산 실패"
            )

        if close_ratio >= self.min_close_ratio:
            # 비율이 높을수록 강도 증가 (0.8 → 0.7, 1.0 → 0.9)
            strength = min(1.0, 0.5 + close_ratio * 0.4)
            return Signal(
                stock_code=stock_code,
                stock_name=stock_name,
                action=Action.BUY,
                strength=strength,
                reason=f"강한 종가 비율 {close_ratio*100:.0f}% (고가 근처 마감)"
            )

        return Signal(
            stock_code=stock_code,
            stock_name=stock_name,
            action=Action.HOLD,
            strength=0.0,
            reason=f"종가 위치 {close_ratio*100:.0f}% (기준: {self.min_close_ratio*100:.0f}%)"
        )

