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
from volume_rank import volume_rank

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [국내주식] ELW시세 - ELW 거래량순위[국내주식-168]
##############################################################################################

COLUMN_MAPPING = {
    'elw_kor_isnm': 'ELW한글종목명',
    'elw_shrn_iscd': 'ELW단축종목코드',
    'elw_prpr': 'ELW현재가',
    'prdy_vrss': '전일대비',
    'prdy_vrss_sign': '전일대비부호',
    'prdy_ctrt': '전일대비율',
    'lstn_stcn': '상장주수',
    'acml_vol': '누적거래량',
    'n_prdy_vol': 'N전일거래량',
    'n_prdy_vol_vrss': 'N전일거래량대비',
    'vol_inrt': '거래량증가율',
    'vol_tnrt': '거래량회전율',
    'nday_vol_tnrt': 'N일거래량회전율',
    'acml_tr_pbmn': '누적거래대금',
    'n_prdy_tr_pbmn': 'N전일거래대금',
    'n_prdy_tr_pbmn_vrss': 'N전일거래대금대비',
    'total_askp_rsqn': '총매도호가잔량',
    'total_bidp_rsqn': '총매수호가잔량',
    'ntsl_rsqn': '순매도잔량',
    'ntby_rsqn': '순매수잔량',
    'seln_rsqn_rate': '매도잔량비율',
    'shnu_rsqn_rate': '매수2잔량비율',
    'stck_cnvr_rate': '주식전환비율',
    'hts_rmnn_dynu': 'HTS잔존일수',
    'invl_val': '내재가치값',
    'tmvl_val': '시간가치값',
    'acpr': '행사가',
    'unas_isnm': '기초자산명',
    'stck_last_tr_date': '최종거래일',
    'unas_shrn_iscd': '기초자산코드',
    'prdy_vol': '전일거래량',
    'lp_hldn_rate': 'LP보유비율',
    'prit': '패리티',
    'prls_qryr_stpr_prc': '손익분기주가가격',
    'delta_val': '델타값',
    'theta': '세타',
    'prls_qryr_rate': '손익분기비율',
    'stck_lstn_date': '주식상장일자',
    'hts_ints_vltl': 'HTS내재변동성',
    'lvrg_val': '레버리지값',
    'lp_ntby_qty': 'LP순매도량'
}

NUMERIC_COLUMNS = [
    'ELW현재가', '전일대비', '전일대비율', '상장주수', '누적거래량', 'N전일거래량', 'N전일거래량대비',
    '거래량증가율', '거래량회전율', 'N일거래량회전율', '누적거래대금', 'N전일거래대금', 'N전일거래대금대비',
    '총매도호가잔량', '총매수호가잔량', '순매도잔량', '순매수잔량', '매도잔량비율', '매수2잔량비율',
    '주식전환비율', 'HTS잔존일수', '내재가치값', '시간가치값', '행사가', '전일거래량', 'LP보유비율',
    '패리티', '손익분기주가가격', '델타값', '세타', '손익분기비율', 'HTS내재변동성', '레버리지값', 'LP순매도량'
]

def main():
    """
    [국내주식] ELW시세
    ELW 거래량순위[국내주식-168]

    ELW 거래량순위 테스트 함수
    
    Parameters:
        - fid_cond_mrkt_div_code (str): 조건시장분류코드 (W)
        - fid_cond_scr_div_code (str): 조건화면분류코드 (20278)
        - fid_unas_input_iscd (str): 기초자산입력종목코드 (000000)
        - fid_input_iscd (str): 발행사 (00000(전체), 00003(한국투자증권) , 00017(KB증권), 00005(미래에셋주식회사)')
        - fid_input_rmnn_dynu_1 (str): 입력잔존일수 ()
        - fid_div_cls_code (str): 콜풋구분코드 (0(전체), 1(콜), 2(풋))
        - fid_input_price_1 (str): 가격(이상) (거래가격1(이상))
        - fid_input_price_2 (str): 가격(이하) (거래가격1(이하))
        - fid_input_vol_1 (str): 거래량(이상) (거래량1(이상))
        - fid_input_vol_2 (str): 거래량(이하) (거래량1(이하))
        - fid_input_date_1 (str): 조회기준일 (입력날짜(기준가 조회기준))
        - fid_rank_sort_cls_code (str): 순위정렬구분코드 (0: 거래량순 1: 평균거래증가율 2: 평균거래회전율 3:거래금액순 4: 순매수잔량순 5: 순매도잔량순)
        - fid_blng_cls_code (str): 소속구분코드 (0: 전체)
        - fid_input_iscd_2 (str): LP발행사 (0000)
        - fid_input_date_2 (str): 만기일-최종거래일조회 (공백)
    Returns:
        - DataFrame: ELW 거래량순위 결과
    
    Example:
        >>> df = volume_rank(fid_cond_mrkt_div_code="W", fid_cond_scr_div_code="20278", fid_unas_input_iscd="000000", fid_input_iscd="00000", fid_input_rmnn_dynu_1="", fid_div_cls_code="0", fid_input_price_1="0", fid_input_price_2="100000", fid_input_vol_1="0", fid_input_vol_2="1000000", fid_input_date_1="20250101", fid_rank_sort_cls_code="0", fid_blng_cls_code="0", fid_input_iscd_2="0000", fid_input_date_2="")
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
        result = volume_rank(
            fid_cond_mrkt_div_code="W",  # 조건시장분류코드
            fid_cond_scr_div_code="20278",  # 조건화면분류코드
            fid_unas_input_iscd="000000",  # 기초자산입력종목코드
            fid_input_iscd="00000",  # 발행사
            fid_input_rmnn_dynu_1="0",  # 입력잔존일수
            fid_div_cls_code="0",  # 콜풋구분코드
            fid_input_price_1="",  # 가격(이상)
            fid_input_price_2="",  # 가격(이하)
            fid_input_vol_1="",  # 거래량(이상)
            fid_input_vol_2="",  # 거래량(이하)
            fid_input_date_1="",  # 조회기준일
            fid_rank_sort_cls_code="0",  # 순위정렬구분코드
            fid_blng_cls_code="0",  # 소속구분코드
            fid_input_iscd_2="0000",  # LP발행사
            fid_input_date_2="",  # 만기일-최종거래일조회
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
        logger.info("=== ELW 거래량순위 결과 ===")
        logger.info("조회된 데이터 건수: %d", len(result))
        print(result)
        
    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise

if __name__ == "__main__":
    main()
