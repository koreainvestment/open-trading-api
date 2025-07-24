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
from inquire_index_price import inquire_index_price

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [국내주식] 업종/기타 > 국내업종 현재지수 [v1_국내주식-063]
##############################################################################################

COLUMN_MAPPING = {
    'bstp_nmix_prpr': '업종 지수 현재가',
    'bstp_nmix_prdy_vrss': '업종 지수 전일 대비',
    'prdy_vrss_sign': '전일 대비 부호',
    'bstp_nmix_prdy_ctrt': '업종 지수 전일 대비율',
    'acml_vol': '누적 거래량',
    'prdy_vol': '전일 거래량',
    'acml_tr_pbmn': '누적 거래 대금',
    'prdy_tr_pbmn': '전일 거래 대금',
    'bstp_nmix_oprc': '업종 지수 시가2',
    'prdy_nmix_vrss_nmix_oprc': '전일 지수 대비 지수 시가2',
    'oprc_vrss_prpr_sign': '시가2 대비 현재가 부호',
    'bstp_nmix_oprc_prdy_ctrt': '업종 지수 시가2 전일 대비율',
    'bstp_nmix_hgpr': '업종 지수 최고가',
    'prdy_nmix_vrss_nmix_hgpr': '전일 지수 대비 지수 최고가',
    'hgpr_vrss_prpr_sign': '최고가 대비 현재가 부호',
    'bstp_nmix_hgpr_prdy_ctrt': '업종 지수 최고가 전일 대비율',
    'bstp_nmix_lwpr': '업종 지수 최저가',
    'prdy_clpr_vrss_lwpr': '전일 종가 대비 최저가',
    'lwpr_vrss_prpr_sign': '최저가 대비 현재가 부호',
    'prdy_clpr_vrss_lwpr_rate': '전일 종가 대비 최저가 비율',
    'ascn_issu_cnt': '상승 종목 수',
    'uplm_issu_cnt': '상한 종목 수',
    'stnr_issu_cnt': '보합 종목 수',
    'down_issu_cnt': '하락 종목 수',
    'lslm_issu_cnt': '하한 종목 수',
    'dryy_bstp_nmix_hgpr': '연중업종지수최고가',
    'dryy_hgpr_vrss_prpr_rate': '연중 최고가 대비 현재가 비율',
    'dryy_bstp_nmix_hgpr_date': '연중업종지수최고가일자',
    'dryy_bstp_nmix_lwpr': '연중업종지수최저가',
    'dryy_lwpr_vrss_prpr_rate': '연중 최저가 대비 현재가 비율',
    'dryy_bstp_nmix_lwpr_date': '연중업종지수최저가일자',
    'total_askp_rsqn': '총 매도호가 잔량',
    'total_bidp_rsqn': '총 매수호가 잔량',
    'seln_rsqn_rate': '매도 잔량 비율',
    'shnu_rsqn_rate': '매수2 잔량 비율',
    'ntby_rsqn': '순매수 잔량'
}

NUMERIC_COLUMNS = []

def main():
    """
    [국내주식] 업종/기타
    국내업종 현재지수[v1_국내주식-063]

    국내업종 현재지수 테스트 함수
    
    Parameters:
        - fid_cond_mrkt_div_code (str): FID 조건 시장 분류 코드 (업종(U))
        - fid_input_iscd (str): FID 입력 종목코드 (코스피(0001), 코스닥(1001), 코스피200(2001) ... 포탈 (FAQ : 종목정보 다운로드(국내) - 업종코드 참조))
    Returns:
        - DataFrame: 국내업종 현재지수 결과
    
    Example:
        >>> df = inquire_index_price(fid_cond_mrkt_div_code="U", fid_input_iscd="0001")
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
        result = inquire_index_price(
            fid_cond_mrkt_div_code="U",  # FID 조건 시장 분류 코드
            fid_input_iscd="0001",  # FID 입력 종목코드
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
        logger.info("=== 국내업종 현재지수 결과 ===")
        logger.info("조회된 데이터 건수: %d", len(result))
        print(result)
        
    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise

if __name__ == "__main__":
    main()
