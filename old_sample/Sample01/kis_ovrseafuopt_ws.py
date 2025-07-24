# 국내주식 실시간 websocket sample
import websocket

import kis_auth as ka
import kis_ovrseafuopt as kb

import os
import json
import requests

import pandas as pd
import numpy as np

import time
import datetime

from io import StringIO
from threading import Thread

from collections import namedtuple, deque

try:
    import websockets

except ImportError:
    print("websocket-client 설치중입니다.")
    os.system('python3 -m pip3 install websocket-client')

from enum import StrEnum


class KIS_WSReq(StrEnum):
    CONTRACT = 'HDFFF020'       # 해외선물옵션 실시간체결가
    BID_ASK = 'HDFFF010'        # 해외선물옵션 실시간호가
    ORDERNOTICE = 'HDFFF1C0'    # 실시간 해외선물옵션 주문내역발생통보
    CCLDNOTICE = 'HDFFF2C0'     # 실시간 해외선물옵션 체결내역발생통보

import talib as ta


class BasicPlan:

    def __init__(self, stock_code, window=20):
        self._stock_code = stock_code
        self._queue = deque(maxlen=window)
        self._prev_ma = None

    def push(self, value):
        self._queue.append(value)
        ma = sum(self._queue) / len(self._queue)
        diff = ma - self._prev_ma if self._prev_ma is not None else None
        self._prev_ma = ma

        print(f"{self._stock_code}****** value: {value}, MA: {ma}, diff: {diff}...")

class RSI_ST:   # RSI(Relative Strength Index, 상대강도지수)라는 주가 지표 계산
    def __init__(self, stock_code, window=21):
        self._stock_code = stock_code
        self._queue = deque(maxlen=window)
        self.rsi_period = window

    def eval(self):
        # dftt = getStreamdDF(self._stock_code)
        # print(self)
        dftt = contract_sub_df.get(self._stock_code).copy()
        dftt = dftt.set_index(['TICK_HOUR'])
        dftt['LAST_PRICE'] = pd.to_numeric(dftt['LAST_PRICE'], errors='coerce').convert_dtypes()
        np_closes = np.array(dftt['LAST_PRICE'], dtype=np.float64)
        rsi = ta.RSI(np_closes, self.rsi_period)

        last_rsi = rsi[-1]

        if last_rsi < 30:
            print(f"({self._stock_code})[BUY] ***RSI: {last_rsi}")    # 통상적으로 RSI가 30 이하면 과매도 상태인 것으로 판단하고 시장이 과도하게 하락했음을 나타냄
        elif last_rsi < 70 and last_rsi >= 30:
            print(f"({self._stock_code})[N/A] ***RSI: {last_rsi}")
        elif last_rsi >= 70:
            print(f"({self._stock_code})[SELL] ***RSI: {last_rsi}")   # 통상적으로 RSI가 70 이상이면 과매수 상태로 간주하고 시장이 과열되었을 가능성이 있음을 나타냄
        else:
            print(self._stock_code)


_today__ = datetime.date.today().strftime("%Y%m%d")

ka.auth()

__DEBUG__ = False  # True

# 실시간 해외주식 계좌체결통보 복호화를 위한 부분 - start
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from base64 import b64decode


# AES256 DECODE: Copied from KIS Developers Github sample code
def aes_cbc_base64_dec(key, iv, cipher_text):
    """
    :param key:  str type AES256 secret key value
    :param iv: str type AES256 Initialize Vector
    :param cipher_text: Base64 encoded AES256 str
    :return: Base64-AES256 decodec str
    """
    cipher = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv.encode('utf-8'))
    return bytes.decode(unpad(cipher.decrypt(b64decode(cipher_text)), AES.block_size))


# 실시간 해외주식 계좌체결통보 복호화를 위한 부분 - end


