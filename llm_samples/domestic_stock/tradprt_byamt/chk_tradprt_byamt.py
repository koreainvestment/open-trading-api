"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from tradprt_byamt import tradprt_byamt

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내주식] 시세분석 > 국내주식 체결금액별 매매비중 [국내주식-192]
##############################################################################################

COLUMN_MAPPING = {
    'prpr_name': '가격명',
    'smtn_avrg_prpr': '합계 평균가격',
    'acml_vol': '합계 거래량',
    'whol_ntby_qty_rate': '합계 순매수비율',
    'ntby_cntg_csnu': '합계 순매수건수',
    'seln_cnqn_smtn': '매도 거래량',
    'whol_seln_vol_rate': '매도 거래량비율',
    'seln_cntg_csnu': '매도 건수',
    'shnu_cnqn_smtn': '매수 거래량',
    'whol_shun_vol_rate': '매수 거래량비율',
    'shnu_cntg_csnu': '매수 건수'
}

NUMERIC_COLUMNS = []

def main():
    """
    국내주식 체결금액별 매매비중 조회 테스트 함수
    
    이 함수는 국내주식 체결금액별 매매비중 API를 호출하여 결과를 출력합니다.
    테스트 데이터로 삼성전자(005930)를 사용합니다.
    
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
        result = tradprt_byamt(fid_cond_mrkt_div_code="J", fid_cond_scr_div_code="11119", fid_input_iscd="005930")
    except ValueError as e:
        logging.error("에러 발생: %s" % str(e))
        return
    
    logging.info("사용 가능한 컬럼: %s", result.columns.tolist())
    
    # 컬럼명 한글 변환 및 데이터 출력
    result = result.rename(columns=COLUMN_MAPPING)
    
    # 숫자형 컬럼 소수점 둘째자리까지 표시 (메타데이터에 number 타입 명시된 필드 없음)
    for col in NUMERIC_COLUMNS:
        if col in result.columns:
            result[col] = pd.to_numeric(result[col], errors='coerce').round(2)
    
    logging.info("결과:")
    print(result)

if __name__ == "__main__":
    main() 