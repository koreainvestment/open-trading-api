from dataclasses import dataclass
from typing import Dict, Optional

from api_client import ApiClient
from config import ENDPOINTS
from logger import get_logger

logger = get_logger(__name__)


@dataclass
class OrderResult:
    success: bool
    order_id: Optional[str]
    message: str
    msg_cd: Optional[str] = None


def parse_order_response(response: Dict[str, object]) -> OrderResult:
    order_id = None
    message = "Order response received"
    success = False
    msg_cd = None

    if isinstance(response, dict):
        rt_cd = response.get("rt_cd")
        msg_cd = response.get("msg_cd")
        msg1 = response.get("msg1")

        output = response.get("output")

        if isinstance(output, dict):
            order_id = (
                output.get("ODNO")
                or output.get("odno")
                or output.get("ord_no")
                or output.get("ordr_id")
            )

        message = str(msg1 or msg_cd or message)
        success = rt_cd == "0" and bool(order_id)

    return OrderResult(
        success=success,
        order_id=order_id,
        message=message,
        msg_cd=str(msg_cd) if msg_cd else None,
    )


class OrderService:
    def __init__(self, api_client: ApiClient, account_no: str) -> None:
        self.api_client = api_client
        self.account_no = account_no

    def submit_limit_order(
        self,
        token: str,
        symbol: str,
        quantity: int,
        price: int,
        side: str,
    ) -> OrderResult:
        logger.info(
            "[ORDER_SUBMIT] side=%s symbol=%s quantity=%s price=%s",
            side,
            symbol,
            quantity,
            price,
        )

        if side not in ("buy", "sell"):
            raise ValueError("side must be either 'buy' or 'sell'")

        if quantity <= 0:
            raise ValueError("quantity must be positive")

        if price <= 0:
            raise ValueError("price must be positive for a limit order")

        tr_id = "VTTC0802U" if side == "buy" else "VTTC0801U"

        body = {
            "CANO": self.account_no,
            "ACNT_PRDT_CD": "01",
            "PDNO": symbol,
            "ORD_DVSN": "00",
            "ORD_QTY": str(quantity),
            "ORD_UNPR": str(price),
        }

        response = self.api_client.request(
            method="POST",
            path=ENDPOINTS["order_submission"],
            token=token,
            json_body=body,
            tr_id=tr_id,
        )

        result = parse_order_response(response)

        if result.success:
            logger.info(
                "[ORDER_OK] side=%s symbol=%s quantity=%s price=%s order_id=%s",
                side,
                symbol,
                quantity,
                price,
                result.order_id,
            )
        else:
            logger.warning(
                "[ORDER_REJECTED] side=%s symbol=%s quantity=%s price=%s msg_cd=%s msg=%s",
                side,
                symbol,
                quantity,
                price,
                result.msg_cd,
                result.message,
            )

        return result