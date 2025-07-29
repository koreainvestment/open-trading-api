# -*- coding: utf-8 -*-
"""
Created on 2025-06-13

@author: LaivData jjlee with cursor
"""

import logging
import sys

import pandas as pd

sys.path.extend(['../..', '.'])  # kis_auth 파일 경로 추가
import kis_auth as ka
from near_new_highlow import near_new_highlow

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [국내주식] 순위분석 > 국내주식 신고_신저근접종목 상위[v1_국내주식-105]
##############################################################################################

COLUMN_MAPPING = {
    'hts_kor_isnm': 'HTS 한글 종목명',
    'mksc_shrn_iscd': '유가증권 단축 종목코드',
    'stck_prpr': '주식 현재가',
    'prdy_vrss_sign': '전일 대비 부호',
    'prdy_vrss': '전일 대비',
    'prdy_ctrt': '전일 대비율',
    'askp': '매도호가',
    'askp_rsqn1': '매도호가 잔량1',
    'bidp': '매수호가',
    'bidp_rsqn1': '매수호가 잔량1',
    'acml_vol': '누적 거래량',
    'new_hgpr': '신 최고가',
    'hprc_near_rate': '고가 근접 비율',
    'new_lwpr': '신 최저가',
    'lwpr_near_rate': '저가 근접 비율',
    'stck_sdpr': '주식 기준가'
}

NUMERIC_COLUMNS = []

def main():
    """
    [국내주식] 순위분석
    국내주식 신고_신저근접종목 상위[v1_국내주식-105]

    국내주식 신고_신저근접종목 상위 테스트 함수
    
    Parameters:
        - fid_aply_rang_vol (str): 적용 범위 거래량 (0: 전체, 100: 100주 이상)
        - fid_cond_mrkt_div_code (str): 조건 시장 분류 코드 (시장구분코드 (주식 J))
        - fid_cond_scr_div_code (str): 조건 화면 분류 코드 (Unique key(20187))
        - fid_div_cls_code (str): 분류 구분 코드 (0:전체, 1:관리종목, 2:투자주의, 3:투자경고)
        - fid_input_cnt_1 (str): 입력 수1 (괴리율 최소)
        - fid_input_cnt_2 (str): 입력 수2 (괴리율 최대)
        - fid_prc_cls_code (str): 가격 구분 코드 (0:신고근접, 1:신저근접)
        - fid_input_iscd (str): 입력 종목코드 (0000:전체, 0001:거래소, 1001:코스닥, 2001:코스피200, 4001: KRX100)
        - fid_trgt_cls_code (str): 대상 구분 코드 (0: 전체)
        - fid_trgt_exls_cls_code (str): 대상 제외 구분 코드 (0:전체, 1:관리종목, 2:투자주의, 3:투자경고, 4:투자위험예고, 5:투자위험, 6:보통주, 7:우선주)
        - fid_aply_rang_prc_1 (str): 적용 범위 가격1 (가격 ~)
        - fid_aply_rang_prc_2 (str): 적용 범위 가격2 (~ 가격)
    Returns:
        - DataFrame: 국내주식 신고_신저근접종목 상위 결과
    
    Example:
        >>> df = near_new_highlow(fid_aply_rang_vol="100", fid_cond_mrkt_div_code="J", fid_cond_scr_div_code="20187", fid_div_cls_code="0", fid_input_cnt_1="0", fid_input_cnt_2="10", fid_prc_cls_code="0", fid_input_iscd="0000", fid_trgt_cls_code="0", fid_trgt_exls_cls_code="0", fid_aply_rang_prc_1="10000", fid_aply_rang_prc_2="50000")
    """
    # pandas 출력 옵션 설정
    pd.set_option('display.max_columns', None)  # 모든 컬럼 표시
    pd.set_option('display.width', None)  # 출력 너비 제한 해제
    pd.set_option('display.max_rows', None)  # 모든 행 표시

    # 토큰 발급
    ka.auth()

    # 국내주식 신고_신저근접종목 상위 파라미터 설정    
    # API 호출
    result = near_new_highlow(
        fid_aply_rang_vol="100",  # 적용 범위 거래량
        fid_cond_mrkt_div_code="J",  # 조건 시장 분류 코드 
        fid_cond_scr_div_code="20187",  # 조건 화면 분류 코드 
        fid_div_cls_code="0",  # 분류 구분 코드 
        fid_input_cnt_1="0",  # 입력 수1 
        fid_input_cnt_2="10",  # 입력 수2 
        fid_prc_cls_code="0",  # 가격 구분 코드 
        fid_input_iscd="0000",  # 입력 종목코드 
        fid_trgt_cls_code="0",  # 대상 구분 코드 
        fid_trgt_exls_cls_code="0",  # 대상 제외 구분 코드 
        fid_aply_rang_prc_1="10000",  # 적용 범위 가격1 
        fid_aply_rang_prc_2="50000",  # 적용 범위 가격2
        )
    
    # 컬럼명 출력
    print("\n=== 사용 가능한 컬럼 목록 ===")
    print(result.columns.tolist())

    # 한글 컬럼명으로 변환
    result = result.rename(columns=COLUMN_MAPPING)

    for col in NUMERIC_COLUMNS:
        if col in result.columns:
            result[col] = pd.to_numeric(result[col], errors='coerce').round(2)

    # 결과 출력
    print("\n=== 국내주식 신고_신저근접종목 상위 결과 ===")
    print(result)

if __name__ == "__main__":
    main()
