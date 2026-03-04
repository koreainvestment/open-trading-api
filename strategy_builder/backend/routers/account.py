"""
계좌 정보 API 라우터
"""

import logging
from datetime import datetime

from fastapi import APIRouter
from pydantic import BaseModel

from core import data_fetcher
from backend import is_authenticated, get_current_mode
import kis_auth as ka

logging.basicConfig(level=logging.INFO)

router = APIRouter()


# ============================================
# Response Models
# ============================================

class LogEntry(BaseModel):
    """로그 항목"""
    type: str  # "info", "success", "error", "warning"
    message: str
    timestamp: str


class AccountInfoResponse(BaseModel):
    """계좌 정보 응답"""
    status: str
    data: dict | None = None
    message: str = ""
    logs: list[LogEntry] = []


class HoldingsResponse(BaseModel):
    """보유 종목 응답"""
    status: str
    data: list[dict] = []
    message: str = ""
    logs: list[LogEntry] = []


class BalanceResponse(BaseModel):
    """예수금 응답"""
    status: str
    data: dict | None = None
    message: str = ""
    logs: list[LogEntry] = []


# ============================================
# API Endpoints
# ============================================

@router.get("/info", response_model=AccountInfoResponse)
async def get_account_info():
    """
    계좌 기본 정보 조회

    Returns:
        AccountInfoResponse with:
        - account_no: 계좌번호 (마스킹)
        - account_type: 계좌유형 (위탁/연금 등)
        - is_vps: 모의투자 여부
    """
    logs = []

    def add_log(log_type: str, message: str):
        logs.append(LogEntry(
            type=log_type,
            message=message,
            timestamp=datetime.now().strftime("%H:%M:%S")
        ))

    try:
        if not is_authenticated():
            add_log("error", "인증이 필요합니다")
            return AccountInfoResponse(
                status="error",
                message="인증이 필요합니다",
                logs=logs
            )

        add_log("info", "계좌 정보 조회 중...")

        trenv = ka.getTREnv()
        
        # 계좌번호 마스킹 (앞 4자리만 표시)
        account_no = trenv.my_acct
        masked_account = f"{account_no[:4]}****"
        
        # 계좌유형 판별
        prod_code = trenv.my_prod
        account_types = {
            "01": "위탁",
            "03": "선물옵션",
            "08": "해외선물",
            "22": "개인연금",
            "29": "퇴직연금",
        }
        account_type = account_types.get(prod_code, "기타")
        
        is_vps = ka.isPaperTrading()

        add_log("success", "계좌 정보 조회 완료")

        return AccountInfoResponse(
            status="success",
            data={
                "account_no": masked_account,
                "account_no_full": f"{account_no}-{prod_code}",
                "account_type": account_type,
                "prod_code": prod_code,
                "is_vps": is_vps,
                "mode": "모의투자" if is_vps else "실전투자",
            },
            logs=logs
        )

    except Exception as e:
        logging.error(f"계좌 정보 조회 에러: {e}")
        add_log("error", f"조회 실패: {str(e)}")
        return AccountInfoResponse(
            status="error",
            message=str(e),
            logs=logs
        )


@router.get("/holdings", response_model=HoldingsResponse)
async def get_holdings():
    """
    보유 종목 목록 조회

    Returns:
        HoldingsResponse with list of:
        - stock_code: 종목코드
        - stock_name: 종목명
        - quantity: 보유수량
        - avg_price: 평균단가
        - current_price: 현재가
        - eval_amount: 평가금액
        - profit_loss: 평가손익
        - profit_rate: 수익률
    """
    logs = []

    def add_log(log_type: str, message: str):
        logs.append(LogEntry(
            type=log_type,
            message=message,
            timestamp=datetime.now().strftime("%H:%M:%S")
        ))

    try:
        if not is_authenticated():
            add_log("error", "인증이 필요합니다")
            return HoldingsResponse(
                status="error",
                message="인증이 필요합니다",
                logs=logs
            )

        add_log("info", "보유 종목 조회 중...")

        # 환경 확인 (trading_state에서 현재 모드 가져오기)
        env_dv = get_current_mode()
        
        holdings_df = data_fetcher.get_holdings(env_dv)

        if holdings_df.empty:
            add_log("info", "보유 종목이 없습니다")
            return HoldingsResponse(
                status="success",
                data=[],
                message="보유 종목이 없습니다",
                logs=logs
            )

        holdings = holdings_df.to_dict("records")
        
        add_log("success", f"보유 종목 {len(holdings)}개 조회 완료")

        return HoldingsResponse(
            status="success",
            data=holdings,
            logs=logs
        )

    except Exception as e:
        logging.error(f"보유 종목 조회 에러: {e}")
        add_log("error", f"조회 실패: {str(e)}")
        return HoldingsResponse(
            status="error",
            message=str(e),
            logs=logs
        )


