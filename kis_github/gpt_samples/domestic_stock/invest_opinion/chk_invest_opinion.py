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
from invest_opinion import invest_opinion

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [국내주식] 종목정보 > 국내주식 종목투자의견[국내주식-188]
##############################################################################################

COLUMN_MAPPING = {
    'stck_bsop_date': '주식영업일자',
    'invt_opnn': '투자의견',
    'invt_opnn_cls_code': '투자의견구분코드',
    'rgbf_invt_opnn': '직전투자의견',
    'rgbf_invt_opnn_cls_code': '직전투자의견구분코드',
    'hts_goal_prc': 'HTS목표가격',
    'stck_prdy_clpr': '주식전일종가',
    'stck_nday_esdg': '주식N일괴리도',
    'nday_dprt': 'N일괴리율',
    'stft_esdg': '주식선물괴리도',
    'dprt': '괴리율'
}

NUMERIC_COLUMNS = []


def main():
    """
    [국내주식] 종목정보
    국내주식 종목투자의견[국내주식-188]

    국내주식 종목투자의견 테스트 함수
    
    Parameters:
        - fid_cond_mrkt_div_code (str): 조건시장분류코드 (J(시장 구분 코드))
        - fid_cond_scr_div_code (str): 조건화면분류코드 (16633(Primary key))
        - fid_input_iscd (str): 입력종목코드 (종목코드(ex) 005930(삼성전자)))
        - fid_input_date_1 (str): 입력날짜1 (이후 ~(ex) 0020231113))
        - fid_input_date_2 (str): 입력날짜2 (~ 이전(ex) 0020240513))
    Returns:
        - DataFrame: 국내주식 종목투자의견 결과
    
    Example:
        >>> df = invest_opinion(fid_cond_mrkt_div_code="J", fid_cond_scr_div_code="16633", fid_input_iscd="005930", fid_input_date_1="20231113", fid_input_date_2="20240513")
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
        result = invest_opinion(
            fid_cond_mrkt_div_code="J",  # 조건시장분류코드
            fid_cond_scr_div_code="16633",  # 조건화면분류코드
            fid_input_iscd="005930",  # 입력종목코드
            fid_input_date_1="20250101",  # 입력날짜1
            fid_input_date_2="20250617",  # 입력날짜2
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
        logger.info("=== 국내주식 종목투자의견 결과 ===")
        logger.info("조회된 데이터 건수: %d", len(result))
        print(result)

    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise


if __name__ == "__main__":
    main()
