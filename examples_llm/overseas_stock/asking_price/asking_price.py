"""
Created on 20250601
"""

import logging
import sys

sys.path.extend(['../..', '.'])
import kis_auth as ka

# 로깅 설정
logging.basicConfig(level=logging.INFO)

##############################################################################################
# [해외주식] 실시간시세 > 해외주식 실시간호가[실시간-021]
##############################################################################################

def asking_price(
        tr_type: str,
        tr_key: str,
) -> tuple[dict, list[str]]:
    """
    해외주식 실시간호가를 이용하여 미국시세 실시간 1호가(매수/매도) 시세가 무료로 제공됩니다. (미국은 유료시세 제공 X)

    아시아 국가의 경우, HTS(efriend Plus) [7781] 시세신청(실시간) 화면에서 유료 서비스 신청 시, 
    "해외주식 실시간호가 HDFSASP0" 을 이용하여 아시아국가 유료시세(실시간호가)를 받아보실 수 있습니다. (24.11.29 반영)
    (아시아 국가 무료시세는 "해외주식 지연호가(아시아) HDFSASP1" 를 이용하시기 바랍니다.)

    Args:
        tr_type (str): [필수] 등록/해제
        tr_key (str): [필수] 종목코드

    Returns:
        message (dict): 메시지 데이터
        columns (list[str]): 컬럼 정보

    Example:
        >>> msg, columns = asking_price("1", "DNASAAPL")
        >>> print(msg, columns)
    """

    # 필수 파라미터 검증
    if tr_type == "":
        raise ValueError("tr_type is required")

    if tr_key == "":
        raise ValueError("tr_key is required")

    tr_id = "HDFSASP0"

    params = {
        "tr_key": tr_key,
    }

    msg = ka.data_fetch(tr_id, tr_type, params)

    columns = [
        "RSYM", "SYMB", "ZDIV", "XYMD", "XHMS", "KYMD", "KHMS",
        "BVOL", "AVOL", "BDVL", "ADVL",
        "PBID1", "PASK1", "VBID1", "VASK1", "DBID1", "DASK1",
        "PBID2", "PASK2", "VBID2", "VASK2", "DBID2", "DASK2",
        "PBID3", "PASK3", "VBID3", "VASK3", "DBID3", "DASK3",
        "PBID4", "PASK4", "VBID4", "VASK4", "DBID4", "DASK4",
        "PBID5", "PASK5", "VBID5", "VASK5", "DBID5", "DASK5",
        "PBID6", "PASK6", "VBID6", "VASK6", "DBID6", "DASK6",
        "PBID7", "PASK7", "VBID7", "VASK7", "DBID7", "DASK7",
        "PBID8", "PASK8", "VBID8", "VASK8", "DBID8", "DASK8",
        "PBID9", "PASK9", "VBID9", "VASK9", "DBID9", "DASK9",
        "PBID10", "PASK10", "VBID10", "VASK10", "DBID10", "DASK10"
    ]

    return msg, columns 