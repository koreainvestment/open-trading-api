# -*- coding: utf-8 -*-
"""
Created on 2025-06-17

@author: LaivData jjlee with cursor
"""

import logging
import sys

import pandas as pd

sys.path.extend(['../..', '.'])  # kis_auth 파일 경로 추가
import kis_auth as ka
from news_title import news_title

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [국내주식] 종목정보 > 종합 시황/공시(제목) [국내주식-141]
##############################################################################################

COLUMN_MAPPING = {
    'output1': '응답상세',
    'cntt_usiq_srno': '내용 조회용 일련번호',
    'news_ofer_entp_code': '뉴스 제공 업체 코드',
    'data_dt': '작성일자',
    'data_tm': '작성시간',
    'hts_pbnt_titl_cntt': 'HTS 공시 제목 내용',
    'news_lrdv_code': '뉴스 대구분',
    'dorg': '자료원',
    'iscd1': '종목 코드1',
    'iscd2': '종목 코드2',
    'iscd3': '종목 코드3',
    'iscd4': '종목 코드4',
    'iscd5': '종목 코드5'
}

NUMERIC_COLUMNS = []


def main():
    """
    [국내주식] 업종/기타
    종합 시황_공시(제목)[국내주식-141]

    종합 시황_공시(제목) 테스트 함수
    
    Parameters:
        - fid_news_ofer_entp_code (str): 뉴스 제공 업체 코드 (공백)
        - fid_cond_mrkt_cls_code (str): 조건 시장 구분 코드 (공백)
        - fid_input_iscd (str): 입력 종목코드 (공백: 전체, 종목코드 : 해당코드가 등록된 뉴스)
        - fid_titl_cntt (str): 제목 내용 (공백)
        - fid_input_date_1 (str): 입력 날짜 (공백: 현재기준, 조회일자(ex 00YYYYMMDD))
        - fid_input_hour_1 (str): 입력 시간 (공백: 현재기준, 조회시간(ex 0000HHMMSS))
        - fid_rank_sort_cls_code (str): 순위 정렬 구분 코드 (공백)
        - fid_input_srno (str): 입력 일련번호 (공백)
    Returns:
        - DataFrame: 종합 시황_공시(제목) 결과
    
    Example:
        >>> df = news_title(fid_news_ofer_entp_code="", fid_cond_mrkt_cls_code="", fid_input_iscd="", fid_titl_cntt="", fid_input_date_1="", fid_input_hour_1="", fid_rank_sort_cls_code="", fid_input_srno="")
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
        result = news_title(
            fid_news_ofer_entp_code="",  # 뉴스 제공 업체 코드
            fid_cond_mrkt_cls_code="",  # 조건 시장 구분 코드
            fid_input_iscd="",  # 입력 종목코드
            fid_titl_cntt="",  # 제목 내용
            fid_input_date_1="",  # 입력 날짜
            fid_input_hour_1="",  # 입력 시간
            fid_rank_sort_cls_code="",  # 순위 정렬 구분 코드
            fid_input_srno="",  # 입력 일련번호
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
        logger.info("=== 종합 시황_공시(제목) 결과 ===")
        logger.info("조회된 데이터 건수: %d", len(result))
        print(result)
        
    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise

if __name__ == "__main__":
    main()
