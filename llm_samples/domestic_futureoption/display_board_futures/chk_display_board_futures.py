"""
Created on 20250112
@author: LaivData SJPark with cursor
"""
import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from display_board_futures import display_board_futures

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내선물옵션] 기본시세 > 국내옵션전광판_선물[국내선물-023]
##############################################################################################

COLUMN_MAPPING = {
    'futs_shrn_iscd': '선물 단축 종목코드',
    'hts_kor_isnm': 'HTS 한글 종목명',
    'futs_prpr': '선물 현재가',
    'futs_prdy_vrss': '선물 전일 대비',
    'prdy_vrss_sign': '전일 대비 부호',
    'futs_prdy_ctrt': '선물 전일 대비율',
    'hts_thpr': 'HTS 이론가',
    'acml_vol': '누적 거래량',
    'futs_askp': '선물 매도호가',
    'futs_bidp': '선물 매수호가',
    'hts_otst_stpl_qty': 'HTS 미결제 약정 수량',
    'futs_hgpr': '선물 최고가',
    'futs_lwpr': '선물 최저가',
    'hts_rmnn_dynu': 'HTS 잔존 일수',
    'total_askp_rsqn': '총 매도호가 잔량',
    'total_bidp_rsqn': '총 매수호가 잔량',
    'futs_antc_cnpr': '선물예상체결가',
    'futs_antc_cntg_vrss': '선물예상체결대비',
    'antc_cntg_vrss_sign': '예상 체결 대비 부호',
    'antc_cntg_prdy_ctrt': '예상 체결 전일 대비율'
}

NUMERIC_COLUMNS = []


def main():
    """
    국내선물옵션 선물전광판 조회 테스트 함수
    
    이 함수는 국내선물옵션 선물전광판 API를 호출하여 결과를 출력합니다.
    
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
        result = display_board_futures(
            fid_cond_mrkt_div_code="F",
            fid_cond_scr_div_code="20503",
            fid_cond_mrkt_cls_code="MKI"
        )
    except ValueError as e:
        logging.error("에러 발생: %s", str(e))
        return

    logging.info("사용 가능한 컬럼: %s", result.columns.tolist())

    # 컬럼명 한글 변환
    result = result.rename(columns=COLUMN_MAPPING)

    # 숫자형 컬럼 소수점 표시 (메타데이터에 number 자료형이 명시된 컬럼 없음)
    for col in NUMERIC_COLUMNS:
        if col in result.columns:
            result[col] = pd.to_numeric(result[col], errors='coerce').round(2)

    logging.info("결과:")
    print(result)


if __name__ == "__main__":
    main()
