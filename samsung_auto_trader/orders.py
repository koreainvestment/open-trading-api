# 매수/매도 주문 전송

from typing import Any, Dict

from config import (
    ACNT_PRDT_CD,
    CANO,
    PATH_ORDER_CASH,
    TR_ID_BUY,
    TR_ID_SELL,
)


class OrderService:
    def __init__(self, client, logger=None) -> None:
        self.client = client
        self.logger = logger

    # 지정가 매수 주문
    def buy_limit(self, symbol: str, quantity: int, price: int) -> Dict[str, Any]:
        body = self._build_order_body(
            symbol=symbol,
            quantity=quantity,
            price=price,
            is_sell=False,
        )


        result = self.client.post(
            path=PATH_ORDER_CASH,
            tr_id=TR_ID_BUY,
            data=body,
        )


        return result

    # 지정가 매도 주문
    def sell_limit(self, symbol: str, quantity: int, price: int) -> Dict[str, Any]:
        body = self._build_order_body(
            symbol=symbol,
            quantity=quantity,
            price=price,
            is_sell=True,
        )


        result = self.client.post(
            path=PATH_ORDER_CASH,
            tr_id=TR_ID_SELL,
            data=body,
        )

        return result

    def _build_order_body(
        self,
        symbol: str,
        quantity: int,
        price: int,
        is_sell: bool,
    ) -> Dict[str, str]:
        return {
            "CANO": CANO,
            "ACNT_PRDT_CD": ACNT_PRDT_CD,
            "PDNO": symbol,
            "ORD_DVSN": "00",       # 00: 지정가
            "ORD_QTY": str(quantity),
            "ORD_UNPR": str(price),
        }
