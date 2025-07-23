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
from cond_search import cond_search

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [국내주식] ELW시세 - ELW 종목검색[국내주식-166]
##############################################################################################

COLUMN_MAPPING = {
    'bond_shrn_iscd': '채권단축종목코드',
    'hts_kor_isnm': 'HTS한글종목명',
    'rght_type_name': '권리유형명',
    'elw_prpr': 'ELW현재가',
    'prdy_vrss': '전일대비',
    'prdy_vrss_sign': '전일대비부호',
    'prdy_ctrt': '전일대비율',
    'acml_vol': '누적거래량',
    'acpr': '행사가',
    'stck_cnvr_rate': '주식전환비율',
    'stck_lstn_date': '주식상장일자',
    'stck_last_tr_date': '주식최종거래일자',
    'hts_rmnn_dynu': 'HTS잔존일수',
    'unas_isnm': '기초자산종목명',
    'unas_prpr': '기초자산현재가',
    'unas_prdy_vrss': '기초자산전일대비',
    'unas_prdy_vrss_sign': '기초자산전일대비부호',
    'unas_prdy_ctrt': '기초자산전일대비율',
    'unas_acml_vol': '기초자산누적거래량',
    'moneyness': 'MONEYNESS',
    'atm_cls_name': 'ATM구분명',
    'prit': '패리티',
    'delta_val': '델타값',
    'hts_ints_vltl': 'HTS내재변동성',
    'tmvl_val': '시간가치값',
    'gear': '기어링',
    'lvrg_val': '레버리지값',
    'prls_qryr_rate': '손익분기비율',
    'cfp': '자본지지점',
    'lstn_stcn': '상장주수',
    'pblc_co_name': '발행회사명',
    'lp_mbcr_name': 'LP회원사명',
    'lp_hldn_rate': 'LP보유비율',
    'elw_rght_form': 'ELW권리형태',
    'elw_ko_barrier': '조기종료발생기준가격',
    'apprch_rate': '접근도',
    'unas_shrn_iscd': '기초자산단축종목코드',
    'mtrt_date': '만기일자',
    'prmm_val': '프리미엄값',
    'stck_lp_fin_date': '주식LP종료일자',
    'tick_conv_prc': '틱환산가',
    'prls_qryr_stpr_prc': '손익분기주가가격',
    'lp_hvol': 'LP보유량'
}

NUMERIC_COLUMNS = [
    'elw_prpr', 'prdy_ctrt', 'acml_vol', 'acpr', 'stck_cnvr_rate', 
    'hts_rmnn_dynu', 'unas_prpr', 'unas_prdy_ctrt', 'unas_acml_vol',
    'moneyness', 'prit', 'delta_val', 'hts_ints_vltl', 'tmvl_val', 
    'gear', 'lvrg_val', 'prls_qryr_rate', 'cfp', 'lstn_stcn', 'pblc_co_name', 'lp_mbcr_name', 'lp_hldn_rate', 'elw_rght_form', 'elw_ko_barrier', 'apprch_rate', 'unas_shrn_iscd', 'mtrt_date', 'prmm_val', 'stck_lp_fin_date', 'tick_conv_prc', 'prls_qryr_stpr_prc', 'lp_hvol'
]

