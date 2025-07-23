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
from credit_balance import credit_balance

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [국내주식] 순위분석 > 국내주식 신용잔고 상위 [국내주식-109]
##############################################################################################

# 통합 컬럼 매핑 (모든 output에서 공통 사용)
COLUMN_MAPPING = {
    'bstp_cls_code': '업종 구분 코드',
    'hts_kor_isnm': 'HTS 한글 종목명',
    'stnd_date1': '기준 일자1',
    'stnd_date2': '기준 일자2',
    'mksc_shrn_iscd': '유가증권 단축 종목코드',
    'hts_kor_isnm': 'HTS 한글 종목명',
    'stck_prpr': '주식 현재가',
    'prdy_vrss': '전일 대비',
    'prdy_vrss_sign': '전일 대비 부호',
    'prdy_ctrt': '전일 대비율',
    'acml_vol': '누적 거래량',
    'whol_loan_rmnd_stcn': '전체 융자 잔고 주수',
    'whol_loan_rmnd_amt': '전체 융자 잔고 금액',
    'whol_loan_rmnd_rate': '전체 융자 잔고 비율',
    'whol_stln_rmnd_stcn': '전체 대주 잔고 주수',
    'whol_stln_rmnd_amt': '전체 대주 잔고 금액',
    'whol_stln_rmnd_rate': '전체 대주 잔고 비율',
    'nday_vrss_loan_rmnd_inrt': 'N일 대비 융자 잔고 증가율',
    'nday_vrss_stln_rmnd_inrt': 'N일 대비 대주 잔고 증가율'
}

NUMERIC_COLUMNS = []

def main():
    """
    [국내주식] 순위분석
    국내주식 신용잔고 상위[국내주식-109]

    국내주식 신용잔고 상위 테스트 함수
    
    Parameters:
        - fid_cond_scr_div_code (str): 조건 화면 분류 코드 (Unique key(11701))
        - fid_input_iscd (str): 입력 종목코드 (0000:전체, 0001:거래소, 1001:코스닥, 2001:코스피200,)
        - fid_option (str): 증가율기간 (2~999)
        - fid_cond_mrkt_div_code (str): 조건 시장 분류 코드 (시장구분코드 (주식 J))
        - fid_rank_sort_cls_code (str): 순위 정렬 구분 코드 ('(융자)0:잔고비율 상위, 1: 잔고수량 상위, 2: 잔고금액 상위, 3: 잔고비율 증가상위, 4: 잔고비율 감소상위  (대주)5:잔고비율 상위, 6: 잔고수량 상위, 7: 잔고금액 상위, 8: 잔고비율 증가상위, 9: 잔고비율 감소상위 ')

    Returns:
        - Tuple[DataFrame, ...]: 국내주식 신용잔고 상위 결과
    
    Example:
        >>> df1, df2 = credit_balance(fid_cond_scr_div_code="11701", fid_input_iscd="0000", fid_option="2", fid_cond_mrkt_div_code="J", fid_rank_sort_cls_code="0")
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
        logger.info("API 호출 시작: 국내주식 신용잔고 상위")
        result1, result2 = credit_balance(
            fid_cond_scr_div_code="11701",  # 조건 화면 분류 코드
            fid_input_iscd="0000",  # 입력 종목코드
            fid_option="2",  # 증가율기간
            fid_cond_mrkt_div_code="J",  # 조건 시장 분류 코드
            fid_rank_sort_cls_code="0",  # 순위 정렬 구분 코드
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

            for col in NUMERIC_COLUMNS:
                if col in result1.columns:
                    result1[col] = pd.to_numeric(result1[col], errors='coerce').round(2)

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
