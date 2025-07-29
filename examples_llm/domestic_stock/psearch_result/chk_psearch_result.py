"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from psearch_result import psearch_result

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내주식] 시세분석 > 종목조건검색조회 [국내주식-039]
##############################################################################################

COLUMN_MAPPING = {
    'code': '종목코드',
    'name': '종목명',
    'daebi': '전일대비부호',
    'price': '현재가',
    'chgrate': '등락율',
    'acml_vol': '거래량',
    'trade_amt': '거래대금',
    'change': '전일대비',
    'cttr': '체결강도',
    'open': '시가',
    'high': '고가',
    'low': '저가',
    'high52': '52주최고가',
    'low52': '52주최저가',
    'expprice': '예상체결가',
    'expchange': '예상대비',
    'expchggrate': '예상등락률',
    'expcvol': '예상체결수량',
    'chgrate2': '전일거래량대비율',
    'expdaebi': '예상대비부호',
    'recprice': '기준가',
    'uplmtprice': '상한가',
    'dnlmtprice': '하한가',
    'stotprice': '시가총액'
}

NUMERIC_COLUMNS = []


def main():
    """
    종목조건검색조회 테스트 함수
    
    이 함수는 종목조건검색조회 API를 호출하여 결과를 출력합니다.
    
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

    # case1 조회
    logging.info("=== case1 조회 ===")
    try:
        result = psearch_result(user_id=trenv.my_htsid, seq="0")
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
