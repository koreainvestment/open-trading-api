"""
Created on 20250101 
@author: LaivData SJPark with cursor
"""


import sys
import logging
from typing import Optional

import pandas as pd

sys.path.extend(['../..', '.'])
import kis_auth as ka

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [국내주식] 시세분석 > 관심종목(멀티종목) 시세조회 [국내주식-205]
##############################################################################################

# 상수 정의
API_URL = "/uapi/domestic-stock/v1/quotations/intstock-multprice"

def intstock_multprice(
    fid_cond_mrkt_div_code_1: str,  # [필수] 조건 시장 분류 코드1 (ex. J)
    fid_input_iscd_1: str,          # [필수] 입력 종목코드1 (ex. 123456)
    fid_cond_mrkt_div_code_2: Optional[str] = None,  # 조건 시장 분류 코드2
    fid_input_iscd_2: Optional[str] = None,          # 입력 종목코드2
    fid_cond_mrkt_div_code_3: Optional[str] = None,  # 조건 시장 분류 코드3
    fid_input_iscd_3: Optional[str] = None,          # 입력 종목코드3
    fid_cond_mrkt_div_code_4: Optional[str] = None,  # 조건 시장 분류 코드4
    fid_input_iscd_4: Optional[str] = None,          # 입력 종목코드4
    fid_cond_mrkt_div_code_5: Optional[str] = None,  # 조건 시장 분류 코드5
    fid_input_iscd_5: Optional[str] = None,          # 입력 종목코드5
    fid_cond_mrkt_div_code_6: Optional[str] = None,  # 조건 시장 분류 코드6
    fid_input_iscd_6: Optional[str] = None,          # 입력 종목코드6
    fid_cond_mrkt_div_code_7: Optional[str] = None,  # 조건 시장 분류 코드7
    fid_input_iscd_7: Optional[str] = None,          # 입력 종목코드7
    fid_cond_mrkt_div_code_8: Optional[str] = None,  # 조건 시장 분류 코드8
    fid_input_iscd_8: Optional[str] = None,          # 입력 종목코드8
    fid_cond_mrkt_div_code_9: Optional[str] = None,  # 조건 시장 분류 코드9
    fid_input_iscd_9: Optional[str] = None,          # 입력 종목코드9
    fid_cond_mrkt_div_code_10: Optional[str] = None, # 조건 시장 분류 코드10
    fid_input_iscd_10: Optional[str] = None,         # 입력 종목코드10
    fid_cond_mrkt_div_code_11: Optional[str] = None, # 조건 시장 분류 코드11
    fid_input_iscd_11: Optional[str] = None,         # 입력 종목코드11
    fid_cond_mrkt_div_code_12: Optional[str] = None, # 조건 시장 분류 코드12
    fid_input_iscd_12: Optional[str] = None,         # 입력 종목코드12
    fid_cond_mrkt_div_code_13: Optional[str] = None, # 조건 시장 분류 코드13
    fid_input_iscd_13: Optional[str] = None,         # 입력 종목코드13
    fid_cond_mrkt_div_code_14: Optional[str] = None, # 조건 시장 분류 코드14
    fid_input_iscd_14: Optional[str] = None,         # 입력 종목코드14
    fid_cond_mrkt_div_code_15: Optional[str] = None, # 조건 시장 분류 코드15
    fid_input_iscd_15: Optional[str] = None,         # 입력 종목코드15
    fid_cond_mrkt_div_code_16: Optional[str] = None, # 조건 시장 분류 코드16
    fid_input_iscd_16: Optional[str] = None,         # 입력 종목코드16
    fid_cond_mrkt_div_code_17: Optional[str] = None, # 조건 시장 분류 코드17
    fid_input_iscd_17: Optional[str] = None,         # 입력 종목코드17
    fid_cond_mrkt_div_code_18: Optional[str] = None, # 조건 시장 분류 코드18
    fid_input_iscd_18: Optional[str] = None,         # 입력 종목코드18
    fid_cond_mrkt_div_code_19: Optional[str] = None, # 조건 시장 분류 코드19
    fid_input_iscd_19: Optional[str] = None,         # 입력 종목코드19
    fid_cond_mrkt_div_code_20: Optional[str] = None, # 조건 시장 분류 코드20
    fid_input_iscd_20: Optional[str] = None,         # 입력 종목코드20
    fid_cond_mrkt_div_code_21: Optional[str] = None, # 조건 시장 분류 코드21
    fid_input_iscd_21: Optional[str] = None,         # 입력 종목코드21
    fid_cond_mrkt_div_code_22: Optional[str] = None, # 조건 시장 분류 코드22
    fid_input_iscd_22: Optional[str] = None,         # 입력 종목코드22
    fid_cond_mrkt_div_code_23: Optional[str] = None, # 조건 시장 분류 코드23
    fid_input_iscd_23: Optional[str] = None,         # 입력 종목코드23
    fid_cond_mrkt_div_code_24: Optional[str] = None, # 조건 시장 분류 코드24
    fid_input_iscd_24: Optional[str] = None,         # 입력 종목코드24
    fid_cond_mrkt_div_code_25: Optional[str] = None, # 조건 시장 분류 코드25
    fid_input_iscd_25: Optional[str] = None,         # 입력 종목코드25
    fid_cond_mrkt_div_code_26: Optional[str] = None, # 조건 시장 분류 코드26
    fid_input_iscd_26: Optional[str] = None,         # 입력 종목코드26
    fid_cond_mrkt_div_code_27: Optional[str] = None, # 조건 시장 분류 코드27
    fid_input_iscd_27: Optional[str] = None,         # 입력 종목코드27
    fid_cond_mrkt_div_code_28: Optional[str] = None, # 조건 시장 분류 코드28
    fid_input_iscd_28: Optional[str] = None,         # 입력 종목코드28
    fid_cond_mrkt_div_code_29: Optional[str] = None, # 조건 시장 분류 코드29
    fid_input_iscd_29: Optional[str] = None,         # 입력 종목코드29
    fid_cond_mrkt_div_code_30: Optional[str] = None, # 조건 시장 분류 코드30
    fid_input_iscd_30: Optional[str] = None          # 입력 종목코드30
) -> pd.DataFrame:
    """
    관심종목(멀티종목) 시세조회 API입니다.
    ① 관심종목 그룹조회 → ② 관심종목 그룹별 종목조회 → ③ 관심종목(멀티종목) 시세조회 순서대로 호출하셔서 관심종목 시세 조회 가능합니다.

    ※ 한 번의 호출에 최대 30종목의 시세 확인 가능합니다.
    그룹별종목조회 결과를 아래와 같이 입력하셔서 총 30종목까지 복수종목 조회 가능합니다.(아래 Example 참고)
    . fid_mrkt_cls_code(시장구분) → FID_COND_MRKT_DIV_CODE_1
    . jong_code(종목코드) 1 → FID_INPUT_ISCD_1
    ...

    한국투자증권 Github 에서 관심종목 복수시세조회 파이썬 샘플코드를 참고하실 수 있습니다.
    https://github.com/koreainvestment/open-trading-api/blob/main/rest/interest_stocks_price.py
    
    Args:
        fid_cond_mrkt_div_code_1 (str): [필수] 조건 시장 분류 코드1 (J:KRX, NX:NXT)
        fid_input_iscd_1 (str): [필수] 입력 종목코드1 (ex. 123456)
        fid_cond_mrkt_div_code_2 (Optional[str]): 조건 시장 분류 코드2
        fid_input_iscd_2 (Optional[str]): 입력 종목코드2
        fid_cond_mrkt_div_code_3 (Optional[str]): 조건 시장 분류 코드3
        fid_input_iscd_3 (Optional[str]): 입력 종목코드3
        fid_cond_mrkt_div_code_4 (Optional[str]): 조건 시장 분류 코드4
        fid_input_iscd_4 (Optional[str]): 입력 종목코드4
        fid_cond_mrkt_div_code_5 (Optional[str]): 조건 시장 분류 코드5
        fid_input_iscd_5 (Optional[str]): 입력 종목코드5
        fid_cond_mrkt_div_code_6 (Optional[str]): 조건 시장 분류 코드6
        fid_input_iscd_6 (Optional[str]): 입력 종목코드6
        fid_cond_mrkt_div_code_7 (Optional[str]): 조건 시장 분류 코드7
        fid_input_iscd_7 (Optional[str]): 입력 종목코드7
        fid_cond_mrkt_div_code_8 (Optional[str]): 조건 시장 분류 코드8
        fid_input_iscd_8 (Optional[str]): 입력 종목코드8
        fid_cond_mrkt_div_code_9 (Optional[str]): 조건 시장 분류 코드9
        fid_input_iscd_9 (Optional[str]): 입력 종목코드9
        fid_cond_mrkt_div_code_10 (Optional[str]): 조건 시장 분류 코드10
        fid_input_iscd_10 (Optional[str]): 입력 종목코드10
        fid_cond_mrkt_div_code_11 (Optional[str]): 조건 시장 분류 코드11
        fid_input_iscd_11 (Optional[str]): 입력 종목코드11
        fid_cond_mrkt_div_code_12 (Optional[str]): 조건 시장 분류 코드12
        fid_input_iscd_12 (Optional[str]): 입력 종목코드12
        fid_cond_mrkt_div_code_13 (Optional[str]): 조건 시장 분류 코드13
        fid_input_iscd_13 (Optional[str]): 입력 종목코드13
        fid_cond_mrkt_div_code_14 (Optional[str]): 조건 시장 분류 코드14
        fid_input_iscd_14 (Optional[str]): 입력 종목코드14
        fid_cond_mrkt_div_code_15 (Optional[str]): 조건 시장 분류 코드15
        fid_input_iscd_15 (Optional[str]): 입력 종목코드15
        fid_cond_mrkt_div_code_16 (Optional[str]): 조건 시장 분류 코드16
        fid_input_iscd_16 (Optional[str]): 입력 종목코드16
        fid_cond_mrkt_div_code_17 (Optional[str]): 조건 시장 분류 코드17
        fid_input_iscd_17 (Optional[str]): 입력 종목코드17
        fid_cond_mrkt_div_code_18 (Optional[str]): 조건 시장 분류 코드18
        fid_input_iscd_18 (Optional[str]): 입력 종목코드18
        fid_cond_mrkt_div_code_19 (Optional[str]): 조건 시장 분류 코드19
        fid_input_iscd_19 (Optional[str]): 입력 종목코드19
        fid_cond_mrkt_div_code_20 (Optional[str]): 조건 시장 분류 코드20
        fid_input_iscd_20 (Optional[str]): 입력 종목코드20
        fid_cond_mrkt_div_code_21 (Optional[str]): 조건 시장 분류 코드21
        fid_input_iscd_21 (Optional[str]): 입력 종목코드21
        fid_cond_mrkt_div_code_22 (Optional[str]): 조건 시장 분류 코드22
        fid_input_iscd_22 (Optional[str]): 입력 종목코드22
        fid_cond_mrkt_div_code_23 (Optional[str]): 조건 시장 분류 코드23
        fid_input_iscd_23 (Optional[str]): 입력 종목코드23
        fid_cond_mrkt_div_code_24 (Optional[str]): 조건 시장 분류 코드24
        fid_input_iscd_24 (Optional[str]): 입력 종목코드24
        fid_cond_mrkt_div_code_25 (Optional[str]): 조건 시장 분류 코드25
        fid_input_iscd_25 (Optional[str]): 입력 종목코드25
        fid_cond_mrkt_div_code_26 (Optional[str]): 조건 시장 분류 코드26
        fid_input_iscd_26 (Optional[str]): 입력 종목코드26
        fid_cond_mrkt_div_code_27 (Optional[str]): 조건 시장 분류 코드27
        fid_input_iscd_27 (Optional[str]): 입력 종목코드27
        fid_cond_mrkt_div_code_28 (Optional[str]): 조건 시장 분류 코드28
        fid_input_iscd_28 (Optional[str]): 입력 종목코드28
        fid_cond_mrkt_div_code_29 (Optional[str]): 조건 시장 분류 코드29
        fid_input_iscd_29 (Optional[str]): 입력 종목코드29
        fid_cond_mrkt_div_code_30 (Optional[str]): 조건 시장 분류 코드30
        fid_input_iscd_30 (Optional[str]): 입력 종목코드30

    Returns:
        pd.DataFrame: 관심종목(멀티종목) 시세 데이터
        
    Example:
        >>> df = intstock_multprice(fid_cond_mrkt_div_code_1="J", fid_input_iscd_1="419530")
        >>> print(df)
    """

    if fid_cond_mrkt_div_code_1 == "":
        raise ValueError("fid_cond_mrkt_div_code_1 is required (e.g. 'J')")
    
    if fid_input_iscd_1 == "":
        raise ValueError("fid_input_iscd_1 is required (e.g. '123456')")

    tr_id = "FHKST11300006"  # 관심종목(멀티종목) 시세조회

    params = {
        "FID_COND_MRKT_DIV_CODE_1": fid_cond_mrkt_div_code_1,
        "FID_INPUT_ISCD_1": fid_input_iscd_1
    }
    
    # 옵션 파라미터 처리
    if fid_cond_mrkt_div_code_2 is not None:
        params["FID_COND_MRKT_DIV_CODE_2"] = fid_cond_mrkt_div_code_2
    if fid_input_iscd_2 is not None:
        params["FID_INPUT_ISCD_2"] = fid_input_iscd_2
    if fid_cond_mrkt_div_code_3 is not None:
        params["FID_COND_MRKT_DIV_CODE_3"] = fid_cond_mrkt_div_code_3
    if fid_input_iscd_3 is not None:
        params["FID_INPUT_ISCD_3"] = fid_input_iscd_3
    if fid_cond_mrkt_div_code_4 is not None:
        params["FID_COND_MRKT_DIV_CODE_4"] = fid_cond_mrkt_div_code_4
    if fid_input_iscd_4 is not None:
        params["FID_INPUT_ISCD_4"] = fid_input_iscd_4
    if fid_cond_mrkt_div_code_5 is not None:
        params["FID_COND_MRKT_DIV_CODE_5"] = fid_cond_mrkt_div_code_5
    if fid_input_iscd_5 is not None:
        params["FID_INPUT_ISCD_5"] = fid_input_iscd_5
    if fid_cond_mrkt_div_code_6 is not None:
        params["FID_COND_MRKT_DIV_CODE_6"] = fid_cond_mrkt_div_code_6
    if fid_input_iscd_6 is not None:
        params["FID_INPUT_ISCD_6"] = fid_input_iscd_6
    if fid_cond_mrkt_div_code_7 is not None:
        params["FID_COND_MRKT_DIV_CODE_7"] = fid_cond_mrkt_div_code_7
    if fid_input_iscd_7 is not None:
        params["FID_INPUT_ISCD_7"] = fid_input_iscd_7
    if fid_cond_mrkt_div_code_8 is not None:
        params["FID_COND_MRKT_DIV_CODE_8"] = fid_cond_mrkt_div_code_8
    if fid_input_iscd_8 is not None:
        params["FID_INPUT_ISCD_8"] = fid_input_iscd_8
    if fid_cond_mrkt_div_code_9 is not None:
        params["FID_COND_MRKT_DIV_CODE_9"] = fid_cond_mrkt_div_code_9
    if fid_input_iscd_9 is not None:
        params["FID_INPUT_ISCD_9"] = fid_input_iscd_9
    if fid_cond_mrkt_div_code_10 is not None:
        params["FID_COND_MRKT_DIV_CODE_10"] = fid_cond_mrkt_div_code_10
    if fid_input_iscd_10 is not None:
        params["FID_INPUT_ISCD_10"] = fid_input_iscd_10
    if fid_cond_mrkt_div_code_11 is not None:
        params["FID_COND_MRKT_DIV_CODE_11"] = fid_cond_mrkt_div_code_11
    if fid_input_iscd_11 is not None:
        params["FID_INPUT_ISCD_11"] = fid_input_iscd_11
    if fid_cond_mrkt_div_code_12 is not None:
        params["FID_COND_MRKT_DIV_CODE_12"] = fid_cond_mrkt_div_code_12
    if fid_input_iscd_12 is not None:
        params["FID_INPUT_ISCD_12"] = fid_input_iscd_12
    if fid_cond_mrkt_div_code_13 is not None:
        params["FID_COND_MRKT_DIV_CODE_13"] = fid_cond_mrkt_div_code_13
    if fid_input_iscd_13 is not None:
        params["FID_INPUT_ISCD_13"] = fid_input_iscd_13
    if fid_cond_mrkt_div_code_14 is not None:
        params["FID_COND_MRKT_DIV_CODE_14"] = fid_cond_mrkt_div_code_14
    if fid_input_iscd_14 is not None:
        params["FID_INPUT_ISCD_14"] = fid_input_iscd_14
    if fid_cond_mrkt_div_code_15 is not None:
        params["FID_COND_MRKT_DIV_CODE_15"] = fid_cond_mrkt_div_code_15
    if fid_input_iscd_15 is not None:
        params["FID_INPUT_ISCD_15"] = fid_input_iscd_15
    if fid_cond_mrkt_div_code_16 is not None:
        params["FID_COND_MRKT_DIV_CODE_16"] = fid_cond_mrkt_div_code_16
    if fid_input_iscd_16 is not None:
        params["FID_INPUT_ISCD_16"] = fid_input_iscd_16
    if fid_cond_mrkt_div_code_17 is not None:
        params["FID_COND_MRKT_DIV_CODE_17"] = fid_cond_mrkt_div_code_17
    if fid_input_iscd_17 is not None:
        params["FID_INPUT_ISCD_17"] = fid_input_iscd_17
    if fid_cond_mrkt_div_code_18 is not None:
        params["FID_COND_MRKT_DIV_CODE_18"] = fid_cond_mrkt_div_code_18
    if fid_input_iscd_18 is not None:
        params["FID_INPUT_ISCD_18"] = fid_input_iscd_18
    if fid_cond_mrkt_div_code_19 is not None:
        params["FID_COND_MRKT_DIV_CODE_19"] = fid_cond_mrkt_div_code_19
    if fid_input_iscd_19 is not None:
        params["FID_INPUT_ISCD_19"] = fid_input_iscd_19
    if fid_cond_mrkt_div_code_20 is not None:
        params["FID_COND_MRKT_DIV_CODE_20"] = fid_cond_mrkt_div_code_20
    if fid_input_iscd_20 is not None:
        params["FID_INPUT_ISCD_20"] = fid_input_iscd_20
    if fid_cond_mrkt_div_code_21 is not None:
        params["FID_COND_MRKT_DIV_CODE_21"] = fid_cond_mrkt_div_code_21
    if fid_input_iscd_21 is not None:
        params["FID_INPUT_ISCD_21"] = fid_input_iscd_21
    if fid_cond_mrkt_div_code_22 is not None:
        params["FID_COND_MRKT_DIV_CODE_22"] = fid_cond_mrkt_div_code_22
    if fid_input_iscd_22 is not None:
        params["FID_INPUT_ISCD_22"] = fid_input_iscd_22
    if fid_cond_mrkt_div_code_23 is not None:
        params["FID_COND_MRKT_DIV_CODE_23"] = fid_cond_mrkt_div_code_23
    if fid_input_iscd_23 is not None:
        params["FID_INPUT_ISCD_23"] = fid_input_iscd_23
    if fid_cond_mrkt_div_code_24 is not None:
        params["FID_COND_MRKT_DIV_CODE_24"] = fid_cond_mrkt_div_code_24
    if fid_input_iscd_24 is not None:
        params["FID_INPUT_ISCD_24"] = fid_input_iscd_24
    if fid_cond_mrkt_div_code_25 is not None:
        params["FID_COND_MRKT_DIV_CODE_25"] = fid_cond_mrkt_div_code_25
    if fid_input_iscd_25 is not None:
        params["FID_INPUT_ISCD_25"] = fid_input_iscd_25
    if fid_cond_mrkt_div_code_26 is not None:
        params["FID_COND_MRKT_DIV_CODE_26"] = fid_cond_mrkt_div_code_26
    if fid_input_iscd_26 is not None:
        params["FID_INPUT_ISCD_26"] = fid_input_iscd_26
    if fid_cond_mrkt_div_code_27 is not None:
        params["FID_COND_MRKT_DIV_CODE_27"] = fid_cond_mrkt_div_code_27
    if fid_input_iscd_27 is not None:
        params["FID_INPUT_ISCD_27"] = fid_input_iscd_27
    if fid_cond_mrkt_div_code_28 is not None:
        params["FID_COND_MRKT_DIV_CODE_28"] = fid_cond_mrkt_div_code_28
    if fid_input_iscd_28 is not None:
        params["FID_INPUT_ISCD_28"] = fid_input_iscd_28
    if fid_cond_mrkt_div_code_29 is not None:
        params["FID_COND_MRKT_DIV_CODE_29"] = fid_cond_mrkt_div_code_29
    if fid_input_iscd_29 is not None:
        params["FID_INPUT_ISCD_29"] = fid_input_iscd_29
    if fid_cond_mrkt_div_code_30 is not None:
        params["FID_COND_MRKT_DIV_CODE_30"] = fid_cond_mrkt_div_code_30
    if fid_input_iscd_30 is not None:
        params["FID_INPUT_ISCD_30"] = fid_input_iscd_30
    
    res = ka._url_fetch(API_URL, tr_id, "", params)
    
    if res.isOK():
        current_data = pd.DataFrame(res.getBody().output)
        logging.info("Data fetch complete.")
        return current_data
    else:
        res.printError(url=API_URL)
        return pd.DataFrame() 