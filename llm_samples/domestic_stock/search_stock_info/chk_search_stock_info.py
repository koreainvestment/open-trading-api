# -*- coding: utf-8 -*-
"""
Created on 2025-06-17

@author: LaivData jjlee with cursor
"""

import logging
import sys

import pandas as pd

sys.path.extend(['../..', '.'])  # kis_auth 파일 경로 추가
import kis_auth as ka
from search_stock_info import search_stock_info

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [국내주식] 종목정보 > 주식기본조회[v1_국내주식-067]
##############################################################################################

COLUMN_MAPPING = {
    'pdno': '상품번호',
    'prdt_type_cd': '상품유형코드',
    'prdt_name': '상품명',
    'prdt_name120': '상품명(120자)',
    'prdt_abrv_name': '상품약어명',
    'prdt_eng_name': '상품영문명',
    'prdt_eng_name120': '상품영문명(120자)',
    'prdt_eng_abrv_name': '상품영문약어명',
    'mket_id_cd': '시장ID코드',
    'scty_grp_id_cd': '증권그룹ID코드',
    'excg_dvsn_cd': '거래소구분코드',
    'setl_mmdd': '결산월일',
    'lstg_stqt': '상장주수',
    'lstg_cptl_amt': '상장자본금액',
    'cpta': '자본금',
    'papr': '액면가',
    'issu_pric': '발행가격',
    'kospi200_item_yn': '코스피200종목여부',
    'scts_mket_lstg_dt': '유가증권시장상장일자',
    'scts_mket_lstg_abol_dt': '유가증권시장상장폐지일자',
    'kosdaq_mket_lstg_dt': '코스닥시장상장일자',
    'kosdaq_mket_lstg_abol_dt': '코스닥시장상장폐지일자',
    'frbd_mket_lstg_dt': '프리보드시장상장일자',
    'frbd_mket_lstg_abol_dt': '프리보드시장상장폐지일자',
    'reits_kind_cd': '리츠종류코드',
    'etf_dvsn_cd': 'ETF구분코드',
    'oilf_fund_yn': '유전펀드여부',
    'idx_bztp_lcls_cd': '지수업종대분류코드',
    'idx_bztp_mcls_cd': '지수업종중분류코드',
    'idx_bztp_scls_cd': '지수업종소분류코드',
    'idx_bztp_lcls_cd_name': '지수업종대분류코드명',
    'idx_bztp_mcls_cd_name': '지수업종중분류코드명',
    'idx_bztp_scls_cd_name': '지수업종소분류코드명',
    'stck_kind_cd': '주식종류코드',
    'mfnd_opng_dt': '뮤추얼펀드개시일자',
    'mfnd_end_dt': '뮤추얼펀드종료일자',
    'dpsi_erlm_cncl_dt': '예탁등록취소일자',
    'etf_cu_qty': 'ETFCU수량',
    'std_pdno': '표준상품번호',
    'dpsi_aptm_erlm_yn': '예탁지정등록여부',
    'etf_txtn_type_cd': 'ETF과세유형코드',
    'etf_type_cd': 'ETF유형코드',
    'lstg_abol_dt': '상장폐지일자',
    'nwst_odst_dvsn_cd': '신주구주구분코드',
    'sbst_pric': '대용가격',
    'thco_sbst_pric': '당사대용가격',
    'thco_sbst_pric_chng_dt': '당사대용가격변경일자',
    'tr_stop_yn': '거래정지여부',
    'admn_item_yn': '관리종목여부',
    'thdt_clpr': '당일종가',
    'bfdy_clpr': '전일종가',
    'clpr_chng_dt': '종가변경일자',
    'std_idst_clsf_cd': '표준산업분류코드',
    'std_idst_clsf_cd_name': '표준산업분류코드명',
    'ocr_no': 'OCR번호',
    'crfd_item_yn': '크라우드펀딩종목여부',
    'elec_scty_yn': '전자증권여부',
    'issu_istt_cd': '발행기관코드',
    'etf_chas_erng_rt_dbnb': 'ETF추적수익율배수',
    'etf_etn_ivst_heed_item_yn': 'ETFETN투자유의종목여부',
    'stln_int_rt_dvsn_cd': '대주이자율구분코드',
    'frnr_psnl_lmt_rt': '외국인개인한도비율',
    'lstg_rqsr_issu_istt_cd': '상장신청인발행기관코드',
    'lstg_rqsr_item_cd': '상장신청인종목코드',
    'trst_istt_issu_istt_cd': '신탁기관발행기관코드',
    'cptt_trad_tr_psbl_yn': 'NXT 거래종목여부',
    'nxt_tr_stop_yn': 'NXT 거래정지여부'
}

NUMERIC_COLUMNS = []


def main():
    """
    [국내주식] 종목정보
    주식기본조회[v1_국내주식-067]

    주식기본조회 테스트 함수
    
    Parameters:
        - prdt_type_cd (str): 상품유형코드 (300: 주식, ETF, ETN, ELW  301 : 선물옵션  302 : 채권  306 : ELS')
        - pdno (str): 상품번호 (종목번호 (6자리) ETN의 경우, Q로 시작 (EX. Q500001))
    Returns:
        - DataFrame: 주식기본조회 결과
    
    Example:
        >>> df = search_stock_info(prdt_type_cd="300", pdno="005930")
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
        result = search_stock_info(
            prdt_type_cd="300",  # 상품유형코드
            pdno="005930",  # 상품번호
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
        logger.info("=== 주식기본조회 결과 ===")
        logger.info("조회된 데이터 건수: %d", len(result))
        print(result)
        
    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise

if __name__ == "__main__":
    main()
