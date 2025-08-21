"""
Created on 2025-08-21

@author: LaivData jjlee with cursor
"""

import sys
sys.path.extend(['../..', '.'])  # kis_auth 파일 경로 추가

import logging
import pandas as pd
import kis_auth as ka
from investor_trade_by_stock_daily import investor_trade_by_stock_daily

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

########################################################################################
# [국내주식] 시세분석 > 종목별 투자자매매동향(일별)[종목별 투자자매매동향(일별)]
########################################################################################

COLUMN_MAPPING = {
    'stck_prpr': '주식 현재가',
    'prdy_vrss': '전일 대비',
    'prdy_vrss_sign': '전일 대비 부호',
    'prdy_ctrt': '전일 대비율',
    'acml_vol': '누적 거래량',
    'prdy_vol': '전일 거래량',
    'rprs_mrkt_kor_name': '대표 시장 한글 명',
    'stck_bsop_date': '주식 영업 일자',
    'stck_clpr': '주식 종가',
    'prdy_vrss': '전일 대비',
    'prdy_vrss_sign': '전일 대비 부호',
    'prdy_ctrt': '전일 대비율',
    'acml_vol': '누적 거래량',
    'acml_tr_pbmn': '누적 거래 대금',
    'stck_oprc': '주식 시가2',
    'stck_hgpr': '주식 최고가',
    'stck_lwpr': '주식 최저가',
    'frgn_ntby_qty': '외국인 순매수 수량',
    'frgn_reg_ntby_qty': '외국인 등록 순매수 수량',
    'frgn_nreg_ntby_qty': '외국인 비등록 순매수 수량',
    'prsn_ntby_qty': '개인 순매수 수량',
    'orgn_ntby_qty': '기관계 순매수 수량',
    'scrt_ntby_qty': '증권 순매수 수량',
    'ivtr_ntby_qty': '투자신탁 순매수 수량',
    'pe_fund_ntby_vol': '사모 펀드 순매수 거래량',
    'bank_ntby_qty': '은행 순매수 수량',
    'insu_ntby_qty': '보험 순매수 수량',
    'mrbn_ntby_qty': '종금 순매수 수량',
    'fund_ntby_qty': '기금 순매수 수량',
    'etc_ntby_qty': '기타 순매수 수량',
    'etc_corp_ntby_vol': '기타 법인 순매수 거래량',
    'etc_orgt_ntby_vol': '기타 단체 순매수 거래량',
    'frgn_reg_ntby_pbmn': '외국인 등록 순매수 대금',
    'frgn_ntby_tr_pbmn': '외국인 순매수 거래 대금',
    'frgn_nreg_ntby_pbmn': '외국인 비등록 순매수 대금',
    'prsn_ntby_tr_pbmn': '개인 순매수 거래 대금',
    'orgn_ntby_tr_pbmn': '기관계 순매수 거래 대금',
    'scrt_ntby_tr_pbmn': '증권 순매수 거래 대금',
    'pe_fund_ntby_tr_pbmn': '사모 펀드 순매수 거래 대금',
    'ivtr_ntby_tr_pbmn': '투자신탁 순매수 거래 대금',
    'bank_ntby_tr_pbmn': '은행 순매수 거래 대금',
    'insu_ntby_tr_pbmn': '보험 순매수 거래 대금',
    'mrbn_ntby_tr_pbmn': '종금 순매수 거래 대금',
    'fund_ntby_tr_pbmn': '기금 순매수 거래 대금',
    'etc_ntby_tr_pbmn': '기타 순매수 거래 대금',
    'etc_corp_ntby_tr_pbmn': '기타 법인 순매수 거래 대금',
    'etc_orgt_ntby_tr_pbmn': '기타 단체 순매수 거래 대금',
    'frgn_seln_vol': '외국인 매도 거래량',
    'frgn_shnu_vol': '외국인 매수2 거래량',
    'frgn_seln_tr_pbmn': '외국인 매도 거래 대금',
    'frgn_shnu_tr_pbmn': '외국인 매수2 거래 대금',
    'frgn_reg_askp_qty': '외국인 등록 매도 수량',
    'frgn_reg_bidp_qty': '외국인 등록 매수 수량',
    'frgn_reg_askp_pbmn': '외국인 등록 매도 대금',
    'frgn_reg_bidp_pbmn': '외국인 등록 매수 대금',
    'frgn_nreg_askp_qty': '외국인 비등록 매도 수량',
    'frgn_nreg_bidp_qty': '외국인 비등록 매수 수량',
    'frgn_nreg_askp_pbmn': '외국인 비등록 매도 대금',
    'frgn_nreg_bidp_pbmn': '외국인 비등록 매수 대금',
    'prsn_seln_vol': '개인 매도 거래량',
    'prsn_shnu_vol': '개인 매수2 거래량',
    'prsn_seln_tr_pbmn': '개인 매도 거래 대금',
    'prsn_shnu_tr_pbmn': '개인 매수2 거래 대금',
    'orgn_seln_vol': '기관계 매도 거래량',
    'orgn_shnu_vol': '기관계 매수2 거래량',
    'orgn_seln_tr_pbmn': '기관계 매도 거래 대금',
    'orgn_shnu_tr_pbmn': '기관계 매수2 거래 대금',
    'scrt_seln_vol': '증권 매도 거래량',
    'scrt_shnu_vol': '증권 매수2 거래량',
    'scrt_seln_tr_pbmn': '증권 매도 거래 대금',
    'scrt_shnu_tr_pbmn': '증권 매수2 거래 대금',
    'ivtr_seln_vol': '투자신탁 매도 거래량',
    'ivtr_shnu_vol': '투자신탁 매수2 거래량',
    'ivtr_seln_tr_pbmn': '투자신탁 매도 거래 대금',
    'ivtr_shnu_tr_pbmn': '투자신탁 매수2 거래 대금',
    'pe_fund_seln_tr_pbmn': '사모 펀드 매도 거래 대금',
    'pe_fund_seln_vol': '사모 펀드 매도 거래량',
    'pe_fund_shnu_tr_pbmn': '사모 펀드 매수2 거래 대금',
    'pe_fund_shnu_vol': '사모 펀드 매수2 거래량',
    'bank_seln_vol': '은행 매도 거래량',
    'bank_shnu_vol': '은행 매수2 거래량',
    'bank_seln_tr_pbmn': '은행 매도 거래 대금',
    'bank_shnu_tr_pbmn': '은행 매수2 거래 대금',
    'insu_seln_vol': '보험 매도 거래량',
    'insu_shnu_vol': '보험 매수2 거래량',
    'insu_seln_tr_pbmn': '보험 매도 거래 대금',
    'insu_shnu_tr_pbmn': '보험 매수2 거래 대금',
    'mrbn_seln_vol': '종금 매도 거래량',
    'mrbn_shnu_vol': '종금 매수2 거래량',
    'mrbn_seln_tr_pbmn': '종금 매도 거래 대금',
    'mrbn_shnu_tr_pbmn': '종금 매수2 거래 대금',
    'fund_seln_vol': '기금 매도 거래량',
    'fund_shnu_vol': '기금 매수2 거래량',
    'fund_seln_tr_pbmn': '기금 매도 거래 대금',
    'fund_shnu_tr_pbmn': '기금 매수2 거래 대금',
    'etc_seln_vol': '기타 매도 거래량',
    'etc_shnu_vol': '기타 매수2 거래량',
    'etc_seln_tr_pbmn': '기타 매도 거래 대금',
    'etc_shnu_tr_pbmn': '기타 매수2 거래 대금',
    'etc_orgt_seln_vol': '기타 단체 매도 거래량',
    'etc_orgt_shnu_vol': '기타 단체 매수2 거래량',
    'etc_orgt_seln_tr_pbmn': '기타 단체 매도 거래 대금',
    'etc_orgt_shnu_tr_pbmn': '기타 단체 매수2 거래 대금',
    'etc_corp_seln_vol': '기타 법인 매도 거래량',
    'etc_corp_shnu_vol': '기타 법인 매수2 거래량',
    'etc_corp_seln_tr_pbmn': '기타 법인 매도 거래 대금',
    'etc_corp_shnu_tr_pbmn': '기타 법인 매수2 거래 대금',
    'bold_yn': 'BOLD 여부'
}

