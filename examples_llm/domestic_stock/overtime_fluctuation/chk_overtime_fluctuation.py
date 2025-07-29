# -*- coding: utf-8 -*-
"""
Created on 2025-06-16

@author: LaivData jjlee with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])  # kis_auth 파일 경로 추가
import kis_auth as ka
from overtime_fluctuation import overtime_fluctuation

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [국내주식] 순위분석 > 국내주식 시간외등락율순위[국내주식-138]
##############################################################################################

# 통합 컬럼 매핑 (모든 output에서 공통 사용)
COLUMN_MAPPING = {
    'ovtm_untp_uplm_issu_cnt': '시간외 단일가 상한 종목 수',
    'ovtm_untp_ascn_issu_cnt': '시간외 단일가 상승 종목 수',
    'ovtm_untp_stnr_issu_cnt': '시간외 단일가 보합 종목 수',
    'ovtm_untp_lslm_issu_cnt': '시간외 단일가 하한 종목 수',
    'ovtm_untp_down_issu_cnt': '시간외 단일가 하락 종목 수',
    'ovtm_untp_acml_vol': '시간외 단일가 누적 거래량',
    'ovtm_untp_acml_tr_pbmn': '시간외 단일가 누적 거래대금',
    'ovtm_untp_exch_vol': '시간외 단일가 거래소 거래량',
    'ovtm_untp_exch_tr_pbmn': '시간외 단일가 거래소 거래대금',
    'ovtm_untp_kosdaq_vol': '시간외 단일가 KOSDAQ 거래량',
    'ovtm_untp_kosdaq_tr_pbmn': '시간외 단일가 KOSDAQ 거래대금',
    'mksc_shrn_iscd': '유가증권 단축 종목코드',
    'hts_kor_isnm': 'HTS 한글 종목명',
    'ovtm_untp_prpr': '시간외 단일가 현재가',
    'ovtm_untp_prdy_vrss': '시간외 단일가 전일 대비',
    'ovtm_untp_prdy_vrss_sign': '시간외 단일가 전일 대비 부호',
    'ovtm_untp_prdy_ctrt': '시간외 단일가 전일 대비율',
    'ovtm_untp_askp1': '시간외 단일가 매도호가1',
    'ovtm_untp_seln_rsqn': '시간외 단일가 매도 잔량',
    'ovtm_untp_bidp1': '시간외 단일가 매수호가1',
    'ovtm_untp_shnu_rsqn': '시간외 단일가 매수 잔량',
    'ovtm_untp_vol': '시간외 단일가 거래량',
    'ovtm_vrss_acml_vol_rlim': '시간외 대비 누적 거래량 비중',
    'stck_prpr': '주식 현재가',
    'acml_vol': '누적 거래량',
    'bidp': '매수호가',
    'askp': '매도호가'
}

NUMERIC_COLUMNS = []

def main():
    """
    [국내주식] 순위분석
    국내주식 시간외등락율순위[국내주식-138]

    국내주식 시간외등락율순위 테스트 함수
    
    Parameters:
        - fid_cond_mrkt_div_code (str): 조건 시장 분류 코드 (시장구분코드 (J: 주식))
        - fid_mrkt_cls_code (str): 시장 구분 코드 (공백 입력)
        - fid_cond_scr_div_code (str): 조건 화면 분류 코드 (Unique key(20234))
        - fid_input_iscd (str): 입력 종목코드 (0000(전체), 0001(코스피), 1001(코스닥))
        - fid_div_cls_code (str): 분류 구분 코드 (1(상한가), 2(상승률), 3(보합),4(하한가),5(하락률))
        - fid_input_price_1 (str): 입력 가격1 (입력값 없을때 전체 (가격 ~))
        - fid_input_price_2 (str): 입력 가격2 (입력값 없을때 전체 (~ 가격))
        - fid_vol_cnt (str): 거래량 수 (입력값 없을때 전체 (거래량 ~))
        - fid_trgt_cls_code (str): 대상 구분 코드 (공백 입력)
        - fid_trgt_exls_cls_code (str): 대상 제외 구분 코드 (공백 입력)

    Returns:
        - Tuple[DataFrame, ...]: 국내주식 시간외등락율순위 결과
    
    Example:
        >>> df1, df2 = overtime_fluctuation(fid_cond_mrkt_div_code="J", fid_mrkt_cls_code="", fid_cond_scr_div_code="20234", fid_input_iscd="0000", fid_div_cls_code="1", fid_input_price_1="", fid_input_price_2="", fid_vol_cnt="", fid_trgt_cls_code="", fid_trgt_exls_cls_code="")
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
        result1, result2 = overtime_fluctuation(
            fid_cond_mrkt_div_code="J",  # 조건 시장 분류 코드
            fid_mrkt_cls_code="",  # 시장 구분 코드
            fid_cond_scr_div_code="20234",  # 조건 화면 분류 코드
            fid_input_iscd="0000",  # 입력 종목코드
            fid_div_cls_code="2",  # 분류 구분 코드
            fid_input_price_1="",  # 입력 가격1
            fid_input_price_2="",  # 입력 가격2
            fid_vol_cnt="",  # 거래량 수
            fid_trgt_cls_code="",  # 대상 구분 코드
            fid_trgt_exls_cls_code="",  # 대상 제외 구분 코드
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
