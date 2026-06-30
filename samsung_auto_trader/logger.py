import logging

#samsung_auto_trader라는 이름의 logger를 만들고INFO 이상의 로그를 출력한다.
def setup_logger() -> logging.Logger:
    logger = logging.getLogger("samsung_auto_trader")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = logging.StreamHandler()
        # [시간] 로그레벨 - 메시지 형식으로 출력
        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