contract_sub_df = dict()  # 실시간 해외주식 체결 결과를 종목별로 저장하기 위한 container
tr_plans = dict()         # 실시간 해외주식 체결 값에 따라 무언가를 수행할 Class 를 저장하기 위한 container
excg_dict = {
    'NYS' : 'NYSE',  #미국뉴욕
    'NAS' : 'NASD',  #미국나스닥
    'AMS' : 'AMEX',  #미국아멕스
    'TSE' : 'TKSE',  #일본도쿄
    'HKS' : 'SEHK',  #홍콩
    'SHS' : 'SHAA',  #중국상해
    'SZS' : 'SZAA',  #중국심천
    'HSX' : 'VNSE',  #베트남호치민,
    'HNX' : 'HASE',  #베트남하노이
    'BAY' : 'NYSE',  #미국뉴욕(주간)
    'BAQ' : 'NASD',  #미국나스닥(주간),
    'BAA' : 'AMEX'   #미국아멕스(주간)
}


#reserved_cols = ['TICK_HOUR', 'STCK_PRPR', 'ACML_VOL']  # 실시간 해외주식 체결 중 사용할 수신시간, 현재가, 누적거래량 만 추출하기 위한 column 정의
reserved_cols = ['TICK_HOUR', 'LAST_PRICE', 'VOL']  # 실시간 해외선물옵션 체결 중 사용할 column 만 추출하기 위한 column 정의

# 해외선물옵션 실시간체결가 column header
contract_cols = ['SERIES_CD',	    # 종목코드	* 각 항목사이에는 구분자로 ^ 사용, 모든 데이터타입은 STRING으로 변환되어 PUSH 처리됨'
                'BSNS_DATE',	    # 영업일자
                'MRKT_OPEN_DATE',	# 장개시일자
                'MRKT_OPEN_TIME',	# 장개시시각
                'MRKT_CLOSE_DATE',	# 장종료일자
                'MRKT_CLOSE_TIME',	# 장종료시각
                'PREV_PRICE',	    # 전일종가 ※ 전일종가, 체결가격, 전일대비가, 시가, 고가, 저가 ※ FFCODE.MST(해외선물종목마스터 파일)의 SCALCDESZ(계산 소수점) 값 참고
                'RECV_DATE',	    # 수신일자
                'TICK_HOUR',	    # 수신시각 ※ 수신시각(RECV_TIME) = 실제 체결시각 ★ pandas time conversion 편의를 위해 이 필드만 이름을 통일한다 'KHMS' 한국시간
                'ACTIVE_FLAG',	    # 본장_전산장구분
                'LAST_PRICE',	    # 체결가격
                'LAST_QNTT',	    # 체결수량
                'PREV_DIFF_PRICE',	# 전일대비가
                'PREV_DIFF_RATE',	# 등락률
                'OPEN_PRICE',	    # 시가
                'HIGH_PRICE',	    # 고가
                'LOW_PRICE',	    # 저가
                'VOL',	            # 누적거래량
                'PREV_SIGN',	    # 전일대비부호
                'QUOTSIGN',	        # 체결구분 ※ 2:매수체결 5:매도체결
                'RECV_TIME2',	    # 수신시각2 만분의일초
                'PSTTL_PRICE',	    # 전일정산가
                'PSTTL_SIGN',	    # 전일정산가대비
                'PSTTL_DIFF_PRICE',	# 전일정산가대비가격
                'PSTTL_DIFF_RATE']	# 전일정산가대비율

