"""한국투자증권 데이터 Provider

api_v1/routers/kis_data.py, api_v1/services/data_service.py 기반.
"""

import logging
import time
from datetime import date, datetime, timedelta
from typing import Callable, List, Optional

# EGW00201: 초당 API 호출 한도 초과
_RATE_LIMIT_CODE = "EGW00201"
_RATE_LIMIT_WAIT = 61  # 초 (KIS 한도 초기화 대기)
_RATE_LIMIT_MAX_RETRIES = 3

from ...models import Bar, Quote, Resolution, IndexBar
from ...models.trading import Subscription
from ...models.market_data import StockInfo, FinancialData
from ...exceptions import KISError
from .auth import KISAuth
from .constants import ApiPath, TrId, EXCHANGE_TO_KIS
from .websocket import KISWebSocket, RealtimePrice

logger = logging.getLogger(__name__)


class KISDataProvider:
    """한국투자증권 데이터 제공자

    DataProvider Protocol 구현.
    """

    def __init__(self, auth: KISAuth):
        """
        Args:
            auth: KISAuth 인스턴스

        사용법:
            auth = KISAuth.from_env()
            provider = KISDataProvider(auth)
        """
        self._auth = auth
        self._ws_client = None  # WebSocket 클라이언트 (필요시 초기화)
    
    def get_history(
        self,
        symbol: str,
        start: date,
        end: date,
        resolution: Resolution = Resolution.DAILY
    ) -> List[Bar]:
        """과거 데이터 조회
        
        Args:
            symbol: 종목코드 (예: "005930")
            start: 시작일
            end: 종료일
            resolution: 해상도 (DAILY 또는 MINUTE)
        
        Returns:
            Bar 리스트 (시간순 정렬)
        """
        if resolution == Resolution.DAILY:
            return self._get_daily_bars(symbol, start, end)
        elif resolution == Resolution.MINUTE:
            return self._get_minute_bars(symbol, end)  # 분봉은 단일 날짜
        else:
            raise ValueError(f"지원하지 않는 해상도: {resolution}")
    
    def _get_daily_bars(self, symbol: str, start: date, end: date) -> List[Bar]:
        """일봉 조회
        
        API: /uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice
        TR ID: FHKST03010100
        """
        start_str = start.strftime("%Y%m%d")
        end_str = end.strftime("%Y%m%d")
        
        all_data = []
        current_end = end_str
        
        while True:
            params = {
                "FID_COND_MRKT_DIV_CODE": "J",
                "FID_INPUT_ISCD": symbol,
                "FID_INPUT_DATE_1": start_str,
                "FID_INPUT_DATE_2": current_end,
                "FID_PERIOD_DIV_CODE": "D",
                "FID_ORG_ADJ_PRC": "0",  # 수정주가
            }

            # EGW00201 rate limit 자동 재시도
            resp = None
            for attempt in range(_RATE_LIMIT_MAX_RETRIES):
                resp = self._auth.get(ApiPath.DOMESTIC_DAILY, params, TrId.DAILY_PRICE)
                if resp.is_ok():
                    break
                if resp.error_code == _RATE_LIMIT_CODE:
                    if attempt < _RATE_LIMIT_MAX_RETRIES - 1:
                        logger.warning(
                            f"[RateLimit] {symbol} EGW00201 — {_RATE_LIMIT_WAIT}초 대기 후 재시도 "
                            f"({attempt + 1}/{_RATE_LIMIT_MAX_RETRIES})"
                        )
                        time.sleep(_RATE_LIMIT_WAIT)
                    continue
                break  # 다른 에러

            if not resp.is_ok():
                logger.error(f"일봉 조회 실패: {symbol} - {resp.error_message}")
                break
            
            data = resp.get_output2()
            if not data:
                break
            
            all_data.extend(data)
            
            # 페이지네이션: 마지막 날짜가 시작일 이전이면 종료
            last_date = data[-1].get("stck_bsop_date", "")
            if last_date <= start_str or len(data) < 100:
                break
            
            current_end = (
                datetime.strptime(last_date, "%Y%m%d") - timedelta(days=1)
            ).strftime("%Y%m%d")
            
            self._auth.smart_sleep()
        
        # Bar 객체로 변환
        bars = []
        for row in all_data:
            try:
                bars.append(Bar(
                    time=datetime.strptime(row.get("stck_bsop_date", ""), "%Y%m%d"),
                    open=float(row.get("stck_oprc", 0)),
                    high=float(row.get("stck_hgpr", 0)),
                    low=float(row.get("stck_lwpr", 0)),
                    close=float(row.get("stck_clpr", 0)),
                    volume=int(row.get("acml_vol", 0)),
                ))
            except (ValueError, TypeError) as e:
                logger.warning(f"데이터 파싱 오류: {e}")
                continue
        
        # 시간순 정렬
        bars.sort(key=lambda b: b.time)
        logger.info(f"일봉 조회 완료: {symbol}, {len(bars)}건")
        return bars
    
    def _get_minute_bars(self, symbol: str, target_date: date) -> List[Bar]:
        """분봉 조회
        
        API: /uapi/domestic-stock/v1/quotations/inquire-time-dailychartprice
        TR ID: FHKST03010230
        
        주의: 분봉은 당일 또는 최근 1년 이내만 조회 가능.
        """
        date_str = target_date.strftime("%Y%m%d")
        
        all_data = []
        current_time = "153000"  # 장 마감 시간부터 역순 조회
        
        for _ in range(10):  # 최대 10페이지
            params = {
                "FID_COND_MRKT_DIV_CODE": "J",
                "FID_INPUT_ISCD": symbol,
                "FID_INPUT_HOUR_1": current_time,
                "FID_INPUT_DATE_1": date_str,
                "FID_PW_DATA_INCU_YN": "Y",
                "FID_FAKE_TICK_INCU_YN": "",
            }
            
            resp = self._auth.get(
                ApiPath.DOMESTIC_MINUTE,
                params,
                "FHKST03010230"
            )
            
            if not resp.is_ok():
                logger.error(f"분봉 조회 실패: {symbol} - {resp.error_message}")
                break
            
            data = resp.get_output2()
            if not data:
                break
            
            all_data.extend(data)
            
            # 다음 페이지: 가장 이른 시간 찾기
            times = [d.get("stck_cntg_hour", "") for d in data if d.get("stck_cntg_hour")]
            min_time = min(times) if times else ""
            
            if min_time <= "090000" or len(data) < 120:
                break
            
            current_time = min_time
            self._auth.smart_sleep()
        
        # Bar 객체로 변환
        bars = []
        seen = set()
        for row in all_data:
            try:
                time_str = row.get("stck_cntg_hour", "")
                dt = datetime.strptime(f"{date_str}{time_str}", "%Y%m%d%H%M%S")
                
                if dt in seen:
                    continue
                seen.add(dt)
                
                bars.append(Bar(
                    time=dt,
                    open=float(row.get("stck_oprc", 0)),
                    high=float(row.get("stck_hgpr", 0)),
                    low=float(row.get("stck_lwpr", 0)),
                    close=float(row.get("stck_prpr", 0)),
                    volume=int(row.get("cntg_vol", 0)),
                ))
            except (ValueError, TypeError) as e:
                logger.warning(f"분봉 파싱 오류: {e}")
                continue
        
        bars.sort(key=lambda b: b.time)
        logger.info(f"분봉 조회 완료: {symbol}, {len(bars)}건")
        return bars
    
    def get_quote(self, symbol: str) -> Quote:
        """현재 호가 조회
        
        API: /uapi/domestic-stock/v1/quotations/inquire-asking-price-exp-ccn
        TR ID: FHKST01010200
        """
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": symbol,
        }
        
        resp = self._auth.get(
            ApiPath.DOMESTIC_ASKING,
            params,
            TrId.ASKING_PRICE
        )
        
        if not resp.is_ok():
            raise KISError(f"호가 조회 실패: {resp.error_message}")
        
        data = resp.get_output1()
        if not data:
            raise KISError(f"호가 데이터 없음: {symbol}")
        
        return Quote(
            time=datetime.now(),
            bid_price=float(data.get("bidp1", 0)),
            bid_size=int(data.get("bidp_rsqn1", 0)),
            ask_price=float(data.get("askp1", 0)),
            ask_size=int(data.get("askp_rsqn1", 0)),
        )
    
    def subscribe_realtime(
        self,
        symbols: List[str],
        on_bar: Callable[[str, Bar], None],
        timeout: Optional[float] = None
    ) -> Subscription:
        """실시간 데이터 구독
        
        WebSocket tr_id: H0STCNT0 (실시간 체결가)
        
        Args:
            symbols: 종목코드 리스트
            on_bar: 콜백 함수 (symbol, Bar) -> None
            timeout: 타임아웃 (초). None이면 무한 실행
        
        Returns:
            Subscription 객체
        """
        # WebSocket 클라이언트 생성
        if self._ws_client is None:
            self._ws_client = KISWebSocket.from_auth(self._auth)

        # RealtimePrice를 Bar로 변환하는 래퍼
        def price_to_bar(symbol: str, price: RealtimePrice):
            try:
                # 시간 파싱 (HHMMSS)
                time_str = price.time
                today = datetime.now().date()
                dt = datetime.combine(
                    today,
                    datetime.strptime(time_str, "%H%M%S").time()
                )
                
                bar = Bar(
                    time=dt,
                    open=float(price.open_price),
                    high=float(price.high_price),
                    low=float(price.low_price),
                    close=float(price.price),
                    volume=price.volume,
                )
                on_bar(symbol, bar)
            except Exception as e:
                logger.error(f"Bar 변환 오류: {e}")
        
        self._ws_client.subscribe_price(symbols, price_to_bar)
        
        sub_id = f"sub_{datetime.now().timestamp()}"
        logger.info(f"실시간 구독 시작: {symbols}")
        
        # 블로킹 실행
        self._ws_client.start(timeout=timeout)
        
        return Subscription(
            id=sub_id,
            symbols=symbols,
            is_active=False  # start() 완료 후 비활성
        )
    
    def subscribe_realtime_async(
        self,
        symbols: List[str],
        on_bar: Callable[[str, Bar], None]
    ) -> "KISWebSocket":
        """실시간 데이터 구독 (비동기)
        
        WebSocket 클라이언트를 반환하여 호출자가 직접 start()를 호출.
        
        Returns:
            KISWebSocket 클라이언트 (호출자가 .start() 호출 필요)
        """
        if self._ws_client is None:
            self._ws_client = KISWebSocket.from_auth(self._auth)

        def price_to_bar(symbol: str, price: RealtimePrice):
            try:
                time_str = price.time
                today = datetime.now().date()
                dt = datetime.combine(
                    today,
                    datetime.strptime(time_str, "%H%M%S").time()
                )
                
                bar = Bar(
                    time=dt,
                    open=float(price.open_price),
                    high=float(price.high_price),
                    low=float(price.low_price),
                    close=float(price.price),
                    volume=price.volume,
                )
                on_bar(symbol, bar)
            except Exception as e:
                logger.error(f"Bar 변환 오류: {e}")
        
        self._ws_client.subscribe_price(symbols, price_to_bar)
        logger.info(f"실시간 구독 등록: {symbols}")
        
        return self._ws_client
    
    def get_stock_info(self, symbol: str) -> Optional[StockInfo]:
        """종목 정보 조회 (미구현)"""
        return None
    
    def get_financial_data(self, symbol: str) -> Optional[FinancialData]:
        """재무 데이터 조회 (미구현)"""
        return None
    
    # ============================================
    # 해외주식 지원
    # ============================================
    
    def get_overseas_daily(
        self,
        symbol: str,
        exchange: str,
        end_date: Optional[date] = None
    ) -> List[Bar]:
        """해외주식 일봉 조회
        
        API: /uapi/overseas-price/v1/quotations/dailyprice
        TR ID: HHDFS76240000
        """
        kis_excd = EXCHANGE_TO_KIS.get(exchange.lower(), exchange.upper()[:3])
        end_str = end_date.strftime("%Y%m%d") if end_date else ""
        
        all_data = []
        tr_cont = ""
        current_bymd = end_str
        
        for _ in range(10):
            params = {
                "AUTH": "",
                "EXCD": kis_excd,
                "SYMB": symbol,
                "GUBN": "0",  # 일봉
                "BYMD": current_bymd,
                "MODP": "1",  # 수정주가
            }
            
            resp = self._auth.get(
                ApiPath.OVERSEAS_DAILY,
                params,
                TrId.OVERSEAS_DAILY,
                tr_cont=tr_cont
            )
            
            if not resp.is_ok():
                logger.error(f"해외주식 조회 실패: {symbol} - {resp.error_message}")
                break
            
            data = resp.get_output2()
            if data:
                all_data.extend(data)
                last_date = data[-1].get("xymd", "")
                if last_date:
                    current_bymd = last_date
            else:
                break
            
            # 연속조회 확인
            tr_cont = getattr(resp.header, 'tr_cont', '')
            if tr_cont not in ["M", "F"]:
                break
            
            tr_cont = "N"
            self._auth.smart_sleep()
        
        # Bar 객체로 변환
        bars = []
        for row in all_data:
            try:
                bars.append(Bar(
                    time=datetime.strptime(row.get("xymd", ""), "%Y%m%d"),
                    open=float(row.get("open", 0)),
                    high=float(row.get("high", 0)),
                    low=float(row.get("low", 0)),
                    close=float(row.get("clos", 0)),
                    volume=int(row.get("tvol", 0)),
                ))
            except (ValueError, TypeError) as e:
                logger.warning(f"해외주식 파싱 오류: {e}")
                continue
        
        bars.sort(key=lambda b: b.time)
        logger.info(f"해외주식 일봉 완료: {symbol}, {len(bars)}건")
        return bars

    # ============================================
    # 업종 지수 (KOSPI, KOSDAQ)
    # ============================================

    def get_index_history(
        self,
        index_code: str,
        start: date,
        end: date,
    ) -> List[IndexBar]:
        """업종 지수 일봉 조회

        Args:
            index_code: 업종코드 ("0001"=KOSPI, "1001"=KOSDAQ)
            start: 시작일
            end: 종료일

        Returns:
            IndexBar 리스트 (오래된 순 정렬)

        API 정보:
            - 경로: /uapi/domestic-stock/v1/quotations/inquire-daily-indexchartprice
            - TR ID: FHKUP03500100
            - 응답: bstp_nmix_prpr(종가), bstp_nmix_oprc(시가), bstp_nmix_hgpr(고가), bstp_nmix_lwpr(저가)

        사용 예:
            # KOSPI 지수 조회
            bars = provider.get_index_history("0001", start_date, end_date)

            # KOSDAQ 지수 조회
            bars = provider.get_index_history("1001", start_date, end_date)
        """
        all_bars: List[IndexBar] = []
        cursor_date = end.strftime("%Y%m%d")
        start_str = start.strftime("%Y%m%d")

        for _ in range(10):  # 최대 10 페이지
            params = {
                "FID_COND_MRKT_DIV_CODE": "U",  # U=업종
                "FID_INPUT_ISCD": index_code,
                "FID_INPUT_DATE_1": start_str,
                "FID_INPUT_DATE_2": cursor_date,
                "FID_PERIOD_DIV_CODE": "D",  # D=일봉
            }

            # EGW00201 rate limit 자동 재시도
            resp = None
            for attempt in range(_RATE_LIMIT_MAX_RETRIES):
                resp = self._auth.get(ApiPath.INDEX_DAILY, params, TrId.INDEX_DAILY)
                if resp.is_ok():
                    break
                if resp.error_code == _RATE_LIMIT_CODE:
                    if attempt < _RATE_LIMIT_MAX_RETRIES - 1:
                        logger.warning(
                            f"[RateLimit] 지수 {index_code} EGW00201 — {_RATE_LIMIT_WAIT}초 대기 후 재시도 "
                            f"({attempt + 1}/{_RATE_LIMIT_MAX_RETRIES})"
                        )
                        time.sleep(_RATE_LIMIT_WAIT)
                    continue
                break

            if not resp.is_ok():
                logger.error(f"지수 조회 실패: {resp.error_message}")
                break

            output = resp.get_output2()
            if not output:
                break

            for item in output:
                dt_str = item.get("stck_bsop_date")
                if not dt_str:
                    continue

                try:
                    bar = IndexBar(
                        time=datetime.strptime(dt_str, "%Y%m%d"),
                        open=float(item.get("bstp_nmix_oprc", 0)),
                        high=float(item.get("bstp_nmix_hgpr", 0)),
                        low=float(item.get("bstp_nmix_lwpr", 0)),
                        close=float(item.get("bstp_nmix_prpr", 0)),
                        volume=int(item.get("acml_vol", 0) or 0),
                    )
                    all_bars.append(bar)
                except (KeyError, ValueError) as e:
                    logger.warning(f"지수 파싱 오류: {e}")
                    continue

            # 페이지네이션 - 시작일까지 도달했는지 확인
            last_date = output[-1].get("stck_bsop_date")
            if not last_date or last_date <= start_str:
                break  # 시작일에 도달했으면 종료

            # 다음 페이지 조회
            cursor_date = (
                datetime.strptime(last_date, "%Y%m%d") - timedelta(days=1)
            ).strftime("%Y%m%d")
            self._auth.smart_sleep()

        # 오래된 순 정렬
        all_bars.sort(key=lambda b: b.time)
        logger.info(f"지수 조회 완료: {index_code}, {len(all_bars)}건")
        return all_bars
