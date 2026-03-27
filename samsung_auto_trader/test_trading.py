"""
거래 로직 테스트 스크립트.
실제 API 호출을 테스트합니다.
"""

import os
import sys
from logger import logger
from auth import get_auth_token
from market_data import get_current_price
from account import get_account_info
from trader import Trader

def test_authentication():
    """토큰 발급 테스트."""
    logger.info("=" * 60)
    logger.info("1. 토큰 발급 테스트")
    logger.info("=" * 60)
    
    try:
        token = get_auth_token()
        if token:
            logger.info(f"✓ 토큰 발급 성공: {token[:20]}...")
            return True
        else:
            logger.error("✗ 토큰 발급 실패")
            return False
    except Exception as e:
        logger.error(f"✗ 토큰 발급 중 오류: {e}")
        return False


def test_market_data():
    """주가 조회 테스트."""
    logger.info("\n" + "=" * 60)
    logger.info("2. 주가 조회 테스트")
    logger.info("=" * 60)
    
    try:
        price = get_current_price()
        if price:
            logger.info(f"✓ 삼성전자(005930) 현재가: {price} KRW")
            return True
        else:
            logger.warning("⚠ 주가 조회 결과 없음")
            return False
    except Exception as e:
        logger.error(f"✗ 주가 조회 중 오류: {e}")
        return False


def test_account():
    """계좌 정보 조회 테스트."""
    logger.info("\n" + "=" * 60)
    logger.info("3. 계좌 정보 조회 테스트")
    logger.info("=" * 60)
    
    try:
        account = get_account_info()
        if account:
            logger.info(f"✓ 계좌 조회 성공")
            logger.info(f"  - 계좌: {account.account_number}")
            logger.info(f"  - 현금: {account.cash_balance} KRW" if account.cash_balance else "  - 현금: 조회 불가")
            logger.info(f"  - 보유 주식: {account.holdings if account.holdings else '없음'}")
            return True
        else:
            logger.warning("⚠ 계좌 정보 조회 실패")
            return False
    except Exception as e:
        logger.error(f"✗ 계좌 조회 중 오류: {e}")
        return False


def test_trading_logic():
    """거래 로직 테스트 (실제 주문은 하지 않음)."""
    logger.info("\n" + "=" * 60)
    logger.info("4. 거래 로직 검증")
    logger.info("=" * 60)
    
    try:
        trader = Trader()
        
        # 거래 시간 확인 테스트
        should_trade = trader.should_trade_now(14, 0)
        logger.info(f"✓ 거래 시간 확인 (14:00): {'거래 가능' if should_trade else '거래 불가'}")
        
        should_trade = trader.should_trade_now(6, 0)
        logger.info(f"✓ 거래 시간 확인 (06:00): {'거래 가능' if should_trade else '거래 불가'}")
        
        return True
    except Exception as e:
        logger.error(f"✗ 거래 로직 검증 중 오류: {e}")
        return False


def main():
    """모든 테스트 실행."""
    logger.info("\n")
    logger.info("╔" + "=" * 58 + "╗")
    logger.info("║" + " 삼성 자동 거래 시스템 - 통합 테스트 시작".center(58) + "║")
    logger.info("╚" + "=" * 58 + "╝")
    
    results = []
    
    # 테스트 실행
    results.append(("토큰 발급", test_authentication()))
    results.append(("주가 조회", test_market_data()))
    results.append(("계좌 조회", test_account()))
    results.append(("거래 로직", test_trading_logic()))
    
    # 결과 요약
    logger.info("\n" + "=" * 60)
    logger.info("테스트 결과 요약")
    logger.info("=" * 60)
    
    for test_name, result in results:
        status = "✓ 성공" if result else "✗ 실패"
        logger.info(f"{test_name}: {status}")
    
    success_count = sum(1 for _, result in results if result)
    total_count = len(results)
    
    logger.info(f"\n총 {success_count}/{total_count} 테스트 통과")
    
    if success_count == total_count:
        logger.info("\n✓ 모든 테스트 통과! 프로그램이 정상 작동합니다.")
    else:
        logger.warning("\n⚠ 일부 테스트 실패. API 설정을 확인하세요.")


if __name__ == "__main__":
    main()
