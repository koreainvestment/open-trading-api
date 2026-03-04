#!/usr/bin/env python3
"""
라이브 트레이딩 예제

이 예제는 kis_backtest를 사용하여 실시간 트레이딩을 수행하는 방법을 보여줍니다.
한국투자증권 API를 통해 실제 주문을 실행합니다.

⚠️ 주의: 이 예제는 실제 자금이 사용됩니다.
         반드시 모의투자 계좌로 먼저 테스트하세요.

실행:
    uv run python examples/live_trading.py --example manual
    uv run python examples/live_trading.py --example position
    uv run python examples/live_trading.py --example stream
    uv run python examples/live_trading.py --example strategy
"""

import sys
import time
from datetime import datetime, date, timedelta
from pathlib import Path

# 프로젝트 루트 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from kis_backtest import LeanClient
from kis_backtest.providers.kis import KISAuth, KISDataProvider, KISBrokerageProvider


# ============================================================================
# 클라이언트 생성 헬퍼
# ============================================================================

def create_live_client():
    """KIS API 인증 및 LiveClient 생성"""
    print("\n[인증] 한국투자증권 API 인증 중...")

    try:
        auth = KISAuth.from_env()
        data_provider = KISDataProvider(auth)
        brokerage_provider = KISBrokerageProvider.from_auth(auth)

        mode_str = "모의투자" if auth.is_paper else "실전투자"
        print(f"  ✓ 인증 성공 ({mode_str}, 계좌: {auth.acct_masked})")

        # LeanClient 생성 후 LiveClient 반환
        client = LeanClient(
            data_provider=data_provider,
            brokerage_provider=brokerage_provider,
        )
        return client.live()

    except Exception as e:
        print(f"  ✗ 인증 실패: {e}")
        print("\n💡 KIS API 인증 정보를 설정하세요.")
        return None


# ============================================================================
# 예제 1: 수동 주문 실행
# ============================================================================

def run_manual_order():
    """수동 주문 실행 예제"""

    print("=" * 60)
    print("수동 주문 예제")
    print("=" * 60)

    live = create_live_client()
    if live is None:
        return

    symbol = "005930"  # 삼성전자

    # 현재가 조회
    print(f"\n[시세] {symbol} 현재 시세 조회 중...")
    try:
        quote = live.get_quote(symbol)
        print(f"  현재가: {quote.price:,.0f}원")
        print(f"  전일대비: {quote.change:+,.0f}원 ({quote.change_pct:+.2f}%)")
    except Exception as e:
        print(f"  시세 조회 실패: {e}")
        return

    # 주문 생성 (시장가 매수 1주)
    print("\n[주문] 시장가 매수 주문 실행 중...")
    print("  종목: 삼성전자 (005930)")
    print("  수량: 1주")
    print("  유형: 시장가")

    try:
        order = live.submit_order(
            symbol=symbol,
            side="buy",
            quantity=1,
            order_type="market",
        )

        print(f"\n  ✓ 주문 제출 완료")
        print(f"    주문번호: {order.id}")
        print(f"    상태: {order.status}")

    except Exception as e:
        print(f"\n  ✗ 주문 실패: {e}")


# ============================================================================
# 예제 2: 포지션 관리
# ============================================================================

def run_position_management():
    """포지션 관리 예제"""

    print("=" * 60)
    print("포지션 관리 예제")
    print("=" * 60)

    live = create_live_client()
    if live is None:
        return

    # 계좌 잔고 조회
    print("\n[잔고] 계좌 잔고 조회 중...")
    try:
        balance = live.get_balance()
        print(f"  예수금: {balance.cash:,.0f}원")
        print(f"  출금가능금액: {balance.available_cash:,.0f}원")
        print(f"  총평가금액: {balance.total_value:,.0f}원")
    except Exception as e:
        print(f"  잔고 조회 실패: {e}")

    # 포지션 조회
    print("\n[포지션] 현재 보유 포지션:")
    print("-" * 50)

    try:
        positions = live.get_positions()

        if not positions:
            print("  보유 종목이 없습니다.")
        else:
            for pos in positions:
                pnl_sign = "+" if pos.unrealized_pnl >= 0 else ""
                pnl_pct = (pos.current_price / pos.average_price - 1) * 100 if pos.average_price > 0 else 0

                print(f"\n  [{pos.symbol}]")
                print(f"    수량: {pos.quantity}주")
                print(f"    평균단가: {pos.average_price:,.0f}원")
                print(f"    현재가: {pos.current_price:,.0f}원")
                print(f"    평가손익: {pnl_sign}{pos.unrealized_pnl:,.0f}원 ({pnl_sign}{pnl_pct:.2f}%)")

    except Exception as e:
        print(f"  포지션 조회 실패: {e}")


