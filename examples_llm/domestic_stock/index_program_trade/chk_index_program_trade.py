"""
Created on 2025-07-09
@author: LaivData jjlee with cursor
"""

import logging
import sys

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka
from index_program_trade import index_program_trade

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

##############################################################################################
# [국내주식] 실시간시세 > 국내지수 실시간프로그램매매 [실시간-028]
##############################################################################################

# 컬럼명 매핑
COLUMN_MAPPING = {
    "bstp_cls_code": "업종 구분 코드",
    "bsop_hour": "영업 시간",
    "arbt_seln_entm_cnqn": "차익 매도 위탁 체결량",
    "arbt_seln_onsl_cnqn": "차익 매도 자기 체결량",
    "arbt_shnu_entm_cnqn": "차익 매수2 위탁 체결량",
    "arbt_shnu_onsl_cnqn": "차익 매수2 자기 체결량",
    "nabt_seln_entm_cnqn": "비차익 매도 위탁 체결량",
    "nabt_seln_onsl_cnqn": "비차익 매도 자기 체결량",
    "nabt_shnu_entm_cnqn": "비차익 매수2 위탁 체결량",
    "nabt_shnu_onsl_cnqn": "비차익 매수2 자기 체결량",
    "arbt_seln_entm_cntg_amt": "차익 매도 위탁 체결 금액",
    "arbt_seln_onsl_cntg_amt": "차익 매도 자기 체결 금액",
    "arbt_shnu_entm_cntg_amt": "차익 매수2 위탁 체결 금액",
    "arbt_shnu_onsl_cntg_amt": "차익 매수2 자기 체결 금액",
    "nabt_seln_entm_cntg_amt": "비차익 매도 위탁 체결 금액",
    "nabt_seln_onsl_cntg_amt": "비차익 매도 자기 체결 금액",
    "nabt_shnu_entm_cntg_amt": "비차익 매수2 위탁 체결 금액",
    "nabt_shnu_onsl_cntg_amt": "비차익 매수2 자기 체결 금액",
    "arbt_smtn_seln_vol": "차익 합계 매도 거래량",
    "arbt_smtm_seln_vol_rate": "차익 합계 매도 거래량 비율",
    "arbt_smtn_seln_tr_pbmn": "차익 합계 매도 거래 대금",
    "arbt_smtm_seln_tr_pbmn_rate": "차익 합계 매도 거래대금 비율",
    "arbt_smtn_shnu_vol": "차익 합계 매수2 거래량",
    "arbt_smtm_shnu_vol_rate": "차익 합계 매수 거래량 비율",
    "arbt_smtn_shnu_tr_pbmn": "차익 합계 매수2 거래 대금",
    "arbt_smtm_shnu_tr_pbmn_rate": "차익 합계 매수 거래대금 비율",
    "arbt_smtn_ntby_qty": "차익 합계 순매수 수량",
    "arbt_smtm_ntby_qty_rate": "차익 합계 순매수 수량 비율",
    "arbt_smtn_ntby_tr_pbmn": "차익 합계 순매수 거래 대금",
    "arbt_smtm_ntby_tr_pbmn_rate": "차익 합계 순매수 거래대금 비율",
    "nabt_smtn_seln_vol": "비차익 합계 매도 거래량",
    "nabt_smtm_seln_vol_rate": "비차익 합계 매도 거래량 비율",
    "nabt_smtn_seln_tr_pbmn": "비차익 합계 매도 거래 대금",
    "nabt_smtm_seln_tr_pbmn_rate": "비차익 합계 매도 거래대금 비율",
    "nabt_smtn_shnu_vol": "비차익 합계 매수2 거래량",
    "nabt_smtm_shnu_vol_rate": "비차익 합계 매수 거래량 비율",
    "nabt_smtn_shnu_tr_pbmn": "비차익 합계 매수2 거래 대금",
    "nabt_smtm_shnu_tr_pbmn_rate": "비차익 합계 매수 거래대금 비율",
    "nabt_smtn_ntby_qty": "비차익 합계 순매수 수량",
    "nabt_smtm_ntby_qty_rate": "비차익 합계 순매수 수량 비율",
    "nabt_smtn_ntby_tr_pbmn": "비차익 합계 순매수 거래 대금",
    "nabt_smtm_ntby_tr_pbmn_rate": "비차익 합계 순매수 거래대금 비율",
    "whol_entm_seln_vol": "전체 위탁 매도 거래량",
    "entm_seln_vol_rate": "위탁 매도 거래량 비율",
    "whol_entm_seln_tr_pbmn": "전체 위탁 매도 거래 대금",
    "entm_seln_tr_pbmn_rate": "위탁 매도 거래대금 비율",
    "whol_entm_shnu_vol": "전체 위탁 매수2 거래량",
    "entm_shnu_vol_rate": "위탁 매수 거래량 비율",
    "whol_entm_shnu_tr_pbmn": "전체 위탁 매수2 거래 대금",
    "entm_shnu_tr_pbmn_rate": "위탁 매수 거래대금 비율",
    "whol_entm_ntby_qt": "전체 위탁 순매수 수량",
    "entm_ntby_qty_rat": "위탁 순매수 수량 비율",
    "whol_entm_ntby_tr_pbmn": "전체 위탁 순매수 거래 대금",
    "entm_ntby_tr_pbmn_rate": "위탁 순매수 금액 비율",
    "whol_onsl_seln_vol": "전체 자기 매도 거래량",
    "onsl_seln_vol_rate": "자기 매도 거래량 비율",
    "whol_onsl_seln_tr_pbmn": "전체 자기 매도 거래 대금",
    "onsl_seln_tr_pbmn_rate": "자기 매도 거래대금 비율",
    "whol_onsl_shnu_vol": "전체 자기 매수2 거래량",
    "onsl_shnu_vol_rate": "자기 매수 거래량 비율",
    "whol_onsl_shnu_tr_pbmn": "전체 자기 매수2 거래 대금",
    "onsl_shnu_tr_pbmn_rate": "자기 매수 거래대금 비율",
    "whol_onsl_ntby_qty": "전체 자기 순매수 수량",
    "onsl_ntby_qty_rate": "자기 순매수량 비율",
    "whol_onsl_ntby_tr_pbmn": "전체 자기 순매수 거래 대금",
    "onsl_ntby_tr_pbmn_rate": "자기 순매수 대금 비율",
    "total_seln_qty": "총 매도 수량",
    "whol_seln_vol_rate": "전체 매도 거래량 비율",
    "total_seln_tr_pbmn": "총 매도 거래 대금",
    "whol_seln_tr_pbmn_rate": "전체 매도 거래대금 비율",
    "shnu_cntg_smtn": "총 매수 수량",
    "whol_shun_vol_rate": "전체 매수 거래량 비율",
    "total_shnu_tr_pbmn": "총 매수2 거래 대금",
    "whol_shun_tr_pbmn_rate": "전체 매수 거래대금 비율",
    "whol_ntby_qty": "전체 순매수 수량",
    "whol_smtm_ntby_qty_rate": "전체 합계 순매수 수량 비율",
    "whol_ntby_tr_pbmn": "전체 순매수 거래 대금",
    "whol_ntby_tr_pbmn_rate": "전체 순매수 거래대금 비율",
    "arbt_entm_ntby_qty": "차익 위탁 순매수 수량",
    "arbt_entm_ntby_tr_pbmn": "차익 위탁 순매수 거래 대금",
    "arbt_onsl_ntby_qty": "차익 자기 순매수 수량",
    "arbt_onsl_ntby_tr_pbmn": "차익 자기 순매수 거래 대금",
    "nabt_entm_ntby_qty": "비차익 위탁 순매수 수량",
    "nabt_entm_ntby_tr_pbmn": "비차익 위탁 순매수 거래 대금",
    "nabt_onsl_ntby_qty": "비차익 자기 순매수 수량",
    "nabt_onsl_ntby_tr_pbmn": "비차익 자기 순매수 거래 대금",
    "acml_vol": "누적 거래량",
    "acml_tr_pbmn": "누적 거래 대금"
}