def main():
    """
    [국내주식] ELW시세
    ELW 종목검색[국내주식-166]

    ELW 종목검색 테스트 함수
    
    Parameters:
        - fid_cond_mrkt_div_code (str): 조건시장분류코드 (ELW(W))
        - fid_cond_scr_div_code (str): 조건화면분류코드 (화면번호(11510))
        - fid_rank_sort_cls_code (str): 순위정렬구분코드 ('정렬1정렬안함(0)종목코드(1)현재가(2)대비율(3)거래량(4)행사가격(5) 전환비율(6)상장일(7)만기일(8)잔존일수(9)레버리지(10)')
        - fid_input_cnt_1 (str): 입력수1 (정렬1기준 - 상위(1)하위(2))
        - fid_rank_sort_cls_code_2 (str): 순위정렬구분코드2 (정렬2)
        - fid_input_cnt_2 (str): 입력수2 (정렬2기준 - 상위(1)하위(2))
        - fid_rank_sort_cls_code_3 (str): 순위정렬구분코드3 (정렬3)
        - fid_input_cnt_3 (str): 입력수3 (정렬3기준 - 상위(1)하위(2))
        - fid_trgt_cls_code (str): 대상구분코드 (0:발행회사종목코드,1:기초자산종목코드,2:FID시장구분코드,3:FID입력날짜1(상장일), 4:FID입력날짜2(만기일),5:LP회원사종목코드,6:행사가기초자산비교>=(1) <=(2),  7:잔존일 이상 이하, 8:현재가, 9:전일대비율, 10:거래량, 11:최종거래일, 12:레버리지)
        - fid_input_iscd (str): 입력종목코드 (발행사종목코드전체(00000))
        - fid_unas_input_iscd (str): 기초자산입력종목코드 ()
        - fid_mrkt_cls_code (str): 시장구분코드 (권리유형전체(A)콜(CO)풋(PO))
        - fid_input_date_1 (str): 입력날짜1 (상장일전체(0)금일(1)7일이하(2)8~30일(3)31~90일(4))
        - fid_input_date_2 (str): 입력날짜2 (만기일전체(0)1개월(1)1~2(2)2~3(3)3~6(4)6~9(5)9~12(6)12이상(7))
        - fid_input_iscd_2 (str): 입력종목코드2 ()
        - fid_etc_cls_code (str): 기타구분코드 (행사가전체(0)>=(1))
        - fid_input_rmnn_dynu_1 (str): 입력잔존일수1 (잔존일이상)
        - fid_input_rmnn_dynu_2 (str): 입력잔존일수2 (잔존일이하)
        - fid_prpr_cnt1 (str): 현재가수1 (현재가이상)
        - fid_prpr_cnt2 (str): 현재가수2 (현재가이하)
        - fid_rsfl_rate1 (str): 등락비율1 (전일대비율이상)
        - fid_rsfl_rate2 (str): 등락비율2 (전일대비율이하)
        - fid_vol1 (str): 거래량1 (거래량이상)
        - fid_vol2 (str): 거래량2 (거래량이하)
        - fid_aply_rang_prc_1 (str): 적용범위가격1 (최종거래일from)
        - fid_aply_rang_prc_2 (str): 적용범위가격2 (최종거래일to)
        - fid_lvrg_val1 (str): 레버리지값1 ()
        - fid_lvrg_val2 (str): 레버리지값2 ()
        - fid_vol3 (str): 거래량3 (LP종료일from)
        - fid_vol4 (str): 거래량4 (LP종료일to)
        - fid_ints_vltl1 (str): 내재변동성1 (내재변동성이상)
        - fid_ints_vltl2 (str): 내재변동성2 (내재변동성이하)
        - fid_prmm_val1 (str): 프리미엄값1 (프리미엄이상)
        - fid_prmm_val2 (str): 프리미엄값2 (프리미엄이하)
        - fid_gear1 (str): 기어링1 (기어링이상)
        - fid_gear2 (str): 기어링2 (기어링이하)
        - fid_prls_qryr_rate1 (str): 손익분기비율1 (손익분기이상)
        - fid_prls_qryr_rate2 (str): 손익분기비율2 (손익분기이하)
        - fid_delta1 (str): 델타1 (델타이상)
        - fid_delta2 (str): 델타2 (델타이하)
        - fid_acpr1 (str): 행사가1 ()
        - fid_acpr2 (str): 행사가2 ()
        - fid_stck_cnvr_rate1 (str): 주식전환비율1 (전환비율이상)
        - fid_stck_cnvr_rate2 (str): 주식전환비율2 (전환비율이하)
        - fid_div_cls_code (str): 분류구분코드 (0:전체,1:일반,2:조기종료)
        - fid_prit1 (str): 패리티1 (패리티이상)
        - fid_prit2 (str): 패리티2 (패리티이하)
        - fid_cfp1 (str): 자본지지점1 (배리어이상)
        - fid_cfp2 (str): 자본지지점2 (배리어이하)
        - fid_input_nmix_price_1 (str): 지수가격1 (LP보유비율이상)
        - fid_input_nmix_price_2 (str): 지수가격2 (LP보유비율이하)
        - fid_egea_val1 (str): E기어링값1 (접근도이상)
        - fid_egea_val2 (str): E기어링값2 (접근도이하)
        - fid_input_dvdn_ert (str): 배당수익율 (손익분기점이상)
        - fid_input_hist_vltl (str): 역사적변동성 (손익분기점이하)
        - fid_theta1 (str): 세타1 (MONEYNESS이상)
        - fid_theta2 (str): 세타2 (MONEYNESS이하)
    Returns:
        - DataFrame: ELW 종목검색 결과
    
    Example:
        >>> df = cond_search(fid_cond_mrkt_div_code="W", fid_cond_scr_div_code="11510", fid_rank_sort_cls_code="0", fid_input_cnt_1="100")
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

        # api 호출
        logger.info("API 호출 ")
        result = cond_search(
            fid_cond_mrkt_div_code="W",  # 조건시장분류코드
            fid_cond_scr_div_code="11510",  # 조건화면분류코드
            fid_rank_sort_cls_code="0",  # 순위정렬구분코드
            fid_input_cnt_1="100",  # 입력수1
            fid_rank_sort_cls_code_2="",  # 순위정렬구분코드2
            fid_input_cnt_2="",  # 입력수2
            fid_rank_sort_cls_code_3="",  # 순위정렬구분코드3
            fid_input_cnt_3="",  # 입력수3
            fid_trgt_cls_code="",  # 대상구분코드
            fid_input_iscd="",  # 입력종목코드
            fid_unas_input_iscd="",  # 기초자산입력종목코드
            fid_mrkt_cls_code="",  # 시장구분코드
            fid_input_date_1="",  # 입력날짜1
            fid_input_date_2="",  # 입력날짜2
            fid_input_iscd_2="",  # 입력종목코드2
            fid_etc_cls_code="",  # 기타구분코드
            fid_input_rmnn_dynu_1="",  # 입력잔존일수1
            fid_input_rmnn_dynu_2="",  # 입력잔존일수2
            fid_prpr_cnt1="",  # 현재가수1
            fid_prpr_cnt2="",  # 현재가수2
            fid_rsfl_rate1="",  # 등락비율1
            fid_rsfl_rate2="",  # 등락비율2
            fid_vol1="",  # 거래량1
            fid_vol2="",  # 거래량2
            fid_aply_rang_prc_1="",  # 적용범위가격1
            fid_aply_rang_prc_2="",  # 적용범위가격2
            fid_lvrg_val1="",  # 레버리지값1
            fid_lvrg_val2="",  # 레버리지값2
            fid_vol3="",  # 거래량3
            fid_vol4="",  # 거래량4
            fid_ints_vltl1="",  # 내재변동성1
            fid_ints_vltl2="",  # 내재변동성2
            fid_prmm_val1="",  # 프리미엄값1
            fid_prmm_val2="",  # 프리미엄값2
            fid_gear1="",  # 기어링1
            fid_gear2="",  # 기어링2
            fid_prls_qryr_rate1="",  # 손익분기비율1
            fid_prls_qryr_rate2="",  # 손익분기비율2
            fid_delta1="",  # 델타1
            fid_delta2="",  # 델타2
            fid_acpr1="",  # 행사가1
            fid_acpr2="",  # 행사가2
            fid_stck_cnvr_rate1="",  # 주식전환비율1
            fid_stck_cnvr_rate2="",  # 주식전환비율2
            fid_div_cls_code="",  # 분류구분코드
            fid_prit1="",  # 패리티1
            fid_prit2="",  # 패리티2
            fid_cfp1="",  # 자본지지점1
            fid_cfp2="",  # 자본지지점2
            fid_input_nmix_price_1="",  # 지수가격1
            fid_input_nmix_price_2="",  # 지수가격2
            fid_egea_val1="",  # E기어링값1
            fid_egea_val2="",  # E기어링값2
            fid_input_dvdn_ert="",  # 배당수익율
            fid_input_hist_vltl="",  # 역사적변동성
            fid_theta1="",  # 세타1
            fid_theta2="",  # 세타2
        )
        
        if result is None or result.empty:
            logger.warning("조회된 데이터가 없습니다.")
            return
        
        # 컬럼명 출력
        logger.info("사용 가능한 컬럼 목록:")
        logger.info(result.columns.tolist())

        # 숫자형 컬럼 소수점 둘째자리까지 표시
        for col in NUMERIC_COLUMNS:
            if col in result.columns:
                result[col] = pd.to_numeric(result[col], errors='coerce').round(2)
        
        # 한글 컬럼명으로 변환
        result = result.rename(columns=COLUMN_MAPPING)
        
        # 컬럼명 출력
        logger.info("사용 가능한 컬럼 목록:")
        logger.info(result.columns.tolist())
                
        # 결과 출력
        logger.info("=== ELW 종목검색 결과 ===")
        logger.info("조회된 데이터 건수: %d", len(result))
        print(result)
        
    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise

if __name__ == "__main__":
    main()