# ============================================================================
# 예제 3: 지정가 주문 및 취소
# ============================================================================

def run_limit_order():
    """지정가 주문 및 취소 예제"""

    print("=" * 60)
    print("지정가 주문 예제")
    print("=" * 60)

    live = create_live_client()
    if live is None:
        return

    symbol = "005930"

    # 현재가 조회
    try:
        quote = live.get_quote(symbol)
        current_price = quote.price
    except Exception as e:
        print(f"시세 조회 실패: {e}")
        return

    # 현재가보다 1% 낮은 가격으로 지정가 매수
    limit_price = int(current_price * 0.99)
    limit_price = (limit_price // 100) * 100  # 호가 단위 맞춤

    print(f"\n[주문] 지정가 매수 주문:")
    print(f"  종목: {symbol}")
    print(f"  현재가: {current_price:,.0f}원")
    print(f"  지정가: {limit_price:,.0f}원 (현재가 대비 -1%)")
    print(f"  수량: 1주")

    try:
        order = live.submit_order(
            symbol=symbol,
            side="buy",
            quantity=1,
            order_type="limit",
            price=limit_price,
        )

        print(f"\n  ✓ 주문 제출 완료")
        print(f"    주문번호: {order.id}")
        print(f"    상태: {order.status}")

        # 5초 대기 후 주문 취소
        print("\n5초 후 주문 취소 예정...")
        time.sleep(5)

        # 주문 취소
        print("\n[취소] 주문 취소 중...")
        success = live.cancel_order(order.id)

        if success:
            print(f"  ✓ 주문 취소 완료")
        else:
            print(f"  ✗ 취소 실패 (이미 체결되었거나 취소됨)")

    except Exception as e:
        print(f"\n  ✗ 오류: {e}")


# ============================================================================
# 예제 4: 실시간 시세 스트리밍
# ============================================================================

def run_realtime_streaming():
    """실시간 시세 스트리밍 예제"""

    print("=" * 60)
    print("실시간 시세 스트리밍")
    print("=" * 60)

    live = create_live_client()
    if live is None:
        return

    symbols = ["005930", "000660", "035420"]  # 삼성전자, SK하이닉스, NAVER

    print(f"\n구독 종목: {', '.join(symbols)}")
    print("실시간 시세 수신 중... (30초 후 자동 종료, Ctrl+C로 즉시 종료)")
    print("-" * 60)

    def on_bar(symbol, bar):
        """실시간 데이터 수신 콜백"""
        timestamp = bar.time.strftime("%H:%M:%S") if hasattr(bar, 'time') else datetime.now().strftime("%H:%M:%S")

        # 색상 (터미널 지원시)
        change = bar.close - bar.open
        color = "\033[92m" if change >= 0 else "\033[91m"
        reset = "\033[0m"
        sign = "+" if change >= 0 else ""

        print(
            f"[{timestamp}] {symbol}: "
            f"{color}{bar.close:,.0f}원 ({sign}{change:,.0f}){reset} "
            f"거래량: {bar.volume:,}"
        )

    try:
        # 30초 타임아웃으로 실행
        live.subscribe_realtime(symbols, on_bar, timeout=30)

    except KeyboardInterrupt:
        print("\n\n스트리밍 종료")


# ============================================================================
# 예제 5: 전략 실행 (실시간 데이터 + 주문)
# ============================================================================

def run_live_strategy():
    """라이브 전략 실행 예제"""

    print("=" * 60)
    print("라이브 전략 실행 예제")
    print("⚠️  실제 주문이 실행될 수 있습니다!")
    print("=" * 60)

    live = create_live_client()
    if live is None:
        return

    symbols = ["005930"]  # 삼성전자

    print(f"\n종목: {symbols}")
    print("전략: RSI 과매도 반등 (데모)")
    print("실행 시간: 60초")
    print("-" * 60)

    # 간단한 전략 상태
    state = {
        "rsi_values": [],
        "last_signal": None,
    }

    def on_bar(symbol, bar):
        """실시간 데이터 수신 콜백"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {symbol}: {bar.close:,.0f}원 (V: {bar.volume:,})")

        # 데모: 실제 RSI 계산 대신 간단한 로직
        state["rsi_values"].append(bar.close)
        if len(state["rsi_values"]) > 14:
            state["rsi_values"].pop(0)

        # 데모 신호 (실제 주문은 주석 처리)
        if len(state["rsi_values"]) >= 14:
            avg = sum(state["rsi_values"]) / len(state["rsi_values"])
            if bar.close < avg * 0.98:  # 평균보다 2% 낮으면
                if state["last_signal"] != "buy":
                    print(f"  📈 매수 신호 발생 (가격이 평균 이하)")
                    state["last_signal"] = "buy"
                    # 실제 주문 (주석 해제시 실행):
                    # live.submit_order(symbol, "buy", 1, "market")

            elif bar.close > avg * 1.02:  # 평균보다 2% 높으면
                if state["last_signal"] != "sell":
                    print(f"  📉 매도 신호 발생 (가격이 평균 이상)")
                    state["last_signal"] = "sell"
                    # 실제 주문 (주석 해제시 실행):
                    # live.submit_order(symbol, "sell", 1, "market")

    def on_fill(order):
        """체결 통보 콜백"""
        print(f"  💰 체결: {order.symbol} {order.side} {order.filled_quantity}주 @ {order.average_price:,.0f}원")

    try:
        print("\n전략 실행 중... (60초 후 자동 종료)")
        live.run_strategy(symbols, on_bar, on_fill, timeout=60)

    except KeyboardInterrupt:
        print("\n\n전략 중지")
        live.stop()

    print("\n전략 실행 완료")


# ============================================================================
# 예제 6: 과거 데이터 조회
# ============================================================================

def run_history_query():
    """과거 데이터 조회 예제"""

    print("=" * 60)
    print("과거 데이터 조회 예제")
    print("=" * 60)

    live = create_live_client()
    if live is None:
        return

    symbol = "005930"
    end_date = date.today()
    start_date = end_date - timedelta(days=30)

    print(f"\n종목: {symbol} (삼성전자)")
    print(f"기간: {start_date} ~ {end_date}")

    try:
        bars = live.get_history(
            symbol=symbol,
            start=start_date.strftime("%Y-%m-%d"),
            end=end_date.strftime("%Y-%m-%d"),
        )

        print(f"\n수신 데이터: {len(bars)}건")
        print("-" * 60)

        # 최근 5일 데이터 출력
        for bar in bars[-5:]:
            print(
                f"  {bar.time.strftime('%Y-%m-%d')}: "
                f"시가 {bar.open:,.0f} / 고가 {bar.high:,.0f} / "
                f"저가 {bar.low:,.0f} / 종가 {bar.close:,.0f} / "
                f"거래량 {bar.volume:,}"
            )

    except Exception as e:
        print(f"데이터 조회 실패: {e}")


# ============================================================================
# 메인 실행
# ============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="KIS Backtest 라이브 트레이딩 예제")
    parser.add_argument(
        "--example",
        choices=[
            "manual",     # 수동 주문
            "position",   # 포지션 관리
            "limit",      # 지정가 주문
            "stream",     # 실시간 시세
            "strategy",   # 전략 실행
            "history",    # 과거 데이터
        ],
        default="manual",
        help="실행할 예제 선택"
    )
    args = parser.parse_args()

    examples = {
        "manual": run_manual_order,
        "position": run_position_management,
        "limit": run_limit_order,
        "stream": run_realtime_streaming,
        "strategy": run_live_strategy,
        "history": run_history_query,
    }

    try:
        examples[args.example]()
    except KeyboardInterrupt:
        print("\n\n중단됨")

    print("\n✅ 완료!")
