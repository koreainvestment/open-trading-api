"""한국투자증권 WebSocket 클라이언트

kis_auth.py 기반 구현 - 환경변수 불필요.

실시간 시세 및 체결 통보 수신.

사용 예:
    from kis_backtest.providers.kis.websocket import KISWebSocket
    from kis_backtest.providers.kis.auth import KISAuth
    
    auth = KISAuth.from_env()
    ws = KISWebSocket.from_auth(auth)
    
    # 실시간 체결가 구독
    def on_price(symbol, data):
        print(f"{symbol}: {data['price']}")
    
    ws.subscribe_price(["005930", "000660"], on_price)
    ws.start()
"""

import asyncio
import json
import logging
import sys
import time
from base64 import b64decode
from collections import namedtuple
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from io import StringIO
from pathlib import Path
from typing import Dict, List, Optional, Any

import pandas as pd
import requests
import websockets
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

# kis_auth import
_root = Path(__file__).resolve().parents[3]  # backtester 루트
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

import kis_auth as ka

logger = logging.getLogger(__name__)


# ============================================
# 상수
# ============================================

class WsTrId:
    """WebSocket TR ID"""
    # 실시간 체결가
    REALTIME_PRICE = "H0STCNT0"
    # 실시간 호가
    REALTIME_QUOTE = "H0STASP0"
    # 체결 통보 (실전)
    FILL_NOTICE_REAL = "H0STCNI0"
    # 체결 통보 (모의)
    FILL_NOTICE_PAPER = "H0STCNI9"


# 실시간 체결가 컬럼
PRICE_COLUMNS = [
    "MKSC_SHRN_ISCD", "STCK_CNTG_HOUR", "STCK_PRPR", "PRDY_VRSS_SIGN",
    "PRDY_VRSS", "PRDY_CTRT", "WGHN_AVRG_STCK_PRC", "STCK_OPRC",
    "STCK_HGPR", "STCK_LWPR", "ASKP1", "BIDP1", "CNTG_VOL", "ACML_VOL",
    "ACML_TR_PBMN", "SELN_CNTG_CSNU", "SHNU_CNTG_CSNU", "NTBY_CNTG_CSNU",
    "CTTR", "SELN_CNTG_SMTN", "SHNU_CNTG_SMTN", "CCLD_DVSN", "SHNU_RATE",
    "PRDY_VOL_VRSS_ACML_VOL_RATE", "OPRC_HOUR", "OPRC_VRSS_PRPR_SIGN",
    "OPRC_VRSS_PRPR", "HGPR_HOUR", "HGPR_VRSS_PRPR_SIGN", "HGPR_VRSS_PRPR",
    "LWPR_HOUR", "LWPR_VRSS_PRPR_SIGN", "LWPR_VRSS_PRPR", "BSOP_DATE",
    "NEW_MKOP_CLS_CODE", "TRHT_YN", "ASKP_RSQN1", "BIDP_RSQN1",
    "TOTAL_ASKP_RSQN", "TOTAL_BIDP_RSQN", "VOL_TNRT",
    "PRDY_SMNS_HOUR_ACML_VOL", "PRDY_SMNS_HOUR_ACML_VOL_RATE",
    "HOUR_CLS_CODE", "MRKT_TRTM_CLS_CODE", "VI_STND_PRC"
]

# 체결 통보 컬럼
FILL_COLUMNS = [
    "CUST_ID", "ACNT_NO", "ODER_NO", "ODER_QTY", "SELN_BYOV_CLS", "RCTF_CLS",
    "ODER_KIND", "ODER_COND", "STCK_SHRN_ISCD", "CNTG_QTY", "CNTG_UNPR",
    "STCK_CNTG_HOUR", "RFUS_YN", "CNTG_YN", "ACPT_YN", "BRNC_NO", "ACNT_NO2",
    "ACNT_NAME", "ORD_COND_PRC", "ORD_EXG_GB", "POPUP_YN", "FILLER", "CRDT_CLS",
    "CRDT_LOAN_DATE", "CNTG_ISNM40", "ODER_PRC"
]


# ============================================
# 데이터 모델
# ============================================

@dataclass
class RealtimePrice:
    """실시간 체결가 데이터"""
    symbol: str              # 종목코드
    time: str                # 체결시간 (HHMMSS)
    price: int               # 현재가
    change_sign: str         # 전일대비부호 (1:상한, 2:상승, 3:보합, 4:하한, 5:하락)
    change: int              # 전일대비
    change_rate: float       # 전일대비율
    open_price: int          # 시가
    high_price: int          # 고가
    low_price: int           # 저가
    volume: int              # 체결거래량
    total_volume: int        # 누적거래량
    ask_price: int           # 매도호가1
    bid_price: int           # 매수호가1


