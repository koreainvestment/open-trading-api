"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from inquire_period_trade_profit import inquire_period_trade_profit

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내주식] 주문/계좌 > 기간별매매손익현황조회[v1_국내주식-060]
##############################################################################################

COLUMN_MAPPING = {
    'trad_dt': '매매일자',
    'pdno': '상품번호',
    'prdt_name': '상품명',
    'trad_dvsn_name': '매매구분명',
    'loan_dt': '대출일자',
    'hldg_qty': '보유수량',
    'pchs_unpr': '매입단가',
    'buy_qty': '매수수량',
    'buy_amt': '매수금액',
    'sll_pric': '매도가격',
    'sll_qty': '매도수량',
    'sll_amt': '매도금액',
    'rlzt_pfls': '실현손익',
    'pfls_rt': '손익률',
    'fee': '수수료',
    'tl_tax': '제세금',
    'loan_int': '대출이자',
    'sll_qty_smtl': '매도수량합계',
    'sll_tr_amt_smtl': '매도거래금액합계',
    'sll_fee_smtl': '매도수수료합계',
    'sll_tltx_smtl': '매도제세금합계',
    'sll_excc_amt_smtl': '매도정산금액합계',
    'buyqty_smtl': '매수수량합계',
    'buy_tr_amt_smtl': '매수거래금액합계',
    'buy_fee_smtl': '매수수수료합계',
    'buy_tax_smtl': '매수제세금합계',
    'buy_excc_amt_smtl': '매수정산금액합계',
    'tot_qty': '총수량',
    'tot_tr_amt': '총거래금액',
    'tot_fee': '총수수료',
    'tot_tltx': '총제세금',
    'tot_excc_amt': '총정산금액',
    'tot_rlzt_pfls': '총실현손익',
    'loan_int': '대출이자',
    'tot_pftrt': '총수익률'
}

NUMERIC_COLUMNS = []


def main():
    """
    기간별매매손익현황조회 테스트 함수
    
    이 함수는 기간별매매손익현황조회 API를 호출하여 결과를 출력합니다.
    
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

    # Case1 조회
    logging.info("=== Case1 조회 ===")
    try:
        result1, result2 = inquire_period_trade_profit(
            cano=trenv.my_acct,
            acnt_prdt_cd=trenv.my_prod,
            sort_dvsn="02",
            inqr_strt_dt="20230216",
            inqr_end_dt="20240301",
            cblc_dvsn="00"
        )
    except ValueError as e:
        logging.error("에러 발생: %s" % str(e))
        return

    # output1 처리
    logging.info("사용 가능한 컬럼 (output1): %s", result1.columns.tolist())

    # 컬럼명 한글 변환 및 데이터 출력
    result1 = result1.rename(columns=COLUMN_MAPPING)

    # 숫자형 컬럼 소수점 둘째자리까지 표시

    for col in NUMERIC_COLUMNS:
        if col in result1.columns:
            result1[col] = pd.to_numeric(result1[col], errors='coerce').round(2)

    logging.info("결과 (output1):")
    print(result1)

    # output2 처리
    logging.info("사용 가능한 컬럼 (output2): %s", result2.columns.tolist())

    # 컬럼명 한글 변환 및 데이터 출력
    result2 = result2.rename(columns=COLUMN_MAPPING)

    # 숫자형 컬럼 소수점 둘째자리까지 표시
    for col in NUMERIC_COLUMNS:
        if col in result2.columns:
            result2[col] = pd.to_numeric(result2[col], errors='coerce').round(2)

    logging.info("결과 (output2):")
    print(result2)


if __name__ == "__main__":
    main()