NUMERIC_COLUMNS = [
    '주식 현재가', '전일 대비', '전일 대비율', '누적 거래량', '전일 거래량', '주식 종가', '누적 거래 대금',
    '주식 시가2', '주식 최고가', '주식 최저가', '외국인 순매수 수량', '외국인 등록 순매수 수량', '외국인 비등록 순매수 수량',
    '개인 순매수 수량', '기관계 순매수 수량', '증권 순매수 수량', '투자신탁 순매수 수량', '사모 펀드 순매수 거래량',
    '은행 순매수 수량', '보험 순매수 수량', '종금 순매수 수량', '기금 순매수 수량', '기타 순매수 수량', '기타 법인 순매수 거래량',
    '기타 단체 순매수 거래량', '외국인 등록 순매수 대금', '외국인 순매수 거래 대금', '외국인 비등록 순매수 대금',
    '개인 순매수 거래 대금', '기관계 순매수 거래 대금', '증권 순매수 거래 대금', '사모 펀드 순매수 거래 대금',
    '투자신탁 순매수 거래 대금', '은행 순매수 거래 대금', '보험 순매수 거래 대금', '종금 순매수 거래 대금',
    '기금 순매수 거래 대금', '기타 순매수 거래 대금', '기타 법인 순매수 거래 대금', '기타 단체 순매수 거래 대금',
    '외국인 매도 거래량', '외국인 매수2 거래량', '외국인 매도 거래 대금', '외국인 매수2 거래 대금', '외국인 등록 매도 수량',
    '외국인 등록 매수 수량', '외국인 등록 매도 대금', '외국인 등록 매수 대금', '외국인 비등록 매도 수량',
    '외국인 비등록 매수 수량', '외국인 비등록 매도 대금', '외국인 비등록 매수 대금', '개인 매도 거래량', '개인 매수2 거래량',
    '개인 매도 거래 대금', '개인 매수2 거래 대금', '기관계 매도 거래량', '기관계 매수2 거래량', '기관계 매도 거래 대금',
    '기관계 매수2 거래 대금', '증권 매도 거래량', '증권 매수2 거래량', '증권 매도 거래 대금', '증권 매수2 거래 대금',
    '투자신탁 매도 거래량', '투자신탁 매수2 거래량', '투자신탁 매도 거래 대금', '투자신탁 매수2 거래 대금',
    '사모 펀드 매도 거래 대금', '사모 펀드 매도 거래량', '사모 펀드 매수2 거래 대금', '사모 펀드 매수2 거래량',
    '은행 매도 거래량', '은행 매수2 거래량', '은행 매도 거래 대금', '은행 매수2 거래 대금', '보험 매도 거래량',
    '보험 매수2 거래량', '보험 매도 거래 대금', '보험 매수2 거래 대금', '종금 매도 거래량', '종금 매수2 거래량',
    '종금 매도 거래 대금', '종금 매수2 거래 대금', '기금 매도 거래량', '기금 매수2 거래량', '기금 매도 거래 대금',
    '기금 매수2 거래 대금', '기타 매도 거래량', '기타 매수2 거래량', '기타 매도 거래 대금', '기타 매수2 거래 대금',
    '기타 단체 매도 거래량', '기타 단체 매수2 거래량', '기타 단체 매도 거래 대금', '기타 단체 매수2 거래 대금',
    '기타 법인 매도 거래량', '기타 법인 매수2 거래량', '기타 법인 매도 거래 대금', '기타 법인 매수2 거래 대금'
]