# 실시간 해외선물옵션호가 column eader
bid_ask_cols = ['SERIES_CD',	    # 종목코드 '각 항목사이에는 구분자로 ^ 사용,모든 데이터타입은 STRING으로 변환되어 PUSH 처리됨'
                'RECV_DATE',	    # 수신일자
                'TICK_HOUR',	    # 수신시각 ※ 수신시각(RECV_TIME) = 실제 체결시각 ★ pandas time conversion 편의를 위해 이 필드만 이름을 통일한다 'KHMS' 한국시간
                'PREV_PRICE',	    # 전일종가 ※ 전일종가, 매수1호가~매도5호가 ※ FFCODE.MST(해외선물종목마스터 파일)의 SCALCDESZ(계산 소수점) 값 참고
                'BID_QNTT_1',	    # 매수1수량
                'BID_NUM_1',	    # 매수1번호
                'BID_PRICE_1',	    # 매수1호가
                'ASK_QNTT_1',	    # 매도1수량
                'ASK_NUM_1',	    # 매도1번호
                'ASK_PRICE_1',	    # 매도1호가
                'BID_QNTT_2',	    # 매수2수량
                'BID_NUM_2',	    # 매수2번호
                'BID_PRICE_2',	    # 매수2호가
                'ASK_QNTT_2',	    # 매도2수량
                'ASK_NUM_2',	    # 매도2번호
                'ASK_PRICE_2',	    # 매도2호가
                'BID_QNTT_3',	    # 매수3수량
                'BID_NUM_3',	    # 매수3번호
                'BID_PRICE_3',	    # 매수3호가
                'ASK_QNTT_3',	    # 매도3수량
                'ASK_NUM_3',	    # 매도3번호
                'ASK_PRICE_3',	    # 매도3호가
                'BID_QNTT_4',	    # 매수4수량
                'BID_NUM_4',	    # 매수4번호
                'BID_PRICE_4',	    # 매수4호가
                'ASK_QNTT_4',	    # 매도4수량
                'ASK_NUM_4',	    # 매도4번호
                'ASK_PRICE_4',	    # 매도4호가
                'BID_QNTT_5',	    # 매수5수량
                'BID_NUM_5',	    # 매수5번호
                'BID_PRICE_5',	    # 매수5호가
                'ASK_QNTT_5',	    # 매도5수량
                'ASK_NUM_5',	    # 매도5번호
                'ASK_PRICE_5',	    # 매도5호가
                'STTL_PRICE']	    # 전일정산가

# 실시간 계좌주문내역발생통보 column header
ordernotice_cols = ['USER_ID',	    # 유저ID 각 항목사이에는 구분자로 ^ 사용, 모든 데이터타입은 STRING으로 변환되어 PUSH 처리됨'
                'ACCT_NO',	        # 계좌번호
                'ORD_DT',	        # 주문일자
                'ODNO',	            # 주문번호
                'ORGN_ORD_DT',	    # 원주문일자
                'ORGN_ODNO',	    # 원주문번호
                'SERIES',	        # 종목명
                'RVSE_CNCL_DVSN_CD',# 정정취소구분코드 해당없음 : 00 , 정정 : 01 , 취소 : 02
                'SLL_BUY_DVSN_CD',	# 매도매수구분코드 01 : 매도, 02 : 매수
                'CPLX_ORD_DVSN_CD',	# 복합주문구분코드 0 (HEDGE청산만 이용)
                'PRCE_TP',	        # 가격구분코드',	# 1:LIMIT, 2:MARKET, 3:STOP(STOP가격시 시장가)
                'FM_EXCG_RCIT_DVSN_CD',	# FM거래소접수구분코드 01:접수전, 02:응답, 03:거부
                'ORD_QTY',	        # 주문수량
                'FM_LMT_PRIC',	    # FMLIMIT가격
                'FM_STOP_ORD_PRIC',	# FMSTOP주문가격
                'TOT_CCLD_QTY',	    # 총체결수량
                'TOT_CCLD_UV',	    # 총체결단가
                'ORD_REMQ', 	    # 잔량
                'FM_ORD_GRP_DT',    # FM주문그룹일자 주문일자(ORD_DT)와 동일
                'ORD_GRP_STNO',	    # 주문그룹번호
                'ORD_DTL_DTIME',    # 주문상세일시
                'OPRT_DTL_DTIME',	# 조작상세일시
                'WORK_EMPL',	    # 주문자
                'CRCY_CD',	        # 통화코드
                'LQD_YN',	        # 청산여부(Y/N)
                'LQD_LMT_PRIC',	    # 청산LIMIT가격
                'LQD_STOP_PRIC',	# 청산STOP가격
                'TRD_COND',	        # 체결조건코드
                'TERM_ORD_VALD_DTIME',	# 기간주문유효상세일시
                'SPEC_TP',	        # 계좌청산유형구분코드
                'ECIS_RSVN_ORD_YN',	# 행사예약주문여부
                'FUOP_ITEM_DVSN_CD',# 선물옵션종목구분코드
                'AUTO_ORD_DVSN_CD']	# 자동주문 전략구분

