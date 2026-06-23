from dataclasses import dataclass
from typing import Any

from config import CANO, ACNT_PRDT_CD, PATH_INQUIRE_BALANCE, TR_ID_BALANCE


@dataclass(frozen=True)
class AccountSnapshot:
    """
    잔고조회 API 응답에서 필요한 값만 뽑아 담는 객체.

    이 객체를 사용하면 잔고조회 API를 여러 번 호출하지 않고,
    한 번 조회한 응답에서 현금, 보유수량, 매도가능수량을 모두 사용할 수 있다.
    """

    available_cash: int
    holding_quantity: int
    sellable_quantity: int


class AccountService:
    def __init__(self, client, logger=None) -> None:
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
            "PRCS_DVSN": "00",
            "CTX_AREA_FK100": "",
            "CTX_AREA_NK100": "",
        }

        result = self.client.get(
            path=PATH_INQUIRE_BALANCE,
            tr_id=TR_ID_BALANCE,
            params=params,
        )

        return result

    def get_account_snapshot(self, symbol: str) -> AccountSnapshot:
        """
        잔고조회 API를 한 번만 호출하고,
        그 응답에서 현금, 보유수량, 매도가능수량을 모두 파싱한다.

        기존 방식:
            get_available_cash()      -> get_balance() 1회
            get_holding_quantity()    -> get_balance() 1회
            get_sellable_quantity()   -> get_balance() 1회

        개선 방식:
            get_account_snapshot()    -> get_balance() 1회
        """

        balance = self.get_balance()

        return AccountSnapshot(
            available_cash=self.parse_available_cash(balance),
            holding_quantity=self.parse_holding_quantity(balance, symbol),
            sellable_quantity=self.parse_sellable_quantity(balance, symbol),
        )

    @staticmethod
    def _to_int(value: Any, default: int = 0) -> int:
        """
        API 응답값을 안전하게 int로 변환한다.
        한국투자 API 응답은 숫자도 문자열로 오는 경우가 많다.
        """

        if value is None:
            return default

        text = str(value).strip().replace(",", "")

        if text == "":
            return default

        try:
            return int(float(text))
        except ValueError:
            return default

    def parse_available_cash(self, balance: dict[str, Any]) -> int:
        """
        잔고조회 응답에서 현금/예수금 정보를 가져온다.

        기존 코드에서 사용하던 dnca_tot_amt를 그대로 사용한다.
        """

        output2 = balance.get("output2", [])

        if not output2:
            return 0

        return self._to_int(output2[0].get("dnca_tot_amt"))

    def parse_holding_quantity(self, balance: dict[str, Any], symbol: str) -> int:
        """
        잔고조회 응답에서 특정 종목의 보유수량 hldg_qty를 가져온다.
        """

        for item in balance.get("output1", []):
            if item.get("pdno") == symbol:
                return self._to_int(item.get("hldg_qty"))

        return 0

    def parse_sellable_quantity(self, balance: dict[str, Any], symbol: str) -> int:
        """
        잔고조회 응답에서 특정 종목의 매도가능수량 ord_psbl_qty를 가져온다.
        """

        for item in balance.get("output1", []):
            if item.get("pdno") == symbol:
                return self._to_int(item.get("ord_psbl_qty"))

        return 0

    # 아래 3개 메서드는 기존 코드와의 호환성을 위해 남겨둔다.
    # 새 trader.py에서는 get_account_snapshot()을 사용하므로 중복 호출이 줄어든다.

    def get_holding_quantity(self, symbol: str) -> int:
        snapshot = self.get_account_snapshot(symbol)
        return snapshot.holding_quantity

    def get_sellable_quantity(self, symbol: str) -> int:
        snapshot = self.get_account_snapshot(symbol)
        return snapshot.sellable_quantity

    def get_available_cash(self) -> int:
        balance = self.get_balance()
        return self.parse_available_cash(balance)
