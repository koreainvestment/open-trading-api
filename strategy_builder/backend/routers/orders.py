"""
주문 실행 API 라우터

Account Information and Pending Orders API:
- GET /account: 통합 계좌 정보 (예수금 + 보유종목)
- GET /pending: 미체결 주문 목록
- POST /cancel: 주문 취소
- POST /account/clear-cache: 캐시 삭제
"""

import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from core.order_executor import OrderExecutor
from core.signal import Action, Signal
from core.data_fetcher import get_deposit, get_holdings, get_pending_orders, cancel_order, clear_balance_cache
from backend import is_authenticated, get_current_mode

logging.basicConfig(level=logging.INFO)

router = APIRouter()

# ============================================
# 계좌 정보 캐싱 (30초)
# ============================================

_account_cache: Optional[dict] = None
_account_cache_time: Optional[datetime] = None
CACHE_TTL_SECONDS = 30

# 미체결 주문 캐시 (5초)
_pending_cache: Optional[list] = None
_pending_cache_time: Optional[datetime] = None
PENDING_CACHE_TTL = 5

# Optimistic Update 보호: 주문 직후 추가된 항목이 API 지연으로 사라지지 않도록
_optimistic_order_nos: set[str] = set()
_optimistic_added_at: Optional[datetime] = None
OPTIMISTIC_GRACE_SECONDS = 15


def _get_cached_account(force_refresh: bool = False) -> dict:
    """캐시된 계좌 정보 반환 (30초 TTL)"""
    global _account_cache, _account_cache_time
    
    now = datetime.now()
    
    # 캐시가 유효한지 확인
    if not force_refresh and _account_cache is not None and _account_cache_time is not None:
        elapsed = (now - _account_cache_time).total_seconds()
        if elapsed < CACHE_TTL_SECONDS:
            return _account_cache
    
    # 캐시 갱신
    env_dv = get_current_mode()
    
    try:
        deposit = get_deposit(env_dv)
        holdings_df = get_holdings(env_dv)
        
        holdings = []
        if not holdings_df.empty:
            holdings = holdings_df.to_dict("records")
        
        _account_cache = {
            "deposit": deposit,
            "holdings": holdings,
            "holdings_count": len(holdings),
            "cached_at": now.isoformat(),
        }
        _account_cache_time = now
        
        return _account_cache
        
    except Exception as e:
        logging.error(f"계좌 정보 조회 에러: {e}")
        # 캐시가 있으면 폴백으로 반환
        if _account_cache is not None:
            return {
                **_account_cache,
                "stale": True,
                "error": str(e)
            }
        return {
            "deposit": {},
            "holdings": [],
            "holdings_count": 0,
            "error": str(e)
        }


def _clear_account_cache():
    """계좌 정보 캐시 삭제 (data_fetcher 잔고 캐시도 함께 삭제)

    Note: 미체결 캐시(_pending_cache, _pending_cache_time)는 건드리지 않음.
    주문 직후 Optimistic Update의 TTL 보호를 유지하기 위함.
    """
    global _account_cache, _account_cache_time
    _account_cache = None
    _account_cache_time = None
    clear_balance_cache()


class OrderRequest(BaseModel):
    """주문 요청"""
    stock_code: str
    stock_name: str
    action: str  # "BUY" or "SELL"
    order_type: str  # "limit" or "market"
    price: int
    quantity: int
    signal_reason: str


class LogEntry(BaseModel):
    """로그 항목"""
    type: str  # "info", "success", "error", "warning"
    message: str
    timestamp: str


class OrderResponse(BaseModel):
    """주문 응답"""
    status: str
    message: str = ""
    data: dict | None = None
    logs: list[LogEntry] = []


