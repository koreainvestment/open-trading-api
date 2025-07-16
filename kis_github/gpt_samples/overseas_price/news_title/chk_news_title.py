"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from news_title import news_title

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [해외주식] 시세분석 > 해외뉴스종합(제목) [해외주식-053]
##############################################################################################

def main():
    """
    해외뉴스종합(제목) 조회 테스트 함수
    
    이 함수는 해외뉴스종합(제목) API를 호출하여 결과를 출력합니다.
    
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
        result = news_title(
            info_gb="",
            class_cd="",
            nation_cd="",
            exchange_cd="",
            symb="",
            data_dt="",
            data_tm="",
            cts=""
        )
    except ValueError as e:
        logging.error("에러 발생: %s" % str(e))
        return
    
    logging.info("사용 가능한 컬럼: %s", result.columns.tolist())
    
    # 컬럼명 한글 변환 및 데이터 출력
    column_mapping = {
        'info_gb': '뉴스구분',
        'news_key': '뉴스키',
        'data_dt': '조회일자',
        'data_tm': '조회시간',
        'class_cd': '중분류',
        'class_name': '중분류명',
        'source': '자료원',
        'nation_cd': '국가코드',
        'exchange_cd': '거래소코드',
        'symb': '종목코드',
        'symb_name': '종목명',
        'title': '제목'
    }
    
    result = result.rename(columns=column_mapping)
    
    # 숫자형 컬럼 소수점 둘째자리까지 표시 (메타데이터에 number 타입 필드 없음)
    numeric_columns = []
    
    for col in numeric_columns:
        if col in result.columns:
            result[col] = pd.to_numeric(result[col], errors='coerce').round(2)
    
    logging.info("결과:")
    print(result)

if __name__ == "__main__":
    main() 