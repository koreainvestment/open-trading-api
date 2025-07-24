"""
Created on 20250101 
@author: LaivData SJPark with cursor
"""
import logging
import sys

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from comp_program_trade_today import comp_program_trade_today

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내주식] 시세분석 > 프로그램매매 종합현황(시간) [국내주식-114]
##############################################################################################

COLUMN_MAPPING = {
    'stck_bsop_date': '주식영업일자',
    'stck_clpr': '주식종가',
    'prdy_vrss': '전일대비',
    'prdy_vrss_sign': '전일대비부호',
    'prdy_ctrt': '전일대비율',
    'acml_vol': '누적거래량',
    'acml_tr_pbmn': '누적거래대금',
    'whol_smtn_seln_vol': '전체합계매도거래량',
    'whol_smtn_shnu_vol': '전체합계매수2',
    'whol_smtn_ntby_qty': '전체합계순매수수량',
    'whol_smtn_seln_tr_pbmn': '전체합계매도거래대금',
    'whol_smtn_shnu_tr_pbmn': '전체합계매수2거래대금',
    'whol_smtn_ntby_tr_pbmn': '전체합계순매수거래대금',
    'whol_ntby_vol_icdc': '전체순매수거래량증감',
    'whol_ntby_tr_pbmn_icdc2': '전체순매수거래대금증감2'
}

NUMERIC_COLUMNS = ['전일대비율', '누적거래량', '누적거래대금', '전체합계매도거래량', '전체합계매수2',
                   '전체합계순매수수량', '전체합계매도거래대금', '전체합계매수2거래대금', '전체합계순매수거래대금']


def main():
    """
    프로그램매매 종합현황(시간) 조회 테스트 함수
    
    이 함수는 프로그램매매 종합현황(시간) API를 호출하여 결과를 출력합니다.
    테스트 데이터로 코스피(K) 시장을 사용합니다.
    
    Returns:
        None
    """

    # pandas 출력 옵션 설정
    pd.set_option('display.max_columns', None)  # 모든 컬럼 표시
    pd.set_option('display.width', None)  # 출력 너비 제한 해제
    pd.set_option('display.max_rows', None)  # 모든 행 표시

    # 인증 토큰 발급
    ka.auth()

    # case1 조회
    logging.info("=== case1 조회 ===")
    try:
        result = comp_program_trade_today(fid_cond_mrkt_div_code="J", fid_mrkt_cls_code="K")
    except ValueError as e:
        logging.error("에러 발생: %s" % str(e))
        return

    logging.info("사용 가능한 컬럼: %s", result.columns.tolist())

    # 컬럼명 한글 변환 및 데이터 출력

    result = result.rename(columns=COLUMN_MAPPING)

    # 숫자형 컬럼 소수점 둘째자리까지 표시 (메타데이터에서 number로 명시된 컬럼만)
    for col in NUMERIC_COLUMNS:
        if col in result.columns:
            result[col] = pd.to_numeric(result[col], errors='coerce').round(2)

    logging.info("결과:")
    print(result)


if __name__ == "__main__":
    main()
