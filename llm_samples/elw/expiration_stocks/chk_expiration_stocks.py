"""
Created on 2025-06-19

@author: LaivData jjlee with cursor
"""

import sys
import logging

import pandas as pd

sys.path.extend(['../..', '.'])  # kis_auth 파일 경로 추가
import kis_auth as ka
from expiration_stocks import expiration_stocks

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [국내주식] ELW시세 - ELW 만기예정/만기종목[국내주식-184]
##############################################################################################

COLUMN_MAPPING = {
    'elw_shrn_iscd': 'ELW단축종목코드',
    'elw_kor_isnm': 'ELW한글종목명',
    'unas_isnm': '기초자산종목명',
    'unas_prpr': '기초자산현재가',
    'acpr': '행사가',
    'stck_cnvr_rate': '주식전환비율',
    'elw_prpr': 'ELW현재가',
    'stck_lstn_date': '주식상장일자',
    'stck_last_tr_date': '주식최종거래일자',
    'total_rdmp_amt': '총상환금액',
    'rdmp_amt': '상환금액',
    'lstn_stcn': '상장주수',
    'lp_hvol': 'LP보유량',
    'ccls_paym_prc': '확정지급2가격',
    'mtrt_vltn_amt': '만기평가금액',
    'evnt_prd_fin_date': '행사2기간종료일자',
    'stlm_date': '결제일자',
    'pblc_prc': '발행가격',
    'unas_shrn_iscd': '기초자산단축종목코드',
    'stnd_iscd': '표준종목코드',
    'rdmp_ask_amt': '상환청구금액'
}

NUMERIC_COLUMNS = [
    '기초자산현재가', '행사가', '주식전환비율', 'ELW현재가', '총상환금액', '상환금액', 
    '상장주수', 'LP보유량', '확정지급2가격', '만기평가금액', '발행가격', '상환청구금액'
]

def main():
    """
    [국내주식] ELW시세
    ELW 만기예정_만기종목[국내주식-184]

    ELW 만기예정_만기종목 테스트 함수
    
    Parameters:
        - fid_cond_mrkt_div_code (str): 조건시장분류코드 (W 입력)
        - fid_cond_scr_div_code (str): 조건화면분류코드 (11547 입력)
        - fid_input_date_1 (str): 입력날짜1 (입력날짜 ~ (ex) 20240402))
        - fid_input_date_2 (str): 입력날짜2 (~입력날짜 (ex) 20240408))
        - fid_div_cls_code (str): 분류구분코드 (0(콜),1(풋),2(전체))
        - fid_etc_cls_code (str): 기타구분코드 (공백 입력)
        - fid_unas_input_iscd (str): 기초자산입력종목코드 (000000(전체), 2001(KOSPI 200), 기초자산코드(종목코드 ex. 삼성전자-005930))
        - fid_input_iscd_2 (str): 발행회사코드 (00000(전체), 00003(한국투자증권), 00017(KB증권), 00005(미래에셋증권))
        - fid_blng_cls_code (str): 결제방법 (0(전체),1(일반),2(조기종료))
        - fid_input_option_1 (str): 입력옵션1 (공백 입력)
    Returns:
        - DataFrame: ELW 만기예정_만기종목 결과
    
    Example:
        >>> df = expiration_stocks(fid_cond_mrkt_div_code="W", fid_cond_scr_div_code="11547", fid_input_date_1="20240402", fid_input_date_2="20240408", fid_div_cls_code="2", fid_etc_cls_code="", fid_unas_input_iscd="000000", fid_input_iscd_2="00000", fid_blng_cls_code="0", fid_input_option_1="")
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
        result = expiration_stocks(
            fid_cond_mrkt_div_code="W",  # 조건시장분류코드
            fid_cond_scr_div_code="11547",  # 조건화면분류코드
            fid_input_date_1="20250101",  # 입력날짜1
            fid_input_date_2="20250930",  # 입력날짜2
            fid_div_cls_code="2",  # 분류구분코드
            fid_etc_cls_code="",  # 기타구분코드
            fid_unas_input_iscd="000000",  # 기초자산입력종목코드
            fid_input_iscd_2="00000",  # 발행회사코드
            fid_blng_cls_code="0",  # 결제방법
            fid_input_option_1="",  # 입력옵션1
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
        logger.info("=== ELW 만기예정_만기종목 결과 ===")
        logger.info("조회된 데이터 건수: %d", len(result))
        print(result)
        
    except Exception as e:
        logger.error("에러 발생: %s", str(e))
        raise

if __name__ == "__main__":
    main()
