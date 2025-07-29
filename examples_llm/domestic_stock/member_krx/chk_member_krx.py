"""
Created on 2025-07-09
@author: LaivData jjlee with cursor
"""

import logging
import sys

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from member_krx import member_krx

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [국내주식] 실시간시세 > 국내주식 실시간회원사 (KRX) [실시간-047]
##############################################################################################

# 컬럼명 매핑
COLUMN_MAPPING = {
    "mksc_shrn_iscd": "유가증권단축종목코드",
    "seln2_mbcr_name1": "매도2회원사명1",
    "seln2_mbcr_name2": "매도2회원사명2",
    "seln2_mbcr_name3": "매도2회원사명3",
    "seln2_mbcr_name4": "매도2회원사명4",
    "seln2_mbcr_name5": "매도2회원사명5",
    "byov_mbcr_name1": "매수회원사명1",
    "byov_mbcr_name2": "매수회원사명2",
    "byov_mbcr_name3": "매수회원사명3",
    "byov_mbcr_name4": "매수회원사명4",
    "byov_mbcr_name5": "매수회원사명5",
    "total_seln_qty1": "총매도수량1",
    "total_seln_qty2": "총매도수량2",
    "total_seln_qty3": "총매도수량3",
    "total_seln_qty4": "총매도수량4",
    "total_seln_qty5": "총매도수량5",
    "total_shnu_qty1": "총매수2수량1",
    "total_shnu_qty2": "총매수2수량2",
    "total_shnu_qty3": "총매수2수량3",
    "total_shnu_qty4": "총매수2수량4",
    "total_shnu_qty5": "총매수2수량5",
    "seln_mbcr_glob_yn_1": "매도거래원구분1",
    "seln_mbcr_glob_yn_2": "매도거래원구분2",
    "seln_mbcr_glob_yn_3": "매도거래원구분3",
    "seln_mbcr_glob_yn_4": "매도거래원구분4",
    "seln_mbcr_glob_yn_5": "매도거래원구분5",
    "shnu_mbcr_glob_yn_1": "매수거래원구분1",
    "shnu_mbcr_glob_yn_2": "매수거래원구분2",
    "shnu_mbcr_glob_yn_3": "매수거래원구분3",
    "shnu_mbcr_glob_yn_4": "매수거래원구분4",
    "shnu_mbcr_glob_yn_5": "매수거래원구분5",
    "seln_mbcr_no1": "매도거래원코드1",
    "seln_mbcr_no2": "매도거래원코드2",
    "seln_mbcr_no3": "매도거래원코드3",
    "seln_mbcr_no4": "매도거래원코드4",
    "seln_mbcr_no5": "매도거래원코드5",
    "shnu_mbcr_no1": "매수거래원코드1",
    "shnu_mbcr_no2": "매수거래원코드2",
    "shnu_mbcr_no3": "매수거래원코드3",
    "shnu_mbcr_no4": "매수거래원코드4",
    "shnu_mbcr_no5": "매수거래원코드5",
    "seln_mbcr_rlim1": "매도회원사비중1",
    "seln_mbcr_rlim2": "매도회원사비중2",
    "seln_mbcr_rlim3": "매도회원사비중3",
    "seln_mbcr_rlim4": "매도회원사비중4",
    "seln_mbcr_rlim5": "매도회원사비중5",
    "shnu_mbcr_rlim1": "매수2회원사비중1",
    "shnu_mbcr_rlim2": "매수2회원사비중2",
    "shnu_mbcr_rlim3": "매수2회원사비중3",
    "shnu_mbcr_rlim4": "매수2회원사비중4",
    "shnu_mbcr_rlim5": "매수2회원사비중5",
    "seln_qty_icdc1": "매도수량증감1",
    "seln_qty_icdc2": "매도수량증감2",
    "seln_qty_icdc3": "매도수량증감3",
    "seln_qty_icdc4": "매도수량증감4",
    "seln_qty_icdc5": "매도수량증감5",
    "shnu_qty_icdc1": "매수2수량증감1",
    "shnu_qty_icdc2": "매수2수량증감2",
    "shnu_qty_icdc3": "매수2수량증감3",
    "shnu_qty_icdc4": "매수2수량증감4",
    "shnu_qty_icdc5": "매수2수량증감5",
    "glob_total_seln_qty": "외국계총매도수량",
    "glob_total_shnu_qty": "외국계총매수2수량",
    "glob_total_seln_qty_icdc": "외국계총매도수량증감",
    "glob_total_shnu_qty_icdc": "외국계총매수2수량증감",
    "glob_ntby_qty": "외국계순매수수량",
    "glob_seln_rlim": "외국계매도비중",
    "glob_shnu_rlim": "외국계매수2비중",
    "seln2_mbcr_eng_name1": "매도2영문회원사명1",
    "seln2_mbcr_eng_name2": "매도2영문회원사명2",
    "seln2_mbcr_eng_name3": "매도2영문회원사명3",
    "seln2_mbcr_eng_name4": "매도2영문회원사명4",
    "seln2_mbcr_eng_name5": "매도2영문회원사명5",
    "byov_mbcr_eng_name1": "매수영문회원사명1",
    "byov_mbcr_eng_name2": "매수영문회원사명2",
    "byov_mbcr_eng_name3": "매수영문회원사명3",
    "byov_mbcr_eng_name4": "매수영문회원사명4",
    "byov_mbcr_eng_name5": "매수영문회원사명5"
}

