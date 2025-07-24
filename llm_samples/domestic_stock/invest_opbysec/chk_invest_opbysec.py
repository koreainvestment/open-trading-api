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
from invest_opbysec import invest_opbysec

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [국내주식] 종목정보 > 국내주식 증권사별 투자의견[국내주식-189]
##############################################################################################

COLUMN_MAPPING = {
    'stck_bsop_date': '주식영업일자',
    'stck_shrn_iscd': '주식단축종목코드',
    'hts_kor_isnm': 'HTS한글종목명',
    'invt_opnn': '투자의견',
    'invt_opnn_cls_code': '투자의견구분코드',
    'rgbf_invt_opnn': '직전투자의견',
    'rgbf_invt_opnn_cls_code': '직전투자의견구분코드',
    'stck_prpr': '주식현재가',
    'prdy_vrss': '전일대비',
    'prdy_vrss_sign': '전일대비부호',
    'prdy_ctrt': '전일대비율',
    'hts_goal_prc': 'HTS목표가격',
    'stck_prdy_clpr': '주식전일종가',
    'stft_esdg': '주식선물괴리도',
    'dprt': '괴리율'
}

NUMERIC_COLUMNS = []

def main():
    """
    [국내주식] 종목정보
    국내주식 증권사별 투자의견[국내주식-189]

    국내주식 증권사별 투자의견 테스트 함수
    
    Parameters:
        - fid_cond_mrkt_div_code (str): 조건시장분류코드 (J(시장 구분 코드))
        - fid_cond_scr_div_code (str): 조건화면분류코드 (16634(Primary key))
        - fid_input_iscd (str): 입력종목코드 (회원사코드 (kis developers 포탈 사이트 포럼-> FAQ -> 종목정보 다운로드(국내) 참조))
        - fid_div_cls_code (str): 분류구분코드 (전체(0) 매수(1) 중립(2) 매도(3))
        - fid_input_date_1 (str): 입력날짜1 (이후 ~)
        - fid_input_date_2 (str): 입력날짜2 (~ 이전)
    Returns:
        - DataFrame: 국내주식 증권사별 투자의견 결과
    
    Example:
        >>> df = invest_opbysec(fid_cond_mrkt_div_code="J", fid_cond_scr_div_code="16634", fid_input_iscd="005930", fid_div_cls_code="0", fid_input_date_1="20250101", fid_input_date_2="20250131")
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
        result = invest_opbysec(
            fid_cond_mrkt_div_code="J",  # 조건시장분류코드
            fid_cond_scr_div_code="16634",  # 조건화면분류코드
            fid_input_iscd="005930",  # 입력종목코드
            fid_div_cls_code="0",  # 분류구분코드
            fid_input_date_1="20250101",  # 입력날짜1
            fid_input_date_2="20250131",  # 입력날짜2
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
        logger.info("=== 국내주식 증권사별 투자의견 결과 ===")
        logger.info("조회된 데이터 건수: %d", len(result))
        print(result)
        
    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise

if __name__ == "__main__":
    main()
