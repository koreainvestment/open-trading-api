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
from bulk_trans_num import bulk_trans_num

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [국내주식] 순위분석 > 국내주식 대량체결건수 상위[국내주식-107]
##############################################################################################

COLUMN_MAPPING = {
    'mksc_shrn_iscd': '유가증권 단축 종목코드',
    'data_rank': '데이터 순위',
    'hts_kor_isnm': 'HTS 한글 종목명',
    'stck_prpr': '주식 현재가',
    'prdy_vrss_sign': '전일 대비 부호',
    'prdy_vrss': '전일 대비',
    'prdy_ctrt': '전일 대비율',
    'acml_vol': '누적 거래량',
    'shnu_cntg_csnu': '매수2 체결 건수',
    'seln_cntg_csnu': '매도 체결 건수',
    'ntby_cnqn': '순매수 체결량'
}

NUMERIC_COLUMNS = []


def main():
    """
    [국내주식] 순위분석
    국내주식 대량체결건수 상위[국내주식-107]

    국내주식 대량체결건수 상위 테스트 함수
    
    Parameters:
        - fid_aply_rang_prc_2 (str): 적용 범위 가격2 (~ 가격)
        - fid_cond_mrkt_div_code (str): 조건 시장 분류 코드 (시장구분코드 (주식 J))
        - fid_cond_scr_div_code (str): 조건 화면 분류 코드 (Unique key(11909))
        - fid_input_iscd (str): 입력 종목코드 (0000:전체, 0001:거래소, 1001:코스닥, 2001:코스피200, 4001: KRX100)
        - fid_rank_sort_cls_code (str): 순위 정렬 구분 코드 (0:매수상위, 1:매도상위)
        - fid_div_cls_code (str): 분류 구분 코드 (0:전체)
        - fid_input_price_1 (str): 입력 가격1 (건별금액 ~)
        - fid_aply_rang_prc_1 (str): 적용 범위 가격1 (가격 ~)
        - fid_input_iscd_2 (str): 입력 종목코드2 (공백:전체종목, 개별종목 조회시 종목코드 (000660))
        - fid_trgt_exls_cls_code (str): 대상 제외 구분 코드 (0:전체)
        - fid_trgt_cls_code (str): 대상 구분 코드 (0:전체)
        - fid_vol_cnt (str): 거래량 수 (거래량 ~)
    Returns:
        - DataFrame: 국내주식 대량체결건수 상위 결과
    
    Example:
        >>> df = bulk_trans_num(fid_aply_rang_prc_2="", fid_cond_mrkt_div_code="J", fid_cond_scr_div_code="11909", fid_input_iscd="0000", fid_rank_sort_cls_code="0", fid_div_cls_code="0", fid_input_price_1="", fid_aply_rang_prc_1="", fid_input_iscd_2="", fid_trgt_exls_cls_code="0", fid_trgt_cls_code="0", fid_vol_cnt="")
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
        logger.info("API 호출 시작: 국내주식 대량체결건수 상위")
        result = bulk_trans_num(
            fid_aply_rang_prc_2="",  # 적용 범위 가격2
            fid_cond_mrkt_div_code="J",  # 조건 시장 분류 코드
            fid_cond_scr_div_code="11909",  # 조건 화면 분류 코드
            fid_input_iscd="0000",  # 입력 종목코드
            fid_rank_sort_cls_code="0",  # 순위 정렬 구분 코드
            fid_div_cls_code="0",  # 분류 구분 코드
            fid_input_price_1="",  # 입력 가격1
            fid_aply_rang_prc_1="",  # 적용 범위 가격1
            fid_input_iscd_2="",  # 입력 종목코드2
            fid_trgt_exls_cls_code="0",  # 대상 제외 구분 코드
            fid_trgt_cls_code="0",  # 대상 구분 코드
            fid_vol_cnt="",  # 거래량 수
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
        logger.info("=== 국내주식 대량체결건수 상위 결과 ===")
        logger.info("조회된 데이터 건수: %d", len(result))
        print(result)

    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise


if __name__ == "__main__":
    main()