@router.get("/balance", response_model=BalanceResponse)
async def get_balance():
    """
    예수금/주문가능금액 조회

    Returns:
        BalanceResponse with:
        - deposit: 예수금총금액
        - total_eval: 총평가금액
        - purchase_amount: 매입금액합계
        - eval_amount: 평가금액합계
        - profit_loss: 평가손익합계
    """
    logs = []

    def add_log(log_type: str, message: str):
        logs.append(LogEntry(
            type=log_type,
            message=message,
            timestamp=datetime.now().strftime("%H:%M:%S")
        ))

    try:
        if not is_authenticated():
            add_log("error", "인증이 필요합니다")
            return BalanceResponse(
                status="error",
                message="인증이 필요합니다",
                logs=logs
            )

        add_log("info", "예수금 조회 중...")

        # 환경 확인 (trading_state에서 현재 모드 가져오기)
        env_dv = get_current_mode()
        
        deposit_info = data_fetcher.get_deposit(env_dv)

        if not deposit_info:
            add_log("warning", "예수금 정보를 가져올 수 없습니다")
            return BalanceResponse(
                status="error",
                message="예수금 정보를 가져올 수 없습니다",
                logs=logs
            )

        add_log("success", "예수금 조회 완료")

        # 금액 포맷팅 추가
        formatted_data = {
            **deposit_info,
            "deposit_formatted": f"{deposit_info.get('deposit', 0):,}원",
            "total_eval_formatted": f"{deposit_info.get('total_eval', 0):,}원",
            "profit_loss_formatted": f"{deposit_info.get('profit_loss', 0):+,}원",
        }

        return BalanceResponse(
            status="success",
            data=formatted_data,
            logs=logs
        )

    except Exception as e:
        logging.error(f"예수금 조회 에러: {e}")
        add_log("error", f"조회 실패: {str(e)}")
        return BalanceResponse(
            status="error",
            message=str(e),
            logs=logs
        )


@router.get("/buyable/{stock_code}")
async def get_buyable(stock_code: str, price: int = 0):
    """
    특정 종목 매수가능금액/수량 조회

    Args:
        stock_code: 종목코드 (6자리)
        price: 주문단가 (0이면 현재가로 조회)

    Returns:
        dict with:
        - amount: 매수가능금액
        - quantity: 매수가능수량
    """
    try:
        if not is_authenticated():
            return {
                "status": "error",
                "message": "인증이 필요합니다"
            }

        # 환경 확인 (trading_state에서 현재 모드 가져오기)
        env_dv = get_current_mode()

        # 가격이 0이면 현재가 조회
        if price <= 0:
            current = data_fetcher.get_current_price(stock_code, env_dv)
            price = current.get("price", 0)
            
            if price <= 0:
                return {
                    "status": "error",
                    "message": "현재가를 조회할 수 없습니다"
                }

        buyable = data_fetcher.get_buyable_amount(stock_code, price, env_dv)

        return {
            "status": "success",
            "data": {
                "stock_code": stock_code,
                "price": price,
                "amount": buyable.get("amount", 0),
                "quantity": buyable.get("quantity", 0),
                "amount_formatted": f"{buyable.get('amount', 0):,}원",
            }
        }

    except Exception as e:
        logging.error(f"매수가능 조회 에러 ({stock_code}): {e}")
        return {
            "status": "error",
            "message": str(e)
        }
