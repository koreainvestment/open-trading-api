"""
서삼스턴 자동 거래 프로그램을 위한 중앙 집중식 로깅 설정.
"""

import logging
import sys
from datetime import datetime
import pytz
import time

# 한국 시간대 설정
KST = pytz.timezone('Asia/Seoul')

class KSTFormatter(logging.Formatter):
    """한국 시간대(KST)를 사용하는 로그 포매터."""
    
    def formatTime(self, record, datefmt=None):
        """한국 시간으로 로그 시간을 포매팅합니다."""
        # UTC 타임스탬프를 한국 시간으로 변환
        kst_time = datetime.fromtimestamp(record.created, tz=KST)
        if datefmt:
            s = kst_time.strftime(datefmt)
        else:
            s = kst_time.strftime('%Y-%m-%d %H:%M:%S')
        return s


def setup_logger():
    """
    로거를 설정하고 반환합니다.
    콘솔 출력과 파일 기록 모두 포함합니다.
    """
    logger = logging.getLogger("SamsungAutoTrader")
    logger.setLevel(logging.DEBUG)

    # KST 포매터 설정
    formatter = KSTFormatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 콘솔 핸들러
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 파일 핸들러 (선택사항)
    kst_now = datetime.now(KST)
    log_filename = f"trading_{kst_now.strftime('%Y%m%d_%H%M%S')}.log"
    file_handler = logging.FileHandler(log_filename)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


# 전역 로거 인스턴스
logger = setup_logger()
