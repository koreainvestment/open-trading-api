"""
삼성 자동 거래 시스템 - 메인 진입점.

이 프로그램은 Korea Investment Open API를 사용하여
삼성전자(005930)를 자동으로 거래합니다.

거래 시간: 09:10 ~ 15:30
거래 환경: 모의 거래 (Mock Trading)
선택 재시도 간격: 30초
"""

import time
import os
from datetime import datetime
import pytz
from logger import logger
from trader import Trader
import config

# 한국 시간대 설정
KST = pytz.timezone('Asia/Seoul')


def get_kst_now():
    """한국 시간(KST)으로 현재 시각을 반환합니다."""
    return datetime.now(KST)


def load_environment():
    """환경 변수를 로드합니다.
    
    GitHub Codespaces User Secrets에서 자동으로 주입되지만,
    로컬 환경에서는 .env 파일이 필요합니다.
    """
    # 로컬 환경에서 개발할 때 .env 파일 지원 (선택사항)
    try:
        from dotenv import load_dotenv
        if os.path.exists('.env'):
            load_dotenv()
    except ImportError:
        pass

    required_vars = ['GH_ACCOUNT', 'GH_APPKEY', 'GH_APPSECRET']
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        logger.error(f"필수 환경 변수가 설정되지 않았습니다: {missing_vars}")
        logger.error("다음 중 하나를 선택하세요:")
        logger.error("\n[GitHub Codespaces 사용 시]")
        logger.error("1. https://github.com/settings/codespaces 접속")
        logger.error("2. Secrets and variables > Codespaces 클릭")
        logger.error("3. 다음 3개 시크릿 생성:")
        logger.error("   - GH_ACCOUNT: <계좌번호>")
        logger.error("   - GH_APPKEY: <앱키>")
        logger.error("   - GH_APPSECRET: <앱시크릿>")
        logger.error("4. Codespaces 재시작 (Stop & Start)")
        logger.error("\n[로컬 환경 사용 시]")
        logger.error("1. .env 파일 생성 (또는 .env.example 복사)")
        logger.error("2. 또는 환경 변수 지정:")
        logger.error("   export GH_ACCOUNT=<계좌번호>")
        logger.error("   export GH_APPKEY=<앱키>")
        logger.error("   export GH_APPSECRET=<앱시크릿>")
        raise ValueError(f"필수 환경 변수 누락: {missing_vars}")

    logger.info("환경 변수 로드 완료")


def main():
    """메인 거래 루프."""
    try:
        logger.info("=" * 60)
        logger.info("삼성 자동 거래 시스템 시작")
        logger.info(f"시작 시간: {get_kst_now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 60)

        # 환경 변수 로드
        load_environment()

        # 트레이더 초기화
        trader = Trader(stock_code=config.TARGET_STOCK)
        logger.info(f"거래 대상: {config.TARGET_STOCK}")
        logger.info(f"거래 시간: {config.TRADING_START_HOUR:02d}:{config.TRADING_START_MINUTE:02d} ~ "
                   f"{config.TRADING_END_HOUR:02d}:{config.TRADING_END_MINUTE:02d}")
        logger.info(f"폴링 간격: {config.POLLING_INTERVAL_SECONDS}초")

        trading_started = False
        trading_ended = False

        while True:
            now = get_kst_now()
            current_hour = now.hour
            current_minute = now.minute

            # 거래 시간 확인
            should_trade = trader.should_trade_now(current_hour, current_minute)

            if should_trade:
                if not trading_started:
                    logger.info(f"거래 시간 시작 {now.strftime('%H:%M:%S')}")
                    trading_started = True
                    trading_ended = False

                # 거래 사이클 실행
                try:
                    trader.execute_trading_cycle()
                except Exception as e:
                    logger.error(f"거래 사이클 실행 중 오류: {e}")
                    logger.info(f"{config.ERROR_RETRY_INTERVAL_SECONDS}초 후 재시도합니다")
                    time.sleep(config.ERROR_RETRY_INTERVAL_SECONDS)
                    continue

                # 다음 사이클까지 대기
                logger.debug(f"다음 사이클까지 {config.POLLING_INTERVAL_SECONDS}초 대기 중...")
                time.sleep(config.POLLING_INTERVAL_SECONDS)

            else:
                # 거래 시간 외
                if trading_started and not trading_ended:
                    logger.info(f"거래 시간 종료 {now.strftime('%H:%M:%S')}")
                    trading_ended = True

                # 상태 로그 (매 정각마다)
                if current_minute == 0:
                    logger.debug(f"거래 시간 외 - {now.strftime('%Y-%m-%d %H:%M:%S')}")

                # 거래 시간 외에는 60초마다 확인
                time.sleep(60)

    except KeyboardInterrupt:
        logger.info("\n프로그램이 사용자에 의해 중단되었습니다")
    except Exception as e:
        logger.error(f"프로그램 오류: {e}")
        raise
    finally:
        logger.info("=" * 60)
        logger.info("삼성 자동 거래 시스템 종료")
        logger.info(f"종료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 60)


if __name__ == "__main__":
    main()
