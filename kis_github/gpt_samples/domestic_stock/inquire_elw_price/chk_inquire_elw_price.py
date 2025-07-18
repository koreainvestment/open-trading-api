# -*- coding: utf-8 -*-
"""
Created on 2025-06-19

@author: LaivData jjlee with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])  # kis_auth 파일 경로 추가
import kis_auth as ka
from inquire_elw_price import inquire_elw_price

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [국내주식] ELW시세 > ELW 현재가 시세 [v1_국내주식-014]
##############################################################################################

COLUMN_MAPPING = {
    'elw_shrn_iscd': 'ELW 단축 종목코드',
    'hts_kor_isnm': 'HTS 한글 종목명',
    'elw_prpr': 'ELW 현재가',
    'prdy_vrss': '전일 대비',
    'prdy_vrss_sign': '전일 대비 부호',
    'prdy_ctrt': '전일 대비율',
    'acml_vol': '누적 거래량',
    'prdy_vrss_vol_rate': '전일 대비 거래량 비율',
    'unas_shrn_iscd': '기초자산 단축 종목코드',
    'unas_isnm': '기초자산 종목명',
    'unas_prpr': '기초자산 현재가',
    'unas_prdy_vrss': '기초자산 전일 대비',
    'unas_prdy_vrss_sign': '기초자산 전일 대비 부호',
    'unas_prdy_ctrt': '기초자산 전일 대비율',
    'bidp': '매수호가',
    'askp': '매도호가',
    'acml_tr_pbmn': '누적 거래 대금',
    'vol_tnrt': '거래량 회전율',
    'elw_oprc': 'ELW 시가2',
    'elw_hgpr': 'ELW 최고가',
    'elw_lwpr': 'ELW 최저가',
    'stck_prdy_clpr': '주식 전일 종가',
    'hts_thpr': 'HTS 이론가',
    'dprt': '괴리율',
    'atm_cls_name': 'ATM구분명',
    'hts_ints_vltl': 'HTS 내재 변동성',
    'acpr': '행사가',
    'pvt_scnd_dmrs_prc': '피벗 2차 디저항 가격',
    'pvt_frst_dmrs_prc': '피벗 1차 디저항 가격',
    'pvt_pont_val': '피벗 포인트 값',
    'pvt_frst_dmsp_prc': '피벗 1차 디지지 가격',
    'pvt_scnd_dmsp_prc': '피벗 2차 디지지 가격',
    'dmsp_val': '디지지 값',
    'dmrs_val': '디저항 값',
    'elw_sdpr': 'ELW 기준가',
    'apprch_rate': '접근도',
    'tick_conv_prc': '틱환산가',
    'invt_epmd_cntt': '투자 유의 내용'
}

NUMERIC_COLUMNS = []

def main():
    """
    [국내주식] ELW시세
    ELW 현재가 시세[v1_국내주식-014]

    ELW 현재가 시세 테스트 함수
    
    Parameters:
        - fid_cond_mrkt_div_code (str): FID 조건 시장 분류 코드 (W : ELW)
        - fid_input_iscd (str): FID 입력 종목코드 (종목번호 (6자리))
        - env_dv (str): [추가] 실전모의구분 (real:실전, demo:모의)
    Returns:
        - DataFrame: ELW 현재가 시세 결과
    
    Example:
        >>> df = inquire_elw_price(fid_cond_mrkt_div_code="W", fid_input_iscd="123456", env_dv="real")  # 실전투자
        >>> df = inquire_elw_price(fid_cond_mrkt_div_code="W", fid_input_iscd="123456", env_dv="demo")  # 모의투자
    """
    try:
        # pandas 출력 옵션 설정
        pd.set_option('display.max_columns', None)  # 모든 컬럼 표시
        pd.set_option('display.width', None)  # 출력 너비 제한 해제
        pd.set_option('display.max_rows', None)  # 모든 행 표시

        # 실전/모의투자 선택 (모의투자 지원 로직)
        env_dv = "real"
        logger.info("투자 환경: %s", "실전투자" if env_dv == "real" else "모의투자")

        # 토큰 발급 (모의투자 지원 로직)
        logger.info("토큰 발급 중...")
        if env_dv == "real":
            ka.auth(svr='prod')  # 실전투자용 토큰
        elif env_dv == "demo":
            ka.auth(svr='vps')   # 모의투자용 토큰
        logger.info("토큰 발급 완료")        
        # API 호출        
        result = inquire_elw_price(
            fid_cond_mrkt_div_code="W",  # FID 조건 시장 분류 코드
            fid_input_iscd="57LA50",  # FID 입력 종목코드
            env_dv="real",  # "real": 실전투자, "demo": 모의투자,  #실전모의구분
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
        logger.info("=== ELW 현재가 시세 결과 (%s) ===", "실전투자" if env_dv == "real" else "모의투자")
        logger.info("조회된 데이터 건수: %d", len(result))
        print(result)
        
    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise

if __name__ == "__main__":
    main()