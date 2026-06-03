from typing import Any, Dict

from config import (
    ACNT_PRDT_CD,
    CANO,
    PATH_ORDER_CASH,
    TR_ID_BUY_DEMO,
    TR_ID_SELL_DEMO,
)


class OrderService:
    def __init__(self, client, logger=None) -> None:
        self.client = client
        self.logger = logger

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
            tr_id=TR_ID_BUY_DEMO,
            data=body,
        )

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
            tr_id=TR_ID_SELL_DEMO,
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
            "CANO": CANO,
            "ACNT_PRDT_CD": ACNT_PRDT_CD,
            "PDNO": symbol,
            "ORD_DVSN": "00",
            "ORD_QTY": str(quantity),
            "ORD_UNPR": str(price),
            "EXCG_ID_DVSN_CD": "KRX",
            "SLL_TYPE": "01" if is_sell else "",
            "CNDT_PRIC": "",
        }
