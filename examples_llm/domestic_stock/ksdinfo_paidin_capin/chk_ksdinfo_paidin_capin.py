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
from ksdinfo_paidin_capin import ksdinfo_paidin_capin

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [국내주식] 종목정보 > 예탁원정보(유상증자일정)[국내주식-143]
##############################################################################################

COLUMN_MAPPING = {
    'record_date': '기준일',
    'sht_cd': '종목코드',
    'tot_issue_stk_qty': '발행주식',
    'issue_stk_qty': '발행할주식',
    'fix_rate': '확정배정율',
    'disc_rate': '할인율',
    'fix_price': '발행예정가',
    'right_dt': '권리락일',
    'sub_term_ft': '청약기간',
    'sub_term': '청약기간',
    'list_date': '상장/등록일',
    'stk_kind': '주식종류'
}

NUMERIC_COLUMNS = []


def main():
    """
    [국내주식] 종목정보
    예탁원정보(유상증자일정)[국내주식-143]

    예탁원정보(유상증자일정) 테스트 함수
    
    Parameters:
        - cts (str): CTS (공백)
        - gb1 (str): 조회구분 (1(청약일별), 2(기준일별))
        - f_dt (str): 조회일자From (일자 ~)
        - t_dt (str): 조회일자To (~ 일자)
        - sht_cd (str): 종목코드 (공백(전체),  특정종목 조회시(종목코드))
    Returns:
        - DataFrame: 예탁원정보(유상증자일정) 결과
    
    Example:
        >>> df = ksdinfo_paidin_capin(cts="", gb1="1", f_dt="20250101", t_dt="20250101", sht_cd="")
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
        result = ksdinfo_paidin_capin(
            cts="",  # CTS
            gb1="1",  # 조회구분
            f_dt="20230301",  # 조회일자From
            t_dt="20240326",  # 조회일자To
            sht_cd="",  # 종목코드
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
        logger.info("=== 예탁원정보(유상증자일정) 결과 ===")
        logger.info("조회된 데이터 건수: %d", len(result))
        print(result)
        
    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise

if __name__ == "__main__":
    main()
