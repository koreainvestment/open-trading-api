from __future__ import annotations

from dataclasses import dataclass
from typing import Any

try:
    from .api_client import KISApiClient
except ImportError:  # pragma: no cover
    from api_client import KISApiClient


@dataclass(frozen=True)
class Quote:
    symbol: str
    price: int
    open_price: int | None = None
    high_price: int | None = None
    low_price: int | None = None
    volume: int | None = None
    raw: dict[str, Any] | None = None


def _to_int(value: Any, default: int | None = None) -> int | None:
    if value is None:
        return default
    try:
        text = str(value).replace(",", "").strip()
        if text == "":
            return default
        return int(float(text))
    except (TypeError, ValueError):
        return default


class MarketDataService:
    def __init__(self, client: KISApiClient, logger) -> None:
        self.client = client
        self.logger = logger

    def get_current_price(self, symbol: str, market_code: str = "J") -> Quote:
        payload = self.client.get(
            "/uapi/domestic-stock/v1/quotations/inquire-price",
            tr_id="FHKST01010100",
            params={
                "FID_COND_MRKT_DIV_CODE": market_code,
                "FID_INPUT_ISCD": symbol,
            },
        )
        output = payload.get("output", {})
        price = _to_int(output.get("stck_prpr"))
        if price is None:
            raise RuntimeError(f"Current price was missing from API response: {payload}")

        quote = Quote(
            symbol=symbol,
            price=price,
            open_price=_to_int(output.get("stck_oprc")),
            high_price=_to_int(output.get("stck_hgpr")),
            low_price=_to_int(output.get("stck_lwpr")),
            volume=_to_int(output.get("acml_vol")),
            raw=output,
        )
        self.logger.info("current price: symbol=%s price=%s", symbol, f"{quote.price:,}")
        return quote
