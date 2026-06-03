from typing import Any, Dict, List

from config import (
    ACNT_PRDT_CD,
    CANO,
    PATH_INQUIRE_BALANCE,
    TR_ID_BALANCE_DEMO,
)


class AccountService:
    def __init__(self, client, logger=None) -> None:
        self.client = client
        self.logger = logger

    def get_balance(self) -> Dict[str, Any]:
        params = {
            "CANO": CANO,
            "ACNT_PRDT_CD": ACNT_PRDT_CD,
            "AFHR_FLPR_YN": "N",
            "OFL_YN": "",
            "INQR_DVSN": "01",
            "UNPR_DVSN": "01",
            "FUND_STTL_ICLD_YN": "N",
            "FNCG_AMT_AUTO_RDPT_YN": "N",
            "PRCS_DVSN": "00",
            "CTX_AREA_FK100": "",
            "CTX_AREA_NK100": "",
        }

        data = self.client.get(
            path=PATH_INQUIRE_BALANCE,
            tr_id=TR_ID_BALANCE_DEMO,
            params=params,
        )

        if self.logger:
            self.logger.info("Balance inquiry completed.")

        return data

    def get_holdings(self) -> List[Dict[str, Any]]:
        data = self.get_balance()
        output1 = data.get("output1", [])

        if isinstance(output1, dict):
            return [output1]

        return output1 or []

    def get_summary(self) -> Dict[str, Any]:
        data = self.get_balance()
        output2 = data.get("output2", [])

        if isinstance(output2, list) and output2:
            return output2[0]

        if isinstance(output2, dict):
            return output2

        return {}

    def get_holding_quantity(self, symbol: str) -> int:
        holdings = self.get_holdings()

        for item in holdings:
            pdno = item.get("pdno") or item.get("PDNO")
            if pdno == symbol:
                qty = (
                    item.get("hldg_qty")
                    or item.get("HLDG_QTY")
                    or item.get("ord_psbl_qty")
                    or item.get("ORD_PSBL_QTY")
                    or "0"
                )
                return int(str(qty).replace(",", ""))

        return 0

    def get_available_cash(self) -> int:
        summary = self.get_summary()

        cash = (
            summary.get("dnca_tot_amt")
            or summary.get("DNCA_TOT_AMT")
            or summary.get("ord_psbl_cash")
            or summary.get("ORD_PSBL_CASH")
            or summary.get("nass_amt")
            or "0"
        )

        return int(str(cash).replace(",", ""))
