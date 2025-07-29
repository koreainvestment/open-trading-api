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
from prefer_disparate_ratio import prefer_disparate_ratio

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [국내주식] 순위분석 > 국내주식 우선주_괴리율 상위[v1_국내주식-094]
##############################################################################################

# 통합 컬럼 매핑
COLUMN_MAPPING = {
    'mksc_shrn_iscd': '유가증권 단축 종목코드',
    'data_rank': '데이터 순위',
    'hts_kor_isnm': 'HTS 한글 종목명',
    'stck_prpr': '주식 현재가',
    'prdy_vrss': '전일 대비',
    'prdy_vrss_sign': '전일 대비 부호',
    'acml_vol': '누적 거래량',
    'prst_iscd': '우선주 종목코드',
    'prst_kor_isnm': '우선주 한글 종목명',
    'prst_prpr': '우선주 현재가',
    'prst_prdy_vrss': '우선주 전일대비',
    'prst_prdy_vrss_sign': '우선주 전일 대비 부호',
    'prst_acml_vol': '우선주 누적 거래량',
    'diff_prpr': '차이 현재가',
    'dprt': '괴리율',
    'prdy_ctrt': '전일 대비율',
    'prst_prdy_ctrt': '우선주 전일 대비율'
}

NUMERIC_COLUMNS = []


def main():
    """
    [국내주식] 순위분석
    국내주식 우선주_괴리율 상위[v1_국내주식-094]

    국내주식 우선주_괴리율 상위 테스트 함수
    
    Parameters:
        - fid_vol_cnt (str): 거래량 수 (입력값 없을때 전체 (거래량 ~))
        - fid_cond_mrkt_div_code (str): 조건 시장 분류 코드 (시장구분코드 (주식 J))
        - fid_cond_scr_div_code (str): 조건 화면 분류 코드 (Unique key( 20177 ))
        - fid_div_cls_code (str): 분류 구분 코드 (0: 전체)
        - fid_input_iscd (str): 입력 종목코드 (0000:전체, 0001:거래소, 1001:코스닥, 2001:코스피200)
        - fid_trgt_cls_code (str): 대상 구분 코드 (0 : 전체)
        - fid_trgt_exls_cls_code (str): 대상 제외 구분 코드 (0 : 전체)
        - fid_input_price_1 (str): 입력 가격1 (입력값 없을때 전체 (가격 ~))
        - fid_input_price_2 (str): 입력 가격2 (입력값 없을때 전체 (~ 가격))
    Returns:
        - DataFrame: 국내주식 우선주_괴리율 상위 결과
    
    Example:
        >>> df = prefer_disparate_ratio(fid_vol_cnt="1000", fid_cond_mrkt_div_code="J", fid_cond_scr_div_code="20177", fid_div_cls_code="0", fid_input_iscd="0000", fid_trgt_cls_code="0", fid_trgt_exls_cls_code="0", fid_input_price_1="10000", fid_input_price_2="50000")
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
        result = prefer_disparate_ratio(
            fid_vol_cnt="1000",  # 거래량 수
            fid_cond_mrkt_div_code="J",  # 조건 시장 분류 코드
            fid_cond_scr_div_code="20177",  # 조건 화면 분류 코드
            fid_div_cls_code="0",  # 분류 구분 코드
            fid_input_iscd="0000",  # 입력 종목코드
            fid_trgt_cls_code="0",  # 대상 구분 코드
            fid_trgt_exls_cls_code="0",  # 대상 제외 구분 코드
            fid_input_price_1="10000",  # 입력 가격1
            fid_input_price_2="50000",  # 입력 가격2
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
        logger.info("=== 국내주식 우선주_괴리율 상위 결과 ===")
        logger.info("조회된 데이터 건수: %d", len(result))
        print(result)

    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise


if __name__ == "__main__":
    main()