# 실시간 계좌체결내역발생통보 column header
ccldnotice_cols = ['USER_ID',	    # 유저ID '각 항목사이에는 구분자로 ^ 사용, 모든 데이터타입은 STRING으로 변환되어 PUSH 처리됨'
                'ACCT_NO',	        # 계좌번호
                'ORD_DT',	        # 주문일자
                'ODNO',	            # 주문번호
                'ORGN_ORD_DT',	    # 원주문일자
                'ORGN_ODNO',	    # 원주문번호
                'SERIES',	        # 종목명
                'RVSE_CNCL_DVSN_CD',# 정정취소구분코드',	# 해당없음 : 00 , 정정 : 01 , 취소 : 02
                'SLL_BUY_DVSN_CD',	# 매도매수구분코드',	# 01 : 매도, 02 : 매수
                'CPLX_ORD_DVSN_CD',	# 복합주문구분코드',	# 0 (HEDGE청산만 이용)
                'PRCE_TP',	        # 가격구분코드
                'FM_EXCG_RCIT_DVSN_CD',	# FM거래소접수구분코드
                'ORD_QTY',	        # 주문수량
                'FM_LMT_PRIC',	    # FMLIMIT가격
                'FM_STOP_ORD_PRIC',	# FMSTOP주문가격
                'TOT_CCLD_QTY',	    # 총체결수량',	# 동일한 주문건에 대한 누적된 체결수량 (하나의 주문건에 여러건의 체결내역 발생)
                'TOT_CCLD_UV',	    # 총체결단가
                'ORD_REMQ',	        # 잔량
                'FM_ORD_GRP_DT',    # FM주문그룹일자
                'ORD_GRP_STNO',	    # 주문그룹번호
                'ORD_DTL_DTIME',    # 주문상세일시
                'OPRT_DTL_DTIME',	# 조작상세일시
                'WORK_EMPL',	    # 주문자
                'CCLD_DT',	        # 체결일자
                'CCNO',	            # 체결번호
                'API_CCNO',	        # API 체결번호
                'CCLD_QTY',	        # 체결수량',	# 매 체결 단위 체결수량임 (여러건 체결내역 누적 체결수량인 총체결수량과 다름)
                'FM_CCLD_PRIC',	    # FM체결가격
                'CRCY_CD',	        # 통화코드
                'TRST_FEE',	        # 위탁수수료
                'ORD_MDIA_ONLINE_YN',	# 주문매체온라인여부
                'FM_CCLD_AMT',	    # FM체결금액
                'FUOP_ITEM_DVSN_CD']# 선물옵션종목구분코드


# 웹소켓 접속키 발급
def get_approval():
    url = ka.getTREnv().my_url
    headers = {"content-type": "application/json"}
    body = {"grant_type": "client_credentials",
            "appkey": ka.getTREnv().my_app,
            "secretkey": ka.getTREnv().my_sec}
    PATH = "oauth2/Approval"
    URL = f"{url}/{PATH}"
    res = requests.post(URL, headers=headers, data=json.dumps(body))
    approval_key = res.json()["approval_key"]
    return approval_key


_connect_key = get_approval()  # websocker 연결Key
_iv = None  # for 복호화
_ekey = None  # for 복호화
executed_df = pd.DataFrame(data=None, columns=contract_cols)  # 체결통보 저장용 DF


