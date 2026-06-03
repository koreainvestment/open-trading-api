from auth import get_access_token
from api_client import KisApiClient
from market_data import MarketDataService
from account import AccountService
from orders import OrderService
from trader import SamsungAutoTrader
from logger import setup_logger
from config import MOCK_BASE_URL


def main() -> None:
    logger = setup_logger()

    token = get_access_token(logger=logger)

    client = KisApiClient(
        base_url=MOCK_BASE_URL,
        access_token=token,
        logger=logger,
    )

    market_data = MarketDataService(client=client, logger=logger)
    account = AccountService(client=client, logger=logger)
    orders = OrderService(client=client, logger=logger)

    trader = SamsungAutoTrader(
        market_data=market_data,
        account=account,
        orders=orders,
        logger=logger,
    )

    trader.run()


if __name__ == "__main__":
    main()
