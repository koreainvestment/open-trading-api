from dataclasses import dataclass
from typing import Dict

from api_client import ApiClient
from config import ENDPOINTS
from logger import get_logger

logger = get_logger(__name__)


@dataclass
class AccountInfo:
    cash_available: int
    stock_quantity: int
    stock_symbol: str


def parse_int(value: object, default: int = 0) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def parse_balance_response(response: Dict[str, object], symbol: str) -> AccountInfo:
    cash_available = 0
    stock_quantity = 0

    output1 = response.get("output1")
    output2 = response.get("output2")
    output = response.get("output")

    # 보유 주식 수량 파싱
    if isinstance(output1, list) and output1:
        for item in output1:
            if not isinstance(item, dict):
                continue

            # 특정 종목만 집계
            if item.get("pdno") == symbol or item.get("stck_shrn_iscd") == symbol:
                if item.get("hldg_qty") is not None:
                    stock_quantity += parse_int(item.get("hldg_qty"))
                elif item.get("ovrs_qty") is not None:
                    stock_quantity += parse_int(item.get("ovrs_qty"))

    elif isinstance(output, list):
        for item in output:
            if not isinstance(item, dict):
                continue

            if item.get("pdno") == symbol or item.get("stck_shrn_iscd") == symbol:
                if item.get("hldg_qty") is not None:
                    stock_quantity += parse_int(item.get("hldg_qty"))
                elif item.get("ovrs_qty") is not None:
                    stock_quantity += parse_int(item.get("ovrs_qty"))

    elif isinstance(output, dict):
        stock_quantity = parse_int(
            output.get("hldg_qty") or output.get("ovrs_qty")
        )

    # 주문 가능 현금 파싱
    if isinstance(output2, list) and output2:
        cash_available = parse_int(
            output2[0].get("ord_psbl_cash")
            or output2[0].get("nxdy_excc_amt")
            or output2[0].get("dnca_tot_amt")
            or output2[0].get("nass_amt")
        )

    elif isinstance(output2, dict):
        cash_available = parse_int(
            output2.get("ord_psbl_cash")
            or output2.get("nxdy_excc_amt")
            or output2.get("dnca_tot_amt")
            or output2.get("nass_amt")
        )

    elif isinstance(output, list) and output:
        cash_available = parse_int(
            output[0].get("ord_psbl_cash")
            or output[0].get("nxdy_excc_amt")
            or output[0].get("dnca_tot_amt")
        )

    elif isinstance(output, dict):
        cash_available = parse_int(
            output.get("ord_psbl_cash")
            or output.get("nxdy_excc_amt")
            or output.get("dnca_tot_amt")
        )

    logger.info(
        "Parsed account info: cash %s, quantity %s",
        cash_available,
        stock_quantity,
    )

    return AccountInfo(
        cash_available=cash_available,
        stock_quantity=stock_quantity,
        stock_symbol=symbol,
    )


class AccountService:
    def __init__(self, api_client: ApiClient, account_no: str) -> None:
        self.api_client = api_client
        self.account_no = account_no

    def get_account_info(self, token: str, symbol: str) -> AccountInfo:
        logger.info("Fetching balance and holdings for account %s", self.account_no)

        params = {
            "CANO": self.account_no,
            "ACNT_PRDT_CD": "01",
            "AFHR_FLPR_YN": "N",
            "OFL_YN": "",
            "INQR_DVSN": "02",
            "UNPR_DVSN": "01",
            "FUND_STTL_ICLD_YN": "N",
            "FNCG_AMT_AUTO_RDPT_YN": "N",
            "PRCS_DVSN": "00",
            "CTX_AREA_FK100": "",
            "CTX_AREA_NK100": "",
        }

        response = self.api_client.request(
            method="GET",
            path=ENDPOINTS["balance_inquiry"],
            token=token,
            params=params,
            tr_id="VTTC8434R",
        )

        return parse_balance_response(response, symbol)