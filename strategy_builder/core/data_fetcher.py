"""
데이터 조회 모듈

Applied Skills: skills/investment-strategy-framework.md
- API 호출 실패 시 빈 DataFrame 반환 (예외 발생 금지)
- 연속조회가 필요한 API는 자동 페이징 처리
"""

import logging
import threading
import time
from datetime import datetime, timedelta

import pandas as pd

import kis_auth as ka

logging.basicConfig(level=logging.INFO)


def _assert_trenv_ready(context: str = "") -> bool:
    """_TRENV 초기화 여부 확인. 미초기화 시 에러 로그 기록 후 False 반환."""
    trenv = ka.getTREnv()
    if not hasattr(trenv, "my_url") or not trenv.my_url:
        logging.error(
            f"KIS API 미인증{f' ({context})' if context else ''}: "
            "재인증이 필요합니다."
        )
        return False
    return True


# =============================================================================
# 잔고 조회 캐시 (holdings + deposit 동일 엔드포인트 병합)
# =============================================================================

_balance_cache_lock = threading.Lock()
_balance_cache = {
    "data": None,
    "timestamp": 0.0,
    "env_dv": None,
}
_BALANCE_CACHE_TTL = 10  # 10초 캐시


def _fetch_balance_raw(env_dv: str = "real"):
    """잔고 API 1회 호출 후 원본 응답 반환 (output1 + output2)"""
    if not _assert_trenv_ready("잔고 조회"):
        return None
    trenv = ka.getTREnv()
    is_real = env_dv in ("real", "prod")
    tr_id = "TTTC8434R" if is_real else "VTTC8434R"

    params = {
        "CANO": trenv.my_acct,
        "ACNT_PRDT_CD": trenv.my_prod,
        "AFHR_FLPR_YN": "N",
        "OFL_YN": "",
        "INQR_DVSN": "02",
        "UNPR_DVSN": "01",
        "FUND_STTL_ICLD_YN": "N",
        "FNCG_AMT_AUTO_RDPT_YN": "N",
        "PRCS_DVSN": "00",
        "CTX_AREA_FK100": "",
        "CTX_AREA_NK100": ""
    }

    res = ka._url_fetch(
        "/uapi/domestic-stock/v1/trading/inquire-balance",
        tr_id, "", params
    )

    if not res.isOK():
        return None

    body = res.getBody()
    return {"output1": body.output1, "output2": body.output2}


def _get_balance_cached(env_dv: str = "real"):
    """캐시된 잔고 원본 데이터 반환 (10초 TTL)"""
    global _balance_cache

    with _balance_cache_lock:
        now = time.monotonic()
        if (
            _balance_cache["data"] is not None
            and _balance_cache["env_dv"] == env_dv
            and (now - _balance_cache["timestamp"]) < _BALANCE_CACHE_TTL
        ):
            return _balance_cache["data"]

    # 캐시 미스: API 호출 (lock 밖에서 실행하여 blocking 최소화)
    data = _fetch_balance_raw(env_dv)

    with _balance_cache_lock:
        _balance_cache = {
            "data": data,
            "timestamp": time.monotonic(),
            "env_dv": env_dv,
        }

    return data


def clear_balance_cache():
    """잔고 캐시 강제 삭제 (주문 후 등)"""
    global _balance_cache
    with _balance_cache_lock:
        _balance_cache = {"data": None, "timestamp": 0.0, "env_dv": None}


# =============================================================================
# 일봉 데이터 조회
# =============================================================================