@router.post("/execute", response_model=OrderResponse)
async def execute_order(request: OrderRequest):
    """
    주문 실행

    Args:
        request: 주문 요청 (OrderRequest)

    Returns:
        OrderResponse with:
        - status: "success" | "error"
        - message: 결과 메시지
        - data: 주문 결과 데이터 (선택)
        - logs: 실행 로그 목록
    """
    logs = []

    def add_log(log_type: str, message: str):
        """로그 추가"""
        logs.append({
            "type": log_type,
            "message": message,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })

    try:
        # 1. 인증 확인
        if not is_authenticated():
            add_log("error", "인증이 필요합니다")
            return OrderResponse(
                status="error",
                message="인증이 필요합니다",
                logs=logs
            )

        add_log("info", f"주문 검증 중: {request.stock_name}")

        # 2. 입력 검증
        if request.quantity <= 0:
            add_log("error", "주문 수량이 올바르지 않습니다")
            return OrderResponse(
                status="error",
                message="주문 수량이 올바르지 않습니다",
                logs=logs
            )

        if request.action not in ["BUY", "SELL"]:
            add_log("error", "주문 구분이 올바르지 않습니다")
            return OrderResponse(
                status="error",
                message="주문 구분이 올바르지 않습니다",
                logs=logs
            )

        if request.order_type not in ["limit", "market"]:
            add_log("error", "주문 유형이 올바르지 않습니다")
            return OrderResponse(
                status="error",
                message="주문 유형이 올바르지 않습니다",
                logs=logs
            )

        add_log("success", "주문 검증 완료")

        # 3. Signal 객체 생성
        # 지정가 주문: strength < 0.8 → order_executor가 target_price 사용
        # 시장가 주문: strength >= 0.8 → order_executor가 시장가 사용
        is_limit_order = request.order_type == "limit"
        signal = Signal(
            stock_code=request.stock_code,
            stock_name=request.stock_name,
            action=Action.BUY if request.action == "BUY" else Action.SELL,
            strength=0.7 if is_limit_order else 1.0,  # 지정가면 0.7, 시장가면 1.0
            reason=request.signal_reason,
            target_price=request.price if is_limit_order else None,
            quantity=request.quantity
        )

        # 주문 유형 로깅
        order_type_display = "지정가" if is_limit_order else "시장가"
        price_display = f"{request.price:,}원" if is_limit_order else "시장가"
        add_log("info", f"주문 실행 중: {request.action} {request.quantity}주 @ {price_display} ({order_type_display})")
        logging.info(f"[주문] order_type={request.order_type}, price={request.price}, strength={signal.strength}, target_price={signal.target_price}")

        # 4. OrderExecutor 호출 (현재 트레이딩 모드 사용)
        env_dv = get_current_mode()
        executor = OrderExecutor(env_dv=env_dv)
        result = executor.execute_signal(signal)

        # 5. 결과 처리
        if result.empty:
            error_reason = "주문 실행 실패"

            if request.action == "SELL":
                quantity = executor.position_manager.get_holding_quantity(request.stock_code)
                if quantity <= 0:
                    error_reason = f"미보유 종목입니다. {request.stock_name}을(를) 보유하고 있지 않습니다."
            elif request.action == "BUY":
                error_reason = "주문이 거부되었습니다. 서버 로그를 확인하세요."

            add_log("error", error_reason)

            return OrderResponse(
                status="error",
                message=error_reason,
                logs=logs
            )

        # 주문 성공 (POST API 응답은 대문자 필드명: ODNO, ORD_TMD, KRX_FWDG_ORD_ORGNO)
        order_id = result.iloc[0].get("ODNO", "")
        order_time = result.iloc[0].get("ORD_TMD", datetime.now().strftime("%H%M%S"))
        order_org_no = result.iloc[0].get("KRX_FWDG_ORD_ORGNO", "")

        order_data = {
            "order_id": order_id,
            "status": "submitted",
            "message": "주문이 접수되었습니다"
        }

        add_log("success", f"주문 실행 성공 (주문번호: {order_id})")

        # 미체결 캐시에 직접 추가 (Optimistic Update)
        global _pending_cache, _pending_cache_time, _optimistic_order_nos, _optimistic_added_at
        if _pending_cache is None:
            _pending_cache = []

        new_pending = PendingOrderItem(
            order_no=str(order_id),
            org_no=str(order_org_no),
            stock_code=request.stock_code,
            stock_name=request.stock_name,
            order_type="매수" if request.action == "BUY" else "매도",
            order_qty=request.quantity,
            order_price=request.price,
            filled_qty=0,
            unfilled_qty=request.quantity,
            order_time=order_time
        )
        _pending_cache.append(new_pending)
        _pending_cache_time = datetime.now()
        _optimistic_order_nos.add(str(order_id))
        _optimistic_added_at = datetime.now()
        logging.info(f"미체결 캐시에 추가: {request.stock_name} {request.action} {request.quantity}주 (TTL {PENDING_CACHE_TTL}초 + Grace {OPTIMISTIC_GRACE_SECONDS}초)")

        # 계좌 캐시 클리어 (잔고 갱신 위해, 미체결 캐시는 유지)
        _clear_account_cache()

        return OrderResponse(
            status="success",
            message="주문이 접수되었습니다",
            data=order_data,
            logs=logs
        )

    except Exception as e:
        logging.error(f"주문 실행 에러: {e}")
        add_log("error", f"주문 실행 에러: {str(e)}")

        return OrderResponse(
            status="error",
            message=str(e),
            logs=logs
        )


