"""
리스크 관리 모듈

Applied Skills: skills/investment-strategy-framework.md
- 손절/익절 조건 체크
- 일일 손실 한도 체크
- 시그널 검증
"""

import logging

from core.signal import Action, Signal

logging.basicConfig(level=logging.INFO)


class RiskManager:
    """
    리스크 관리 클래스
    """

    def __init__(
        self,
        stop_loss_pct: float = -5.0,
        take_profit_pct: float = 10.0,
        max_position_pct: float = 20.0,
        daily_loss_limit: int = 100000
    ):
        """
        Args:
            stop_loss_pct: 손절 기준 (%, 예: -5.0)
            take_profit_pct: 익절 기준 (%, 예: 10.0)
            max_position_pct: 최대 포지션 비중 (%)
            daily_loss_limit: 일일 손실 한도 (원)
        """
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct
        self.max_position_pct = max_position_pct
        self.daily_loss_limit = daily_loss_limit

        self._daily_loss: int = 0

    def check_stop_loss(
        self,
        current_price: int,
        avg_price: int
    ) -> bool:
        """
        손절 조건 체크

        Args:
            current_price: 현재가
            avg_price: 평균단가

        Returns:
            True if stop loss triggered
        """
        if avg_price <= 0:
            return False

        profit_rate = (current_price - avg_price) / avg_price * 100

        return profit_rate <= self.stop_loss_pct

    def check_take_profit(
        self,
        current_price: int,
        avg_price: int
    ) -> bool:
        """
        익절 조건 체크

        Args:
            current_price: 현재가
            avg_price: 평균단가

        Returns:
            True if take profit triggered
        """
        if avg_price <= 0:
            return False

        profit_rate = (current_price - avg_price) / avg_price * 100

        return profit_rate >= self.take_profit_pct

    def check_daily_limit(self, loss_amount: int) -> bool:
        """
        일일 손실 한도 체크

        Args:
            loss_amount: 추가 손실 예상 금액

        Returns:
            True if within limit (주문 가능)
        """
        return (self._daily_loss + abs(loss_amount)) <= self.daily_loss_limit

    def add_daily_loss(self, amount: int) -> None:
        """
        일일 손실 누적

        Args:
            amount: 손실 금액 (양수)
        """
        self._daily_loss += abs(amount)

    def reset_daily_loss(self) -> None:
        """일일 손실 초기화 (매일 장 시작 시)"""
        self._daily_loss = 0

    def get_profit_rate(self, current_price: int, avg_price: int) -> float:
        """
        수익률 계산

        Args:
            current_price: 현재가
            avg_price: 평균단가

        Returns:
            수익률 (%)
        """
        if avg_price <= 0:
            return 0.0

        return (current_price - avg_price) / avg_price * 100

    def validate_buy_signal(
        self,
        signal: Signal,
        current_price: int,
        total_asset: int
    ) -> Signal:
        """
        매수 시그널 검증

        Args:
            signal: 원본 시그널
            current_price: 현재가
            total_asset: 총 자산

        Returns:
            검증된 시그널 (위반 시 HOLD로 변경)
        """
        if signal.action != Action.BUY:
            return signal

        # 포지션 비중 체크
        if signal.quantity and current_price > 0:
            position_value = signal.quantity * current_price
            position_pct = position_value / total_asset * 100 if total_asset > 0 else 100

            if position_pct > self.max_position_pct:
                logging.warning(
                    f"포지션 비중 초과: {position_pct:.1f}% > {self.max_position_pct}%"
                )
                return Signal(
                    stock_code=signal.stock_code,
                    stock_name=signal.stock_name,
                    action=Action.HOLD,
                    strength=0.0,
                    reason=f"리스크 초과: 포지션 비중 {position_pct:.1f}%"
                )

        return signal

    def validate_sell_signal(
        self,
        signal: Signal,
        current_price: int,
        avg_price: int
    ) -> Signal:
        """
        매도 시그널 검증

        skill: SELL 유지 (손절은 항상 허용)

        Args:
            signal: 원본 시그널
            current_price: 현재가
            avg_price: 평균단가

        Returns:
            검증된 시그널
        """
        if signal.action != Action.SELL:
            return signal

        # 손절 시그널은 강도 높임
        if self.check_stop_loss(current_price, avg_price):
            return Signal(
                stock_code=signal.stock_code,
                stock_name=signal.stock_name,
                action=Action.SELL,
                strength=1.0,  # 시장가 주문
                reason=f"손절 ({self.get_profit_rate(current_price, avg_price):.1f}%)"
            )

        return signal

