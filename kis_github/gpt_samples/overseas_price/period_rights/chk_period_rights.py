"""
Created on 20250601 
@author: LaivData SJPark with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from period_rights import period_rights

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [해외주식] 시세분석 > 해외주식 기간별권리조회 [해외주식-052]
##############################################################################################

def main():
    """
    해외주식 기간별권리조회 테스트 함수
    
    이 함수는 해외주식 기간별권리조회 API를 호출하여 결과를 출력합니다.
    
    Returns:
        None
    """

    # pandas 출력 옵션 설정
    pd.set_option('display.max_columns', None)  # 모든 컬럼 표시
    pd.set_option('display.width', None)  # 출력 너비 제한 해제
    pd.set_option('display.max_rows', None)  # 모든 행 표시
    
    # 인증 토큰 발급
    ka.auth()
    
    # case1 조회
    logging.info("=== case1 조회 ===")
    try:
        result = period_rights(
            rght_type_cd="%%",
            inqr_dvsn_cd="02",
            inqr_strt_dt="20240417",
            inqr_end_dt="20240417"
        )
    except ValueError as e:
        logging.error("에러 발생: %s" % str(e))
        return
    
    logging.info("사용 가능한 컬럼: %s", result.columns.tolist())
    
    # 컬럼명 한글 변환 및 데이터 출력
    column_mapping = {
        'bass_dt': '기준일자',
        'rght_type_cd': '권리유형코드',
        'pdno': '상품번호',
        'prdt_name': '상품명',
        'prdt_type_cd': '상품유형코드',
        'std_pdno': '표준상품번호',
        'acpl_bass_dt': '현지기준일자',
        'sbsc_strt_dt': '청약시작일자',
        'sbsc_end_dt': '청약종료일자',
        'cash_alct_rt': '현금배정비율',
        'stck_alct_rt': '주식배정비율',
        'crcy_cd': '통화코드',
        'crcy_cd2': '통화코드2',
        'crcy_cd3': '통화코드3',
        'crcy_cd4': '통화코드4',
        'alct_frcr_unpr': '배정외화단가',
        'stkp_dvdn_frcr_amt2': '주당배당외화금액2',
        'stkp_dvdn_frcr_amt3': '주당배당외화금액3',
        'stkp_dvdn_frcr_amt4': '주당배당외화금액4',
        'dfnt_yn': '확정여부'
    }
    
    result = result.rename(columns=column_mapping)
    
    # 숫자형 컬럼 소수점 둘째자리까지 표시
    numeric_columns = []
    
    for col in numeric_columns:
        if col in result.columns:
            result[col] = pd.to_numeric(result[col], errors='coerce').round(2)
    
    logging.info("결과:")
    print(result)

if __name__ == "__main__":
    main() 