# ============================================
# 계좌 정보 API
# ============================================


class AccountResponse(BaseModel):
    """계좌 정보 응답"""
    status: str
    deposit: dict
    holdings: list
    holdings_count: int
    cached_at: str | None = None
    stale: bool = False
    error: str | None = None


class PendingOrderItem(BaseModel):
    """미체결 주문 항목"""
    order_no: str
    org_no: str = ""
    stock_code: str
    stock_name: str
    order_type: str
    order_qty: int
    order_price: int
    filled_qty: int
    unfilled_qty: int
    order_time: str


class PendingOrdersResponse(BaseModel):
    """미체결 주문 응답"""
    status: str
    orders: list[PendingOrderItem]
    total_count: int


class CancelOrderRequest(BaseModel):
    """주문 취소 요청"""
    order_no: str
    org_no: str = ""
    stock_code: str
    qty: int


class CancelOrderResponse(BaseModel):
    """주문 취소 응답"""
    status: str
    success: bool
    order_no: str
    message: str


@router.get("/account", response_model=AccountResponse)
async def get_account_info():
    """통합 계좌 정보 조회
    
    예수금과 보유종목 정보를 통합하여 반환합니다.
    30초 캐싱이 적용되어 있습니다.
    
    Returns:
        - deposit: 예수금 정보 (deposit, total_eval, purchase_amount, eval_amount, profit_loss)
        - holdings: 보유종목 목록
        - holdings_count: 보유종목 수
        - cached_at: 캐시 시간
        - stale: 캐시된 데이터 사용 여부 (API 실패 시 true)
    """
    if not is_authenticated():
        raise HTTPException(status_code=401, detail="인증이 필요합니다")
    
    account = _get_cached_account()
    
    return AccountResponse(
        status="success",
        deposit=account.get("deposit", {}),
        holdings=account.get("holdings", []),
        holdings_count=account.get("holdings_count", 0),
        cached_at=account.get("cached_at"),
        stale=account.get("stale", False),
        error=account.get("error")
    )


@router.post("/account/clear-cache")
async def clear_account_cache():
    """계좌 정보 캐시 삭제
    
    캐시를 삭제하여 다음 조회 시 최신 데이터를 가져옵니다.
    """
    if not is_authenticated():
        raise HTTPException(status_code=401, detail="인증이 필요합니다")
    
    _clear_account_cache()
    
    return {
        "status": "success",
        "message": "캐시가 삭제되었습니다"
    }