@dataclass
class FillNotice:
    """체결 통보 데이터"""
    customer_id: str         # 고객ID
    account_no: str          # 계좌번호
    order_no: str            # 주문번호
    order_qty: int           # 주문수량
    side: str                # 매도매수구분 (01:매도, 02:매수)
    symbol: str              # 종목코드
    fill_qty: int            # 체결수량
    fill_price: int          # 체결단가
    fill_time: str           # 체결시간
    is_fill: bool            # 체결여부 (True:체결, False:접수)
    is_rejected: bool        # 거부여부


# ============================================
# 유틸리티 함수
# ============================================

def aes_cbc_base64_dec(key: str, iv: str, cipher_text: str) -> str:
    """AES CBC 복호화"""
    if key is None or iv is None:
        raise AttributeError("key and iv cannot be None")
    
    cipher = AES.new(key.encode("utf-8"), AES.MODE_CBC, iv.encode("utf-8"))
    return bytes.decode(unpad(cipher.decrypt(b64decode(cipher_text)), AES.block_size))


def parse_system_response(data: str) -> dict:
    """시스템 응답 파싱 (구독 확인, PINGPONG 등)"""
    rdic = json.loads(data)
    
    tr_id = rdic["header"]["tr_id"]
    tr_key = rdic["header"].get("tr_key")
    encrypt = rdic["header"].get("encrypt")
    
    is_ok = False
    is_unsub = False
    is_pingpong = False
    tr_msg = None
    iv = None
    ekey = None
    
    if rdic.get("body") is not None:
        is_ok = rdic["body"].get("rt_cd") == "0"
        tr_msg = rdic["body"].get("msg1", "")
        
        if "output" in rdic["body"]:
            iv = rdic["body"]["output"].get("iv")
            ekey = rdic["body"]["output"].get("key")
        
        is_unsub = tr_msg.startswith("UNSUB") if tr_msg else False
    else:
        is_pingpong = tr_id == "PINGPONG"
    
    return {
        "is_ok": is_ok,
        "tr_id": tr_id,
        "tr_key": tr_key,
        "tr_msg": tr_msg,
        "is_unsub": is_unsub,
        "is_pingpong": is_pingpong,
        "iv": iv,
        "ekey": ekey,
        "encrypt": encrypt,
    }


# ============================================
# WebSocket 클라이언트
# ============================================

