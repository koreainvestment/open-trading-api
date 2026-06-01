from __future__ import annotations

from dataclasses import dataclass
from typing import Any

try:
    from .api_client import KISApiClient
except ImportError:  # pragma: no cover
    from api_client import KISApiClient


@dataclass(frozen=True)
class OrderResult:
    side: str
    symbol: str
    quantity: int
    price: int
    accepted: bool
    order_no: str | None
    raw: dict[str, Any]


class OrderService:
    def __init__(self, client: KISApiClient, logger, account_number: str, account_product_code: str) -> None:
        self.client = client
        self.logger = logger
        self.account_number = account_number
        self.account_product_code = account_product_code

    def place_limit_order(self, side: str, symbol: str, quantity: int, price: int) -> OrderResult:
        side = side.lower().strip()
        if side not in {"buy", "sell"}:
            raise ValueError("side must be 'buy' or 'sell'")

        tr_id = "VTTC0012U" if side == "buy" else "VTTC0011U"
        payload = {
            "CANO": self.account_number,
            "ACNT_PRDT_CD": self.account_product_code,
            "PDNO": symbol,
            "ORD_DVSN": "00",
            "ORD_QTY": str(quantity),
            "ORD_UNPR": str(price),
            "EXCG_ID_DVSN_CD": "KRX",
            "SLL_TYPE": "01",
            "CNDT_PRIC": "",
        }

        self.logger.info(
            "%s order request: symbol=%s quantity=%s price=%s",
            side,
            symbol,
            quantity,
            f"{price:,}",
        )
        response = self.client.post(
            "/uapi/domestic-stock/v1/trading/order-cash",
            tr_id=tr_id,
            body=payload,
            use_hashkey=True,
        )

        output = response.get("output", {}) if isinstance(response.get("output", {}), dict) else {}
        order_no = str(output.get("odno") or output.get("ORD_NO") or output.get("order_no") or "").strip() or None
        result = OrderResult(
            side=side,
            symbol=symbol,
            quantity=quantity,
            price=price,
            accepted=True,
            order_no=order_no,
            raw=response,
        )
        self.logger.info("%s order accepted: order_no=%s", side, order_no or "unknown")
        return result
