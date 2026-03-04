"""
10가지 기본 전략 실행 예제

모든 기본 전략을 실행하고 결과를 출력합니다.

사용법:
    python examples/run_all_strategies.py
    python examples/run_all_strategies.py --stock 005930
    python examples/run_all_strategies.py --env vps
"""

import argparse
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import kis_auth as ka
from strategy.strategy_01_golden_cross import GoldenCrossStrategy
from strategy.strategy_02_momentum import MomentumStrategy
from strategy.strategy_03_week52_high import Week52HighStrategy
from strategy.strategy_04_consecutive import ConsecutiveStrategy
from strategy.strategy_05_disparity import DisparityStrategy
from strategy.strategy_06_breakout_fail import BreakoutFailStrategy
from strategy.strategy_07_strong_close import StrongCloseStrategy
from strategy.strategy_08_volatility import VolatilityStrategy
from strategy.strategy_09_mean_reversion import MeanReversionStrategy
from strategy.strategy_10_trend_filter import TrendFilterStrategy

# 전략 목록
STRATEGIES = [
    ("01", "골든크로스", GoldenCrossStrategy),
    ("02", "모멘텀", MomentumStrategy),
    ("03", "52주 신고가", Week52HighStrategy),
    ("04", "연속 상승/하락", ConsecutiveStrategy),
    ("05", "이격도", DisparityStrategy),
    ("06", "돌파 실패", BreakoutFailStrategy),
    ("07", "강한 종가", StrongCloseStrategy),
    ("08", "변동성 확장", VolatilityStrategy),
    ("09", "평균회귀", MeanReversionStrategy),
    ("10", "추세 필터", TrendFilterStrategy),
]

# 테스트 종목
DEFAULT_STOCKS = [
    {"code": "005930", "name": "삼성전자"},
    {"code": "000660", "name": "SK하이닉스"},
    {"code": "035720", "name": "카카오"},
]


def run_all_strategies(stocks: list, verbose: bool = True):
    """모든 전략 실행"""
    results = []

    print("\n" + "=" * 70)
    print(" 10가지 기본 전략 실행")
    print("=" * 70)

    for num, name, strategy_class in STRATEGIES:
        strategy = strategy_class()

        print(f"\n[{num}] {name} (필요 일수: {strategy.required_days})")
        print("-" * 50)

        for stock in stocks:
            try:
                signal = strategy.generate_signal(stock["code"], stock["name"])

                action_symbol = {
                    "buy": "▲ BUY ",
                    "sell": "▼ SELL",
                    "hold": "  HOLD"
                }[signal.action.value]

                print(f"  {stock['name']:10} [{stock['code']}] {action_symbol} "
                      f"강도={signal.strength:.2f} | {signal.reason}")

                results.append({
                    "strategy": name,
                    "stock": stock["name"],
                    "action": signal.action.value,
                    "strength": signal.strength,
                    "reason": signal.reason
                })

            except Exception as e:
                print(f"  {stock['name']:10} [{stock['code']}] 오류: {e}")

            time.sleep(0.5)  # API 호출 간격

    # 요약
    print("\n" + "=" * 70)
    print(" 결과 요약")
    print("=" * 70)

    buy_signals = [r for r in results if r["action"] == "buy"]
    sell_signals = [r for r in results if r["action"] == "sell"]

    print(f"\n총 시그널: {len(results)}")
    print(f"  매수 시그널: {len(buy_signals)}")
    print(f"  매도 시그널: {len(sell_signals)}")
    print(f"  홀드: {len(results) - len(buy_signals) - len(sell_signals)}")

    if buy_signals:
        print("\n[매수 시그널]")
        for r in buy_signals:
            print(f"  - {r['strategy']}: {r['stock']} (강도={r['strength']:.2f})")

    if sell_signals:
        print("\n[매도 시그널]")
        for r in sell_signals:
            print(f"  - {r['strategy']}: {r['stock']} (강도={r['strength']:.2f})")

    print("\n" + "=" * 70)

    return results


def main():
    parser = argparse.ArgumentParser(description="10가지 기본 전략 실행")
    parser.add_argument("--stock", type=str, help="특정 종목만 테스트 (종목코드)")
    parser.add_argument("--env", type=str, default="vps",
                        choices=["prod", "vps"], help="실행 환경 (prod=실전, vps=모의)")
    parser.add_argument("--name", type=str, default="종목", help="종목명 (--stock과 함께 사용)")

    args = parser.parse_args()

    # 인증
    print("KIS API 인증 중...")
    ka.auth(svr=args.env)
    print("인증 완료\n")

    # 종목 설정
    if args.stock:
        stocks = [{"code": args.stock, "name": args.name}]
    else:
        stocks = DEFAULT_STOCKS

    # 실행
    run_all_strategies(stocks)


if __name__ == "__main__":
    main()