class KISWebSocket:
    """한국투자증권 WebSocket 클라이언트 - kis_auth 기반
    
    kis_auth.py의 auth_ws(), KISWebSocket 사용.
    """
    
    def __init__(
        self,
        auth: "KISAuth",  # type: ignore
        hts_id: Optional[str] = None
    ):
        """
        Args:
            auth: KISAuth 인스턴스
            hts_id: HTS ID (체결통보에 필요, None이면 kis_devlp.yaml의 my_htsid 사용)
        """
        self.auth = auth
        self.is_paper = auth.is_paper
        
        # HTS ID
        if hts_id:
            self.hts_id = hts_id
        else:
            # kis_devlp.yaml에서 자동 로드
            env = ka.getEnv()
            self.hts_id = env.get("my_htsid", "")
        
        # kis_auth 환경 사용
        tr_env = ka.getTREnv()
        self._api_url = tr_env.my_url
        self._ws_url = tr_env.my_url_ws
        
        # kis_auth의 auth_ws() 호출하여 approval_key 발급
        svr = "vps" if self.is_paper else "prod"
        ka.auth_ws(svr=svr)
        
        # 구독 관리
        self._subscriptions: Dict[str, dict] = {}
        self._data_map: Dict[str, dict] = {}
        
        # 콜백
        self._price_callback: Optional[Callable[[str, RealtimePrice], None]] = None
        self._fill_callback: Optional[Callable[[FillNotice], None]] = None
        self._on_result: Optional[Callable] = None
        
        # 재연결
        self._max_retries = 5
        self._retry_count = 0
        self._running = False
        
        logger.info(f"KISWebSocket (kis_auth) 초기화: is_paper={self.is_paper}, ws_url={self._ws_url}")
    
    @classmethod
    def from_auth(cls, auth: "KISAuth", hts_id: Optional[str] = None) -> "KISWebSocket":  # type: ignore
        """KISAuth 인스턴스로 초기화 (권장)
        
        Args:
            auth: KISAuth 인스턴스
            hts_id: HTS ID (선택, None이면 kis_devlp.yaml에서 자동 로드)
        
        Returns:
            KISWebSocket 인스턴스
        """
        return cls(auth, hts_id)
    
    @classmethod
    def from_env(cls, mode: Optional[str] = None, hts_id: Optional[str] = None) -> "KISWebSocket":
        """환경변수 대신 kis_devlp.yaml에서 로드 (하위 호환)
        
        Args:
            mode: "live" 또는 "paper" (None이면 "paper")
            hts_id: HTS ID (선택)
        
        Returns:
            KISWebSocket 인스턴스
        """
        from .auth import KISAuth
        auth = KISAuth.from_env(mode)
        return cls(auth, hts_id)
    
    # ========================================
    # 접속키 발급
    # ========================================
    
    def get_approval_key(self) -> str:
        """WebSocket 접속키 반환
        
        kis_auth.auth_ws()가 이미 호출되어 approval_key 발급됨.
        """
        # kis_auth의 _base_headers_ws에서 approval_key 가져오기
        headers_ws = ka._getBaseHeader_ws()
        approval_key = headers_ws.get("approval_key", "")
        
        if not approval_key:
            # 재발급
            svr = "vps" if self.is_paper else "prod"
            ka.auth_ws(svr=svr)
            headers_ws = ka._getBaseHeader_ws()
            approval_key = headers_ws.get("approval_key", "")
        
        return approval_key
    
    # ========================================
    # 구독 요청 생성
    # ========================================
    
    def _create_subscribe_message(self, tr_id: str, tr_key: str, tr_type: str = "1") -> dict:
        """구독 요청 메시지 생성
        
        Args:
            tr_id: TR ID (예: H0STCNT0)
            tr_key: 종목코드 또는 HTS ID
            tr_type: "1"=등록, "2"=해제
        """
        approval_key = self.get_approval_key()
        return {
            "header": {
                "approval_key": approval_key,
                "custtype": "P",
                "tr_type": tr_type,
                "content-type": "utf-8"
            },
            "body": {
                "input": {
                    "tr_id": tr_id,
                    "tr_key": tr_key
                }
            }
        }
    
    def _price_request(self, tr_type: str, tr_key: str, **kwargs) -> tuple:
        """실시간 체결가 요청 생성"""
        msg = self._create_subscribe_message(WsTrId.REALTIME_PRICE, tr_key, tr_type)
        return msg, PRICE_COLUMNS
    
    def _fill_request(self, tr_type: str, tr_key: str, **kwargs) -> tuple:
        """체결 통보 요청 생성"""
        tr_id = WsTrId.FILL_NOTICE_PAPER if self.is_paper else WsTrId.FILL_NOTICE_REAL
        msg = self._create_subscribe_message(tr_id, tr_key, tr_type)
        return msg, FILL_COLUMNS
    
    # ========================================
    # 구독 관리
    # ========================================
    
    def subscribe_price(
        self,
        symbols: List[str],
        callback: Callable[[str, RealtimePrice], None]
    ) -> None:
        """실시간 체결가 구독
        
        Args:
            symbols: 종목코드 리스트 (예: ["005930", "000660"])
            callback: 콜백 함수 (symbol, RealtimePrice) -> None
        """
        self._price_callback = callback
        
        name = "price"
        if name not in self._subscriptions:
            self._subscriptions[name] = {
                "func": self._price_request,
                "items": [],
                "kwargs": None
            }
        
        if isinstance(symbols, str):
            symbols = [symbols]
        
        self._subscriptions[name]["items"].extend(symbols)
        logger.info(f"실시간 체결가 구독 등록: {symbols}")
    
    def subscribe_fills(
        self,
        callback: Callable[[FillNotice], None],
        hts_id: Optional[str] = None
    ) -> None:
        """체결 통보 구독
        
        Args:
            callback: 콜백 함수 (FillNotice) -> None
            hts_id: HTS ID. None이면 self.hts_id 또는 환경변수 사용
        """
        if hts_id:
            self.hts_id = hts_id
        
        if not self.hts_id:
            raise ValueError("HTS ID가 필요합니다. KISWebSocket.from_auth() 사용을 권장합니다.")
        
        self._fill_callback = callback
        
        name = "fill"
        self._subscriptions[name] = {
            "func": self._fill_request,
            "items": [self.hts_id],
            "kwargs": None
        }
        logger.info(f"체결 통보 구독 등록: {self.hts_id}")
    
    # ========================================
    # 메시지 처리
    # ========================================
    
    async def _handle_message(self, ws, raw: str) -> None:
        """수신 메시지 처리"""
        logger.debug(f"수신: {raw[:100]}...")
        
        # 실시간 데이터 (0 또는 1로 시작)
        if raw[0] in ["0", "1"]:
            await self._handle_realtime_data(raw)
        # 시스템 메시지 (JSON)
        else:
            await self._handle_system_message(ws, raw)
    
    async def _handle_system_message(self, ws, raw: str) -> None:
        """시스템 메시지 처리 (구독 확인, PINGPONG 등)"""
        rsp = parse_system_response(raw)
        
        tr_id = rsp["tr_id"]
        
        # 암호화 키 저장
        if rsp["iv"] and rsp["ekey"]:
            if tr_id not in self._data_map:
                self._data_map[tr_id] = {}
            self._data_map[tr_id]["encrypt"] = rsp["encrypt"]
            self._data_map[tr_id]["key"] = rsp["ekey"]
            self._data_map[tr_id]["iv"] = rsp["iv"]
        
        # PINGPONG 처리
        if rsp["is_pingpong"]:
            logger.debug(f"PINGPONG 수신 및 응답")
            await ws.pong(raw)
            return
        
        # 구독 결과
        if rsp["is_ok"]:
            logger.info(f"구독 성공: {tr_id} - {rsp['tr_msg']}")
        else:
            logger.warning(f"구독 응답: {tr_id} - {rsp['tr_msg']}")
    
    async def _handle_realtime_data(self, raw: str) -> None:
        """실시간 데이터 처리"""
        parts = raw.split("|")
        if len(parts) < 4:
            logger.warning(f"잘못된 데이터 형식: {raw[:50]}")
            return
        
        encrypted = parts[0] == "1"
        tr_id = parts[1]
        # count = int(parts[2])  # 데이터 건수
        data = parts[3]
        
        # 암호화된 경우 복호화
        dm = self._data_map.get(tr_id, {})
        if encrypted and dm.get("key") and dm.get("iv"):
            try:
                data = aes_cbc_base64_dec(dm["key"], dm["iv"], data)
            except Exception as e:
                logger.error(f"복호화 실패: {e}")
                return
        
        # 컬럼 정보 가져오기
        columns = dm.get("columns", [])
        if not columns:
            if tr_id == WsTrId.REALTIME_PRICE:
                columns = PRICE_COLUMNS
            elif tr_id in (WsTrId.FILL_NOTICE_REAL, WsTrId.FILL_NOTICE_PAPER):
                columns = FILL_COLUMNS
        
        # DataFrame으로 파싱
        try:
            df = pd.read_csv(
                StringIO(data),
                header=None,
                sep="^",
                names=columns,
                dtype=object
            )
        except Exception as e:
            logger.error(f"데이터 파싱 오류: {e}")
            return
        
        # TR ID별 콜백 호출
        if tr_id == WsTrId.REALTIME_PRICE and self._price_callback:
            self._process_price_data(df)
        elif tr_id in (WsTrId.FILL_NOTICE_REAL, WsTrId.FILL_NOTICE_PAPER) and self._fill_callback:
            self._process_fill_data(df)
    
    def _process_price_data(self, df: pd.DataFrame) -> None:
        """실시간 체결가 데이터 처리 및 콜백"""
        for _, row in df.iterrows():
            try:
                price_data = RealtimePrice(
                    symbol=str(row.get("MKSC_SHRN_ISCD", "")),
                    time=str(row.get("STCK_CNTG_HOUR", "")),
                    price=int(row.get("STCK_PRPR", 0) or 0),
                    change_sign=str(row.get("PRDY_VRSS_SIGN", "")),
                    change=int(row.get("PRDY_VRSS", 0) or 0),
                    change_rate=float(row.get("PRDY_CTRT", 0) or 0),
                    open_price=int(row.get("STCK_OPRC", 0) or 0),
                    high_price=int(row.get("STCK_HGPR", 0) or 0),
                    low_price=int(row.get("STCK_LWPR", 0) or 0),
                    volume=int(row.get("CNTG_VOL", 0) or 0),
                    total_volume=int(row.get("ACML_VOL", 0) or 0),
                    ask_price=int(row.get("ASKP1", 0) or 0),
                    bid_price=int(row.get("BIDP1", 0) or 0),
                )
                
                self._price_callback(price_data.symbol, price_data)
                
            except Exception as e:
                logger.error(f"체결가 콜백 오류: {e}")
    
    def _process_fill_data(self, df: pd.DataFrame) -> None:
        """체결 통보 데이터 처리 및 콜백"""
        for _, row in df.iterrows():
            try:
                is_fill = str(row.get("CNTG_YN", "")) == "2"
                is_rejected = str(row.get("RFUS_YN", "")) == "Y"
                
                notice = FillNotice(
                    customer_id=str(row.get("CUST_ID", "")),
                    account_no=str(row.get("ACNT_NO", "")),
                    order_no=str(row.get("ODER_NO", "")),
                    order_qty=int(row.get("ODER_QTY", 0) or 0),
                    side=str(row.get("SELN_BYOV_CLS", "")),
                    symbol=str(row.get("STCK_SHRN_ISCD", "")),
                    fill_qty=int(row.get("CNTG_QTY", 0) or 0),
                    fill_price=int(row.get("CNTG_UNPR", 0) or 0),
                    fill_time=str(row.get("STCK_CNTG_HOUR", "")),
                    is_fill=is_fill,
                    is_rejected=is_rejected,
                )
                
                self._fill_callback(notice)
                
            except Exception as e:
                logger.error(f"체결통보 콜백 오류: {e}")
    
    # ========================================
    # 실행
    # ========================================
    
    async def _send_subscribe(self, ws, func, tr_type: str, items: List[str], kwargs: dict = None) -> None:
        """구독 요청 전송"""
        k = kwargs or {}
        for item in items:
            msg, columns = func(tr_type, item, **k)
            
            # 컬럼 정보 저장
            tr_id = msg["body"]["input"]["tr_id"]
            if tr_id not in self._data_map:
                self._data_map[tr_id] = {}
            self._data_map[tr_id]["columns"] = columns
            
            logger.info(f"구독 요청 전송: {tr_id} - {item}")
            await ws.send(json.dumps(msg))
            await asyncio.sleep(0.1)  # rate limit
    
    async def _subscriber(self, ws) -> None:
        """메시지 수신 루프"""
        async for raw in ws:
            await self._handle_message(ws, raw)
    
    async def _runner(self) -> None:
        """WebSocket 실행"""
        if len(self._subscriptions) == 0:
            raise ValueError("구독할 항목이 없습니다.")
        
        if len(self._subscriptions) > 40:
            raise ValueError("최대 구독 수는 40개입니다.")
        
        # 접속키 발급
        self.get_approval_key()
        
        url = self._ws_url
        logger.info(f"WebSocket 연결: {url}")
        
        while self._retry_count < self._max_retries and self._running:
            try:
                async with websockets.connect(url, ping_interval=30, ping_timeout=10) as ws:
                    logger.info("WebSocket 연결 성공")
                    self._retry_count = 0
                    
                    # 구독 요청 전송
                    for name, sub in self._subscriptions.items():
                        await self._send_subscribe(
                            ws,
                            sub["func"],
                            "1",
                            sub["items"],
                            sub["kwargs"]
                        )
                    
                    # 메시지 수신
                    await self._subscriber(ws)
                    
            except websockets.exceptions.ConnectionClosed as e:
                logger.warning(f"연결 종료: {e}")
                self._retry_count += 1
                if self._running:
                    logger.info(f"재연결 시도 {self._retry_count}/{self._max_retries}")
                    await asyncio.sleep(2)
            except Exception as e:
                logger.error(f"WebSocket 오류: {e}")
                self._retry_count += 1
                if self._running:
                    await asyncio.sleep(2)
        
        if self._retry_count >= self._max_retries:
            logger.error("최대 재연결 시도 횟수 초과")
    
    def start(self, timeout: Optional[float] = None) -> None:
        """WebSocket 시작 (블로킹)
        
        Args:
            timeout: 실행 시간 제한 (초). None이면 무한 실행
        """
        self._running = True
        
        try:
            if timeout:
                asyncio.run(asyncio.wait_for(self._runner(), timeout=timeout))
            else:
                asyncio.run(self._runner())
        except asyncio.TimeoutError:
            logger.info(f"타임아웃 ({timeout}초)")
        except KeyboardInterrupt:
            logger.info("사용자 중단 (Ctrl+C)")
        finally:
            self._running = False
    
    def stop(self) -> None:
        """WebSocket 종료"""
        self._running = False
        logger.info("WebSocket 종료 요청")
    
    # ========================================
    # 속성
    # ========================================
    
    @property
    def is_running(self) -> bool:
        """실행 상태"""
        return self._running
    
    @property
    def subscribed_symbols(self) -> List[str]:
        """구독 중인 종목 목록"""
        price_sub = self._subscriptions.get("price", {})
        return price_sub.get("items", [])
