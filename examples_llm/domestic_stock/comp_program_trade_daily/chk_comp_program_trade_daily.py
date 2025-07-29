"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from comp_program_trade_daily import comp_program_trade_daily

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내주식] 시세분석 > 프로그램매매 종합현황(일별)[국내주식-115]
##############################################################################################

COLUMN_MAPPING = {
    'stck_bsop_date': '주식 영업 일자',
    'nabt_entm_seln_tr_pbmn': '비차익 위탁 매도 거래 대금',
    'nabt_onsl_seln_vol': '비차익 자기 매도 거래량',
    'whol_onsl_seln_tr_pbmn': '전체 자기 매도 거래 대금',
    'arbt_smtn_shnu_vol': '차익 합계 매수2 거래량',
    'nabt_smtn_shnu_tr_pbmn': '비차익 합계 매수2 거래 대금',
    'arbt_entm_ntby_qty': '차익 위탁 순매수 수량',
    'nabt_entm_ntby_tr_pbmn': '비차익 위탁 순매수 거래 대금',
    'arbt_entm_seln_vol': '차익 위탁 매도 거래량',
    'nabt_entm_seln_vol_rate': '비차익 위탁 매도 거래량 비율',
    'nabt_onsl_seln_vol_rate': '비차익 자기 매도 거래량 비율',
    'whol_onsl_seln_tr_pbmn_rate': '전체 자기 매도 거래 대금 비율',
    'arbt_smtm_shun_vol_rate': '차익 합계 매수 거래량 비율',
    'nabt_smtm_shun_tr_pbmn_rate': '비차익 합계 매수 거래대금 비율',
    'arbt_entm_ntby_qty_rate': '차익 위탁 순매수 수량 비율',
    'nabt_entm_ntby_tr_pbmn_rate': '비차익 위탁 순매수 거래 대금',
    'arbt_entm_seln_vol_rate': '차익 위탁 매도 거래량 비율',
    'nabt_entm_seln_tr_pbmn_rate': '비차익 위탁 매도 거래 대금 비',
    'nabt_onsl_seln_tr_pbmn': '비차익 자기 매도 거래 대금',
    'whol_smtn_seln_vol': '전체 합계 매도 거래량',
    'arbt_smtn_shnu_tr_pbmn': '차익 합계 매수2 거래 대금',
    'whol_entm_shnu_vol': '전체 위탁 매수2 거래량',
    'arbt_entm_ntby_tr_pbmn': '차익 위탁 순매수 거래 대금',
    'nabt_onsl_ntby_qty': '비차익 자기 순매수 수량',
    'arbt_entm_seln_tr_pbmn': '차익 위탁 매도 거래 대금',
    'whol_seln_vol_rate': '전체 매도 거래량 비율',
    'whol_entm_shnu_vol_rate': '전체 위탁 매수 거래량 비율',
    'whol_entm_seln_tr_pbmn': '전체 위탁 매도 거래 대금',
    'nabt_smtm_seln_vol': '비차익 합계 매도 거래량',
    'arbt_entm_shnu_vol': '차익 위탁 매수2 거래량',
    'nabt_entm_shnu_tr_pbmn': '비차익 위탁 매수2 거래 대금',
    'whol_onsl_shnu_vol': '전체 자기 매수2 거래량',
    'arbt_onsl_ntby_tr_pbmn': '차익 자기 순매수 거래 대금',
    'nabt_smtn_ntby_qty': '비차익 합계 순매수 수량',
    'arbt_onsl_seln_vol': '차익 자기 매도 거래량',
    'whol_entm_ntby_qty': '전체 위탁 순매수 수량',
    'nabt_onsl_ntby_tr_pbmn': '비차익 자기 순매수 거래 대금',
    'arbt_onsl_seln_tr_pbmn': '차익 자기 매도 거래 대금',
    'nabt_smtm_seln_tr_pbmn_rate': '비차익 합계 매도 거래대금 비율',
    'arbt_entm_shnu_vol_rate': '차익 위탁 매수 거래량 비율',
    'nabt_entm_shnu_tr_pbmn_rate': '비차익 위탁 매수 거래 대금 비',
    'whol_onsl_shnu_tr_pbmn': '전체 자기 매수2 거래 대금',
    'arbt_onsl_ntby_tr_pbmn_rate': '차익 자기 순매수 거래 대금 비',
    'nabt_smtm_ntby_qty_rate': '비차익 합계 순매수 수량 비율',
    'arbt_onsl_seln_vol_rate': '차익 자기 매도 거래량 비율',
    'whol_entm_seln_vol': '전체 위탁 매도 거래량',
    'arbt_entm_shnu_tr_pbmn': '차익 위탁 매수2 거래 대금',
    'nabt_onsl_shnu_vol': '비차익 자기 매수2 거래량',
    'whol_smtn_shnu_vol': '전체 합계 매수2 거래량',
    'arbt_smtn_ntby_tr_pbmn': '차익 합계 순매수 거래 대금',
    'arbt_smtn_seln_vol': '차익 합계 매도 거래량',
    'whol_entm_seln_tr_pbmn_rate': '전체 위탁 매도 거래 대금 비율',
    'nabt_onsl_seln_vol_rate': '전체 자기 매도 거래량 비율',
    'arbt_onsl_shnu_vol_rate': '차익 자기 매수 거래량 비율',
    'nabt_smtm_shun_vol_rate': '비차익 합계 매수 거래량 비율',
    'whol_shun_tr_pbmn_rate': '전체 매수 거래대금 비율',
    'nabt_entm_ntby_qty_rate': '비차익 위탁 순매수 수량 비율',
    'arbt_smtm_seln_tr_pbmn_rate': '차익 합계 매도 거래대금 비율',
    'arbt_onsl_shnu_vol': '차익 자기 매수2 거래량',
    'nabt_onsl_shnu_tr_pbmn': '비차익 자기 매수2 거래 대금',
    'nabt_smtn_shnu_vol': '비차익 합계 매수2 거래량',
    'whol_smtn_shnu_tr_pbmn': '전체 합계 매수2 거래 대금',
    'arbt_smtm_ntby_qty': '차익 합계 순매수 수량',
    'nabt_smtn_ntby_tr_pbmn': '비차익 합계 순매수 거래 대금',
    'arbt_smtn_seln_tr_pbmn': '차익 합계 매도 거래 대금',
    'arbt_onsl_shnu_tr_pbmn_rate': '차익 자기 매수 거래 대금 비율',
    'whol_shun_vol_rate': '전체 매수 거래량 비율',
    'arbt_smtm_ntby_tr_pbmn_rate': '차익 합계 순매수 거래대금 비율',
    'whol_entm_ntby_qty_rate': '전체 위탁 순매수 수량 비율',
    'arbt_smtm_seln_tr_pbmn_rate': '차익 합계 매도 거래대금 비율'
}

NUMERIC_COLUMNS = []


def main():
    """
    프로그램매매 종합현황(일별) 조회 테스트 함수
    
    이 함수는 프로그램매매 종합현황(일별) API를 호출하여 결과를 출력합니다.
    
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
        result = comp_program_trade_daily(
            fid_cond_mrkt_div_code="J",
            fid_mrkt_cls_code="K",
            fid_input_date_1="20250101",
            fid_input_date_2="20250617"
        )
    except ValueError as e:
        logging.error("에러 발생: %s" % str(e))
        return

    logging.info("사용 가능한 컬럼: %s", result.columns.tolist())

    # 컬럼명 한글 변환 및 데이터 출력

    result = result.rename(columns=COLUMN_MAPPING)

    # 숫자형 컬럼 (메타데이터에 number로 명시적으로 선언된 필드가 없음)

    for col in NUMERIC_COLUMNS:
        if col in result.columns:
            result[col] = pd.to_numeric(result[col], errors='coerce').round(2)

    logging.info("결과:")
    print(result)


if __name__ == "__main__":
    main()
