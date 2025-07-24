"""
Created on 20250116 
@author: LaivData SJPark with cursor
"""

import sys
import logging
from typing import Tuple

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내선물옵션] 주문/계좌 > (야간)선물옵션 증거금 상세 [국내선물-024]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-futureoption/v1/trading/ngt-margin-detail"


def ngt_margin_detail(
        cano: str,  # 종합계좌번호
        acnt_prdt_cd: str,  # 계좌상품코드
        mgna_dvsn_cd: str  # 증거금 구분코드
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    (야간)선물옵션 증거금상세 API입니다.
    한국투자 HTS(eFriend Force) > [2537] 야간선물옵션 증거금상세 화면 의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
    
    Args:
        cano (str): [필수] 종합계좌번호
        acnt_prdt_cd (str): [필수] 계좌상품코드 (ex. 03)
        mgna_dvsn_cd (str): [필수] 증거금 구분코드 (ex. 01:위탁, 02:유지)

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]: (output1, output2, output3) 데이터프레임
        
    Example:
        >>> df1, df2, df3 = ngt_margin_detail(cano=trenv.my_acct, acnt_prdt_cd=trenv.my_prod, mgna_dvsn_cd="01")
        >>> print(df1)
    """

    if cano == "":
        raise ValueError("cano is required")

    if acnt_prdt_cd == "":
        raise ValueError("acnt_prdt_cd is required (e.g. '03')")

    if mgna_dvsn_cd == "":
        raise ValueError("mgna_dvsn_cd is required (e.g. '01:위탁, 02:유지')")

    tr_id = "CTFN7107R"  # (야간)선물옵션 증거금 상세

    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "MGNA_DVSN_CD": mgna_dvsn_cd
    }

    res = ka._url_fetch(API_URL, tr_id, "", params)

    if res.isOK():
        output1_data = pd.DataFrame(res.getBody().output1)
        output2_data = pd.DataFrame(res.getBody().output2)
        output3_data = pd.DataFrame([res.getBody().output3])

        return output1_data, output2_data, output3_data
    else:
        res.printError(url=API_URL)
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
