"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from overtime_exp_trans_fluct import overtime_exp_trans_fluct

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내주식] 시세분석 > 국내주식 시간외예상체결등락률 [국내주식-140]
##############################################################################################

COLUMN_MAPPING = {
    'data_rank': '데이터 순위',
    'iscd_stat_cls_code': '종목 상태 구분 코드',
    'stck_shrn_iscd': '주식 단축 종목코드',
    'hts_kor_isnm': 'HTS 한글 종목명',
    'ovtm_untp_antc_cnpr': '시간외 단일가 예상 체결가',
    'ovtm_untp_antc_cntg_vrss': '시간외 단일가 예상 체결 대비',
    'ovtm_untp_antc_cntg_vrsssign': '시간외 단일가 예상 체결 대비',
    'ovtm_untp_antc_cntg_ctrt': '시간외 단일가 예상 체결 대비율',
    'ovtm_untp_askp_rsqn1': '시간외 단일가 매도호가 잔량1',
    'ovtm_untp_bidp_rsqn1': '시간외 단일가 매수호가 잔량1',
    'ovtm_untp_antc_cnqn': '시간외 단일가 예상 체결량',
    'itmt_vol': '장중 거래량',
    'stck_prpr': '주식 현재가'
}

NUMERIC_COLUMNS = []


def main():
    """
    국내주식 시간외예상체결등락률 조회 테스트 함수
    
    이 함수는 국내주식 시간외예상체결등락률 API를 호출하여 결과를 출력합니다.
    
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
        result = overtime_exp_trans_fluct(
            fid_cond_mrkt_div_code="J",
            fid_cond_scr_div_code="11186",
            fid_input_iscd="0000",
            fid_rank_sort_cls_code="0",
            fid_div_cls_code="0"
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