# 숫자형 컬럼 리스트
NUMERIC_COLUMNS = [
    "arbt_seln_entm_cnqn", "arbt_seln_onsl_cnqn", "arbt_shnu_entm_cnqn", "arbt_shnu_onsl_cnqn",
    "nabt_seln_entm_cnqn", "nabt_seln_onsl_cnqn", "nabt_shnu_entm_cnqn", "nabt_shnu_onsl_cnqn",
    "arbt_seln_entm_cntg_amt", "arbt_seln_onsl_cntg_amt", "arbt_shnu_entm_cntg_amt", "arbt_shnu_onsl_cntg_amt",
    "nabt_seln_entm_cntg_amt", "nabt_seln_onsl_cntg_amt", "nabt_shnu_entm_cntg_amt", "nabt_shnu_onsl_cntg_amt",
    "arbt_smtn_seln_vol", "arbt_smtm_seln_vol_rate", "arbt_smtn_seln_tr_pbmn", "arbt_smtm_seln_tr_pbmn_rate",
    "arbt_smtn_shnu_vol", "arbt_smtm_shnu_vol_rate", "arbt_smtn_shnu_tr_pbmn", "arbt_smtm_shnu_tr_pbmn_rate",
    "arbt_smtn_ntby_qty", "arbt_smtm_ntby_qty_rate", "arbt_smtn_ntby_tr_pbmn", "arbt_smtm_ntby_tr_pbmn_rate",
    "nabt_smtn_seln_vol", "nabt_smtm_seln_vol_rate", "nabt_smtn_seln_tr_pbmn", "nabt_smtm_seln_tr_pbmn_rate",
    "nabt_smtn_shnu_vol", "nabt_smtm_shnu_vol_rate", "nabt_smtn_shnu_tr_pbmn", "nabt_smtm_shnu_tr_pbmn_rate",
    "nabt_smtn_ntby_qty", "nabt_smtm_ntby_qty_rate", "nabt_smtn_ntby_tr_pbmn", "nabt_smtm_ntby_tr_pbmn_rate",
    "whol_entm_seln_vol", "entm_seln_vol_rate", "whol_entm_seln_tr_pbmn", "entm_seln_tr_pbmn_rate",
    "whol_entm_shnu_vol", "entm_shnu_vol_rate", "whol_entm_shnu_tr_pbmn", "entm_shnu_tr_pbmn_rate",
    "whol_entm_ntby_qt", "entm_ntby_qty_rat", "whol_entm_ntby_tr_pbmn", "entm_ntby_tr_pbmn_rate",
    "whol_onsl_seln_vol", "onsl_seln_vol_rate", "whol_onsl_seln_tr_pbmn", "onsl_seln_tr_pbmn_rate",
    "whol_onsl_shnu_vol", "onsl_shnu_vol_rate", "whol_onsl_shnu_tr_pbmn", "onsl_shnu_tr_pbmn_rate",
    "whol_onsl_ntby_qty", "onsl_ntby_qty_rate", "whol_onsl_ntby_tr_pbmn", "onsl_ntby_tr_pbmn_rate",
    "total_seln_qty", "whol_seln_vol_rate", "total_seln_tr_pbmn", "whol_seln_tr_pbmn_rate",
    "shnu_cntg_smtn", "whol_shun_vol_rate", "total_shnu_tr_pbmn", "whol_shun_tr_pbmn_rate",
    "whol_ntby_qty", "whol_smtm_ntby_qty_rate", "whol_ntby_tr_pbmn", "whol_ntby_tr_pbmn_rate",
    "arbt_entm_ntby_qty", "arbt_entm_ntby_tr_pbmn", "arbt_onsl_ntby_qty", "arbt_onsl_ntby_tr_pbmn",
    "nabt_entm_ntby_qty", "nabt_entm_ntby_tr_pbmn", "nabt_onsl_ntby_qty", "nabt_onsl_ntby_tr_pbmn",
    "acml_vol", "acml_tr_pbmn"
]


def main():
    """
    국내지수 실시간프로그램매매
    
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
    kws.subscribe(request=index_program_trade, data=["0001", "0128"])

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