def get_daily_prices(
    stock_code: str,
    days: int = 100,
    env_dv: str = "real"
) -> pd.DataFrame:
    """
    일봉 데이터를 조회하여 정규화된 DataFrame 반환

    Args:
        stock_code: 종목코드 (6자리)
        days: 조회 기간 (일)
        env_dv: 환경 구분 (real/demo)

    Returns:
        DataFrame with columns:
        - date: 날짜 (YYYYMMDD)
        - open: 시가
        - high: 고가
        - low: 저가
        - close: 종가
        - volume: 거래량

    Note:
        skill: API 실패 시 빈 DataFrame 반환
    """
    if not _assert_trenv_ready(f"일봉 조회 {stock_code}"):
        return pd.DataFrame()

    try:
        end_date = datetime.now().strftime("%Y%m%d")
        start_date = (datetime.now() - timedelta(days=days + 50)).strftime("%Y%m%d")

        # TR_ID 설정
        tr_id = "FHKST03010100"

        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code,
            "FID_INPUT_DATE_1": start_date,
            "FID_INPUT_DATE_2": end_date,
            "FID_PERIOD_DIV_CODE": "D",
            "FID_ORG_ADJ_PRC": "0"  # 수정주가
        }

        res = ka._url_fetch(
            "/uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice",
            tr_id, "", params
        )

        if not res.isOK():
            logging.warning(f"API 호출 실패: {stock_code}")
            return pd.DataFrame()

        df = pd.DataFrame(res.getBody().output2)

        if df.empty:
            logging.warning(f"데이터 없음: {stock_code}")
            return pd.DataFrame()

        # 정규화
        df = df.rename(columns={
            "stck_bsop_date": "date",
            "stck_oprc": "open",
            "stck_hgpr": "high",
            "stck_lwpr": "low",
            "stck_clpr": "close",
            "acml_vol": "volume"
        })

        # 필요한 컬럼만 선택
        df = df[["date", "open", "high", "low", "close", "volume"]]

        # 숫자형 변환
        for col in ["open", "high", "low", "close", "volume"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        # 날짜순 정렬 (과거 → 최근)
        df = df.sort_values("date").reset_index(drop=True)

        # 요청한 일수만큼만 반환
        return df.tail(days).reset_index(drop=True)

    except Exception as e:
        logging.error(f"데이터 조회 에러 ({stock_code}): {e}")
        return pd.DataFrame()


# =============================================================================
# 현재가 조회
# =============================================================================

def get_current_price(
    stock_code: str,
    env_dv: str = "real"
) -> dict:
    """
    현재가 시세 조회

    Args:
        stock_code: 종목코드 (6자리)
        env_dv: 환경 구분 (real/demo)

    Returns:
        dict with keys:
        - price: 현재가
        - change: 전일대비
        - change_rate: 전일대비율
        - high: 고가
        - low: 저가
        - volume: 거래량
        - w52_high: 52주 최고가
        - w52_low: 52주 최저가

    Note:
        skill: API 실패 시 빈 dict 반환
    """
    if not _assert_trenv_ready(f"현재가 조회 {stock_code}"):
        return {}

    try:
        tr_id = "FHKST01010100"

        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code
        }

        res = ka._url_fetch(
            "/uapi/domestic-stock/v1/quotations/inquire-price",
            tr_id, "", params
        )

        if not res.isOK():
            logging.warning(f"현재가 조회 실패: {stock_code}")
            return {}

        output = res.getBody().output

        return {
            "price": int(output.get("stck_prpr", 0)),
            "change": int(output.get("prdy_vrss", 0)),
            "change_rate": float(output.get("prdy_ctrt", 0)),
            "high": int(output.get("stck_hgpr", 0)),
            "low": int(output.get("stck_lwpr", 0)),
            "volume": int(output.get("acml_vol", 0)),
            "w52_high": int(output.get("w52_hgpr", 0)),
            "w52_low": int(output.get("w52_lwpr", 0)),
        }

    except Exception as e:
        logging.error(f"현재가 조회 에러 ({stock_code}): {e}")
        return {}


# =============================================================================
# 잔고 조회
# =============================================================================

