import sys

import pandas as pd
import logging

sys.path.extend(['../..', '.'])  # kis_auth 파일 경로 추가
import kis_auth as ka
from volume_rank import volume_rank

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [국내주식] 순위분석 > 거래량순위[v1_국내주식-047]
##############################################################################################

# 통합 컬럼 매핑
COLUMN_MAPPING = {
    'hts_kor_isnm': 'HTS 한글 종목명',
    'mksc_shrn_iscd': '가중권 단축 종목코드',
    'data_rank': '데이터 순위',
    'stck_prpr': '주식 현재가',
    'prdy_vrss_sign': '전일 대비 부호',
    'prdy_vrss': '전일 대비',
    'prdy_ctrt': '전일 대비율',
    'acml_vol': '누적 거래량',
    'prdy_vol': '전일 거래량',
    'lstn_stcn': '상장 주식수',
    'avrg_vol': '평균 거래량',
    'n_befr_clpr_vrss_prpr_rate': '전일종가대비현재가(%)',
    'vol_inrt': '거래량증가율',
    'vol_tnrt': '거래량회전율',
    'nday_vol_tnrt': 'N일 거래량회전율',
    'avrg_tr_pbmn': '평균 거래 대금',
    'tr_pbmn_tnrt': '거래대금회전율',
    'nday_tr_pbmn_tnrt': 'N일 거래대금회전율',
    'acml_tr_pbmn': '누적 거래 대금'
}

NUMERIC_COLUMNS = []


def main():
    """
    [국내주식] 순위분석
    순위분석[v1_국내주식-047]

    국내주식 순위분석 조회 테스트 함수
    
    Parameters:
        - fid_cond_mrkt_div_code (str): 조건 시장 분류 코드 ("J": KRX, "NX": NXT, "UN": 통합, "W": ELW)
        - fid_cond_scr_div_code (str): 조건 화면 분류 코드 ("20171")
        - fid_input_iscd (str): 입력 종목코드 ("0000": 전체, 기타: 업종코드)
        - fid_div_cls_code (str): 분류 구분 코드 ("0": 전체, "1": 보통주, "2": 우선주)
        - fid_blng_cls_code (str): 소속 구분 코드 ("0": 평균거래량, "1": 거래증가율, "2": 평균거래회전율, "3": 거래금액순, "4": 평균거래금액회전율)
        - fid_trgt_cls_code (str): 대상 구분 코드 (9자리, "1" or "0", 차례대로 증거금 30% 40% 50% 60% 100% 신용보증금 30% 40% 50% 60%)
        - fid_trgt_exls_cls_code (str): 대상 제외 구분 코드 (10자리, "1" or "0", 차례대로 투자위험/경고/주의 관리종목 정리매매 불성실공시 우선주 거래정지 ETF ETN 신용주문불가 SPAC)
        - fid_input_price_1 (str): 입력 가격1 (가격 ~, 전체 가격 대상 조회 시 공란)
        - fid_input_price_2 (str): 입력 가격2 (~ 가격, 전체 가격 대상 조회 시 공란)
        - fid_vol_cnt (str): 거래량 수 (거래량 ~, 전체 거래량 대상 조회 시 공란)
        - fid_input_date_1 (str): 입력 날짜1 (공란)
        - tr_cont (str): 연속 거래 여부
        - dataframe (Optional[pd.DataFrame]): 누적 데이터프레임

    Returns:
        - DataFrame: 국내주식 순위분석 조회 결과
    
    Example:
        >>> df = volume_rank(fid_cond_mrkt_div_code="J", fid_cond_scr_div_code="20171", fid_input_iscd="0000", fid_div_cls_code="0", fid_blng_cls_code="0", fid_trgt_cls_code="111111111", fid_trgt_exls_cls_code="0000000000", fid_input_price_1="0", fid_input_price_2="1000000", fid_vol_cnt="100000", fid_input_date_1="")
    """
    # pandas 출력 옵션 설정
    pd.set_option('display.max_columns', None)  # 모든 컬럼 표시
    pd.set_option('display.width', None)  # 출력 너비 제한 해제
    pd.set_option('display.max_rows', None)  # 모든 행 표시

    # 토큰 발급
    ka.auth()

    # API 호출
    result = volume_rank(
        fid_cond_mrkt_div_code="J",
        fid_cond_scr_div_code="20171",
        fid_input_iscd="0002",
        fid_div_cls_code="0",
        fid_blng_cls_code="0",
        fid_trgt_cls_code="111111111",
        fid_trgt_exls_cls_code="000000",
        fid_input_price_1="0",
        fid_input_price_2="0",
        fid_vol_cnt="0",
        fid_input_date_1="0",
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
