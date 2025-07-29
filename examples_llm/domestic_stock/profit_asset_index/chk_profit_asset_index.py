import logging
import sys

import pandas as pd

sys.path.extend(['../..', '.'])  # kis_auth 파일 경로 추가
import kis_auth as ka
from profit_asset_index import profit_asset_index

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [국내주식] 순위분석 > 국내주식 수익자산지표 순위[v1_국내주식-090]
##############################################################################################

COLUMN_MAPPING = {
    'data_rank': '데이터 순위',
    'hts_kor_isnm': 'HTS 한글 종목명',
    'prdy_vrss_sign': '전일 대비 부호',
    'mksc_shrn_iscd': '유가증권 단축 종목코드',
    'stck_prpr': '주식 현재가',
    'prdy_vrss': '전일 대비',
    'prdy_ctrt': '전일 대비율',
    'acml_vol': '누적 거래량',
    'sale_totl_prfi': '매출 총 이익',
    'bsop_prti': '영업 이익',
    'op_prfi': '경상 이익',
    'thtr_ntin': '당기순이익',
    'total_aset': '자산총계',
    'total_lblt': '부채총계',
    'total_cptl': '자본총계',
    'stac_month': '결산 월',
    'stac_month_cls_code': '결산 월 구분 코드',
    'iqry_csnu': '조회 건수'
}

NUMERIC_COLUMNS = []


def main():
    """
    [국내주식] 순위분석
    국내주식 수익자산지표 순위[v1_국내주식-090]

    국내주식 수익자산지표 순위 테스트 함수
    
    Parameters:
        - fid_cond_mrkt_div_code (str): 조건 시장 분류 코드 (시장구분코드 (주식 J))
        - fid_trgt_cls_code (str): 대상 구분 코드 (0:전체)
        - fid_cond_scr_div_code (str): 조건 화면 분류 코드 (Unique key( 20173 ))
        - fid_input_iscd (str): 입력 종목코드 (0000:전체, 0001:거래소, 1001:코스닥, 2001:코스피200)
        - fid_div_cls_code (str): 분류 구분 코드 (0:전체)
        - fid_input_price_1 (str): 입력 가격1 (입력값 없을때 전체 (가격 ~))
        - fid_input_price_2 (str): 입력 가격2 (입력값 없을때 전체 (~ 가격))
        - fid_vol_cnt (str): 거래량 수 (입력값 없을때 전체 (거래량 ~))
        - fid_input_option_1 (str): 입력 옵션1 (회계연도 (2023))
        - fid_input_option_2 (str): 입력 옵션2 (0: 1/4분기 , 1: 반기, 2: 3/4분기, 3: 결산)
        - fid_rank_sort_cls_code (str): 순위 정렬 구분 코드 (0:매출이익 1:영업이익 2:경상이익 3:당기순이익 4:자산총계 5:부채총계 6:자본총계)
        - fid_blng_cls_code (str): 소속 구분 코드 (0:전체)
        - fid_trgt_exls_cls_code (str): 대상 제외 구분 코드 (0:전체)
    Returns:
        - DataFrame: 국내주식 수익자산지표 순위 결과
    
    Example:
        >>> df = profit_asset_index(fid_cond_mrkt_div_code="J", fid_trgt_cls_code="0", fid_cond_scr_div_code="20173", fid_input_iscd="0000", fid_div_cls_code="0", fid_input_price_1="", fid_input_price_2="", fid_vol_cnt="", fid_input_option_1="2023", fid_input_option_2="0", fid_rank_sort_cls_code="0", fid_blng_cls_code="0", fid_trgt_exls_cls_code="0")
    """
    # pandas 출력 옵션 설정
    pd.set_option('display.max_columns', None)  # 모든 컬럼 표시
    pd.set_option('display.width', None)  # 출력 너비 제한 해제
    pd.set_option('display.max_rows', None)  # 모든 행 표시

    # 토큰 발급
    ka.auth()

    # API 호출
    result = profit_asset_index(
        fid_cond_mrkt_div_code="J",  # 조건 시장 분류 코드,
        fid_trgt_cls_code="0",  # 대상 구분 코드,
        fid_cond_scr_div_code="20173",  # 조건 화면 분류 코드,
        fid_input_iscd="0000",  # 입력 종목코드,
        fid_div_cls_code="0",  # 분류 구분 코드,
        fid_input_price_1="",  # 입력 가격1,
        fid_input_price_2="",  # 입력 가격2,
        fid_vol_cnt="",  # 거래량 수,
        fid_input_option_1="2023",  # 입력 옵션1,
        fid_input_option_2="0",  # 입력 옵션2,
        fid_rank_sort_cls_code="0",  # 순위 정렬 구분 코드,
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
    print("\n=== 국내주식 수익자산지표 순위 결과 ===")
    print(result)


if __name__ == "__main__":
    main()
