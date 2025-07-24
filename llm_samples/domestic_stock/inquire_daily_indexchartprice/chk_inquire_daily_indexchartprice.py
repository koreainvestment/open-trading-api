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
from inquire_daily_indexchartprice import inquire_daily_indexchartprice

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [국내주식] 기본시세 > 국내주식기간별시세(일/주/월/년) [v1_국내주식-021]
##############################################################################################

# 통합 컬럼 매핑 (모든 output에서 공통 사용)
COLUMN_MAPPING = {
    'bstp_nmix_prdy_vrss': '업종 지수 전일 대비',
    'prdy_vrss_sign': '전일 대비 부호',
    'bstp_nmix_prdy_ctrt': '업종 지수 전일 대비율',
    'prdy_nmix': '전일 지수',
    'acml_vol': '누적 거래량',
    'acml_tr_pbmn': '누적 거래 대금',
    'hts_kor_isnm': 'HTS 한글 종목명',
    'bstp_nmix_prpr': '업종 지수 현재가',
    'bstp_cls_code': '업종 구분 코드',
    'prdy_vol': '전일 거래량',
    'bstp_nmix_oprc': '업종 지수 시가',
    'bstp_nmix_hgpr': '업종 지수 최고가',
    'bstp_nmix_lwpr': '업종 지수 최저가',
    'futs_prdy_oprc': '업종 전일 시가',
    'futs_prdy_hgpr': '업종 전일 최고가',
    'futs_prdy_lwpr': '업종 전일 최저가',
    'stck_bsop_date': '영업 일자',
    'bstp_nmix_prpr': '업종 지수 현재가',
    'bstp_nmix_oprc': '업종 지수 시가',
    'bstp_nmix_hgpr': '업종 지수 최고가',
    'bstp_nmix_lwpr': '업종 지수 최저가',
    'acml_vol': '누적 거래량',
    'acml_tr_pbmn': '누적 거래 대금',
    'mod_yn': '변경 여부'
}

NUMERIC_COLUMNS = []

def main():
    """
    [국내주식] 업종/기타
    국내주식업종기간별시세(일_주_월_년)[v1_국내주식-021]

    국내주식업종기간별시세(일_주_월_년) 테스트 함수
    
    Parameters:
        - fid_cond_mrkt_div_code (str): 조건 시장 분류 코드 (업종 : U)
        - fid_input_iscd (str): 업종 상세코드 (0001 : 종합 0002 : 대형주 ... 포탈 (FAQ : 종목정보 다운로드(국내) - 업종코드 참조))
        - fid_input_date_1 (str): 조회 시작일자 (조회 시작일자 (ex. 20220501))
        - fid_input_date_2 (str): 조회 종료일자 (조회 종료일자 (ex. 20220530))
        - fid_period_div_code (str): 기간분류코드 (D:일봉 W:주봉, M:월봉, Y:년봉)
        - env_dv (str): [추가] 실전모의구분 (real:실전, demo:모의)

    Returns:
        - Tuple[DataFrame, ...]: 국내주식업종기간별시세(일_주_월_년) 결과
    
    Example:
        >>> df1, df2 = inquire_daily_indexchartprice(fid_cond_mrkt_div_code="U", fid_input_iscd="0001", fid_input_date_1="20250101", fid_input_date_2="20250131", fid_period_div_code="D", env_dv="real")  # 실전투자
        >>> df1, df2 = inquire_daily_indexchartprice(fid_cond_mrkt_div_code="U", fid_input_iscd="0001", fid_input_date_1="20250101", fid_input_date_2="20250131", fid_period_div_code="D", env_dv="demo")  # 모의투자
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
        
        # API 호출 (모의투자 지원 로직)        
        result1, result2 = inquire_daily_indexchartprice(
            fid_cond_mrkt_div_code="U",  # 조건 시장 분류 코드
            fid_input_iscd="0001",  # 업종 상세코드
            fid_input_date_1="20250101",  # 조회 시작일자
            fid_input_date_2="20250131",  # 조회 종료일자
            fid_period_div_code="D",  # 기간분류코드
            env_dv="real",  # "real": 실전투자, "demo": 모의투자,  # [추가] 실전모의구분
        )
        
        # 결과 확인
        results = [result1, result2]
        if all(result is None or result.empty for result in results):
            logger.warning("조회된 데이터가 없습니다.")
            return
        

        # output1 결과 처리
        logger.info("=== output1 조회 (%s) ===", "실전투자" if env_dv == "real" else "모의투자")
        if not result1.empty:
            logger.info("사용 가능한 컬럼: %s", result1.columns.tolist())
            
            # 통합 컬럼명 한글 변환 (필요한 컬럼만 자동 매핑됨)
            result1 = result1.rename(columns=COLUMN_MAPPING)

            for col in NUMERIC_COLUMNS:
                if col in result1.columns:
                    result1[col] = pd.to_numeric(result1[col], errors='coerce').round(2)

            logger.info("output1 결과:")
            print(result1)
        else:
            logger.info("output1 데이터가 없습니다.")

        # output2 결과 처리
        logger.info("=== output2 조회 (%s) ===", "실전투자" if env_dv == "real" else "모의투자")
        if not result2.empty:
            logger.info("사용 가능한 컬럼: %s", result2.columns.tolist())
            
            # 통합 컬럼명 한글 변환 (필요한 컬럼만 자동 매핑됨)
            result2 = result2.rename(columns=COLUMN_MAPPING)

            for col in NUMERIC_COLUMNS:
                if col in result2.columns:
                    result2[col] = pd.to_numeric(result2[col], errors='coerce').round(2)

            logger.info("output2 결과:")
            print(result2)
        else:
            logger.info("output2 데이터가 없습니다.")

        
    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise

if __name__ == "__main__":
    main()