#!/usr/bin/env python3
"""
기본 백테스트 예제

이 예제는 kis_backtest를 사용하여 간단한 백테스트를 수행하는 방법을 보여줍니다.
한국투자증권 API를 통해 데이터를 수집하고, Lean 엔진으로 백테스트를 실행합니다.

실행 방법:
    uv run python examples/basic_backtest.py --example basic
    uv run python examples/basic_backtest.py --example custom
    uv run python examples/basic_backtest.py --example all

필수 조건:
    - Docker Desktop 실행 중
    - KIS API 인증 설정 완료
"""

import os
import sys
from datetime import date, timedelta
from pathlib import Path

# 프로젝트 루트 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from kis_backtest import LeanClient
from kis_backtest.providers.kis import KISAuth, KISDataProvider

# 날짜 설정: 오늘 기준
TODAY = date.today()
ONE_YEAR_AGO = TODAY - timedelta(days=365)

# 날짜 문자열
START_DATE = ONE_YEAR_AGO.strftime("%Y-%m-%d")
END_DATE = TODAY.strftime("%Y-%m-%d")


def create_client():
    """KIS API 인증 및 LeanClient 생성"""
    print("\n[1/4] 한국투자증권 API 인증 중...")

    try:
        auth = KISAuth.from_env()
        data_provider = KISDataProvider(auth)

        mode_str = "모의투자" if auth.is_paper else "실전투자"
        print(f"  ✓ 인증 성공 ({mode_str}, 계좌: {auth.acct_masked})")

        return LeanClient(data_provider=data_provider)
    except Exception as e:
        print(f"  ✗ 인증 실패: {e}")
        print("\n💡 KIS API 인증 정보를 설정하세요.")
        return None


# ============================================================================
# 예제 1: 내장 전략 백테스트 (backtest_strategy)
# ============================================================================

