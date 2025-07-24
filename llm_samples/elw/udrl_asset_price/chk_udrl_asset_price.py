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
from udrl_asset_price import udrl_asset_price

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [국내주식] ELW시세 - ELW 기초자산별 종목시세[국내주식-186]
##############################################################################################

COLUMN_MAPPING = {
    'elw_shrn_iscd': 'ELW단축종목코드',
    'hts_kor_isnm': 'HTS한글종목명',
    'elw_prpr': 'ELW현재가',
    'prdy_vrss': '전일대비',
    'prdy_vrss_sign': '전일대비부호',
    'prdy_ctrt': '전일대비율',
    'acml_vol': '누적거래량',
    'acpr': '행사가',
    'prls_qryr_stpr_prc': '손익분기주가가격',
    'hts_rmnn_dynu': 'HTS잔존일수',
    'hts_ints_vltl': 'HTS내재변동성',
    'stck_cnvr_rate': '주식전환비율',
    'lp_hvol': 'LP보유량',
    'lp_rlim': 'LP비중',
    'lvrg_val': '레버리지값',
    'gear': '기어링',
    'delta_val': '델타값',
    'gama': '감마',
    'vega': '베가',
    'theta': '세타',
    'prls_qryr_rate': '손익분기비율',
    'cfp': '자본지지점',
    'prit': '패리티',
    'invl_val': '내재가치값',
    'tmvl_val': '시간가치값',
    'hts_thpr': 'HTS이론가',
    'stck_lstn_date': '주식상장일자',
    'stck_last_tr_date': '주식최종거래일자',
    'lp_ntby_qty': 'LP순매도량'
}

NUMERIC_COLUMNS = [
    'ELW현재가', '전일대비', '전일대비율', '누적거래량', '행사가', '손익분기주가가격', 
    'HTS잔존일수', 'HTS내재변동성', '주식전환비율', 'LP보유량', 'LP비중', '레버리지값', 
    '기어링', '델타값', '감마', '베가', '세타', '손익분기비율', '자본지지점', '패리티', 
    '내재가치값', '시간가치값', 'HTS이론가', 'LP순매도량'
]

def main():
    """
    [국내주식] ELW시세
    ELW 기초자산별 종목시세[국내주식-186]

    ELW 기초자산별 종목시세 테스트 함수
    
    Parameters:
        - fid_cond_mrkt_div_code (str): 조건시장분류코드 (시장구분(W))
        - fid_cond_scr_div_code (str): 조건화면분류코드 (Uniquekey(11541))
        - fid_mrkt_cls_code (str): 시장구분코드 (전체(A),콜(C),풋(P))
        - fid_input_iscd (str): 입력종목코드 ('00000(전체), 00003(한국투자증권) , 00017(KB증권), 00005(미래에셋주식회사)')
        - fid_unas_input_iscd (str): 기초자산입력종목코드 ()
        - fid_vol_cnt (str): 거래량수 (전일거래량(정수량미만))
        - fid_trgt_exls_cls_code (str): 대상제외구분코드 (거래불가종목제외(0:미체크,1:체크))
        - fid_input_price_1 (str): 입력가격1 (가격~원이상)
        - fid_input_price_2 (str): 입력가격2 (가격~월이하)
        - fid_input_vol_1 (str): 입력거래량1 (거래량~계약이상)
        - fid_input_vol_2 (str): 입력거래량2 (거래량~계약이하)
        - fid_input_rmnn_dynu_1 (str): 입력잔존일수1 (잔존일(~일이상))
        - fid_input_rmnn_dynu_2 (str): 입력잔존일수2 (잔존일(~일이하))
        - fid_option (str): 옵션 (옵션상태(0:없음,1:ATM,2:ITM,3:OTM))
        - fid_input_option_1 (str): 입력옵션1 ()
        - fid_input_option_2 (str): 입력옵션2 ()
    Returns:
        - DataFrame: ELW 기초자산별 종목시세 결과
    
    Example:
        >>> df = udrl_asset_price(fid_cond_mrkt_div_code="W", fid_cond_scr_div_code="11541", fid_mrkt_cls_code="A", fid_input_iscd="00000", fid_unas_input_iscd="005930", fid_vol_cnt="1000", fid_trgt_exls_cls_code="0", fid_input_price_1="1000", fid_input_price_2="5000", fid_input_vol_1="100", fid_input_vol_2="1000", fid_input_rmnn_dynu_1="30", fid_input_rmnn_dynu_2="90", fid_option="0", fid_input_option_1="", fid_input_option_2="")
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
        result = udrl_asset_price(
            fid_cond_mrkt_div_code="W",  # 조건시장분류코드
            fid_cond_scr_div_code="11541",  # 조건화면분류코드
            fid_mrkt_cls_code="A",  # 시장구분코드
            fid_input_iscd="00000",  # 입력종목코드
            fid_unas_input_iscd="005930",  # 기초자산입력종목코드
            fid_vol_cnt="",  # 거래량수
            fid_trgt_exls_cls_code="0",  # 대상제외구분코드
            fid_input_price_1="",  # 입력가격1
            fid_input_price_2="",  # 입력가격2
            fid_input_vol_1="",  # 입력거래량1
            fid_input_vol_2="",  # 입력거래량2
            fid_input_rmnn_dynu_1="",  # 입력잔존일수1
            fid_input_rmnn_dynu_2="",  # 입력잔존일수2
            fid_option="0",  # 옵션
            fid_input_option_1="",  # 입력옵션1
            fid_input_option_2="",  # 입력옵션2
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
        logger.info("=== ELW 기초자산별 종목시세 결과 ===")
        logger.info("조회된 데이터 건수: %d", len(result))
        print(result)
        
    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise

if __name__ == "__main__":
    main()