# added_data 는 종목코드(실시간체결, 실시간호가) 또는 HTS_ID(체결통보)
def _build_message(app_key, tr_id, added_data, tr_type='1'):
    _h = {
        "approval_key": app_key,
        "custtype": 'P',
        "tr_type": tr_type,
        "content-type": "utf-8"
    }
    _inp = {
        "tr_id": tr_id,
        "tr_key": added_data
    }
    _b = {
        "input": _inp
    }
    _data = {
        "header": _h,
        "body": _b
    }

    d1 = json.dumps(_data)

    return d1


# sub_data 는 종목코드(실시간체결, 실시간호가) 또는 HTS_ID(실시간 계좌체결발생통보)
def subscribe(ws, sub_type, app_key, sub_data):  # 세션 종목코드(실시간체결, 실시간호가) 등록
    ws.send(_build_message(app_key, sub_type, sub_data), websocket.ABNF.OPCODE_TEXT)

    time.sleep(.1)


def unsubscribe(ws, sub_type, app_key, sub_data): # 세션 종목코드(실시간체결, 실시간호가) 등록해제
    ws.send(_build_message(app_key, sub_type, sub_data, '2'), websocket.ABNF.OPCODE_TEXT)

    time.sleep(.1)


# streaming data 를 이용해 주어진 bar 크기(예: 1분, 5분 등)의 OHLC(x분봉) 데이터프레임을 반환한다.
# 이때 streamign data 는 websocket client 가 시작한 다음부터 지금까지의 해당 종목의 가격 정보를 의미한다.
# ** 동시호가 시간은 OHLC data 가 모두 NA 가 된다.
def getStreamdDF(stock_code, bar_sz='1Min'):
    df3 = contract_sub_df.get(stock_code).copy()
    df3 = df3.set_index(['TICK_HOUR'])
    df3['LAST_PRICE'] = pd.to_numeric(df3['LAST_PRICE'], errors='coerce').convert_dtypes()
    df3 = df3['LAST_PRICE'].resample(bar_sz).ohlc()

    return df3

