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
from updown_rate import updown_rate

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [국내주식] ELW시세 - ELW 상승률순위[국내주식-167]
##############################################################################################

COLUMN_MAPPING = {
    'hts_kor_isnm': 'HTS한글종목명',
    'elw_shrn_iscd': 'ELW단축종목코드',
    'elw_prpr': 'ELW현재가',
    'prdy_vrss': '전일대비',
    'prdy_vrss_sign': '전일대비부호',
    'prdy_ctrt': '전일대비율',
    'acml_vol': '누적거래량',
    'stck_sdpr': '주식기준가',
    'sdpr_vrss_prpr_sign': '기준가대비현재가부호',
    'sdpr_vrss_prpr': '기준가대비현재가',
    'sdpr_vrss_prpr_rate': '기준가대비현재가비율',
    'stck_oprc': '주식시가2',
    'oprc_vrss_prpr_sign': '시가2대비현재가부호',
    'oprc_vrss_prpr': '시가2대비현재가',
    'oprc_vrss_prpr_rate': '시가2대비현재가비율',
    'stck_hgpr': '주식최고가',
    'stck_lwpr': '주식최저가',
    'prd_rsfl_sign': '기간등락부호',
    'prd_rsfl': '기간등락',
    'prd_rsfl_rate': '기간등락비율',
    'stck_cnvr_rate': '주식전환비율',
    'hts_rmnn_dynu': 'HTS잔존일수',
    'acpr': '행사가',
    'unas_isnm': '기초자산명',
    'unas_shrn_iscd': '기초자산코드',
    'lp_hldn_rate': 'LP보유비율',
    'prit': '패리티',
    'prls_qryr_stpr_prc': '손익분기주가가격',
    'delta_val': '델타값',
    'theta': '세타',
    'prls_qryr_rate': '손익분기비율',
    'stck_lstn_date': '주식상장일자',
    'stck_last_tr_date': '주식최종거래일자',
    'hts_ints_vltl': 'HTS내재변동성',
    'lvrg_val': '레버리지값'
}

NUMERIC_COLUMNS = [
    'ELW현재가', '전일대비', '전일대비율', '누적거래량', '주식기준가', '기준가대비현재가', '기준가대비현재가비율',
    '주식시가2', '시가2대비현재가', '시가2대비현재가비율', '주식최고가', '주식최저가', '기간등락', '기간등락비율',
    '주식전환비율', 'HTS잔존일수', '행사가', 'LP보유비율', '패리티', '손익분기주가가격', '델타값', '세타', '손익분기비율',
    'HTS내재변동성', '레버리지값'
]

def main():
    """
    [국내주식] ELW시세
    ELW 상승률순위[국내주식-167]

    ELW 상승률순위 테스트 함수
    
    Parameters:
        - fid_cond_mrkt_div_code (str): 사용자권한정보 (시장구분코드 (W))
        - fid_cond_scr_div_code (str): 거래소코드 (Unique key(20277))
        - fid_unas_input_iscd (str): 상승율/하락율 구분 ('000000(전체), 2001(코스피200) , 3003(코스닥150), 005930(삼성전자) ')
        - fid_input_iscd (str): N일자값 ('00000(전체), 00003(한국투자증권) , 00017(KB증권), 00005(미래에셋주식회사)')
        - fid_input_rmnn_dynu_1 (str): 거래량조건 ('0(전체), 1(1개월이하), 2(1개월~2개월),  3(2개월~3개월), 4(3개월~6개월), 5(6개월~9개월),6(9개월~12개월), 7(12개월이상)')
        - fid_div_cls_code (str): NEXT KEY BUFF (0(전체), 1(콜), 2(풋))
        - fid_input_price_1 (str): 사용자권한정보 ()
        - fid_input_price_2 (str): 거래소코드 ()
        - fid_input_vol_1 (str): 상승율/하락율 구분 ()
        - fid_input_vol_2 (str): N일자값 ()
        - fid_input_date_1 (str): 거래량조건 ()
        - fid_rank_sort_cls_code (str): NEXT KEY BUFF ('0(상승율), 1(하락율), 2(시가대비상승율) , 3(시가대비하락율), 4(변동율)')
        - fid_blng_cls_code (str): 사용자권한정보 (0(전체))
        - fid_input_date_2 (str): 거래소코드 ()
    Returns:
        - DataFrame: ELW 상승률순위 결과
    
    Example:
        >>> df = updown_rate(fid_cond_mrkt_div_code="W", fid_cond_scr_div_code="20277", fid_unas_input_iscd="000000", fid_input_iscd="00000", fid_input_rmnn_dynu_1="0", fid_div_cls_code="0", fid_input_price_1="", fid_input_price_2="", fid_input_vol_1="", fid_input_vol_2="", fid_input_date_1="", fid_rank_sort_cls_code="0", fid_blng_cls_code="0", fid_input_date_2="")
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
        result = updown_rate(
            fid_cond_mrkt_div_code="W",  # 사용자권한정보
            fid_cond_scr_div_code="20277",  # 거래소코드
            fid_unas_input_iscd="000000",  # 상승율/하락율 구분
            fid_input_iscd="00000",  # N일자값
            fid_input_rmnn_dynu_1="0",  # 거래량조건
            fid_div_cls_code="0",  # NEXT KEY BUFF
            fid_input_price_1="",  # 사용자권한정보
            fid_input_price_2="",  # 거래소코드
            fid_input_vol_1="",  # 상승율/하락율 구분
            fid_input_vol_2="",  # N일자값
            fid_input_date_1="1",  # 거래량조건
            fid_rank_sort_cls_code="0",  # NEXT KEY BUFF
            fid_blng_cls_code="0",  # 사용자권한정보
            fid_input_date_2="",  # 거래소코드
        )
        
        if result is None or result.empty:
            logger.warning("조회된 데이터가 없습니다.")
            return
        
        # 컬럼명 출력
        logger.info("사용 가능한 컬럼 목록:")
        logger.info(result.columns.tolist())

        # 한글 컬럼명으로 변환
        result = result.rename(columns=COLUMN_MAPPING)
        
        # 숫자 컬럼 처리
        for col in NUMERIC_COLUMNS:
            if col in result.columns:
                result[col] = pd.to_numeric(result[col], errors='coerce').round(2)
        
        # 결과 출력
        logger.info("=== ELW 상승률순위 결과 ===")
        logger.info("조회된 데이터 건수: %d", len(result))
        print(result)
        
    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise

if __name__ == "__main__":
    main()
