"""한국투자증권 브로커리지 Provider

주문, 잔고 조회, 체결 통보.
"""

import logging
from datetime import datetime
from typing import Callable, List, Optional

import os
from ...models import Order, Position, OrderSide, OrderType, OrderStatus
from ...models.trading import AccountBalance, Subscription
from ...exceptions import KISError, KISOrderError
from .auth import KISAuth
from .constants import ApiPath, TrId, OrderDivision
from .websocket import KISWebSocket, FillNotice

logger = logging.getLogger(__name__)


class KISBrokerageProvider:
    """한국투자증권 브로커리지 제공자
    
    BrokerageProvider Protocol 구현.
    """
    
    def __init__(
        self,
        app_key: str,
        app_secret: str,
        account_no: str,
        is_paper: bool = True,
        prod_code: str = "01"
    ):
        """
        Args:
            app_key: 앱키
            app_secret: 앱시크리트
            account_no: 계좌번호
            is_paper: 모의투자 여부
            prod_code: 상품코드
        """
        self._auth = KISAuth(app_key, app_secret, account_no, is_paper, prod_code)
        self._ws_client = None
        logger.info(f"KISBrokerageProvider 초기화: is_paper={is_paper}")

    @classmethod
    def from_auth(cls, auth: KISAuth) -> "KISBrokerageProvider":
        """KISAuth 인스턴스에서 직접 생성 (중복 ka.auth() 호출 방지)"""
        instance = cls.__new__(cls)
        instance._auth = auth
        instance._ws_client = None
        logger.info(f"KISBrokerageProvider 초기화: is_paper={auth.is_paper}")
        return instance

    def submit_order(
        self,
        symbol: str,
        side: OrderSide,
        quantity: int,
        order_type: OrderType = OrderType.MARKET,
        price: Optional[float] = None
    ) -> Order:
        """주문 제출
        
        API: /uapi/domestic-stock/v1/trading/order-cash
        TR ID:
        - 매수 실전: TTTC0802U, 모의: VTTC0802U
        - 매도 실전: TTTC0801U, 모의: VTTC0801U
        """
        # TR ID 결정 (개발계면 항상 실전 TR)
        if side == OrderSide.BUY:
            tr_id = self._get_tr_id(TrId.CASH_BUY_REAL, TrId.CASH_BUY_PAPER)
        else:
            tr_id = self._get_tr_id(TrId.CASH_SELL_REAL, TrId.CASH_SELL_PAPER)
        
        # 주문구분 및 가격
        if order_type == OrderType.MARKET:
            ord_dvsn = OrderDivision.MARKET
            ord_unpr = "0"
        else:
            ord_dvsn = OrderDivision.LIMIT
            if price is None:
                raise KISOrderError("지정가 주문은 가격이 필요합니다.")
            ord_unpr = str(int(price))
        
        body = {
            "CANO": self._auth.account_no,
            "ACNT_PRDT_CD": self._auth.account_prod,
            "PDNO": symbol,
            "ORD_DVSN": ord_dvsn,
            "ORD_QTY": str(quantity),
            "ORD_UNPR": ord_unpr,
        }
        
        resp = self._auth.post(ApiPath.DOMESTIC_ORDER, body, tr_id)
        
        if not resp.is_ok():
            raise KISOrderError(
                f"주문 실패: {resp.error_message}",
                error_code=resp.error_code,
                error_message=resp.error_message
            )
        
        output = resp.get_output()
        order_no = output.get("ODNO", "") if output else ""
        
        return Order(
            id=order_no,
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
            filled_quantity=0,
            average_price=0,
            status=OrderStatus.SUBMITTED,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    
    def cancel_order(self, order_id: str) -> bool:
        """주문 취소
        
        API: /uapi/domestic-stock/v1/trading/order-rvsecncl
        TR ID: TTTC0803U (실전), VTTC0803U (모의)
        """
        tr_id = self._get_tr_id(TrId.ORDER_CANCEL_REAL, TrId.ORDER_CANCEL_PAPER)
        
        body = {
            "CANO": self._auth.account_no,
            "ACNT_PRDT_CD": self._auth.account_prod,
            "KRX_FWDG_ORD_ORGNO": "",
            "ORGN_ODNO": order_id,
            "ORD_DVSN": "00",
            "RVSE_CNCL_DVSN_CD": "02",  # 취소
            "ORD_QTY": "0",
            "ORD_UNPR": "0",
            "QTY_ALL_ORD_YN": "Y"  # 전량
        }
        
        resp = self._auth.post(ApiPath.DOMESTIC_CANCEL, body, tr_id)
        
        if resp.is_ok():
            logger.info(f"주문 취소 완료: {order_id}")
            return True
        else:
            logger.error(f"주문 취소 실패: {order_id} - {resp.error_message}")
            return False
    
    def modify_order(
        self,
        order_id: str,
        quantity: Optional[int] = None,
        price: Optional[float] = None
    ) -> Order:
        """주문 정정
        
        API: /uapi/domestic-stock/v1/trading/order-rvsecncl
        TR ID: TTTC0803U (실전), VTTC0803U (모의)
        """
        tr_id = self._get_tr_id(TrId.ORDER_CANCEL_REAL, TrId.ORDER_CANCEL_PAPER)
        
        body = {
            "CANO": self._auth.account_no,
            "ACNT_PRDT_CD": self._auth.account_prod,
            "KRX_FWDG_ORD_ORGNO": "",
            "ORGN_ODNO": order_id,
            "ORD_DVSN": "00",
            "RVSE_CNCL_DVSN_CD": "01",  # 정정
            "ORD_QTY": str(quantity) if quantity else "0",
            "ORD_UNPR": str(int(price)) if price else "0",
            "QTY_ALL_ORD_YN": "N" if quantity else "Y"
        }
        
        resp = self._auth.post(ApiPath.DOMESTIC_CANCEL, body, tr_id)
        
        if not resp.is_ok():
            raise KISOrderError(f"주문 정정 실패: {resp.error_message}")
        
        output = resp.get_output()
        new_order_no = output.get("ODNO", "") if output else order_id
        
        return Order(
            id=new_order_no,
            symbol="",  # 원래 주문에서 가져와야 함
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT if price else OrderType.MARKET,
            quantity=quantity or 0,
            price=price,
            filled_quantity=0,
            average_price=0,
            status=OrderStatus.SUBMITTED,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    
    def get_positions(self) -> List[Position]:
        """포지션(잔고) 조회
        
        API: /uapi/domestic-stock/v1/trading/inquire-balance
        TR ID: TTTC8434R (실전), VTTC8434R (모의)
        """
        tr_id = self._get_tr_id(TrId.BALANCE_REAL, TrId.BALANCE_PAPER)
        
        params = {
            "CANO": self._auth.account_no,
            "ACNT_PRDT_CD": self._auth.account_prod,
            "AFHR_FLPR_YN": "N",
            "OFL_YN": "",
            "INQR_DVSN": "02",
            "UNPR_DVSN": "01",
            "FUND_STTL_ICLD_YN": "N",
            "FNCG_AMT_AUTO_RDPT_YN": "N",
            "PRCS_DVSN": "01",
            "CTX_AREA_FK100": "",
            "CTX_AREA_NK100": ""
        }
        
        resp = self._auth.get(ApiPath.DOMESTIC_BALANCE, params, tr_id)
        
        if not resp.is_ok():
            raise KISError(f"잔고 조회 실패: {resp.error_message}")
        
        data = resp.get_output1()
        if not data:
            return []
        
        positions = []
        for item in data:
            try:
                qty = int(item.get("hldg_qty", 0))
                if qty <= 0:
                    continue
                
                positions.append(Position(
                    symbol=item.get("pdno", ""),
                    quantity=qty,
                    average_price=float(item.get("pchs_avg_pric", 0)),
                    current_price=float(item.get("prpr", 0)),
                    unrealized_pnl=float(item.get("evlu_pfls_amt", 0)),
                    unrealized_pnl_percent=float(item.get("evlu_pfls_rt", 0)),
                    name=item.get("prdt_name", ""),
                ))
            except (ValueError, TypeError) as e:
                logger.warning(f"잔고 파싱 오류: {e}")
                continue
        
        logger.info(f"잔고 조회 완료: {len(positions)}건")
        return positions
    
    def _get_tr_id(self, real_tr: str, paper_tr: str) -> str:
        """TR ID 결정"""
        return paper_tr if self._auth.is_paper else real_tr
    
    def get_balance(self) -> AccountBalance:
        """계좌 잔고 조회
        
        잔고 조회 API의 output2 사용.
        """
        tr_id = self._get_tr_id(TrId.BALANCE_REAL, TrId.BALANCE_PAPER)
        
        params = {
            "CANO": self._auth.account_no,
            "ACNT_PRDT_CD": self._auth.account_prod,
            "AFHR_FLPR_YN": "N",
            "OFL_YN": "",
            "INQR_DVSN": "02",
            "UNPR_DVSN": "01",
            "FUND_STTL_ICLD_YN": "N",
            "FNCG_AMT_AUTO_RDPT_YN": "N",
            "PRCS_DVSN": "01",
            "CTX_AREA_FK100": "",
            "CTX_AREA_NK100": ""
        }
        
        resp = self._auth.get(ApiPath.DOMESTIC_BALANCE, params, tr_id)
        
        if not resp.is_ok():
            raise KISError(f"잔고 조회 실패: {resp.error_message}")
        
        data = resp.get_output2()
        if not data or len(data) == 0:
            return AccountBalance(
                total_cash=0,
                available_cash=0,
                total_equity=0,
                total_pnl=0,
                total_pnl_percent=0,
                currency="KRW"
            )
        
        item = data[0] if isinstance(data, list) else data
        
        return AccountBalance(
            total_cash=float(item.get("dnca_tot_amt", 0)),
            available_cash=float(item.get("nass_amt", 0)),
            total_equity=float(item.get("tot_evlu_amt", 0)),
            total_pnl=float(item.get("evlu_pfls_smtl_amt", 0)),
            total_pnl_percent=float(item.get("evlu_pfls_rt", 0)),
            currency="KRW"
        )
    
    def get_orders(self, status: Optional[OrderStatus] = None) -> List[Order]:
        """주문 내역 조회
        
        API: /uapi/domestic-stock/v1/trading/inquire-daily-ccld
        TR ID: TTTC8001R (실전), VTTC8001R (모의)
        
        TODO: 구현 필요
        """
        logger.warning("주문 내역 조회는 아직 구현되지 않음")
        return []
    
    def subscribe_fills(
        self,
        on_fill: Callable[[Order], None],
        hts_id: Optional[str] = None,
        timeout: Optional[float] = None
    ) -> Subscription:
        """체결 통보 구독
        
        WebSocket tr_id: H0STCNI0 (체결 통보)
        
        Args:
            on_fill: 콜백 함수 (Order) -> None
            hts_id: HTS ID. None이면 kis_devlp.yaml의 my_htsid 사용
            timeout: 타임아웃 (초). None이면 무한 실행
        
        Returns:
            Subscription 객체
        """
        if hts_id is None:
            # kis_devlp.yaml에서 자동 로드
            import sys
            from pathlib import Path
            _root = Path(__file__).resolve().parents[3]
            if str(_root) not in sys.path:
                sys.path.insert(0, str(_root))
            import kis_auth as ka
            env = ka.getEnv()
            hts_id = env.get("my_htsid", "")
        
        if not hts_id:
            raise KISError("HTS ID가 필요합니다. ~/KIS/config/kis_devlp.yaml의 my_htsid를 설정하세요.")
        
        # WebSocket 클라이언트 생성 (kis_auth 기반)
        if self._ws_client is None:
            self._ws_client = KISWebSocket.from_auth(self._auth, hts_id)
        
        # FillNotice를 Order로 변환하는 래퍼
        def notice_to_order(notice: FillNotice):
            try:
                side = OrderSide.BUY if notice.side == "02" else OrderSide.SELL
                status = OrderStatus.FILLED if notice.is_fill else OrderStatus.SUBMITTED
                
                if notice.is_rejected:
                    status = OrderStatus.REJECTED
                
                order = Order(
                    id=notice.order_no,
                    symbol=notice.symbol,
                    side=side,
                    order_type=OrderType.LIMIT,
                    quantity=notice.order_qty,
                    price=float(notice.fill_price) if notice.fill_price else None,
                    filled_quantity=notice.fill_qty,
                    average_price=float(notice.fill_price) if notice.fill_price else 0,
                    status=status,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                on_fill(order)
            except Exception as e:
                logger.error(f"Order 변환 오류: {e}")
        
        self._ws_client.subscribe_fills(notice_to_order)
        
        sub_id = f"fills_{datetime.now().timestamp()}"
        logger.info(f"체결 통보 구독 시작: {hts_id}")
        
        # 블로킹 실행
        self._ws_client.start(timeout=timeout)
        
        return Subscription(
            id=sub_id,
            symbols=[],
            is_active=False
        )
    
    def subscribe_fills_async(
        self,
        on_fill: Callable[[Order], None],
        hts_id: Optional[str] = None
    ) -> "KISWebSocket":
        """체결 통보 구독 (비동기)
        
        WebSocket 클라이언트를 반환하여 호출자가 직접 start()를 호출.
        
        Returns:
            KISWebSocket 클라이언트 (호출자가 .start() 호출 필요)
        """
        if hts_id is None:
            # kis_devlp.yaml에서 자동 로드
            import sys
            from pathlib import Path
            _root = Path(__file__).resolve().parents[3]
            if str(_root) not in sys.path:
                sys.path.insert(0, str(_root))
            import kis_auth as ka
            env = ka.getEnv()
            hts_id = env.get("my_htsid", "")
        
        if not hts_id:
            raise KISError("HTS ID가 필요합니다. ~/KIS/config/kis_devlp.yaml의 my_htsid를 설정하세요.")
        
        if self._ws_client is None:
            self._ws_client = KISWebSocket.from_auth(self._auth, hts_id)
        
        def notice_to_order(notice: FillNotice):
            try:
                side = OrderSide.BUY if notice.side == "02" else OrderSide.SELL
                status = OrderStatus.FILLED if notice.is_fill else OrderStatus.SUBMITTED
                
                if notice.is_rejected:
                    status = OrderStatus.REJECTED
                
                order = Order(
                    id=notice.order_no,
                    symbol=notice.symbol,
                    side=side,
                    order_type=OrderType.LIMIT,
                    quantity=notice.order_qty,
                    price=float(notice.fill_price) if notice.fill_price else None,
                    filled_quantity=notice.fill_qty,
                    average_price=float(notice.fill_price) if notice.fill_price else 0,
                    status=status,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                on_fill(order)
            except Exception as e:
                logger.error(f"Order 변환 오류: {e}")
        
        self._ws_client.subscribe_fills(notice_to_order)
        logger.info(f"체결 통보 구독 등록: {hts_id}")
        
        return self._ws_client
