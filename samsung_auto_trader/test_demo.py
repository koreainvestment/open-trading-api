"""
삼성 자동 거래 시스템 - 테스트/데모 모드

환경변수 없이 주요 모듈의 동작을 테스트합니다.
"""

import os
import sys
from datetime import datetime

# 테스트용 환경변수 설정 (실제 자격증명 대신 더미값 사용)
os.environ['GH_ACCOUNT'] = 'TEST_ACCOUNT_12345'
os.environ['GH_APPKEY'] = 'TEST_APPKEY_dummy'
os.environ['GH_APPSECRET'] = 'TEST_APPSECRET_dummy'

print("=" * 70)
print("삼성 자동 거래 시스템 - 테스트 데모")
print("=" * 70)
print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# 모듈 임포트 및 테스트
try:
    print("✓ logger 모듈 로드 중...")
    from logger import logger
    logger.info("logger 모듈 로드 완료")
    print()

    print("✓ config 모듈 로드 중...")
    import config
    print(f"  - 거래 대상: {config.TARGET_STOCK}")
    print(f"  - 거래 시간: {config.TRADING_START_HOUR:02d}:{config.TRADING_START_MINUTE:02d} ~ "
          f"{config.TRADING_END_HOUR:02d}:{config.TRADING_END_MINUTE:02d}")
    print(f"  - 매수 오프셋: {config.BUY_OFFSET} KRW")
    print(f"  - 매도 오프셋: {config.SELL_OFFSET} KRW")
    print(f"  - 폴링 간격: {config.POLLING_INTERVAL_SECONDS}초")
    print()

    print("✓ Trader 클래스 로드 중...")
    from trader import Trader
    trader = Trader()
    print(f"  - Trader 초기화 완료 (거래 대상: {trader.stock_code})")
    print()

    print("✓ 거래 시간 확인 로직 테스트...")
    test_times = [
        (9, 9, "거래 전"),
        (9, 10, "거래 시작"),
        (12, 0, "거래 중"),
        (15, 29, "거래 중"),
        (15, 30, "거래 종료"),
        (16, 0, "거래 후"),
    ]
    for hour, minute, label in test_times:
        should_trade = trader.should_trade_now(hour, minute)
        status = "✓ 거래 가능" if should_trade else "✗ 거래 불가"
        print(f"  {hour:02d}:{minute:02d} ({label}): {status}")
    print()

    print("✓ API 클라이언트 로드 중...")
    from api_client import api_client
    print(f"  - API 기본 URL: {api_client.base_url}")
    print(f"  - 타임아웃: {api_client.timeout}초")
    print(f"  - 최대 재시도: {api_client.max_retries}회")
    print()

    print("✓ 환경변수 확인...")
    print(f"  - GH_ACCOUNT: {os.getenv('GH_ACCOUNT')}")
    print(f"  - GH_APPKEY: {os.getenv('GH_APPKEY', '(not set)')[:20]}...")
    print(f"  - GH_APPSECRET: {os.getenv('GH_APPSECRET', '(not set)')[:20]}...")
    print()

    print("=" * 70)
    print("모든 모듈이 정상 로드되었습니다! ✓")
    print("=" * 70)
    print()
    print("📋 다음 단계:")
    print()
    print("1. GitHub Codespaces 시크릿 설정:")
    print("   https://github.com/settings/codespaces")
    print("   → Secrets and variables > Codespaces > New secret")
    print("   → GH_ACCOUNT, GH_APPKEY, GH_APPSECRET 등록")
    print()
    print("2. 또는 로컬 .env 파일 설정:")
    print("   cp .env.example .env")
    print("   (텍스트 에디터로 .env 파일 편집)")
    print()
    print("3. 프로그램 실행:")
    print("   python main.py")
    print()
    print("=" * 70)

except Exception as e:
    print(f"✗ 오류 발생: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
