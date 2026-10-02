from __future__ import annotations

from dataclasses import dataclass
from typing import Any

try:
    from .api_client import KISApiClient
except ImportError:  # pragma: no cover
    from api_client import KISApiClient


def _first_value(mapping: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in mapping and mapping[key] not in (None, ""):
            return mapping[key]
    return None


def _to_int(value: Any) -> int:
    try:
        return int(float(str(value).replace(",", "").strip()))
    except (TypeError, ValueError):
        return 0


@dataclass(frozen=True)
class Holding:
    symbol: str
    name: str
    quantity: int
    average_price: int
    current_price: int
    evaluation_profit_loss: int
    raw: dict[str, Any]


@dataclass(frozen=True)
class AccountSnapshot:
    cash: int
    available_cash: int
    total_value: int
    holdings: list[Holding]
    raw_summary: dict[str, Any]
    raw_holdings: list[dict[str, Any]]


class AccountService:
    def __init__(self, client: KISApiClient, logger, account_number: str, account_product_code: str) -> None:
        self.client = client
        self.logger = logger
        self.account_number = account_number
        self.account_product_code = account_product_code

    def get_snapshot(self) -> AccountSnapshot:
        payload = self.client.get(
            "/uapi/domestic-stock/v1/trading/inquire-balance",
            tr_id="VTTC8434R",
            params={
                "CANO": self.account_number,
                "ACNT_PRDT_CD": self.account_product_code,
                "AFHR_FLPR_YN": "N",
                "OFL_YN": "",
                "INQR_DVSN": "02",
                "UNPR_DVSN": "01",
                "FUND_STTL_ICLD_YN": "N",
                "FNCG_AMT_AUTO_RDPT_YN": "N",
                "PRCS_DVSN": "00",
                "CTX_AREA_FK100": "",
                "CTX_AREA_NK100": "",
            },
        )

        output1 = payload.get("output1", []) or []
        output2 = payload.get("output2", []) or []
        if isinstance(output1, dict):
            output1 = [output1]
        if isinstance(output2, dict):
            output2 = [output2]

        summary = output2[0] if output2 else {}
        holdings: list[Holding] = []
        for item in output1:
            holdings.append(
                Holding(
                    symbol=str(_first_value(item, "pdno", "PDNO", "prdt_no", "shtn_pdno") or "").strip(),
                    name=str(_first_value(item, "prdt_name", "PDT_NM", "hldg_item_name") or "").strip(),
                    quantity=_to_int(_first_value(item, "hldg_qty", "hold_qty", "qty")),
                    average_price=_to_int(_first_value(item, "pchs_avg_pric", "avg_prc", "pchs_unpr")),
                    current_price=_to_int(_first_value(item, "prpr", "stck_prpr", "current_price")),
                    evaluation_profit_loss=_to_int(_first_value(item, "evlu_pfls_amt", "pl_amt", "evaluation_profit_loss")),
                    raw=item,
                )
            )

        snapshot = AccountSnapshot(
            cash=_to_int(_first_value(summary, "dnca_tot_amt", "cash", "tot_cash_amt")),
            available_cash=_to_int(
                _first_value(summary, "prvs_rcdl_excc_amt", "available_cash", "ord_psbl_cash")
            ),
            total_value=_to_int(_first_value(summary, "tot_evlu_amt", "total_value", "evlu_amt_smtl_amt")),
            holdings=holdings,
            raw_summary=summary,
            raw_holdings=output1,
        )
        self.logger.info(
            "holdings snapshot: cash=%s available=%s holdings=%s",
            f"{snapshot.cash:,}",
            f"{snapshot.available_cash:,}",
            len(snapshot.holdings),
        )
        return snapshot
