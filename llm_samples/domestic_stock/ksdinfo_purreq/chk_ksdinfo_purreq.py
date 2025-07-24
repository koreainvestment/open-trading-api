# -*- coding: utf-8 -*-
"""
Created on 2025-06-17

@author: LaivData jjlee with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])  # kis_auth 파일 경로 추가
import kis_auth as ka
from ksdinfo_purreq import ksdinfo_purreq

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [국내주식] 종목정보 > 예탁원정보(주식매수청구일정)[국내주식-146]
##############################################################################################

# 통합 컬럼 매핑
COLUMN_MAPPING = {
    'record_date': '기준일',
    'sht_cd': '종목코드',
    'stk_kind': '주식종류',
    'opp_opi_rcpt_term': '반대의사접수시한',
    'buy_req_rcpt_term': '매수청구접수시한',
    'buy_req_price': '매수청구가격',
    'buy_amt_pay_dt': '매수대금지급일',
    'meet_dt': '주총일'
}

NUMERIC_COLUMNS = []

def main():
    """
    [국내주식] 종목정보
    예탁원정보(주식매수청구일정)[국내주식-146]

    예탁원정보(주식매수청구일정) 테스트 함수
    
    Parameters:
        - sht_cd (str): 종목코드 (공백: 전체,  특정종목 조회시 : 종목코드)
        - t_dt (str): 조회일자To (~ 일자)
        - f_dt (str): 조회일자From (일자 ~)
        - cts (str): CTS (공백)
    Returns:
        - DataFrame: 예탁원정보(주식매수청구일정) 결과
    
    Example:
        >>> df = ksdinfo_purreq(sht_cd="", t_dt="20250131", f_dt="20250101", cts="")
    """
    try:
        # pandas 출력 옵션 설정
        pd.set_option('display.max_columns', None)  # 모든 컬럼 표시
        pd.set_option('display.width', None)  # 출력 너비 제한 해제
        pd.set_option('display.max_rows', None)  # 모든 행 표시

        # 토큰 발급
        logger.info("토큰 발급 중...")
        ka.auth()
        logger.info("토큰 발급 완료")        
        
        # API 호출        
        result = ksdinfo_purreq(
            sht_cd="",  # 종목코드
            t_dt="20250131",  # 조회일자To
            f_dt="20250101",  # 조회일자From
            cts="",  # CTS
        )
        
        if result is None or result.empty:
            logger.warning("조회된 데이터가 없습니다.")
            return
        
        # 컬럼명 출력
        logger.info("사용 가능한 컬럼 목록:")
        logger.info(result.columns.tolist())

        # 한글 컬럼명으로 변환
        result = result.rename(columns=COLUMN_MAPPING)

        for col in NUMERIC_COLUMNS:
            if col in result.columns:
                result[col] = pd.to_numeric(result[col], errors='coerce').round(2)

        # 결과 출력
        logger.info("=== 예탁원정보(주식매수청구일정) 결과 ===")
        logger.info("조회된 데이터 건수: %d", len(result))
        print(result)
        
    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise

if __name__ == "__main__":
    main()
