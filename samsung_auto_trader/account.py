from typing import Any

from config import CANO, ACNT_PRDT_CD, PATH_INQUIRE_BALANCE, TR_ID_BALANCE


class AccountService:
    def __init__(self, client, logger=None):
        self.client = client
        self.logger = logger

    # 계좌 전체 잔고조회 API를 호출한다.
    def get_balance(self) -> dict[str, Any]:
        params = {
            "CANO": CANO,
            "ACNT_PRDT_CD": ACNT_PRDT_CD,
            "AFHR_FLPR_YN": "N",
            "OFL_YN": "",
            "INQR_DVSN": "02",
            "UNPR_DVSN": "01",
            "FUND_STTL_ICLD_YN": "N",
            "FNCG_AMT_AUTO_RDPT_YN": "N",
            "PRCS_DVSN": "01",
            "CTX_AREA_FK100": "",
            "CTX_AREA_NK100": "",
        }

        result = self.client.get(
            path=PATH_INQUIRE_BALANCE,
            tr_id=TR_ID_BALANCE,
            params=params,
        )

        return result

    # 특정 종목의 보유수량 hldg_qty를 가져온다.
    def get_holding_quantity(self, symbol: str) -> int:
        balance = self.get_balance()

        for item in balance.get("output1", []):
            if item.get("pdno") == symbol:
                return int(item.get("hldg_qty", "0"))

        return 0

    # 특정 종목의 매도가능수량 ord_psbl_qty를 가져온다.
    def get_sellable_quantity(self, symbol: str) -> int:
        balance = self.get_balance()

        for item in balance.get("output1", []):
            if item.get("pdno") == symbol:
                return int(item.get("ord_psbl_qty", "0"))

        return 0

    # 계좌의 현금 또는 주문가능금액을 가져온다.
    def get_available_cash(self) -> int:
        balance = self.get_balance()
        output2 = balance.get("output2", [])

        if not output2:
            return 0

        return int(output2[0].get("dnca_tot_amt", "0"))
