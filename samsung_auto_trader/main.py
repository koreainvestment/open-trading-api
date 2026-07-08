from auth import get_access_token
from api_client import KisApiClient
from market_data import MarketDataService
from account import AccountService
from orders import OrderService
from trader import SamsungAutoTrader
from logger import setup_logger
from config import MOCK_BASE_URL


def main() -> None:
    # 로그 설정
    logger = setup_logger()  

    # 한국투자 API 토큰 발급 또는 재사용
    token = get_access_token(logger=logger)

    # API 요청을 보낼 client 생성
    client = KisApiClient(  
        base_url=MOCK_BASE_URL,
        access_token=token,
        logger=logger,
    )

    # 현재가 조회 서비스 생성
    market_data = MarketDataService(client=client, logger=logger) 
    # 계좌 조회 서비스 생성
    account = AccountService(client=client, logger=logger)
    # 주문 서비스 생성
    orders = OrderService(client=client, logger=logger)

    # 자동매매 객체 생성
    trader = SamsungAutoTrader(
        market_data=market_data,
        account=account,
        orders=orders,
        logger=logger,
    )

    # 자동매매 실행
    trader.run()


if __name__ == "__main__":
    main()
