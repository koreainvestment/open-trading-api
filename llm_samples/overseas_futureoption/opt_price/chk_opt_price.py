"""
Created on 20250101
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from opt_price import opt_price

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [해외선물옵션] 기본시세 > 해외옵션종목현재가 [해외선물-035]
##############################################################################################

# 컬럼명 매핑
COLUMN_MAPPING = {
    'proc_date': '최종처리일자',
    'proc_time': '최종처리시각',
    'open_price': '시가',
    'high_price': '고가',
    'low_price': '저가',
    'last_price': '현재가',
    'vol': '누적거래수량',
    'prev_diff_flag': '전일대비구분',
    'prev_diff_price': '전일대비가격',
    'prev_diff_rate': '전일대비율',
    'bid_qntt': '매수1수량',
    'bid_price': '매수1호가',
    'ask_qntt': '매도1수량',
    'ask_price': '매도1호가',
    'trst_mgn': '증거금',
    'exch_cd': '거래소코드',
    'crc_cd': '거래통화',
    'trd_fr_date': '상장일',
    'expr_date': '만기일',
    'trd_to_date': '최종거래일',
    'remn_cnt': '잔존일수',
    'last_qntt': '체결량',
    'tot_ask_qntt': '총매도잔량',
    'tot_bid_qntt': '총매수잔량',
    'tick_size': '틱사이즈',
    'open_date': '장개시일자',
    'open_time': '장개시시각',
    'close_date': '장종료일자',
    'close_time': '장종료시각',
    'sbsnsdate': '영업일자',
    'sttl_price': '정산가'
}

# 숫자형 컬럼
NUMERIC_COLUMNS = []

def main():
    """
    해외옵션종목현재가 조회 테스트 함수
    
    이 함수는 해외옵션종목현재가 API를 호출하여 결과를 출력합니다.
    
    Returns:
        None
    """

    # pandas 출력 옵션 설정
    pd.set_option('display.max_columns', None)  # 모든 컬럼 표시
    pd.set_option('display.width', None)  # 출력 너비 제한 해제
    pd.set_option('display.max_rows', None)  # 모든 행 표시
    
    # 인증 토큰 발급
    ka.auth()
    
    # 해외옵션종목현재가 조회
    logging.info("=== 해외옵션종목현재가 조회 ===")
    try:
        result = opt_price(srs_cd="DXM24")
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