def run_builtin_strategy_backtest():
    """내장 SMA 크로스오버 전략 백테스트"""

    print("=" * 60)
    print("예제 1: 내장 전략 백테스트 (SMA 크로스오버)")
    print("=" * 60)

    client = create_client()
    if client is None:
        return None

    # 내장 전략 사용 (sma_crossover)
    print("\n[2/4] 백테스트 설정...")
    print(f"  - 전략: sma_crossover (단기MA 10일, 장기MA 30일)")
    print(f"  - 종목: 005930 (삼성전자)")
    print(f"  - 기간: {START_DATE} ~ {END_DATE}")
    print(f"  - 초기자본: 1억원")

    print("\n[3/4] 백테스트 실행 중...")
    print("  (Docker 이미지 다운로드 시 시간이 걸릴 수 있습니다)")

    try:
        result = client.backtest_strategy(
            strategy_id="sma_crossover",
            symbols=["005930"],
            start_date=START_DATE,
            end_date=END_DATE,
            params={
                "fast_period": 10,
                "slow_period": 30,
            },
            initial_cash=100_000_000,
            market_type="krx",
        )

        # 결과 출력
        print("\n[4/4] 백테스트 결과")
        print("-" * 40)
        print(f"  총 수익률: {result.total_return_pct:.2f}%")
        print(f"  연간 수익률 (CAGR): {result.cagr:.2f}%")
        print(f"  샤프 비율: {result.sharpe_ratio:.2f}")
        print(f"  소르티노 비율: {result.sortino_ratio:.2f}")
        print(f"  최대 낙폭: {result.max_drawdown:.2f}%")
        print(f"  총 거래 수: {result.total_trades}")
        print(f"  승률: {result.win_rate:.1%}")
        print(f"  수익/손실 비율: {result.profit_factor:.2f}")
        print(f"  실행 시간: {result.duration_seconds:.1f}초")
        print("-" * 40)

        # 리포트 생성
        output_dir = Path("examples/output/reports")
        output_dir.mkdir(parents=True, exist_ok=True)

        report_path = client.report(
            result=result,
            output_path=output_dir / "sma_crossover_report.html",
            title="SMA 크로스오버 전략 백테스트",
            subtitle=f"삼성전자 (005930) | {START_DATE} ~ {END_DATE}",
        )
        print(f"\n📊 리포트 생성: {report_path}")

        print("\n" + "=" * 60)
        print("백테스트 완료!")
        print("=" * 60)

        return result

    except Exception as e:
        print(f"\n❌ 백테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return None


# ============================================================================
# 예제 2: 커스텀 알고리즘 백테스트 (backtest_custom)
# ============================================================================

def get_custom_strategy_code():
    """커스텀 전략 코드 생성

    KRX 주식은 AddData + KRXEquity 커스텀 데이터 클래스 사용
    """
    return f'''
from AlgorithmImports import *

class KRXEquity(PythonData):
    """한국 주식 커스텀 데이터"""

    def GetSource(self, config, date, isLive):
        symbol = config.Symbol.Value.lower()
        source = f"/Data/equity/krx/daily/{{symbol}}.csv"
        return SubscriptionDataSource(source, SubscriptionTransportMedium.LocalFile, FileFormat.Csv)

    def Reader(self, config, line, date, isLive):
        if not line.strip():
            return None

        data = KRXEquity()
        data.Symbol = config.Symbol

        try:
            cols = line.split(",")
            data.Time = datetime.strptime(cols[0], "%Y%m%d")
            data.Value = float(cols[4])
            data["Open"] = float(cols[1])
            data["High"] = float(cols[2])
            data["Low"] = float(cols[3])
            data["Close"] = float(cols[4])
            data["Volume"] = int(cols[5])
        except Exception:
            return None

        return data


class RSIMeanReversion(QCAlgorithm):
    """
    RSI 평균 회귀 전략

    - RSI가 30 이하로 하락 후 30을 상향 돌파하면 매수
    - RSI가 70 이상으로 상승 후 70을 하향 돌파하면 매도
    """

    def Initialize(self):
        self.SetStartDate({ONE_YEAR_AGO.year}, {ONE_YEAR_AGO.month}, {ONE_YEAR_AGO.day})
        self.SetEndDate({TODAY.year}, {TODAY.month}, {TODAY.day})
        self.SetCash(100000000)

        # KRX 주식은 커스텀 데이터 클래스 사용
        self.symbol = self.AddData(KRXEquity, "005930", Resolution.Daily).Symbol

        # 수동 RSI 계산
        self.rsi_period = 14
        self.prices = []
        self.rsi_value = 50
        self.prev_rsi = 50
        self.oversold = 30
        self.overbought = 70

        self.SetWarmUp(self.rsi_period + 5)

    def OnData(self, data):
        if not data.ContainsKey(self.symbol):
            return

        bar = data[self.symbol]
        if bar is None:
            return

        # 가격 저장 및 RSI 계산
        self.prices.append(bar.Close)
        if len(self.prices) > self.rsi_period + 1:
            self.prices.pop(0)

        if len(self.prices) >= self.rsi_period + 1:
            self.rsi_value = self._calculate_rsi()

        if self.IsWarmingUp:
            self.prev_rsi = self.rsi_value
            return

        holdings = self.Portfolio[self.symbol].Quantity
        current_rsi = self.rsi_value

        # 과매도 후 반등 (매수 신호)
        if self.prev_rsi <= self.oversold < current_rsi:
            if holdings <= 0:
                self.SetHoldings(self.symbol, 0.95)
                self.Debug(f"매수: {{self.Time}}, RSI={{current_rsi:.2f}}")

        # 과매수 후 하락 (매도 신호)
        elif self.prev_rsi >= self.overbought > current_rsi:
            if holdings > 0:
                self.Liquidate(self.symbol)
                self.Debug(f"매도: {{self.Time}}, RSI={{current_rsi:.2f}}")

        self.prev_rsi = current_rsi

    def _calculate_rsi(self):
        """RSI 계산"""
        gains = []
        losses = []
        for i in range(1, len(self.prices)):
            change = self.prices[i] - self.prices[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))

        avg_gain = sum(gains[-self.rsi_period:]) / self.rsi_period
        avg_loss = sum(losses[-self.rsi_period:]) / self.rsi_period

        if avg_loss == 0:
            return 100

        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))
'''


def run_custom_strategy_backtest():
    """커스텀 알고리즘 코드로 백테스트"""

    print("=" * 60)
    print("예제 2: 커스텀 알고리즘 백테스트 (RSI 평균회귀)")
    print("=" * 60)

    client = create_client()
    if client is None:
        return None

    print("\n[2/4] 백테스트 설정...")
    print(f"  - 전략: RSI 평균회귀 (RSI 14)")
    print(f"  - 종목: 005930 (삼성전자)")
    print(f"  - 기간: {START_DATE} ~ {END_DATE}")
    print(f"  - 매수: RSI 30 하향 돌파 후 반등")
    print(f"  - 매도: RSI 70 상향 돌파 후 하락")

    print("\n[3/4] 백테스트 실행 중...")

    try:
        # 커스텀 코드로 백테스트
        result = client.backtest_custom(
            algorithm_code=get_custom_strategy_code(),
            symbols=["005930"],
            start_date=START_DATE,
            end_date=END_DATE,
            initial_cash=100_000_000,
            market_type="krx",
        )

        # 결과 출력
        print("\n[4/4] 백테스트 결과")
        print("-" * 40)
        print(f"  총 수익률: {result.total_return_pct:.2f}%")
        print(f"  연간 수익률 (CAGR): {result.cagr:.2f}%")
        print(f"  샤프 비율: {result.sharpe_ratio:.2f}")
        print(f"  최대 낙폭: {result.max_drawdown:.2f}%")
        print(f"  총 거래 수: {result.total_trades}")
        print(f"  승률: {result.win_rate:.1%}")
        print(f"  실행 시간: {result.duration_seconds:.1f}초")
        print("-" * 40)

        # 리포트 생성
        output_dir = Path("examples/output/reports")
        output_dir.mkdir(parents=True, exist_ok=True)

        report_path = client.report(
            result=result,
            output_path=output_dir / "rsi_mean_reversion_report.html",
            title="RSI 평균회귀 전략 백테스트",
            subtitle=f"삼성전자 (005930) | {START_DATE} ~ {END_DATE}",
        )
        print(f"\n📊 리포트 생성: {report_path}")

        print("\n" + "=" * 60)
        print("백테스트 완료!")
        print("=" * 60)

        return result

    except Exception as e:
        print(f"\n❌ 백테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return None


# ============================================================================
# 메인 실행
# ============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="KIS Backtest 기본 백테스트 예제")
    parser.add_argument(
        "--example",
        choices=["basic", "custom", "all"],
        default="basic",
        help="실행할 예제 선택 (basic: 내장전략, custom: 커스텀코드, all: 전체)"
    )
    args = parser.parse_args()

    print("\n" + "🚀 " * 20)
    print("KIS Backtest 기본 백테스트 예제")
    print("🚀 " * 20)

    if args.example in ["basic", "all"]:
        run_builtin_strategy_backtest()

    if args.example in ["custom", "all"]:
        print("\n")
        run_custom_strategy_backtest()
