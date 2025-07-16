# -*- coding: utf-8 -*-
"""
Created on 2025-06-18

@author: LaivData jjlee with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])  # kis_auth 파일 경로 추가
import kis_auth as ka
import lp_trade_trend

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 통합 컬럼 매핑 (모든 output에서 공통 사용)
COLUMN_MAPPING = {
    'elw_prpr': 'ELW현재가',
    'prdy_vrss_sign': '전일대비부호',
    'prdy_vrss': '전일대비',
    'prdy_ctrt': '전일대비율',
    'acml_vol': '누적거래량',
    'prdy_vol': '전일거래량',
    'stck_cnvr_rate': '주식전환비율',
    'prit': '패리티',
    'lvrg_val': '레버리지값',
    'gear': '기어링',
    'prls_qryr_rate': '손익분기비율',
    'cfp': '자본지지점',
    'invl_val': '내재가치값',
    'tmvl_val': '시간가치값',
    'acpr': '행사가',
    'elw_ko_barrier': '조기종료발생기준가격',
    'stck_bsop_date': '주식영업일자',
    'elw_prpr': 'ELW현재가',
    'prdy_vrss_sign': '전일대비부호',
    'prdy_vrss': '전일대비',
    'prdy_ctrt': '전일대비율',
    'lp_seln_qty': 'LP매도수량',
    'lp_seln_avrg_unpr': 'LP매도평균단가',
    'lp_shnu_qty': 'LP매수수량',
    'lp_shnu_avrg_unpr': 'LP매수평균단가',
    'lp_hvol': 'LP보유량',
    'lp_hldn_rate': 'LP보유비율',
    'prsn_deal_qty': '개인매매수량',
    'apprch_rate': '접근도'
}

def main():
    """
    [국내주식] ELW시세
    ELW LP매매추이[국내주식-182]

    ELW LP매매추이 테스트 함수
    
    Parameters:
        - fid_cond_mrkt_div_code (str): 조건시장분류코드 (시장구분(W))
        - fid_input_iscd (str): 입력종목코드 (입력종목코드(ex 52K577(미래 K577KOSDAQ150콜))

    Returns:
        - Tuple[DataFrame, ...]: ELW LP매매추이 결과
    
    Example:
        >>> df1, df2 = lp_trade_trend(fid_cond_mrkt_div_code="W", fid_input_iscd="52K577")
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

        # ELW LP매매추이 파라미터 설정
        logger.info("API 파라미터 설정 중...")
        fid_cond_mrkt_div_code = "W"  # 조건시장분류코드
        fid_input_iscd = "52K577"  # 입력종목코드

        
        # API 호출
        logger.info("API 호출 시작: ELW LP매매추이")
        result1, result2 = lp_trade_trend.lp_trade_trend(
            fid_cond_mrkt_div_code=fid_cond_mrkt_div_code,  # 조건시장분류코드
            fid_input_iscd=fid_input_iscd,  # 입력종목코드
        )
        
        # 결과 확인
        results = [result1, result2]
        if all(result is None or result.empty for result in results):
            logger.warning("조회된 데이터가 없습니다.")
            return
        

        # output1 결과 처리
        logger.info("=== output1 조회 ===")
        if not result1.empty:
            logger.info("사용 가능한 컬럼: %s", result1.columns.tolist())
            
            # 통합 컬럼명 한글 변환 (필요한 컬럼만 자동 매핑됨)
            result1 = result1.rename(columns=COLUMN_MAPPING)
            logger.info("output1 결과:")
            print(result1)
        else:
            logger.info("output1 데이터가 없습니다.")

        # output2 결과 처리
        logger.info("=== output2 조회 ===")
        if not result2.empty:
            logger.info("사용 가능한 컬럼: %s", result2.columns.tolist())
            
            # 통합 컬럼명 한글 변환 (필요한 컬럼만 자동 매핑됨)
            result2 = result2.rename(columns=COLUMN_MAPPING)
            logger.info("output2 결과:")
            print(result2)
        else:
            logger.info("output2 데이터가 없습니다.")

        
    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise

if __name__ == "__main__":
    main()
