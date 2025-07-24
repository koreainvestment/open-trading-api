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
from exp_trans_updown import exp_trans_updown

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [국내주식] 순위분석 > 국내주식 예상체결 상승_하락상위[v1_국내주식-103]
##############################################################################################

COLUMN_MAPPING = {
    'stck_shrn_iscd': '주식 단축 종목코드',
    'hts_kor_isnm': 'HTS 한글 종목명',
    'stck_prpr': '주식 현재가',
    'prdy_vrss': '전일 대비',
    'prdy_vrss_sign': '전일 대비 부호',
    'prdy_ctrt': '전일 대비율',
    'stck_sdpr': '주식 기준가',
    'seln_rsqn': '매도 잔량',
    'askp': '매도호가',
    'bidp': '매수호가',
    'shnu_rsqn': '매수2 잔량',
    'cntg_vol': '체결 거래량',
    'antc_tr_pbmn': '체결 거래대금',
    'total_askp_rsqn': '총 매도호가 잔량',
    'total_bidp_rsqn': '총 매수호가 잔량'
}

NUMERIC_COLUMNS = []

def main():
    """
    [국내주식] 순위분석
    국내주식 예상체결 상승_하락상위[v1_국내주식-103]

    국내주식 예상체결 상승_하락상위 테스트 함수
    
    Parameters:
        - fid_rank_sort_cls_code (str): 순위 정렬 구분 코드 (0:상승률1:상승폭2:보합3:하락율4:하락폭5:체결량6:거래대금)
        - fid_cond_mrkt_div_code (str): 조건 시장 분류 코드 (시장구분코드 (주식 J))
        - fid_cond_scr_div_code (str): 조건 화면 분류 코드 (Unique key(20182))
        - fid_input_iscd (str): 입력 종목코드 (0000:전체, 0001:거래소, 1001:코스닥, 2001:코스피200, 4001: KRX100)
        - fid_div_cls_code (str): 분류 구분 코드 (0:전체 1:보통주 2:우선주)
        - fid_aply_rang_prc_1 (str): 적용 범위 가격1 (입력값 없을때 전체 (가격 ~))
        - fid_vol_cnt (str): 거래량 수 (입력값 없을때 전체 (거래량 ~))
        - fid_pbmn (str): 거래대금 (입력값 없을때 전체 (거래대금 ~) 천원단위)
        - fid_blng_cls_code (str): 소속 구분 코드 (0: 전체)
        - fid_mkop_cls_code (str): 장운영 구분 코드 (0:장전예상1:장마감예상)
    Returns:
        - DataFrame: 국내주식 예상체결 상승_하락상위 결과
    
    Example:
        >>> df = exp_trans_updown(fid_rank_sort_cls_code="0", fid_cond_mrkt_div_code="J", fid_cond_scr_div_code="20182", fid_input_iscd="0000", fid_div_cls_code="0", fid_aply_rang_prc_1="", fid_vol_cnt="", fid_pbmn="", fid_blng_cls_code="0", fid_mkop_cls_code="0")
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
        result = exp_trans_updown(
            fid_rank_sort_cls_code="0",  # 순위 정렬 구분 코드
            fid_cond_mrkt_div_code="J",  # 조건 시장 분류 코드
            fid_cond_scr_div_code="20182",  # 조건 화면 분류 코드
            fid_input_iscd="0000",  # 입력 종목코드
            fid_div_cls_code="0",  # 분류 구분 코드
            fid_aply_rang_prc_1="",  # 적용 범위 가격1
            fid_vol_cnt="",  # 거래량 수
            fid_pbmn="",  # 거래대금
            fid_blng_cls_code="0",  # 소속 구분 코드
            fid_mkop_cls_code="0",  # 장운영 구분 코드
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
        logger.info("=== 국내주식 예상체결 상승_하락상위 결과 ===")
        logger.info("조회된 데이터 건수: %d", len(result))
        print(result)
        
    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise

if __name__ == "__main__":
    main()
