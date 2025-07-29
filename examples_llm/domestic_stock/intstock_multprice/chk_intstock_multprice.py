"""
Created on 20250101 
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from intstock_multprice import intstock_multprice

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내주식] 시세분석 > 관심종목(멀티종목) 시세조회 [국내주식-205]
##############################################################################################

COLUMN_MAPPING = {
    'kospi_kosdaq_cls_name': '코스피 코스닥 구분 명',
    'mrkt_trtm_cls_name': '시장 조치 구분 명',
    'hour_cls_code': '시간 구분 코드',
    'inter_shrn_iscd': '관심 단축 종목코드',
    'inter_kor_isnm': '관심 한글 종목명',
    'inter2_prpr': '관심2 현재가',
    'inter2_prdy_vrss': '관심2 전일 대비',
    'prdy_vrss_sign': '전일 대비 부호',
    'prdy_ctrt': '전일 대비율',
    'acml_vol': '누적 거래량',
    'inter2_oprc': '관심2 시가',
    'inter2_hgpr': '관심2 고가',
    'inter2_lwpr': '관심2 저가',
    'inter2_llam': '관심2 하한가',
    'inter2_mxpr': '관심2 상한가',
    'inter2_askp': '관심2 매도호가',
    'inter2_bidp': '관심2 매수호가',
    'seln_rsqn': '매도 잔량',
    'shnu_rsqn': '매수2 잔량',
    'total_askp_rsqn': '총 매도호가 잔량',
    'total_bidp_rsqn': '총 매수호가 잔량',
    'acml_tr_pbmn': '누적 거래 대금',
    'inter2_prdy_clpr': '관심2 전일 종가',
    'oprc_vrss_hgpr_rate': '시가 대비 최고가 비율',
    'intr_antc_cntg_vrss': '관심 예상 체결 대비',
    'intr_antc_cntg_vrss_sign': '관심 예상 체결 대비 부호',
    'intr_antc_cntg_prdy_ctrt': '관심 예상 체결 전일 대비율',
    'intr_antc_vol': '관심 예상 거래량',
    'inter2_sdpr': '관심2 기준가'
}

NUMERIC_COLUMNS = []


def main():
    """
    관심종목(멀티종목) 시세조회 테스트 함수
    
    이 함수는 관심종목(멀티종목) 시세조회 API를 호출하여 결과를 출력합니다.
    테스트 데이터로 419530, 092070을 사용합니다.
    
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
        result = intstock_multprice(
            fid_cond_mrkt_div_code_1="J",
            fid_input_iscd_1="419530",
            fid_cond_mrkt_div_code_2="J",
            fid_input_iscd_2="092070"
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
