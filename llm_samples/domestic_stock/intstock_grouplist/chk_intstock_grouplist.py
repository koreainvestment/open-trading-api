"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from intstock_grouplist import intstock_grouplist

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내주식] 시세분석 > 관심종목 그룹조회 [국내주식-204]
##############################################################################################

COLUMN_MAPPING = {
    'date': '일자',
    'trnm_hour': '전송 시간',
    'data_rank': '데이터 순위',
    'inter_grp_code': '관심 그룹 코드',
    'inter_grp_name': '관심 그룹 명',
    'ask_cnt': '요청 개수'
}

NUMERIC_COLUMNS = []

def main():
    """
    관심종목 그룹조회 테스트 함수
    
    이 함수는 관심종목 그룹조회 API를 호출하여 결과를 출력합니다.
    
    Returns:
        None
    """

    # pandas 출력 옵션 설정
    pd.set_option('display.max_columns', None)  # 모든 컬럼 표시
    pd.set_option('display.width', None)  # 출력 너비 제한 해제
    pd.set_option('display.max_rows', None)  # 모든 행 표시
    
    # 인증 토큰 발급
    ka.auth()
    
    # case1 테스트
    logging.info("=== case1 테스트 ===")
    try:
        result = intstock_grouplist(type="1", fid_etc_cls_code="00", user_id="dttest11")
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