# 수신데이터 파싱
def _dparse(data):
    global executed_df
    d1 = data.split("|")
    dp_ = None

    hcols = []

    if len(d1) >= 4:
        tr_id = d1[1]
        if tr_id == KIS_WSReq.CONTRACT:  # 실시간체결
            hcols = contract_cols
        elif tr_id == KIS_WSReq.BID_ASK: # 해외선물옵션 실시간호가
            hcols = bid_ask_cols
        elif tr_id == KIS_WSReq.ORDERNOTICE:  # 주문내역발생통보
            hcols = ordernotice_cols
        elif tr_id == KIS_WSReq.CCLDNOTICE:  # 체결내역발생통보
            hcols = ccldnotice_cols
        else:
            pass

        if tr_id in (KIS_WSReq.CONTRACT, KIS_WSReq.BID_ASK):  # 실시간체결, 실시간호가
            dp_ = pd.read_csv(StringIO(d1[3]), header=None, sep='^', names=hcols, dtype=object)  # 수신데이터 parsing
            
            print(dp_)  # 실시간체결, 실시간호가 수신 데이터 파싱 결과 확인
            
            dp_['TICK_HOUR'] = _today__ + dp_['TICK_HOUR']    # 수신시간
            dp_['TICK_HOUR'] = pd.to_datetime(dp_['TICK_HOUR'], format='%Y%m%d%H%M%S', errors='coerce')
        else:  # 실시간 계좌체결발생통보는 암호화되어서 수신되므로 복호화 과정이 필요
            dp_ = pd.read_csv(StringIO(aes_cbc_base64_dec(_ekey, _iv, d1[3])), header=None, sep='^', names=hcols,  # 수신데이터 parsing 및 복호화
                              dtype=object)

            print(dp_)  # 실시간 계좌체결발생통보 수신 파싱 결과 확인

            if __DEBUG__: print(f'***EXECUTED CCLDNOTICE [{dp_.to_string(header=False, index=False)}]')

        if tr_id == KIS_WSReq.CONTRACT: # 실시간 체결
            if __DEBUG__: print(dp_.to_string(header=False, index=False))
            stock_code = dp_[dp_.columns[0]].values.tolist()[0]
            df2_ = dp_[reserved_cols]
            # dft_ = pd.concat([contract_sub_df.get(stock_code), df2_], axis=0, ignore_index=True)
            # 선택된 열이 비어 있거나 모든 값이 NA인지 확인
            selected_df = contract_sub_df.get(stock_code)
            if selected_df is not None and not selected_df.dropna().empty:
                dft_ = pd.concat([selected_df, df2_], axis=0, ignore_index=True)
            else:
                dft_ = df2_
            contract_sub_df[stock_code] = dft_
            ######### 이 부분에서 로직을 적용한 후 매수/매도를 수행하면 될 듯!!

            val1 =  dp_['LAST_PRICE'].tolist()[0]
            tr_plans[stock_code].push(float(val1))  # 이동평균값 활용
            # tr_plans[stock_code].eval()         # RSI(Relative Strength Index, 상대강도지수)라는 주가 지표 계산 활용
            stock_df =  dp_['SERIES_CD'].tolist()[0]   # 종목코드
            # [해외선물옵션] 주문/계좌 > 해외선물옵션 주문가능조회 (선물옵션구분fuop_dvsn)
            # 선물옵션구분 00:전체 / 01:선물 / 02:옵션
            rt_data = kb.get_overseasfuopt_inquire_psamount(itm_no=stock_df, dvsn="00", pric=0, ordyn="")
            ord_qty = rt_data.loc[0, 'fm_new_ord_psbl_qty']  # 신규주문가능수량  총주문가능수량(fm_tot_ord_psbl_qty), 시장가총주문가능수량(fm_mkpr_tot_ord_psbl_qty)
            print("[주문가능수량!] : " + ord_qty)

            ###########################################################
            # [해외선물옵션] 주문/계좌 > 해외선물옵션주문 (종목번호<6자리 5자리> + 매수매도구분ord_dv + 가격구분dvsn + 주문수량qty + 주문가격limt_pric + 주문가격stop_pric)
            # 매수매도구분ord_dv  01 : 매도, 02 : 매수   # 가격구분dvsn : 	1.지정, 2. 시장, 3. STOP, 4 S/L
            # 주문가격limt_pric : 지정가인 경우 가격 입력 * 시장가, STOP주문인 경우, 빈칸("") 입력
            # 주문가격stop_pric : STOP 주문 가격 입력   * 시장가, 지정가인 경우, 빈칸("") 입력
            # rt_data = kb.get_overseasfuopt_order(itm_no=stock_df, ord_dv="02", dvsn="1", qty=ord_qty, limt_pric=val1, stop_pric=0)
            # print(rt_data.ORD_DT + "+" + rt_data.ODNO) # 주문일자+주문접수번호

            print("매수/매도 조건 주문 : " + val1)
            ###########################################################

        elif tr_id == KIS_WSReq.CCLDNOTICE:  # 체결통보의 경우, 일단 executed_df 에만 저장해 둠
            if __DEBUG__: print(dp_.to_string(header=False, index=False))
            executed_df = pd.concat([executed_df, dp_], axis=0, ignore_index=True)

        else:
            pass
    else:
        print("Data length error...{data}")


def _get_sys_resp(data):
    global _iv
    global _ekey

    isPingPong = False
    isUnSub = False
    isOk = False
    tr_msg = None
    tr_key = None

    rdic = json.loads(data)

    tr_id = rdic['header']['tr_id']
    if tr_id != "PINGPONG": tr_key = rdic['header']['tr_key']
    if rdic.get("body", None) is not None:
        isOk = True if rdic["body"]["rt_cd"] == "0" else False
        tr_msg = rdic["body"]["msg1"]
        # 복호화를 위한 key 를 추출
        if 'output' in rdic["body"]:
            _iv = rdic["body"]["output"]["iv"]
            _ekey = rdic["body"]["output"]["key"]
        isUnSub = True if tr_msg[:5] == "UNSUB" else False
    else:
        isPingPong = True if tr_id == "PINGPONG" else False

    nt2 = namedtuple('SysMsg', ['isOk', 'tr_id', 'tr_key', 'isUnSub', 'isPingPong'])
    d = {
        'isOk': isOk,
        'tr_id': tr_id,
        'tr_key': tr_key,
        'isUnSub': isUnSub,
        'isPingPong': isPingPong
    }

    return nt2(**d)


