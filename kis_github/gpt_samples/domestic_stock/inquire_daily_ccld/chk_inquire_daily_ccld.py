"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from inquire_daily_ccld import inquire_daily_ccld

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내주식] 주문/계좌 > 주식일별주문체결조회[v1_국내주식-005]
##############################################################################################

COLUMN_MAPPING = {
    'ord_dt': '주문일자',
    'ord_gno_brno': '주문채번지점번호',
    'odno': '주문번호',
    'orgn_odno': '원주문번호',
    'ord_dvsn_name': '주문구분명',
    'sll_buy_dvsn_cd': '매도매수구분코드',
    'sll_buy_dvsn_cd_name': '매도매수구분코드명',
    'pdno': '상품번호',
    'prdt_name': '상품명',
    'ord_qty': '주문수량',
    'ord_unpr': '주문단가',
    'ord_tmd': '주문시각',
    'tot_ccld_qty': '총체결수량',
    'avg_prvs': '평균가',
    'cncl_yn': '취소여부',
    'tot_ccld_amt': '총체결금액',
    'loan_dt': '대출일자',
    'ordr_empno': '주문자사번',
    'ord_dvsn_cd': '주문구분코드',
    'cnc_cfrm_qty': '취소확인수량',
    'rmn_qty': '잔여수량',
    'rjct_qty': '거부수량',
    'ccld_cndt_name': '체결조건명',
    'inqr_ip_addr': '조회IP주소',
    'cpbc_ordp_ord_rcit_dvsn_cd': '전산주문표주문접수구분코드',
    'cpbc_ordp_infm_mthd_dvsn_cd': '전산주문표통보방법구분코드',
    'infm_tmd': '통보시각',
    'ctac_tlno': '연락전화번호',
    'prdt_type_cd': '상품유형코드',
    'excg_dvsn_cd': '거래소구분코드',
    'cpbc_ordp_mtrl_dvsn_cd': '전산주문표자료구분코드',
    'ord_orgno': '주문조직번호',
    'rsvn_ord_end_dt': '예약주문종료일자',
    'excg_id_dvsn_Cd': '거래소ID구분코드',
    'stpm_cndt_pric': '스톱지정가조건가격',
    'stpm_efct_occr_dtmd': '스톱지정가효력발생상세시각',
    'tot_ord_qty': '총주문수량',
    'tot_ccld_qty': '총체결수량',
    'tot_ccld_amt': '매입평균가격',
    'prsm_tlex_smtl': '총체결금액',
    'pchs_avg_pric': '추정제비용합계'
}

NUMERIC_COLUMNS = []


def main():
    """
    주식일별주문체결조회 테스트 함수
    
    이 함수는 주식일별주문체결조회 API를 호출하여 결과를 출력합니다.
    
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
        result1, result2 = inquire_daily_ccld(
            env_dv="real",
            pd_dv="inner",
            cano=trenv.my_acct,
            acnt_prdt_cd=trenv.my_prod,
            inqr_strt_dt="20220810",
            inqr_end_dt="20220810",
            sll_buy_dvsn_cd="00",
            inqr_dvsn="00",
            pdno="005930",
            ccld_dvsn="00",
            inqr_dvsn_3="00"
        )
    except ValueError as e:
        logging.error("에러 발생: %s" % str(e))
        return

    # output1 처리
    logging.info("=== output1 결과 ===")
    logging.info("사용 가능한 컬럼: %s", result1.columns.tolist())

    # 컬럼명 한글 변환 및 데이터 출력
    result1 = result1.rename(columns=COLUMN_MAPPING)

    # 숫자형 컬럼 소수점 둘째자리까지 표시 (메타데이터에 number 자료형이 명시된 필드 없음)
    for col in NUMERIC_COLUMNS:
        if col in result1.columns:
            result1[col] = pd.to_numeric(result1[col], errors='coerce').round(2)

    logging.info("결과:")
    print(result1)

    # output2 처리
    logging.info("=== output2 결과 ===")
    logging.info("사용 가능한 컬럼: %s" % result2.columns.tolist())

    # 컬럼명 한글 변환 및 데이터 출력
    result2 = result2.rename(columns=COLUMN_MAPPING)

    # 숫자형 컬럼 소수점 둘째자리까지 표시 (메타데이터에 number 자료형이 명시된 필드 없음)
    for col in NUMERIC_COLUMNS:
        if col in result2.columns:
            result2[col] = pd.to_numeric(result2[col], errors='coerce').round(2)

    logging.info("결과:")
    print(result2)


if __name__ == "__main__":
    main()
