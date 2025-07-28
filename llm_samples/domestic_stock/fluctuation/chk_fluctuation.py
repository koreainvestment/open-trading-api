import sys

import pandas as pd

sys.path.extend(['../..', '.']) # kis_auth 파일 경로 추가
import kis_auth as ka
from fluctuation import fluctuation

##############################################################################################
# [국내주식] 순위분석 > 등락률 순위[v1_국내주식-088]
##############################################################################################

COLUMN_MAPPING = {
    "stck_shrn_iscd": "주식 단축 종목코드",
    "data_rank": "데이터 순위",
    "hts_kor_isnm": "HTS 한글 종목명",
    "stck_prpr": "주식 현재가",
    "prdy_vrss": "전일 대비",
    "prdy_vrss_sign": "전일 대비 부호",
    "prdy_ctrt": "전일 대비율",
    "acml_vol": "누적 거래량",
    "stck_hgpr": "주식 최고가",
    "hgpr_hour": "최고가 시간",
    "acml_hgpr_date": "누적 최고가 일자",
    "stck_lwpr": "주식 최저가",
    "lwpr_hour": "최저가 시간",
    "acml_lwpr_date": "누적 최저가 일자",
    "lwpr_vrss_prpr_rate": "저가 대비 현재가 비율",
    "dsgt_date_clpr_vrss_prpr_rate": "영업 일수 대비 현재가 비율",
    "cnnt_ascn_dynu": "연속 상승 일수",
    "hgpr_vrss_prpr_rate": "고가 대비 현재가 비율",
    "cnnt_down_dynu": "연속 하락 일수",
    "oprc_vrss_prpr_sign": "시가 대비 부호",
    "oprc_vrss_prpr": "시가 대비",
    "oprc_vrss_prpr_rate": "시가 대비 현재가 비율",
    "prd_rsfl": "기간 등락",
    "prd_rsfl_rate": "기간 등락 비율"
}

NUMERIC_COLUMNS = []

def main():
    """
    [국내주식] 순위분석
    등락률 순위[v1_국내주식-088]

    국내주식 등락률 순위 조회 테스트 함수
    
    Parameters:
        - fid_cond_mrkt_div_code (str): 조건 시장 분류 코드 (J: 주식, W: ELW, Q: ETF)
        - fid_cond_scr_div_code (str): 조건 화면 분류 코드 (20170: 등락률)
        - fid_input_iscd (str): 입력 종목코드 (0000: 전체)
        - fid_rank_sort_cls_code (str): 순위 정렬 구분 코드 (0000: 등락률순)
        - fid_input_cnt_1 (str): 입력 수1 (조회할 종목 수)
        - fid_prc_cls_code (str): 가격 구분 코드 (0: 전체)
        - fid_input_price_1 (str): 입력 가격1 (하한가)
        - fid_input_price_2 (str): 입력 가격2 (상한가)
        - fid_vol_cnt (str): 거래량 수 (최소 거래량)
        - fid_trgt_cls_code (str): 대상 구분 코드 (9자리, "1" or "0", 증거금30% 40% 50% 60% 100% 신용보증금30% 40% 50% 60%)
        - fid_trgt_exls_cls_code (str): 대상 제외 구분 코드 (10자리, "1" or "0", 투자위험/경고/주의 관리종목 정리매매 불성실공시 우선주 거래정지 ETF ETN 신용주문불가 SPAC)
        - fid_div_cls_code (str): 분류 구분 코드 (0: 전체)
        - fid_rsfl_rate1 (str): 등락 비율1 (하락률 하한)
        - fid_rsfl_rate2 (str): 등락 비율2 (상승률 상한)
        - tr_cont (str): 연속 거래 여부
        - dataframe (Optional[pd.DataFrame]): 누적 데이터프레임
        
    Returns:
        - DataFrame: 국내주식 등락률 순위 조회 결과
        
    Example:
        >>> df = fluctuation(fid_cond_mrkt_div_code="J", fid_cond_scr_div_code="20170", fid_input_iscd="0000", fid_rank_sort_cls_code="0", fid_input_cnt_1="0", fid_prc_cls_code="0", fid_input_price_1="", fid_input_price_2="", fid_vol_cnt="", fid_trgt_cls_code="0", fid_trgt_exls_cls_code="0", fid_div_cls_code="0", fid_rsfl_rate1="", fid_rsfl_rate2="")
    """
    # pandas 출력 옵션 설정
    pd.set_option('display.max_columns', None)  # 모든 컬럼 표시
    pd.set_option('display.width', None)  # 출력 너비 제한 해제
    pd.set_option('display.max_rows', None)  # 모든 행 표시

    # 토큰 발급
    ka.auth()

    # API 호출
    result = fluctuation(
        fid_cond_mrkt_div_code="J",
        fid_cond_scr_div_code="20170",
        fid_input_iscd="0000",
        fid_rank_sort_cls_code="0",
        fid_input_cnt_1="0",
        fid_prc_cls_code="0",
        fid_input_price_1="",
        fid_input_price_2="",
        fid_vol_cnt="",
        fid_trgt_cls_code="0",
        fid_trgt_exls_cls_code="0",
        fid_div_cls_code="0",
        fid_rsfl_rate1="",
        fid_rsfl_rate2="",
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
    print("\n=== 국내주식 거래량순위 조회 결과 ===")
    print(result)

if __name__ == "__main__":
    main()