def get_holdings(env_dv: str = "real") -> pd.DataFrame:
    """
    보유 종목 잔고 조회 (캐시 사용 - get_deposit와 동일 엔드포인트)

    Args:
        env_dv: 환경 구분 (real/demo 또는 prod/vps)

    Returns:
        DataFrame with columns:
        - stock_code: 종목코드
        - stock_name: 종목명
        - quantity: 보유수량
        - avg_price: 평균단가
        - current_price: 현재가
        - eval_amount: 평가금액
        - profit_loss: 평가손익
        - profit_rate: 수익률
    """
    try:
        raw = _get_balance_cached(env_dv)

        if raw is None:
            logging.warning("잔고 조회 실패")
            return pd.DataFrame()

        df = pd.DataFrame(raw["output1"])

        if df.empty:
            return pd.DataFrame()

        # 정규화
        df = df.rename(columns={
            "pdno": "stock_code",
            "prdt_name": "stock_name",
            "hldg_qty": "quantity",
            "pchs_avg_pric": "avg_price",
            "prpr": "current_price",
            "evlu_amt": "eval_amount",
            "evlu_pfls_amt": "profit_loss",
            "evlu_pfls_rt": "profit_rate"
        })

        df = df[[
            "stock_code", "stock_name", "quantity", "avg_price",
            "current_price", "eval_amount", "profit_loss", "profit_rate"
        ]]

        # 숫자형 변환
        for col in ["quantity", "avg_price", "current_price", "eval_amount", "profit_loss"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        df["profit_rate"] = pd.to_numeric(df["profit_rate"], errors="coerce")

        # 보유수량 0 제외
        df = df[df["quantity"] > 0]

        return df.reset_index(drop=True)

    except Exception as e:
        logging.error(f"잔고 조회 에러: {e}")
        return pd.DataFrame()


# =============================================================================
# 매수가능금액 조회
# =============================================================================

def get_buyable_amount(
    stock_code: str,
    price: int,
    env_dv: str = "real"
) -> dict:
    """
    매수가능금액/수량 조회

    Args:
        stock_code: 종목코드
        price: 주문단가 (시장가 조회 시 현재가 입력)
        env_dv: 환경 구분 (real/demo 또는 prod/vps)

    Returns:
        dict with keys:
        - amount: 매수가능금액 (미수 미사용)
        - quantity: 매수가능수량 (미수 미사용)
    """
    if not _assert_trenv_ready(f"매수가능 조회 {stock_code}"):
        return {"amount": 0, "quantity": 0}

    try:
        trenv = ka.getTREnv()

        # env_dv 정규화: real/prod → 실전, demo/vps → 모의
        is_real = env_dv in ("real", "prod")
        tr_id = "TTTC8908R" if is_real else "VTTC8908R"

        params = {
            "CANO": trenv.my_acct,
            "ACNT_PRDT_CD": trenv.my_prod,
            "PDNO": stock_code,
            "ORD_UNPR": str(price),
            "ORD_DVSN": "01",  # 시장가 기준
            "CMA_EVLU_AMT_ICLD_YN": "N",
            "OVRS_ICLD_YN": "N"
        }

        res = ka._url_fetch(
            "/uapi/domestic-stock/v1/trading/inquire-psbl-order",
            tr_id, "", params
        )

        if not res.isOK():
            logging.warning(f"매수가능 조회 실패: {stock_code}")
            return {"amount": 0, "quantity": 0}

        output = res.getBody().output

        return {
            "amount": int(output.get("nrcvb_buy_amt", 0)),
            "quantity": int(output.get("nrcvb_buy_qty", 0))
        }

    except Exception as e:
        logging.error(f"매수가능 조회 에러 ({stock_code}): {e}")
        return {"amount": 0, "quantity": 0}


# =============================================================================
# 예수금 조회
# =============================================================================

def get_deposit(env_dv: str = "real") -> dict:
    """
    예수금 및 계좌 요약 조회 (캐시 사용 - get_holdings와 동일 엔드포인트)

    Args:
        env_dv: 환경 구분 (real/demo 또는 prod/vps)

    Returns:
        dict with keys:
        - deposit: 예수금총금액
        - total_eval: 총평가금액
        - purchase_amount: 매입금액합계
        - eval_amount: 평가금액합계
        - profit_loss: 평가손익합계

    Note:
        skill: API 실패 시 빈 dict 반환
    """
    try:
        raw = _get_balance_cached(env_dv)

        if raw is None:
            logging.warning("예수금 조회 실패")
            return {}

        # output2: 계좌 요약 정보
        output2 = raw["output2"]

        if isinstance(output2, list) and len(output2) > 0:
            summary = output2[0]
        elif isinstance(output2, dict):
            summary = output2
        else:
            logging.warning("예수금 데이터 형식 오류")
            return {}

        return {
            "deposit": int(summary.get("dnca_tot_amt", 0)),
            "total_eval": int(summary.get("tot_evlu_amt", 0)),
            "purchase_amount": int(summary.get("pchs_amt_smtl_amt", 0)),
            "eval_amount": int(summary.get("evlu_amt_smtl_amt", 0)),
            "profit_loss": int(summary.get("evlu_pfls_smtl_amt", 0)),
        }

    except Exception as e:
        logging.error(f"예수금 조회 에러: {e}")
        return {}


# =============================================================================
# 호가 정보 조회
# =============================================================================

def get_orderbook(
    stock_code: str,
    env_dv: str = "real"
) -> dict:
    """
    주식 호가 정보 조회 (10단계 호가)

    Args:
        stock_code: 종목코드 (6자리)
        env_dv: 환경 구분 (real/demo 또는 prod/vps)

    Returns:
        dict with keys:
        - stock_code: 종목코드
        - stock_name: 종목명
        - current_price: 현재가
        - ask_prices: 매도호가 10단계 (list[int])
        - ask_volumes: 매도잔량 10단계 (list[int])
        - bid_prices: 매수호가 10단계 (list[int])
        - bid_volumes: 매수잔량 10단계 (list[int])
        - total_ask_volume: 총 매도잔량
        - total_bid_volume: 총 매수잔량
        - expected_price: 예상체결가
        - expected_volume: 예상체결량

    Note:
        skill: API 실패 시 빈 dict 반환
    """
    if not _assert_trenv_ready(f"호가 조회 {stock_code}"):
        return {}

    try:
        tr_id = "FHKST01010200"

        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code
        }

        res = ka._url_fetch(
            "/uapi/domestic-stock/v1/quotations/inquire-asking-price-exp-ccn",
            tr_id, "", params
        )

        if not res.isOK():
            logging.warning(f"호가 조회 실패: {stock_code}")
            return {}

        body = res.getBody()
        output1 = body.output1  # 호가 정보
        output2 = body.output2  # 예상체결 정보

        # 호가 데이터 파싱
        ask_prices = []
        ask_volumes = []
        bid_prices = []
        bid_volumes = []

        for i in range(1, 11):
            # 매도호가
            ask_price = int(output1.get(f"askp{i}", 0))
            ask_volume = int(output1.get(f"askp_rsqn{i}", 0))
            ask_prices.append(ask_price)
            ask_volumes.append(ask_volume)

            # 매수호가
            bid_price = int(output1.get(f"bidp{i}", 0))
            bid_volume = int(output1.get(f"bidp_rsqn{i}", 0))
            bid_prices.append(bid_price)
            bid_volumes.append(bid_volume)

        return {
            "stock_code": stock_code,
            "stock_name": output1.get("hts_kor_isnm", ""),
            "current_price": int(output2.get("stck_prpr", 0)) if output2 else 0,
            "ask_prices": ask_prices,
            "ask_volumes": ask_volumes,
            "bid_prices": bid_prices,
            "bid_volumes": bid_volumes,
            "total_ask_volume": int(output1.get("total_askp_rsqn", 0)),
            "total_bid_volume": int(output1.get("total_bidp_rsqn", 0)),
            "expected_price": int(output2.get("antc_cnpr", 0)) if output2 else 0,
            "expected_volume": int(output2.get("antc_cnqn", 0)) if output2 else 0,
        }

    except Exception as e:
        logging.error(f"호가 조회 에러 ({stock_code}): {e}")
        return {}


