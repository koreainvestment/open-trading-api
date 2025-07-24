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
from quick_change import quick_change

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [국내주식] ELW시세 - ELW 당일급변종목[국내주식-171]
##############################################################################################

COLUMN_MAPPING = {
    'elw_shrn_iscd': 'ELW단축종목코드',
    'elw_kor_isnm': 'ELW한글종목명',
    'elw_prpr': 'ELW현재가',
    'prdy_vrss_sign': '전일대비부호',
    'prdy_vrss': '전일대비',
    'prdy_ctrt': '전일대비율',
    'askp': '매도호가',
    'bidp': '매수호가',
    'total_askp_rsqn': '총매도호가잔량',
    'total_bidp_rsqn': '총매수호가잔량',
    'acml_vol': '누적거래량',
    'stnd_val': '기준값',
    'stnd_val_vrss': '기준값대비',
    'stnd_val_ctrt': '기준값대비율'
}

NUMERIC_COLUMNS = [
    'ELW현재가', '전일대비', '전일대비율', '누적거래량', '누적거래대금', 
    '기준값', '기준값대비', '기준값대비율'
]

def main():
    """
    [국내주식] ELW시세
    ELW 당일급변종목[국내주식-171]

    ELW 당일급변종목 테스트 함수
    
    Parameters:
        - fid_cond_mrkt_div_code (str): 조건시장분류코드 (시장구분코드 (W))
        - fid_cond_scr_div_code (str): 조건화면분류코드 (Unique key(20287))
        - fid_unas_input_iscd (str): 기초자산입력종목코드 ('000000(전체), 2001(코스피200) , 3003(코스닥150), 005930(삼성전자) ')
        - fid_input_iscd (str): 발행사 ('00000(전체), 00003(한국투자증권) , 00017(KB증권), 00005(미래에셋주식회사)')
        - fid_mrkt_cls_code (str): 시장구분코드 (Unique key(A))
        - fid_input_price_1 (str): 가격(이상) ()
        - fid_input_price_2 (str): 가격(이하) ()
        - fid_input_vol_1 (str): 거래량(이상) ()
        - fid_input_vol_2 (str): 거래량(이하) ()
        - fid_hour_cls_code (str): 시간구분코드 (1(분), 2(일))
        - fid_input_hour_1 (str): 입력 일 또는 분 ()
        - fid_input_hour_2 (str): 기준시간(분 선택 시) ()
        - fid_rank_sort_cls_code (str): 순위정렬구분코드 ('1(가격급등), 2(가격급락), 3(거래량급증) , 4(매수잔량급증), 5(매도잔량급증)')
        - fid_blng_cls_code (str): 결재방법 (0(전체), 1(일반), 2(조기종료))
    Returns:
        - DataFrame: ELW 당일급변종목 결과
    
    Example:
        >>> df = quick_change(fid_cond_mrkt_div_code="W", fid_cond_scr_div_code="20287", fid_unas_input_iscd="000000", fid_input_iscd="00000", fid_mrkt_cls_code="A", fid_input_price_1="", fid_input_price_2="", fid_input_vol_1="", fid_input_vol_2="", fid_hour_cls_code="1", fid_input_hour_1="", fid_input_hour_2="", fid_rank_sort_cls_code="1", fid_blng_cls_code="0")
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
        logger.info("API 호출")
        result = quick_change(
            fid_cond_mrkt_div_code="W",  # 조건시장분류코드
            fid_cond_scr_div_code="20287",  # 조건화면분류코드
            fid_unas_input_iscd="000000",  # 기초자산입력종목코드
            fid_input_iscd="00000",  # 발행사
            fid_mrkt_cls_code="A",  # 시장구분코드
            fid_input_price_1="",  # 가격(이상)
            fid_input_price_2="",  # 가격(이하)
            fid_input_vol_1="",  # 거래량(이상)
            fid_input_vol_2="",  # 거래량(이하)
            fid_hour_cls_code="1",  # 시간구분코드
            fid_input_hour_1="0",  # 입력 일 또는 분
            fid_input_hour_2="",  # 기준시간(분 선택 시)
            fid_rank_sort_cls_code="1",  # 순위정렬구분코드
            fid_blng_cls_code="0"  # 결재방법
        )
        
        if result is None or result.empty:
            logger.warning("조회된 데이터가 없습니다.")
            return
        
        # 컬럼명 출력
        logger.info("사용 가능한 컬럼 목록:")
        logger.info(result.columns.tolist())

        # 한글 컬럼명으로 변환
        result = result.rename(columns=COLUMN_MAPPING)
        
        # 숫자형 컬럼 소수점 둘째자리까지 표시
        for col in NUMERIC_COLUMNS:
            if col in result.columns:
                result[col] = pd.to_numeric(result[col], errors='coerce').round(2)

        # 결과 출력
        logger.info("=== ELW 당일급변종목 결과 ===")
        logger.info("조회된 데이터 건수: %d", len(result))
        print(result)
        
    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise

if __name__ == "__main__":
    main()
