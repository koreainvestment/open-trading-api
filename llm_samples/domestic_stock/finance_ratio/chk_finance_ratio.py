import sys

import pandas as pd

sys.path.extend(['../..', '.']) # kis_auth 파일 경로 추가
import kis_auth as ka
from finance_ratio import finance_ratio

##############################################################################################
# [국내주식] 순위분석 > 국내주식 재무비율 순위[v1_국내주식-092]
##############################################################################################


COLUMN_MAPPING = {
    'data_rank': '데이터 순위',
    'hts_kor_isnm': 'HTS 한글 종목명',
    'mksc_shrn_iscd': '유가증권 단축 종목코드',
    'stck_prpr': '주식 현재가',
    'prdy_vrss': '전일 대비',
    'prdy_vrss_sign': '전일 대비 부호',
    'prdy_ctrt': '전일 대비율',
    'acml_vol': '누적 거래량',
    'cptl_op_prfi': '총자본경상이익율',
    'cptl_ntin_rate': '총자본 순이익율',
    'sale_totl_rate': '매출액 총이익율',
    'sale_ntin_rate': '매출액 순이익율',
    'bis': '자기자본비율',
    'lblt_rate': '부채 비율',
    'bram_depn': '차입금 의존도',
    'rsrv_rate': '유보 비율',
    'grs': '매출액 증가율',
    'op_prfi_inrt': '경상 이익 증가율',
    'bsop_prfi_inrt': '영업 이익 증가율',
    'ntin_inrt': '순이익 증가율',
    'equt_inrt': '자기자본 증가율',
    'cptl_tnrt': '총자본회전율',
    'sale_bond_tnrt': '매출 채권 회전율',
    'totl_aset_inrt': '총자산 증가율',
    'stac_month': '결산 월',
    'stac_month_cls_code': '결산 월 구분 코드',
    'iqry_csnu': '조회 건수'
}

NUMERIC_COLUMNS = []

def main():
    """
    [국내주식] 순위분석
    국내주식 재무비율 순위[v1_국내주식-092]

    국내주식 재무비율 순위 테스트 함수
    
    Parameters:
        - fid_trgt_cls_code (str): 대상 구분 코드 (0 : 전체)
        - fid_cond_mrkt_div_code (str): 조건 시장 분류 코드 (시장구분코드 (주식 J))
        - fid_cond_scr_div_code (str): 조건 화면 분류 코드 (Unique key( 20175 ))
        - fid_input_iscd (str): 입력 종목코드 (0000:전체, 0001:거래소, 1001:코스닥, 2001:코스피200)
        - fid_div_cls_code (str): 분류 구분 코드 (0 : 전체)
        - fid_input_price_1 (str): 입력 가격1 (입력값 없을때 전체 (가격 ~))
        - fid_input_price_2 (str): 입력 가격2 (입력값 없을때 전체 (~ 가격))
        - fid_vol_cnt (str): 거래량 수 (입력값 없을때 전체 (거래량 ~))
        - fid_input_option_1 (str): 입력 옵션1 (회계년도 입력 (ex 2023))
        - fid_input_option_2 (str): 입력 옵션2 (0: 1/4분기 , 1: 반기, 2: 3/4분기, 3: 결산)
        - fid_rank_sort_cls_code (str): 순위 정렬 구분 코드 (7: 수익성 분석, 11 : 안정성 분석, 15: 성장성 분석, 20: 활동성 분석)
        - fid_blng_cls_code (str): 소속 구분 코드 (0)
        - fid_trgt_exls_cls_code (str): 대상 제외 구분 코드 (0 : 전체)
    Returns:
        - DataFrame: 국내주식 재무비율 순위 결과
    
    Example:
        >>> df = finance_ratio(fid_trgt_cls_code="0", fid_cond_mrkt_div_code="J", fid_cond_scr_div_code="20175", fid_input_iscd="0000", fid_div_cls_code="0", fid_input_price_1="", fid_input_price_2="", fid_vol_cnt="", fid_input_option_1="2023", fid_input_option_2="3", fid_rank_sort_cls_code="7", fid_blng_cls_code="0", fid_trgt_exls_cls_code="0")
    """
    # pandas 출력 옵션 설정
    pd.set_option('display.max_columns', None)  # 모든 컬럼 표시
    pd.set_option('display.width', None)  # 출력 너비 제한 해제
    pd.set_option('display.max_rows', None)  # 모든 행 표시

    # 토큰 발급
    ka.auth()    
    
    # API 호출
    result = finance_ratio(
        fid_trgt_cls_code="0",  # 대상 구분 코드,
        fid_cond_mrkt_div_code="J",  # 조건 시장 분류 코드,
        fid_cond_scr_div_code="20175",  # 조건 화면 분류 코드,
        fid_input_iscd="0000",  # 입력 종목코드,
        fid_div_cls_code="0",  # 분류 구분 코드,
        fid_input_price_1="",  # 입력 가격1,
        fid_input_price_2="",  # 입력 가격2,
        fid_vol_cnt="",  # 거래량 수,
        fid_input_option_1="2023",  # 입력 옵션1,
        fid_input_option_2="3",  # 입력 옵션2,
        fid_rank_sort_cls_code="7",  # 순위 정렬 구분 코드,
        fid_blng_cls_code="0",  # 소속 구분 코드,
        fid_trgt_exls_cls_code="0",  # 대상 제외 구분 코드
    )
    
    # 컬럼명 출력
    print("\n=== 사용 가능한 컬럼 목록 ===")
    print(result.columns.tolist())

    # 한글 컬럼명으로 변환
    result = result.rename(columns=COLUMN_MAPPING)

    for col in NUMERIC_COLUMNS:
        if col in result.columns:
            result[col] = pd.to_numeric(result[col], errors='coerce').round(2)

    # 결과 출력
    print("\n=== 국내주식 재무비율 순위 결과 ===")
    print(result)

if __name__ == "__main__":
    main()
