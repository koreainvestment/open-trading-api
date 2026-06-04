from typing import Any

from config import TR_ID_BALANCE


class AccountService:
    def __init__(self, client):
        self.client = client

    def get_balance(self) -> dict[str, Any]:
        params = {
            "CANO": self.client.account_no,
            "ACNT_PRDT_CD": self.client.account_product_code,
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
            path="/uapi/domestic-stock/v1/trading/inquire-balance",
            tr_id=TR_ID_BALANCE,
            params=params,
        )

        return result

    def get_holding_quantity(self, symbol: str) -> int:
        balance = self.get_balance()

        for item in balance.get("output1", []):
            if item.get("pdno") == symbol:
                return int(item.get("hldg_qty", "0"))

        return 0

    def get_sellable_quantity(self, symbol: str) -> int:
        balance = self.get_balance()

        for item in balance.get("output1", []):
            if item.get("pdno") == symbol:
                return int(item.get("ord_psbl_qty", "0"))

        return 0

    def get_available_cash(self) -> int:
        balance = self.get_balance()
        output2 = balance.get("output2", [])

        if not output2:
            return 0

        return int(output2[0].get("dnca_tot_amt", "0"))
