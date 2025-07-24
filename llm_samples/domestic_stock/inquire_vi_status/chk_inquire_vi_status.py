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

from inquire_vi_status import inquire_vi_status

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [국내주식] 기본시세 > 변동성완화장치(VI) 현황[v1_국내주식-055]
##############################################################################################

COLUMN_MAPPING = {
    'Output1': '응답상세',
    'hts_kor_isnm': 'HTS 한글 종목명',
    'mksc_shrn_iscd': '유가증권 단축 종목코드',
    'vi_cls_code': 'VI발동상태',
    'bsop_date': '영업 일자',
    'cntg_vi_hour': 'VI발동시간',
    'vi_cncl_hour': 'VI해제시간',
    'vi_kind_code': 'VI종류코드',
    'vi_prc': 'VI발동가격',
    'vi_stnd_prc': '정적VI발동기준가격',
    'vi_dprt': '정적VI발동괴리율',
    'vi_dmc_stnd_prc': '동적VI발동기준가격',
    'vi_dmc_dprt': '동적VI발동괴리율',
    'vi_count': 'VI발동횟수'
}

NUMERIC_COLUMNS = []

def main():
    """
    [국내주식] 업종/기타
    변동성완화장치(VI) 현황[v1_국내주식-055]

    변동성완화장치(VI) 현황 테스트 함수
    
    Parameters:
        - fid_div_cls_code (str): FID 분류 구분 코드 (0:전체 1:상승 2:하락)
        - fid_cond_scr_div_code (str): FID 조건 화면 분류 코드 (20139)
        - fid_mrkt_cls_code (str): FID 시장 구분 코드 (0:전체 K:거래소 Q:코스닥)
        - fid_input_iscd (str): FID 입력 종목코드 ()
        - fid_rank_sort_cls_code (str): FID 순위 정렬 구분 코드 (0:전체1:정적2:동적3:정적&동적)
        - fid_input_date_1 (str): FID 입력 날짜1 (영업일)
        - fid_trgt_cls_code (str): FID 대상 구분 코드 ()
        - fid_trgt_exls_cls_code (str): FID 대상 제외 구분 코드 ()
    Returns:
        - DataFrame: 변동성완화장치(VI) 현황 결과
    
    Example:
        >>> df = inquire_vi_status(fid_div_cls_code="0", fid_cond_scr_div_code="20139", fid_mrkt_cls_code="0", fid_input_iscd="", fid_rank_sort_cls_code="0", fid_input_date_1="20250101", fid_trgt_cls_code="", fid_trgt_exls_cls_code="")
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
        result = inquire_vi_status(
            fid_div_cls_code="0",  # FID 분류 구분 코드
            fid_cond_scr_div_code="20139",  # FID 조건 화면 분류 코드
            fid_mrkt_cls_code="0",  # FID 시장 구분 코드
            fid_input_iscd="",  # FID 입력 종목코드
            fid_rank_sort_cls_code="0",  # FID 순위 정렬 구분 코드
            fid_input_date_1="20200420",  # FID 입력 날짜1
            fid_trgt_cls_code="0",  # FID 대상 구분 코드
            fid_trgt_exls_cls_code="",  # FID 대상 제외 구분 코드
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
        logger.info("=== 변동성완화장치(VI) 현황 결과 ===")
        logger.info("조회된 데이터 건수: %d", len(result))
        print(result)
        
    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise

if __name__ == "__main__":
    main()
