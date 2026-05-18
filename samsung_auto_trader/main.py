from config import load_config
from logger import configure_logger, get_logger
from trader import StockTrader


def main() -> None:
    configure_logger()
    logger = get_logger(__name__)
    logger.info("Starting Samsung Auto Trader.")

    config = load_config()
    trader = StockTrader(config)
    trader.run()


if __name__ == "__main__":
    main()