@router.get("/pending", response_model=PendingOrdersResponse)
async def get_pending_orders_api():
    """미체결 주문 목록 조회

    오늘 접수된 미체결 주문 목록을 반환합니다.
    5초 캐싱이 적용되어 있습니다.

    Returns:
        - orders: 미체결 주문 목록
        - total_count: 미체결 주문 수
    """
    global _pending_cache, _pending_cache_time, _optimistic_order_nos, _optimistic_added_at

    if not is_authenticated():
        raise HTTPException(status_code=401, detail="인증이 필요합니다")

    # 캐시 확인 (5초 TTL)
    now = datetime.now()
    if _pending_cache is not None and _pending_cache_time is not None:
        elapsed = (now - _pending_cache_time).total_seconds()
        if elapsed < PENDING_CACHE_TTL:
            return PendingOrdersResponse(
                status="success",
                orders=_pending_cache,
                total_count=len(_pending_cache)
            )

    env_dv = get_current_mode()

    try:
        df, api_success = get_pending_orders(env_dv)

        # API 실패 시 (rate limit 등) 이전 캐시 반환 + TTL 갱신
        if not api_success:
            logging.info("미체결 조회 API 실패 - 이전 캐시 반환")
            if _pending_cache is not None:
                _pending_cache_time = now
                return PendingOrdersResponse(
                    status="success",
                    orders=_pending_cache,
                    total_count=len(_pending_cache)
                )

        # API 결과 파싱
        api_orders: list[PendingOrderItem] = []
        api_order_nos: set[str] = set()
        if not df.empty:
            for _, row in df.iterrows():
                ono = str(row.get("order_no", ""))
                if not ono or ono in api_order_nos:
                    continue
                api_order_nos.add(ono)
                api_orders.append(PendingOrderItem(
                    order_no=ono,
                    org_no=str(row.get("org_no", "")),
                    stock_code=str(row.get("stock_code", "")),
                    stock_name=str(row.get("stock_name", "")),
                    order_type=str(row.get("order_type", "")),
                    order_qty=int(row.get("order_qty", 0)),
                    order_price=int(row.get("order_price", 0)),
                    filled_qty=int(row.get("filled_qty", 0)),
                    unfilled_qty=int(row.get("unfilled_qty", 0)),
                    order_time=str(row.get("order_time", ""))
                ))

        # Optimistic Grace Period: API에 아직 안 나타난 최근 주문 보존
        merged = list(api_orders)
        if _optimistic_added_at and _optimistic_order_nos:
            grace_elapsed = (now - _optimistic_added_at).total_seconds()
            if grace_elapsed < OPTIMISTIC_GRACE_SECONDS:
                missing = _optimistic_order_nos - api_order_nos
                if missing and _pending_cache:
                    for item in _pending_cache:
                        if item.order_no in missing:
                            merged.append(item)
                    logging.info(f"Optimistic Grace: {len(missing)}건 보존 ({grace_elapsed:.0f}s/{OPTIMISTIC_GRACE_SECONDS}s)")
            else:
                _optimistic_order_nos.clear()
                _optimistic_added_at = None
                logging.info("Optimistic Grace 만료 - API 결과만 사용")

        if merged:
            logging.info(f"미체결 캐시 업데이트: API {len(api_orders)}건 + Optimistic {len(merged) - len(api_orders)}건")
        _pending_cache = merged
        _pending_cache_time = now

        return PendingOrdersResponse(
            status="success",
            orders=merged,
            total_count=len(merged)
        )

    except Exception as e:
        logging.error(f"미체결 주문 조회 에러: {e}")
        if _pending_cache is not None:
            _pending_cache_time = now
            return PendingOrdersResponse(
                status="success",
                orders=_pending_cache,
                total_count=len(_pending_cache)
            )
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cancel", response_model=CancelOrderResponse)
async def cancel_order_api(request: CancelOrderRequest):
    """주문 취소
    
    미체결 주문을 취소합니다.
    
    Args:
        order_no: 취소할 주문번호
        stock_code: 종목코드
        qty: 취소수량
        
    Returns:
        - success: 취소 성공 여부
        - order_no: 취소된 주문번호
        - message: 결과 메시지
    """
    if not is_authenticated():
        raise HTTPException(status_code=401, detail="인증이 필요합니다")
    
    env_dv = get_current_mode()
    
    try:
        logging.info(f"취소 요청 수신: order_no={request.order_no}, org_no='{request.org_no}'")
        result = cancel_order(
            order_no=request.order_no,
            stock_code=request.stock_code,
            qty=request.qty,
            org_no=request.org_no,
            env_dv=env_dv
        )

        # 캐시 업데이트
        global _pending_cache, _pending_cache_time, _optimistic_order_nos
        if result.get("success"):
            _optimistic_order_nos.discard(request.order_no)
            if _pending_cache is not None:
                _pending_cache = [
                    p for p in _pending_cache
                    if p.order_no != request.order_no
                ]
                logging.info(f"미체결 캐시에서 제거: 주문번호 {request.order_no}")
            _clear_account_cache()
        else:
            # 취소 실패: 이미 체결되었거나 존재하지 않는 주문
            # Optimistic 캐시와 Grace에서도 제거 (체결된 주문이 UI에 남지 않도록)
            _optimistic_order_nos.discard(request.order_no)
            if _pending_cache is not None:
                _pending_cache = [
                    p for p in _pending_cache
                    if p.order_no != request.order_no
                ]
            _pending_cache_time = None
            logging.info(f"취소 실패(체결 완료 추정) - 캐시에서 제거: 주문번호 {request.order_no}")

        return CancelOrderResponse(
            status="success" if result.get("success") else "error",
            success=result.get("success", False),
            order_no=result.get("order_no", request.order_no),
            message=result.get("message") or ""
        )
        
    except Exception as e:
        logging.error(f"주문 취소 에러: {e}")
        raise HTTPException(status_code=500, detail=str(e))
