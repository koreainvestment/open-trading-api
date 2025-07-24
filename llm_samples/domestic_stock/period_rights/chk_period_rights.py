"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from period_rights import period_rights

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내주식] 주문/계좌 > 기간별계좌권리현황조회 [국내주식-211]
##############################################################################################

COLUMN_MAPPING = {
    'acno10': '계좌번호10',
    'rght_type_cd': '권리유형코드',
    'bass_dt': '기준일자',
    'rght_cblc_type_cd': '권리잔고유형코드',
    'rptt_pdno': '대표상품번호',
    'pdno': '상품번호',
    'prdt_type_cd': '상품유형코드',
    'shtn_pdno': '단축상품번호',
    'prdt_name': '상품명',
    'cblc_qty': '잔고수량',
    'last_alct_qty': '최종배정수량',
    'excs_alct_qty': '초과배정수량',
    'tot_alct_qty': '총배정수량',
    'last_ftsk_qty': '최종단수주수량',
    'last_alct_amt': '최종배정금액',
    'last_ftsk_chgs': '최종단수주대금',
    'rdpt_prca': '상환원금',
    'dlay_int_amt': '지연이자금액',
    'lstg_dt': '상장일자',
    'sbsc_end_dt': '청약종료일자',
    'cash_dfrm_dt': '현금지급일자',
    'rqst_qty': '신청수량',
    'rqst_amt': '신청금액',
    'rqst_dt': '신청일자',
    'rfnd_dt': '환불일자',
    'rfnd_amt': '환불금액',
    'lstg_stqt': '상장주수',
    'tax_amt': '세금금액',
    'sbsc_unpr': '청약단가'
}

NUMERIC_COLUMNS = [
    '잔고수량',
    '최종배정수량',
    '초과배정수량',
    '총배정수량',
    '최종단수주수량',
    '최종배정금액',
    '최종단수주대금',
    '상환원금',
    '지연이자금액',
    '신청수량',
    '신청금액',
    '환불금액',
    '상장주수',
    '세금금액',
    '청약단가'
]


def main():
    """
    기간별계좌권리현황조회 테스트 함수
    
    이 함수는 기간별계좌권리현황조회 API를 호출하여 결과를 출력합니다.
    
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

    # 기간별계좌권리현황조회
    logging.info("=== 기간별계좌권리현황조회 ===")
    try:
        result = period_rights(inqr_dvsn="03", cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, inqr_strt_dt="20250101",
                               inqr_end_dt="20250103")
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
