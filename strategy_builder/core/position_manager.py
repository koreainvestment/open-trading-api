"""
포지션 관리 모듈

Applied Skills: skills/investment-strategy-framework.md
- 현재 보유 포지션 조회
- 중복 주문 방지
"""

import logging
from typing import Optional

import pandas as pd

from core import data_fetcher

logging.basicConfig(level=logging.INFO)


class PositionManager:
    """
    보유 포지션 관리 클래스
    """

    def __init__(self, env_dv: str = "real"):
        """
        Args:
            env_dv: 환경 구분 (real/demo)
        """
        self.env_dv = env_dv
        self._holdings_cache: Optional[pd.DataFrame] = None

    def get_positions(self, refresh: bool = False) -> pd.DataFrame:
        """
        현재 보유 종목 목록 조회

        Args:
            refresh: 캐시 무시하고 새로 조회

        Returns:
            DataFrame with columns:
            - stock_code: 종목코드
            - stock_name: 종목명
            - quantity: 보유수량
            - avg_price: 평균단가
            - current_price: 현재가
            - eval_amount: 평가금액
            - profit_loss: 평가손익
            - profit_rate: 수익률
        """
        if self._holdings_cache is None or refresh:
            self._holdings_cache = data_fetcher.get_holdings(self.env_dv)

        return self._holdings_cache

    def check_duplicate(self, stock_code: str) -> bool:
        """
        해당 종목 보유 여부 확인

        Args:
            stock_code: 종목코드

        Returns:
            True if already holding
        """
        holdings = self.get_positions()

        if holdings.empty:
            return False

        return stock_code in holdings["stock_code"].values

    def get_position(self, stock_code: str) -> Optional[dict]:
        """
        특정 종목의 포지션 정보 조회

        Args:
            stock_code: 종목코드

        Returns:
            포지션 정보 dict 또는 None
        """
        holdings = self.get_positions()

        if holdings.empty:
            return None

        position = holdings[holdings["stock_code"] == stock_code]

        if position.empty:
            return None

        return position.iloc[0].to_dict()

    def get_holding_quantity(self, stock_code: str) -> int:
        """
        특정 종목의 보유수량 조회

        Args:
            stock_code: 종목코드

        Returns:
            보유수량 (미보유 시 0)
        """
        position = self.get_position(stock_code)

        if position is None:
            return 0

        return int(position.get("quantity", 0))

    def get_avg_price(self, stock_code: str) -> Optional[int]:
        """
        특정 종목의 평균단가 조회

        Args:
            stock_code: 종목코드

        Returns:
            평균단가 (미보유 시 None)
        """
        position = self.get_position(stock_code)

        if position is None:
            return None

        return int(position.get("avg_price", 0))

    def refresh(self) -> None:
        """캐시 갱신"""
        self._holdings_cache = None
        self.get_positions(refresh=True)

