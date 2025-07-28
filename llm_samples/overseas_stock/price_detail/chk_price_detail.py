# -*- coding: utf-8 -*-
"""
Created on 2025-06-30

@author: LaivData jjlee with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])  # kis_auth 파일 경로 추가
import kis_auth as ka
from price_detail import price_detail

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [해외주식] 기본시세 > 해외주식 현재가상세[v1_해외주식-029]
##############################################################################################

COLUMN_MAPPING = {
    'rsym': '실시간조회종목코드',
    'pvol': '전일거래량',
    'open': '시가',
    'high': '고가',
    'low': '저가',
    'last': '현재가',
    'base': '전일종가',
    'tomv': '시가총액',
    'pamt': '전일거래대금',
    'uplp': '상한가',
    'dnlp': '하한가',
    'h52p': '52주최고가',
    'h52d': '52주최고일자',
    'l52p': '52주최저가',
    'l52d': '52주최저일자',
    'perx': 'PER',
    'pbrx': 'PBR',
    'epsx': 'EPS',
    'bpsx': 'BPS',
    'shar': '상장주수',
    'mcap': '자본금',
    'curr': '통화',
    'zdiv': '소수점자리수',
    'vnit': '매매단위',
    't_xprc': '원환산당일가격',
    't_xdif': '원환산당일대비',
    't_xrat': '원환산당일등락',
    'p_xprc': '원환산전일가격',
    'p_xdif': '원환산전일대비',
    'p_xrat': '원환산전일등락',
    't_rate': '당일환율',
    'p_rate': '전일환율',
    't_xsgn': '원환산당일기호',
    'p_xsng': '원환산전일기호',
    'e_ordyn': '거래가능여부',
    'e_hogau': '호가단위',
    'e_icod': '업종(섹터)',
    'e_parp': '액면가',
    'tvol': '거래량',
    'tamt': '거래대금',
    'etyp_nm': 'ETP 분류명'
}

NUMERIC_COLUMNS = ['소수점자리수', '전일거래량', '시가', '고가', '저가', '현재가', '전일종가', '시가총액', '전일거래대금', '상한가', '하한가', '52주최고가',
                    '52주최저가', 'PER', 'PBR', 'EPS', 'BPS', '원환산당일가격', '원환산당일대비', '원환산당일등락', '원환산전일가격', '원환산전일대비', '원환산전일등락', '당일환율', '전일환율', '액면가', '거래량', '거래대금']

def main():
    """
    [해외주식] 기본시세
    해외주식 현재가상세[v1_해외주식-029]

    해외주식 현재가상세 테스트 함수
    
    Parameters:
        - auth (str): 사용자권한정보 ()
        - excd (str): 거래소명 (HKS : 홍콩 NYS : 뉴욕 NAS : 나스닥 AMS : 아멕스 TSE : 도쿄 SHS : 상해 SZS : 심천 SHI : 상해지수 SZI : 심천지수 HSX : 호치민 HNX : 하노이 BAY : 뉴욕(주간) BAQ : 나스닥(주간) BAA : 아멕스(주간))
        - symb (str): 종목코드 ()

    Returns:
        - DataFrame: 해외주식 현재가상세 결과
    
    Example:
        >>> df = price_detail(auth="", excd="NAS", symb="TSLA")
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
        logger.info("API 호출")
        result = price_detail(
            auth="",  # 사용자권한정보
            excd="NAS",  # 거래소명
            symb="TSLA",  # 종목코드
        )
        
        if result is None or result.empty:
            logger.warning("조회된 데이터가 없습니다.")
            return
        
        # 컬럼명 출력
        logger.info("사용 가능한 컬럼 목록:")
        logger.info(result.columns.tolist())

        # 한글 컬럼명으로 변환
        result = result.rename(columns=COLUMN_MAPPING)
        
        # 숫자형 컬럼 소수점 둘째자리까지 표시
        for col in NUMERIC_COLUMNS:
            if col in result.columns:
                result[col] = pd.to_numeric(result[col], errors='coerce').round(2)
        
        # 결과 출력
        logger.info("=== 해외주식 현재가상세 결과 ===")
        logger.info("조회된 데이터 건수: %d", len(result))
        print(result)
        
    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise

if __name__ == "__main__":
    main()