def main():
    """
    [국내주식] 시세분석
    종목별 투자자매매동향(일별)[종목별 투자자매매동향(일별)]

    종목별 투자자매매동향(일별) 테스트 함수
    
    Parameters:
        - fid_cond_mrkt_div_code (str): 조건 시장 분류 코드 (J:KRX, NX:NXT, UN:통합)
        - fid_input_iscd (str): 입력 종목코드 (종목번호 (6자리))
        - fid_input_date_1 (str): 입력 날짜1 (입력 날짜(20250812))
        - fid_org_adj_prc (str): 수정주가 원주가 가격 (공란 입력)
        - fid_etc_cls_code (str): 기타 구분 코드 (공란 입력)

    Returns:
        - DataFrame: 종목별 투자자매매동향(일별) 결과
    
    Example:
        >>> df1, df2 = investor_trade_by_stock_daily(fid_cond_mrkt_div_code="J", fid_input_iscd="005930", fid_input_date_1="20250812", fid_org_adj_prc="", fid_etc_cls_code="")
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

        # API 호출 및 다중 output 결과 처리
        logger.info("API 호출 시작: 종목별 투자자매매동향(일별)")
        result1, result2 = investor_trade_by_stock_daily(
            fid_cond_mrkt_div_code="J",  # 조건 시장 분류 코드
            fid_input_iscd="005930",  # 입력 종목코드
            fid_input_date_1="20250812",  # 입력 날짜1
            fid_org_adj_prc="",  # 수정주가 원주가 가격
            fid_etc_cls_code="",  # 기타 구분 코드
        )
        
        if result1 is None or result2 is None:
            logger.error("API 호출 결과가 None입니다.")
            return
        
        # output1 결과 처리
        logger.info("=== output1 결과 ===")
        logger.info("사용 가능한 컬럼: %s", result1.columns.tolist())
        
        # 안전한 컬럼명 매핑
        available_cols1 = {k: v for k, v in COLUMN_MAPPING.items() if k in result1.columns}
        result1 = result1.rename(columns=available_cols1)
        
        # 숫자형 컬럼 변환 및 처리
        for col in NUMERIC_COLUMNS:
            if col in result1.columns:
                try:
                    result1[col] = pd.to_numeric(result1[col], errors='coerce').round(2)
                except Exception as e:
                    logger.warning("컬럼 %s 변환 실패: %s", col, str(e))
        
        logger.info("결과:")
        print(result1)
        
        # output2 결과 처리
        logger.info("=== output2 결과 ===")
        logger.info("사용 가능한 컬럼: %s", result2.columns.tolist())
        
        # 안전한 컬럼명 매핑
        available_cols2 = {k: v for k, v in COLUMN_MAPPING.items() if k in result2.columns}
        result2 = result2.rename(columns=available_cols2)
        
        # 숫자형 컬럼 변환 및 처리
        for col in NUMERIC_COLUMNS:
            if col in result2.columns:
                try:
                    result2[col] = pd.to_numeric(result2[col], errors='coerce').round(2)
                except Exception as e:
                    logger.warning("컬럼 %s 변환 실패: %s", col, str(e))
        
        logger.info("결과(output2):")
        print(result2)
        
        return result1, result2
        
    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise

if __name__ == "__main__":
    main()