# =============================================================================
# 미체결 주문 조회
# =============================================================================

def get_pending_orders(env_dv: str = "real") -> tuple[pd.DataFrame, bool]:
    """
    미체결 주문 목록 조회

    Returns:
        tuple[DataFrame, bool]: (미체결 목록, API 성공 여부)
        API 실패 시 (empty DataFrame, False), 성공(0건 포함) 시 True
    """
    if not _assert_trenv_ready("미체결 주문 조회"):
        return pd.DataFrame(), False

    try:
        trenv = ka.getTREnv()

        # env_dv 정규화: real/prod → 실전, demo/vps → 모의
        is_real = env_dv in ("real", "prod")
        tr_id = "TTTC8001R" if is_real else "VTTC8001R"
        
        params = {
            "CANO": trenv.my_acct,
            "ACNT_PRDT_CD": trenv.my_prod,
            "INQR_STRT_DT": datetime.now().strftime("%Y%m%d"),
            "INQR_END_DT": datetime.now().strftime("%Y%m%d"),
            "SLL_BUY_DVSN_CD": "00",  # 전체
            "INQR_DVSN": "00",  # 역순
            "PDNO": "",  # 전체 종목
            "CCLD_DVSN": "01",  # 미체결
            "ORD_GNO_BRNO": "",
            "ODNO": "",
            "INQR_DVSN_3": "00",
            "INQR_DVSN_1": "",
            "CTX_AREA_FK100": "",
            "CTX_AREA_NK100": ""
        }
        
        res = ka._url_fetch(
            "/uapi/domestic-stock/v1/trading/inquire-daily-ccld",
            tr_id, "", params
        )
        
        if not res.isOK():
            logging.warning("미체결 주문 조회 실패")
            return pd.DataFrame(), False

        df = pd.DataFrame(res.getBody().output1)

        if df.empty:
            return pd.DataFrame(), True
        
        df = df.rename(columns={
            "odno": "order_no",
            "ord_orgno": "org_no",
            "pdno": "stock_code",
            "prdt_name": "stock_name",
            "sll_buy_dvsn_cd_name": "order_type",
            "ord_qty": "order_qty",
            "ord_unpr": "order_price",
            "tot_ccld_qty": "filled_qty",
            "rmn_qty": "unfilled_qty",
            "ord_tmd": "order_time"
        })

        # 필요한 컬럼만 선택
        columns = [
            "order_no", "org_no", "stock_code", "stock_name", "order_type",
            "order_qty", "order_price", "filled_qty", "unfilled_qty", "order_time"
        ]
        df = df[[col for col in columns if col in df.columns]]
        
        # 숫자형 변환
        for col in ["order_qty", "order_price", "filled_qty", "unfilled_qty"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        
        # 미체결 수량이 0보다 큰 것만 필터
        if "unfilled_qty" in df.columns:
            df = df[df["unfilled_qty"] > 0]
        
        return df.reset_index(drop=True), True

    except Exception as e:
        logging.error(f"미체결 주문 조회 에러: {e}")
        return pd.DataFrame(), False


# =============================================================================
# 주문 취소
# =============================================================================

def cancel_order(
    order_no: str,
    stock_code: str,
    qty: int,
    org_no: str = "",
    env_dv: str = "real"
) -> dict:
    """
    주문 취소
    
    Args:
        order_no: 주문번호
        stock_code: 종목코드
        qty: 취소수량
        env_dv: 환경 구분 (real/demo 또는 prod/vps)
        
    Returns:
        dict with keys:
        - success: 취소 성공 여부
        - order_no: 취소된 주문번호
        - message: 결과 메시지
        
    Note:
        skill: API 실패 시 success=False 반환
    """
    if not _assert_trenv_ready(f"주문 취소 {order_no}"):
        return {"success": False, "order_no": order_no, "message": "재인증이 필요합니다"}

    try:
        trenv = ka.getTREnv()

        is_real = env_dv in ("real", "prod")
        tr_id = "TTTC0013U" if is_real else "VTTC0013U"
        
        params = {
            "CANO": trenv.my_acct,
            "ACNT_PRDT_CD": trenv.my_prod,
            "KRX_FWDG_ORD_ORGNO": org_no,
            "ORGN_ODNO": order_no,
            "ORD_DVSN": "00",
            "RVSE_CNCL_DVSN_CD": "02",
            "ORD_QTY": str(qty),
            "ORD_UNPR": "0",
            "QTY_ALL_ORD_YN": "Y",
            "EXCG_ID_DVSN_CD": "KRX",
        }
        
        logging.info(f"주문 취소 요청: tr_id={tr_id}, order_no={order_no}, org_no='{org_no}'")
        res = ka._url_fetch(
            "/uapi/domestic-stock/v1/trading/order-rvsecncl",
            tr_id, "", params, postFlag=True
        )
        if not res.isOK():
            body = res.getBody()
            error_msg = getattr(body, 'msg1', None) or "취소 실패"
            logging.warning(f"주문 취소 실패: {order_no} - {error_msg}")
            return {
                "success": False,
                "order_no": order_no,
                "message": str(error_msg)
            }
        
        output = res.getBody().output
        
        return {
            "success": True,
            "order_no": output.get("ODNO", order_no),
            "message": "주문이 취소되었습니다"
        }
        
    except Exception as e:
        logging.error(f"주문 취소 에러 ({order_no}): {e}")
        return {
            "success": False,
            "order_no": order_no,
            "message": str(e)
        }

