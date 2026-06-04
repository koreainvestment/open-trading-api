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

        if self.logger:
            self.logger.info("Buy order request: %s", body)

        return self.client.post(
            path=PATH_ORDER_CASH,
            tr_id=TR_ID_BUY,
            data=body,
        )

    # 지정가 매도 주문
    def sell_limit(self, symbol: str, quantity: int, price: int) -> Dict[str, Any]:
        body = self._build_order_body(
            symbol=symbol,
            quantity=quantity,
            price=price,
            is_sell=True,
        )

        if self.logger:
            self.logger.info("Sell order request: %s", body)

        return self.client.post(
            path=PATH_ORDER_CASH,
            tr_id=TR_ID_SELL,
            data=body,
        )

    def _build_order_body(
        self,
        symbol: str,
        quantity: int,
        price: int,
        is_sell: bool,
    ) -> Dict[str, str]:
        return {
            "CANO": CANO, # 계좌번호 앞부분
            "ACNT_PRDT_CD": ACNT_PRDT_CD, # 계좌상품코드
            "PDNO": symbol, # 종목코드
            "ORD_DVSN": "00", # 주문구분, 00은 지정가
            "ORD_QTY": str(quantity), # 주문수량
            "ORD_UNPR": str(price), # 주문가격
            "EXCG_ID_DVSN_CD": "KRX",
            "SLL_TYPE": "01" if is_sell else "",
            "CNDT_PRIC": "",
        }
