from __future__ import annotations

import argparse
import logging

try:
    from .account import AccountService
    from .api_client import KISApiClient
    from .auth import AuthManager
    from .config import Settings
    from .logger import setup_logging
    from .market_data import MarketDataService
    from .orders import OrderService
    from .trader import SamsungAutoTrader
except ImportError:  # pragma: no cover
    from account import AccountService
    from api_client import KISApiClient
    from auth import AuthManager
    from config import Settings
    from logger import setup_logging
    from market_data import MarketDataService
    from orders import OrderService
    from trader import SamsungAutoTrader


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Samsung Electronics mock auto trader for KIS Open API")
    parser.add_argument("--poll-seconds", type=int, help="override polling interval in seconds")
    parser.add_argument("--offset-krw", type=int, help="override price offset around current price")
    parser.add_argument("--quantity", type=int, help="override order quantity")
    return parser


def _replace_settings(settings: Settings, **changes) -> Settings:
    values = settings.__dict__.copy()
    values.update(changes)
    return Settings(**values)


def main() -> None:
    args = build_parser().parse_args()
    settings = Settings.from_env()

    if args.poll_seconds is not None:
        settings = _replace_settings(settings, poll_interval_seconds=args.poll_seconds)
    if args.offset_krw is not None:
        settings = _replace_settings(settings, price_offset_krw=args.offset_krw)
    if args.quantity is not None:
        settings = _replace_settings(settings, order_quantity=args.quantity)

    logger = setup_logging(logging.INFO)
    logger.info("starting Samsung auto trader for %s", settings.symbol)

    auth_manager = AuthManager(
        base_url=settings.base_url,
        appkey=settings.appkey,
        appsecret=settings.appsecret,
        cache_path=settings.token_cache_path,
        logger=logger,
        timeout_seconds=settings.request_timeout_seconds,
    )
    client = KISApiClient(
        base_url=settings.base_url,
        appkey=settings.appkey,
        appsecret=settings.appsecret,
        auth_manager=auth_manager,
        logger=logger,
        timeout_seconds=settings.request_timeout_seconds,
        retry_count=settings.retry_count,
        retry_backoff_seconds=settings.retry_backoff_seconds,
    )

    market_data = MarketDataService(client, logger)
    account = AccountService(client, logger, settings.account_number, settings.account_product_code)
    orders = OrderService(client, logger, settings.account_number, settings.account_product_code)
    trader = SamsungAutoTrader(
        symbol=settings.symbol,
        market_code=settings.market_code,
        price_offset_krw=settings.price_offset_krw,
        order_quantity=settings.order_quantity,
        poll_interval_seconds=settings.poll_interval_seconds,
        verify_delay_seconds=settings.verify_delay_seconds,
        trading_start=settings.trading_start,
        trading_end=settings.trading_end,
        market_data=market_data,
        account=account,
        orders=orders,
        logger=logger,
    )

    trader.run()


if __name__ == "__main__":
    main()
