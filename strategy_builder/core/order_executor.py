"""
주문 실행 모듈

Applied Skills: skills/investment-strategy-framework.md
- Signal → 실제 주문 변환
- 주문 전 검증 수행
- 주문 구분 매핑
"""

import logging
import math

import pandas as pd

import kis_auth as ka
from core import data_fetcher
from core.position_manager import PositionManager
from core.risk_manager import RiskManager
from core.signal import Action, Signal

logging.basicConfig(level=logging.INFO)


class OrderExecutor:
    """
    주문 실행 클래스
    """

    def __init__(self, env_dv: str = "demo", allow_duplicate_buy: bool = True):
        """
        Args:
            env_dv: 환경 구분 (real/demo, prod/vps)
            allow_duplicate_buy: 중복 매수 허용 여부 (기본값: True)
                - True: 이미 보유 중인 종목도 추가 매수 가능
                - False: 이미 보유 중인 종목 매수 불가 (기존 동작)
        """
        self.env_dv = env_dv
        self.allow_duplicate_buy = allow_duplicate_buy
        self.position_manager = PositionManager(env_dv)
        self.risk_manager = RiskManager()

    def execute_signal(self, signal: Signal) -> pd.DataFrame:
        """
        시그널을 실제 주문으로 실행

        Args:
            signal: 투자 시그널

        Returns:
            주문 결과 DataFrame (실패 시 빈 DataFrame)

        흐름:
            1. HOLD 시그널 → 무시
            2. 시그널 강도 체크
            3. 중복 주문 체크 (매수)
            4. 보유 여부 체크 (매도)
            5. 주문 파라미터 결정
            6. order_cash() 호출
        """
        # 1. HOLD 시그널 무시
        if signal.action == Action.HOLD:
            logging.info(f"HOLD 시그널 - 주문 생략: {signal.stock_name}")
            return pd.DataFrame()

        # 2. 시그널 강도 체크
        if not signal.is_actionable():
            logging.info(f"약한 시그널 - 주문 생략: {signal} (strength < 0.5)")
            return pd.DataFrame()

        # 3. 매수: 중복 보유 체크 (allow_duplicate_buy가 False일 때만)
        if signal.action == Action.BUY and not self.allow_duplicate_buy:
            if self.position_manager.check_duplicate(signal.stock_code):
                logging.warning(f"이미 보유 중 - 매수 생략: {signal.stock_name}")
                return pd.DataFrame()

        # 4. 매도: 보유 여부 체크
        if signal.action == Action.SELL:
            quantity = self.position_manager.get_holding_quantity(signal.stock_code)
            if quantity <= 0:
                logging.warning(f"미보유 종목 - 매도 생략: {signal.stock_name}")
                return pd.DataFrame()

        # 5. 주문 파라미터 결정
        ord_dvsn, ord_unpr = self._determine_order_type(signal)
        ord_qty = self._calculate_quantity(signal)

        if ord_qty <= 0:
            logging.warning(f"주문 수량 0 - 주문 생략: {signal.stock_name}")
            return pd.DataFrame()

        # 6. 주문 실행
        return self._execute_order(
            signal=signal,
            ord_dvsn=ord_dvsn,
            ord_unpr=ord_unpr,
            ord_qty=ord_qty
        )

    @staticmethod
    def _get_tick_size(price: int) -> int:
        """한국 주식시장 호가단위 (2023년 기준)"""
        if price < 2000:
            return 1
        elif price < 5000:
            return 5
        elif price < 20000:
            return 10
        elif price < 50000:
            return 50
        elif price < 200000:
            return 100
        elif price < 500000:
            return 500
        else:
            return 1000

    @staticmethod
    def _round_to_tick(price: int) -> int:
        """가격을 호가단위로 내림 (매수 시 유리한 방향)"""
        tick = OrderExecutor._get_tick_size(price)
        return int(math.floor(price / tick) * tick)

    def _determine_order_type(self, signal: Signal) -> tuple:
        """
        시그널 강도에 따른 주문 구분 결정

        skill:
            0.8 이상: 시장가 (ord_dvsn="01", ord_unpr="0")
            그 외: 지정가 (ord_dvsn="00", ord_unpr=현재가)

        Returns:
            (ord_dvsn, ord_unpr)
        """
        if signal.is_strong():
            return ("01", "0")

        # 지정가
        if signal.target_price:
            adjusted = self._round_to_tick(int(signal.target_price))
            if adjusted != int(signal.target_price):
                logging.info(
                    f"[호가단위 조정] {signal.target_price} → {adjusted} "
                    f"(tick={self._get_tick_size(int(signal.target_price))})"
                )
            return ("00", str(adjusted))

        # 현재가로 지정가
        price_info = data_fetcher.get_current_price(signal.stock_code, self.env_dv)
        current_price = price_info.get("price", 0)

        if current_price <= 0:
            return ("01", "0")

        adjusted = self._round_to_tick(int(current_price))
        return ("00", str(adjusted))

    def _calculate_quantity(self, signal: Signal) -> int:
        """
        주문 수량 계산

        Args:
            signal: 투자 시그널

        Returns:
            주문 수량
        """
        # 시그널에 수량이 지정된 경우
        if signal.quantity:
            return signal.quantity

        # 매도: 전량 매도
        if signal.action == Action.SELL:
            return self.position_manager.get_holding_quantity(signal.stock_code)

        # 매수: 기본 1주 (실제로는 투자금액 기반 계산 필요)
        return 1

    def _execute_order(
        self,
        signal: Signal,
        ord_dvsn: str,
        ord_unpr: str,
        ord_qty: int
    ) -> pd.DataFrame:
        """
        실제 주문 실행

        Args:
            signal: 투자 시그널
            ord_dvsn: 주문구분
            ord_unpr: 주문단가
            ord_qty: 주문수량

        Returns:
            주문 결과 DataFrame
        """
        try:
            trenv = ka.getTREnv()

            # TR_ID 설정
            if self.env_dv == "real":
                tr_id = "TTTC0802U" if signal.action == Action.BUY else "TTTC0801U"
            else:
                tr_id = "VTTC0802U" if signal.action == Action.BUY else "VTTC0801U"

            params = {
                "CANO": trenv.my_acct,
                "ACNT_PRDT_CD": trenv.my_prod,
                "PDNO": signal.stock_code,
                "ORD_DVSN": ord_dvsn,
                "ORD_QTY": str(ord_qty),
                "ORD_UNPR": ord_unpr,
            }

            ord_type_name = "시장가" if ord_dvsn == "01" else "지정가"
            logging.info(
                f"주문 실행: {signal.stock_name} "
                f"{signal.action.value.upper()} "
                f"{ord_qty}주 @ {ord_unpr}원 ({ord_type_name}, ord_dvsn={ord_dvsn})"
            )
            logging.info(f"[DEBUG] tr_id={tr_id}, CANO={trenv.my_acct}, ACNT_PRDT_CD={trenv.my_prod}, PDNO={signal.stock_code}, env_dv={self.env_dv}")

            res = ka._url_fetch(
                "/uapi/domestic-stock/v1/trading/order-cash",
                tr_id, "", params, postFlag=True
            )

            if res.isOK():
                result = pd.DataFrame([res.getBody().output])
                logging.info(f"주문 성공: {result.to_dict()}")

                # 포지션 캐시 갱신
                self.position_manager.refresh()

                return result
            else:
                logging.error(f"주문 실패: {signal.stock_name}")
                res.printError("/uapi/domestic-stock/v1/trading/order-cash")
                return pd.DataFrame()

        except Exception as e:
            logging.error(f"주문 실행 에러: {e}")
            return pd.DataFrame()