def on_data(ws, data, resp_type, data_continu):
    # print(f"On data => {resp_type}, {data_continu}, {data}") #return only 1, True
    pass


def on_message(ws, data):
    if data[0] in ('0', '1'):  # 실시간체결 or 실시간호가
        _dparse(data)
    else:  # system message or PINGPONG
        rsp = _get_sys_resp(data)
        if rsp.isPingPong:
            ws.send(data, websocket.ABNF.OPCODE_PING)
        else:
            if (not rsp.isUnSub and rsp.tr_id == KIS_WSReq.CONTRACT):
                contract_sub_df[rsp.tr_key] = pd.DataFrame(columns=reserved_cols)

                ########################################################################
                #### 이 부분에서 전략을 수행할 class 를 등록한다.
                #### 실제 주문 실행은 _dparse 함수에서 처리
                tr_plans[rsp.tr_key] = BasicPlan(rsp.tr_key)   # 이동 평균선 계산 (웹소켓 프로그램 실행시 수집된 데이터만 반영)
                # tr_plans[rsp.tr_key] = RSI_ST(rsp.tr_key)    # RSI(Relative Strength Index, 상대강도지수)라는 주가 지표 계산
                ########################################################################

            elif (rsp.isUnSub):
                del (contract_sub_df[rsp.tr_key])
            else:
                print(rsp)


def on_error(ws, error):
    print('error=', error)

def on_close(ws, status_code, close_msg):
    print('on_close close_status_code=', status_code, " close_msg=", close_msg)


def on_open(ws):
    # stocks 에는 40개까지만 가능
    stocks = ('6EV24', '6EU24', 'ESU24', 'OESU24 C5450', 'ONQU24 C18900', 'OESU24 C6000')   # 해외선물옵션
    for scode in stocks:
        subscribe(ws, KIS_WSReq.BID_ASK, _connect_key, scode)       # 실시간 호가(미국)
        subscribe(ws, KIS_WSReq.CONTRACT, _connect_key, scode)      # 실시간 체결

    # unsubscribe(ws, KIS_WSReq.CONTRACT, _connect_key, "RBAQAAPL")   #실시간 체결 연결해제
    # subscribe(ws, KIS_WSReq.CONTRACT, _connect_key, "RBAQAAPL")     #실시간 체결 연결등록
    # unsubscribe(ws, KIS_WSReq.BID_USA, _connect_key, "RBAQAAPL")    #실시간 호가(미국) 연결해제
    # subscribe(ws, KIS_WSReq.BID_USA, _connect_key, "RBAQAAPL")      #실시간 호가(미국) 연결등록
    # 실시간 계좌체결발생통보를 등록한다. 계좌체결발생통보 결과는 executed_df 에 저장된다.
    #subscribe(ws, KIS_WSReq.ORDERNOTICE, _connect_key, "HTS ID 입력")        # "HTS ID 입력 하세요" 계좌주문내역발생통보
    subscribe(ws, KIS_WSReq.CCLDNOTICE, _connect_key, "HTS ID 입력")  # "HTS ID 입력 하세요" 계좌체결내역발생통보


ws = websocket.WebSocketApp("ws://ops.koreainvestment.com:21000/tryitout",
                            on_open=on_open, on_message=on_message, on_error=on_error, on_data=on_data)

ws.run_forever() # 실시간 웹소켓 연결 작동
