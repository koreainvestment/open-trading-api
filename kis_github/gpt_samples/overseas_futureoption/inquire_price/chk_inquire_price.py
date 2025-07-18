# -*- coding: utf-8 -*-
"""
Created on 2025-07-02

@author: LaivData jjlee with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from inquire_price import inquire_price

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [해외선물옵션] 기본시세 > 해외선물종목현재가 [v1_해외선물-009]
##############################################################################################

# 상수 정의
COLUMN_MAPPING = {
    'proc_date': '최종처리일자',
    'high_price': '고가',
    'proc_time': '최종처리시각',
    'open_price': '시가',
    'trst_mgn': '증거금',
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
    'prev_price': '전일종가',
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

NUMERIC_COLUMNS = ['고가', '시가', '저가', '현재가', '누적거래수량', '전일대비가격', '전일대비율', '매수1수량', '매수1호가', '매도1수량', '매도1호가',
                    '전일종가', '증거금', '체결량', '총매도잔량', '총매수잔량', '틱사이즈', '정산가']

def main():
    """
    [해외선물옵션] 기본시세
    해외선물종목현재가[v1_해외선물-009]

    해외선물종목현재가 테스트 함수
    
    Parameters:
        - srs_cd (str): 종목코드 (ex) BONU25 ※ 종목코드 "포럼 > FAQ > 종목정보 다운로드(해외) - 해외지수선물" 참고)

    Returns:
        - DataFrame: 해외선물종목현재가 결과
    
    Example:
        >>> df = inquire_price(srs_cd="BONU25")
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

        # 해외선물종목현재가 파라미터 설정
        logger.info("API 파라미터 설정 중...")
        srs_cd = "BONU25"  # 종목코드

        
        # API 호출
        logger.info("API 호출 시작: 해외선물종목현재가")
        result = inquire_price(
            srs_cd=srs_cd,  # 종목코드
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
        logger.info("=== 해외선물종목현재가 결과 ===")
        logger.info("조회된 데이터 건수: %d", len(result))
        print(result)
        
    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise

if __name__ == "__main__":
    main()
