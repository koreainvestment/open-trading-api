"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from order_resv_ccnl import order_resv_ccnl

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내주식] 주문/계좌 > 주식예약주문조회[v1_국내주식-020]
##############################################################################################

COLUMN_MAPPING = {
    'rsvn_ord_seq': '예약주문 순번',
    'rsvn_ord_ord_dt': '예약주문주문일자',
    'rsvn_ord_rcit_dt': '예약주문접수일자',
    'pdno': '상품번호',
    'ord_dvsn_cd': '주문구분코드',
    'ord_rsvn_qty': '주문예약수량',
    'tot_ccld_qty': '총체결수량',
    'cncl_ord_dt': '취소주문일자',
    'ord_tmd': '주문시각',
    'ctac_tlno': '연락전화번호',
    'rjct_rson2': '거부사유2',
    'odno': '주문번호',
    'rsvn_ord_rcit_tmd': '예약주문접수시각',
    'kor_item_shtn_name': '한글종목단축명',
    'sll_buy_dvsn_cd': '매도매수구분코드',
    'ord_rsvn_unpr': '주문예약단가',
    'tot_ccld_amt': '총체결금액',
    'loan_dt': '대출일자',
    'cncl_rcit_tmd': '취소접수시각',
    'prcs_rslt': '처리결과',
    'ord_dvsn_name': '주문구분명',
    'tmnl_mdia_kind_cd': '단말매체종류코드',
    'rsvn_end_dt': '예약종료일자'
}

NUMERIC_COLUMNS = []


def main():
    """
    주식예약주문조회 테스트 함수
    
    이 함수는 주식예약주문조회 API를 호출하여 결과를 출력합니다.
    
    Returns:
        None
    """

    # pandas 출력 옵션 설정
    pd.set_option('display.max_columns', None)  # 모든 컬럼 표시
    pd.set_option('display.width', None)  # 출력 너비 제한 해제
    pd.set_option('display.max_rows', None)  # 모든 행 표시

    # 인증 토큰 발급
    ka.auth()

    trenv = ka.getTREnv()

    # case1 조회
    logging.info("=== case1 조회 ===")
    try:
        result = order_resv_ccnl(
            rsvn_ord_ord_dt="20220729",
            rsvn_ord_end_dt="20220810",
            tmnl_mdia_kind_cd="00",
            cano=trenv.my_acct,
            acnt_prdt_cd=trenv.my_prod,
            prcs_dvsn_cd="0",
            cncl_yn="Y"
        )
    except ValueError as e:
        logging.error("에러 발생: %s" % str(e))
        return

    logging.info("사용 가능한 컬럼: %s", result.columns.tolist())

    # 컬럼명 한글 변환 및 데이터 출력
    result = result.rename(columns=COLUMN_MAPPING)

    # 숫자형 컬럼 소수점 둘째자리까지 표시
    for col in NUMERIC_COLUMNS:
        if col in result.columns:
            result[col] = pd.to_numeric(result[col], errors='coerce').round(2)

    logging.info("결과:")
    print(result)


if __name__ == "__main__":
    main()
