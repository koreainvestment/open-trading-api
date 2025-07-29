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
from inquire_time_futurechartprice import inquire_time_futurechartprice

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [해외선물옵션] 기본시세 > 해외선물 분봉조회[해외선물-016]
##############################################################################################

# 상수 정의
COLUMN_MAPPING = {
    'ret_cnt': '자료개수',
    'last_n_cnt': 'N틱최종개수',
    'index_key': '이전조회KEY',
    'data_date': '일자',
    'data_time': '시각',
    'open_price': '시가',
    'high_price': '고가',
    'low_price': '저가',
    'last_price': '체결가격',
    'last_qntt': '체결수량',
    'vol': '누적거래수량',
    'prev_diff_flag': '전일대비구분',
    'prev_diff_price': '전일대비가격',
    'prev_diff_rate': '전일대비율'
}
NUMERIC_COLUMNS = ['전일대비구분', '전일대비가격', '전일대비율', '시가', '고가', '저가', '체결가격', '체결수량', '누적거래수량']

def main():
    """
    [해외선물옵션] 기본시세
    해외선물 분봉조회[해외선물-016]

    해외선물 분봉조회 테스트 함수
    
    Parameters:
        - srs_cd (str): 종목코드 (ex) BONU25 ※ 종목코드 "포럼 > FAQ > 종목정보 다운로드(해외) - 해외지수선물" 참고)
        - exch_cd (str): 거래소코드 (EUREX)
        - start_date_time (str): 조회시작일시 (공백)
        - close_date_time (str): 조회종료일시 (ex) 20230823)
        - qry_tp (str): 조회구분 (Q : 최초조회시 , P : 다음키(INDEX_KEY) 입력하여 조회시)
        - qry_cnt (str): 요청개수 (120 (조회갯수))
        - qry_gap (str): 묶음개수 (5 (분간격))
        - index_key (str): 이전조회KEY (다음조회(QRY_TP를 P로 입력) 시, 이전 호출의 "output1 > index_key" 기입하여 조회)

    Returns:
        - DataFrame: 해외선물 분봉조회 결과
    
    Example:
        >>> df1, df2 = inquire_time_futurechartprice(srs_cd="BONU25", exch_cd="EUREX", start_date_time="20250101", close_date_time="20250702", qry_tp="", qry_cnt="120", qry_gap="5", index_key="")
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
        logger.info("API 호출 시작: 해외선물 분봉조회")
        result1, result2 = inquire_time_futurechartprice(
            srs_cd="BONU25",  # 종목코드
            exch_cd="EUREX",  # 거래소코드
            start_date_time="20250101",  # 조회시작일시
            close_date_time="20250701",  # 조회종료일시
            qry_tp="Q",  # 조회구분
            qry_cnt="120",  # 요청개수
            qry_gap="1",  # 묶음개수
            index_key="",  # 이전조회KEY
        )
        
        # 결과 확인
        results = [result1, result2]
        if all(result is None or result.empty for result in results):
            logger.warning("조회된 데이터가 없습니다.")
            return
        

        # output1 결과 처리
        logger.info("=== output1 조회 ===")
        if not result1.empty:
            logger.info("사용 가능한 컬럼: %s", result1.columns.tolist())
            
            # 통합 컬럼명 한글 변환 (필요한 컬럼만 자동 매핑됨)
            result1 = result1.rename(columns=COLUMN_MAPPING)
            for col in NUMERIC_COLUMNS:
                if col in result1.columns:
                    result1[col] = pd.to_numeric(result1[col], errors='coerce').round(2)
            logger.info("output1 결과:")
            print(result1)
        else:
            logger.info("output1 데이터가 없습니다.")

        # output2 결과 처리
        logger.info("=== output2 조회 ===")
        if not result2.empty:
            logger.info("사용 가능한 컬럼: %s", result2.columns.tolist())
            
            # 통합 컬럼명 한글 변환 (필요한 컬럼만 자동 매핑됨)
            result2 = result2.rename(columns=COLUMN_MAPPING)
            for col in NUMERIC_COLUMNS:
                if col in result2.columns:
                    result2[col] = pd.to_numeric(result2[col], errors='coerce').round(2)
            logger.info("output2 결과:")
            print(result2)
        else:
            logger.info("output2 데이터가 없습니다.")

        
    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise

if __name__ == "__main__":
    main()
