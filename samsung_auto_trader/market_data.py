from config import (
    MARKET_DIV_CODE,
    PATH_INQUIRE_PRICE,
    TR_ID_PRICE,
)

# 시세 조회 기능을 담당하는 클래스
class MarketDataService:
    def __init__(self, client, logger=None) -> None:
        self.client = client
        self.logger = logger

    # sumbol 현재가를 조회해서 정수로 반환
    def get_current_price(self, symbol: str) -> int:
        params = {
            "FID_COND_MRKT_DIV_CODE": MARKET_DIV_CODE,
            "FID_INPUT_ISCD": symbol,
        }

        data = self.client.get(
            path=PATH_INQUIRE_PRICE,
            tr_id=TR_ID_PRICE,
            params=params,
        )

        output = data.get("output", {})
        price_text = output.get("stck_prpr")  # stck_prpr:현재가    

        # 예외처리
        if price_text is None:
            raise RuntimeError(f"Current price field not found: {data}")

        price = int(str(price_text).replace(",", ""))

        # Current price of 005930: 356500와 같은 로그 출력
        if self.logger:
            self.logger.info("Current price of %s: %s", symbol, price)

        return price