# 숫자형 컬럼 리스트 (문자열 컬럼 제외)
NUMERIC_COLUMNS = [
    "total_seln_qty1", "total_seln_qty2", "total_seln_qty3", "total_seln_qty4", "total_seln_qty5",
    "total_shnu_qty1", "total_shnu_qty2", "total_shnu_qty3", "total_shnu_qty4", "total_shnu_qty5",
    "seln_mbcr_rlim1", "seln_mbcr_rlim2", "seln_mbcr_rlim3", "seln_mbcr_rlim4", "seln_mbcr_rlim5",
    "shnu_mbcr_rlim1", "shnu_mbcr_rlim2", "shnu_mbcr_rlim3", "shnu_mbcr_rlim4", "shnu_mbcr_rlim5",
    "seln_qty_icdc1", "seln_qty_icdc2", "seln_qty_icdc3", "seln_qty_icdc4", "seln_qty_icdc5",
    "shnu_qty_icdc1", "shnu_qty_icdc2", "shnu_qty_icdc3", "shnu_qty_icdc4", "shnu_qty_icdc5",
    "glob_total_seln_qty", "glob_total_shnu_qty", "glob_total_seln_qty_icdc", "glob_total_shnu_qty_icdc",
    "glob_ntby_qty", "glob_seln_rlim", "glob_shnu_rlim"
]


def main():
    """
    국내주식 실시간회원사 (KRX)
    
    [참고자료]
종목코드 마스터파일 파이썬 정제코드는 한국투자증권 Github 참고 부탁드립니다.
https://github.com/koreainvestment/open-trading-api/tree/main/stocks_info

[호출 데이터]
헤더와 바디 값을 합쳐 JSON 형태로 전송합니다.

[응답 데이터]
1. 정상 등록 여부 (JSON)
- JSON["body"]["msg1"] - 정상 응답 시, SUBSCRIBE SUCCESS
- JSON["body"]["output"]["iv"] - 실시간 결과 복호화에 필요한 AES256 IV (Initialize Vector)
- JSON["body"]["output"]["key"] - 실시간 결과 복호화에 필요한 AES256 Key

2. 실시간 결과 응답 ( | 로 구분되는 값)
ex) 0|H0STCNT0|004|005930^123929^73100^5^...
- 암호화 유무 : 0 암호화 되지 않은 데이터 / 1 암호화된 데이터
- TR_ID : 등록한 tr_id (ex. H0STCNT0)
- 데이터 건수 : (ex. 001 인 경우 데이터 건수 1건, 004인 경우 데이터 건수 4건)
- 응답 데이터 : 아래 response 데이터 참조 ( ^로 구분됨)
    """

    # pandas 출력 옵션 설정
    pd.set_option('display.max_columns', None)  # 모든 컬럼 표시
    pd.set_option('display.width', None)  # 출력 너비 제한 해제
    pd.set_option('display.max_rows', None)  # 모든 행 표시

    # 인증 토큰 발급
    ka.auth()
    ka.auth_ws()

    # 인증(auth_ws()) 이후에 선언
    kws = ka.KISWebSocket(api_url="/tryitout")

    # 조회
    kws.subscribe(request=member_krx, data=["005930", "000660"])

    # 결과 표시
    def on_result(ws, tr_id: str, result: pd.DataFrame, data_map: dict):
        try:            
            # 안전한 컬럼명 매핑 (존재하는 컬럼에 대해서만 한글명 적용)
            if not result.empty:
                # 컬럼명 매핑
                existing_columns = {col: COLUMN_MAPPING[col] for col in result.columns if col in COLUMN_MAPPING}
                if existing_columns:
                    result = result.rename(columns=existing_columns)
                    logging.info(f"컬럼명 매핑 완료: {len(existing_columns)}개 컬럼")
                
                # 안전한 숫자형 컬럼 변환 (존재하는 컬럼에 대해서만 적용)
                NUMERIC_COLUMNS_to_convert = [col for col in NUMERIC_COLUMNS if col in result.columns]
                if NUMERIC_COLUMNS_to_convert:
                    for col in NUMERIC_COLUMNS_to_convert:
                        try:
                            # 한글명으로 변환된 컬럼이 있는지 확인
                            tarcol = COLUMN_MAPPING.get(col, col)
                            if tarcol in result.columns:
                                result[tarcol] = pd.to_numeric(result[tarcol], errors='coerce')
                        except Exception as e:
                            logging.warning(f"컬럼 '{col}' 숫자 변환 실패: {e}")
                    logging.info(f"숫자형 변환 완료: {len(NUMERIC_COLUMNS_to_convert)}개 컬럼")
            
            logging.info("결과:")
            print(result)
        except Exception as e:
            logging.error(f"결과 처리 중 오류: {e}")
            logging.error(f"받은 데이터: {result}")

    kws.start(on_result=on_result)


if __name__ == "__main__":
    main()