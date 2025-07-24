"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from intstock_stocklist_by_group import intstock_stocklist_by_group

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내주식] 시세분석 > 관심종목 그룹별 종목조회 [국내주식-203]
##############################################################################################

COLUMN_MAPPING = {
    'fid_mrkt_cls_code': 'FID 시장 구분 코드',
    'data_rank': '데이터 순위',
    'exch_code': '거래소코드',
    'jong_code': '종목코드',
    'color_code': '생상 코드',
    'memo': '메모',
    'hts_kor_isnm': 'HTS 한글 종목명',
    'fxdt_ntby_qty': '기준일 순매수 수량',
    'cntg_unpr': '체결단가',
    'cntg_cls_code': '체결 구분 코드'
}

NUMERIC_COLUMNS = []


def main():
    """
    관심종목 그룹별 종목조회 테스트 함수
    
    이 함수는 관심종목 그룹별 종목조회 API를 호출하여 결과를 출력합니다.
    
    Returns:
        None
    """

    # pandas 출력 옵션 설정
    pd.set_option('display.max_columns', None)  # 모든 컬럼 표시
    pd.set_option('display.width', None)  # 출력 너비 제한 해제
    pd.set_option('display.max_rows', None)  # 모든 행 표시

    # 인증 토큰 발급
    ka.auth()

    # case1 테스트
    logging.info("=== case1 테스트 ===")
    try:
        result1, result2 = intstock_stocklist_by_group(
            type="1",
            user_id="dttest11",
            inter_grp_code="001",
            fid_etc_cls_code="4"
        )
    except ValueError as e:
        logging.error("에러 발생: %s", str(e))
        return

    # output1 블록
    logging.info("사용 가능한 컬럼 (output1): %s", result1.columns.tolist())

    # 컬럼명 한글 변환
    COLUMN_MAPPING = {
        'data_rank': '데이터 순위',
        'inter_grp_name': '관심 그룹 명'
    }

    result1 = result1.rename(columns=COLUMN_MAPPING)

    # 숫자형 컬럼 소수점 표시 (메타데이터에 number 타입 필드 없음)
    NUMERIC_COLUMNS = []

    for col in NUMERIC_COLUMNS:
        if col in result1.columns:
            result1[col] = pd.to_numeric(result1[col], errors='coerce').round(2)

    logging.info("결과 (output1):")
    print(result1)

    # output2 블록
    logging.info("사용 가능한 컬럼 (output2): %s", result2.columns.tolist())

    # 컬럼명 한글 변환
    result2 = result2.rename(columns=COLUMN_MAPPING)

    # 숫자형 컬럼 소수점 표시 (메타데이터에 number 타입 필드 없음)
    for col in NUMERIC_COLUMNS:
        if col in result2.columns:
            result2[col] = pd.to_numeric(result2[col], errors='coerce').round(2)

    logging.info("결과 (output2):")
    print(result2)


if __name__ == "__main__":
    main()
