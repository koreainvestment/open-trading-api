# -*- coding: utf-8 -*-
"""
Created on 2025-06-18

@author: LaivData jjlee with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])  # kis_auth 파일 경로 추가
import kis_auth as ka
import lp_trade_trend

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [국내주식] ELW시세 - ELW LP매매추이[국내주식-182]
##############################################################################################

COLUMN_MAPPING = {
    'cntg_hour': '체결시간',
    'elw_prpr': 'ELW현재가',
    'prdy_vrss_sign': '전일대비부호',
    'prdy_vrss': '전일대비',
    'prdy_ctrt': '전일대비율',
    'acml_vol': '누적거래량',
    'acml_tr_pbmn': '누적거래대금',
    'lp_buy_qty': 'LP매수수량',
    'lp_sell_qty': 'LP매도수량',
    'lp_ntby_qty': 'LP순매수수량',
    'lp_buy_amt': 'LP매수금액',
    'lp_sell_amt': 'LP매도금액',
    'lp_ntby_amt': 'LP순매수금액',
    'inst_deal_qty': '기관매매수량',
    'frgn_deal_qty': '외국인매매수량',
    'prsn_deal_qty': '개인매매수량',
    'apprch_rate': '접근도'
}

NUMERIC_COLUMNS = [
    'ELW현재가', '전일대비', '전일대비율', '누적거래량', '누적거래대금',
    'LP매수수량', 'LP매도수량', 'LP순매수수량', 'LP매수금액', 'LP매도금액', 
    'LP순매수금액', '기관매매수량', '외국인매매수량', '개인매매수량', '접근도'
]

def main():
    """
    [국내주식] ELW시세
    ELW LP매매추이[국내주식-182]

    ELW LP매매추이 테스트 함수
    
    Parameters:
        - fid_cond_mrkt_div_code (str): 조건시장분류코드 (시장구분(W))
        - fid_input_iscd (str): 입력종목코드 (입력종목코드(ex 52K577(미래 K577KOSDAQ150콜))

    Returns:
        - Tuple[DataFrame, ...]: ELW LP매매추이 결과
    
    Example:
        >>> df1, df2 = lp_trade_trend(fid_cond_mrkt_div_code="W", fid_input_iscd="52K577")
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
        result1, result2 = lp_trade_trend.lp_trade_trend(
            fid_cond_mrkt_div_code="W",  # 조건시장분류코드
            fid_input_iscd="52K577",  # 입력종목코드
        )
        
        # 첫 번째 결과 처리
        if result1 is None or result1.empty:
            logger.warning("첫 번째 조회된 데이터가 없습니다.")
        else:
            # 컬럼명 출력
            logger.info("첫 번째 결과 사용 가능한 컬럼 목록:")
            logger.info(result1.columns.tolist())

            # 한글 컬럼명으로 변환
            result1 = result1.rename(columns=COLUMN_MAPPING)
            
            # 숫자 컬럼 처리
            for col in NUMERIC_COLUMNS:
                if col in result1.columns:
                    result1[col] = pd.to_numeric(result1[col], errors='coerce').round(2)
            # 결과 출력 (output1)
            logger.info("=== output1 ===")
            logger.info("조회된 데이터 건수: %d", len(result1))
            print("output1:")
            print(result1)

        # 두 번째 결과 처리
        if result2 is None or result2.empty:
            logger.warning("두 번째 조회된 데이터가 없습니다.")
        else:
            # 컬럼명 출력
            logger.info("두 번째 결과 사용 가능한 컬럼 목록:")
            logger.info(result2.columns.tolist())

            # 한글 컬럼명으로 변환
            result2 = result2.rename(columns=COLUMN_MAPPING)
            
            # 숫자 컬럼 처리
            for col in NUMERIC_COLUMNS:
                if col in result2.columns:
                    result2[col] = pd.to_numeric(result2[col], errors='coerce').round(2)
            
            # 결과 출력 (output2)
            logger.info("=== output2 ===")
            logger.info("조회된 데이터 건수: %d", len(result2))
            print("output2:")
            print(result2)
    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise

if __name__ == "__main__":
    main()
