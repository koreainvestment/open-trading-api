# 국내주식 실시간 websocket sample
import websocket

import kis_auth as ka
import kis_domstk as kb

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
    BID_ASK = 'H0STASP0'   # 실시간 국내주식 호가
    CONTRACT = 'H0STCNT0'  # 실시간 국내주식 체결
    NOTICE = 'H0STCNI0'    # 실시간 계좌체결발생통보


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
        dftt['STCK_PRPR'] = pd.to_numeric(dftt['STCK_PRPR'], errors='coerce').convert_dtypes()
        np_closes = np.array(dftt['STCK_PRPR'], dtype=np.float64)
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

# 실시간 국내주식 계좌체결통보 복호화를 위한 부분-start
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


# 실시간 국내주식 계좌체결통보 복호화를 위한 부분 - end


contract_sub_df = dict()  # 실시간 국내주식 체결 결과를 종목별로 저장하기 위한 container
tr_plans = dict()         # 실시간 국내주식 체결 값에 따라 무언가를 수행할 Class 를 저장하기 위한 container

reserved_cols = ['TICK_HOUR', 'STCK_PRPR', 'ACML_VOL']  # 실시간 국내주식 체결 중 사용할 column 만 추출하기 위한 column 정의

# 실시간 국내주식체결 column header
contract_cols = ['MKSC_SHRN_ISCD',
                 'TICK_HOUR',  # pandas time conversion 편의를 위해 이 필드만 이름을 통일한다
                 'STCK_PRPR',  # 현재가
                 'PRDY_VRSS_SIGN',  # 전일 대비 부호
                 'PRDY_VRSS',  # 전일 대비
                 'PRDY_CTRT',  # 전일 대비율
                 'WGHN_AVRG_STCK_PRC',  # 가중 평균 주식 가격
                 'STCK_OPRC',  # 시가
                 'STCK_HGPR',  # 고가
                 'STCK_LWPR',  # 저가
                 'ASKP1',  # 매도호가1
                 'BIDP1',  # 매수호가1
                 'CNTG_VOL',  # 체결 거래량
                 'ACML_VOL',  # 누적 거래량
                 'ACML_TR_PBMN',  # 누적 거래 대금
                 'SELN_CNTG_CSNU',  # 매도 체결 건수
                 'SHNU_CNTG_CSNU',  # 매수 체결 건수
                 'NTBY_CNTG_CSNU',  # 순매수 체결 건수
                 'CTTR',  # 체결강도
                 'SELN_CNTG_SMTN',  # 총 매도 수량
                 'SHNU_CNTG_SMTN',  # 총 매수 수량
                 'CCLD_DVSN',  # 체결구분 (1:매수(+), 3:장전, 5:매도(-))
                 'SHNU_RATE',  # 매수비율
                 'PRDY_VOL_VRSS_ACML_VOL_RATE',  # 전일 거래량 대비 등락율
                 'OPRC_HOUR',  # 시가 시간
                 'OPRC_VRSS_PRPR_SIGN',  # 시가대비구분
                 'OPRC_VRSS_PRPR',  # 시가대비
                 'HGPR_HOUR',
                 'HGPR_VRSS_PRPR_SIGN',
                 'HGPR_VRSS_PRPR',
                 'LWPR_HOUR',
                 'LWPR_VRSS_PRPR_SIGN',
                 'LWPR_VRSS_PRPR',
                 'BSOP_DATE',  # 영업 일자
                 'NEW_MKOP_CLS_CODE',  # 신 장운영 구분 코드
                 'TRHT_YN',
                 'ASKP_RSQN1',
                 'BIDP_RSQN1',
                 'TOTAL_ASKP_RSQN',
                 'TOTAL_BIDP_RSQN',
                 'VOL_TNRT',  # 거래량 회전율
                 'PRDY_SMNS_HOUR_ACML_VOL',  # 전일 동시간 누적 거래량
                 'PRDY_SMNS_HOUR_ACML_VOL_RATE',  # 전일 동시간 누적 거래량 비율
                 'HOUR_CLS_CODE',  # 시간 구분 코드(0 : 장중 )
                 'MRKT_TRTM_CLS_CODE',
                 'VI_STND_PRC']

# 실시간 국내주식호가 column eader
bid_ask_cols = ['MKSC_SHRN_ISCD',
                'TICK_HOUR',  # pandas time conversion 편의를 위해 이 필드만 이름을 통일한다
                'HOUR_CLS_CODE',  # 시간 구분 코드(0 : 장중 )
                'ASKP1',  # 매도호가1
                'ASKP2',
                'ASKP3',
                'ASKP4',
                'ASKP5',
                'ASKP6',
                'ASKP7',
                'ASKP8',
                'ASKP9',
                'ASKP10',
                'BIDP1',  # 매수호가1
                'BIDP2',
                'BIDP3',
                'BIDP4',
                'BIDP5',
                'BIDP6',
                'BIDP7',
                'BIDP8',
                'BIDP9',
                'BIDP10',
                'ASKP_RSQN1',  # 매도호가 잔량1
                'ASKP_RSQN2',
                'ASKP_RSQN3',
                'ASKP_RSQN4',
                'ASKP_RSQN5',
                'ASKP_RSQN6',
                'ASKP_RSQN7',
                'ASKP_RSQN8',
                'ASKP_RSQN9',
                'ASKP_RSQN10',
                'BIDP_RSQN1',  # 매수호가 잔량1
                'BIDP_RSQN2',
                'BIDP_RSQN3',
                'BIDP_RSQN4',
                'BIDP_RSQN5',
                'BIDP_RSQN6',
                'BIDP_RSQN7',
                'BIDP_RSQN8',
                'BIDP_RSQN9',
                'BIDP_RSQN10',
                'TOTAL_ASKP_RSQN',  # 총 매도호가 잔량
                'TOTAL_BIDP_RSQN',  # 총 매수호가 잔량
                'OVTM_TOTAL_ASKP_RSQN',
                'OVTM_TOTAL_BIDP_RSQN',
                'ANTC_CNPR',
                'ANTC_CNQN',
                'ANTC_VOL',
                'ANTC_CNTG_VRSS',
                'ANTC_CNTG_VRSS_SIGN',
                'ANTC_CNTG_PRDY_CTRT',
                'ACML_VOL',  # 누적 거래량
                'TOTAL_ASKP_RSQN_ICDC',
                'TOTAL_BIDP_RSQN_ICDC',
                'OVTM_TOTAL_ASKP_ICDC',
                'OVTM_TOTAL_BIDP_ICDC',
                'STCK_DEAL_CLS_CODE']

# 실시간 계좌체결발생통보 column header
notice_cols = ['CUST_ID',  # HTS ID
               'ACNT_NO',
               'ODER_NO',  # 주문번호
               'OODER_NO',  # 원주문번호
               'SELN_BYOV_CLS',  # 매도매수구분
               'RCTF_CLS',  # 정정구분
               'ODER_KIND',  # 주문종류(00 : 지정가,01 : 시장가,02 : 조건부지정가)
               'ODER_COND',  # 주문조건
               'STCK_SHRN_ISCD',  # 주식 단축 종목코드
               'CNTG_QTY',  # 체결 수량(체결통보(CNTG_YN=2): 체결 수량, 주문·정정·취소·거부 접수 통보(CNTG_YN=1): 주문수량의미)
               'CNTG_UNPR',  # 체결단가
               'STCK_CNTG_HOUR',  # 주식 체결 시간
               'RFUS_YN',  # 거부여부(0 : 승인, 1 : 거부)
               'CNTG_YN',  # 체결여부(1 : 주문,정정,취소,거부,, 2 : 체결 (★ 체결만 볼 경우 2번만 ))
               'ACPT_YN',  # 접수여부(1 : 주문접수, 2 : 확인 )
               'BRNC_NO',  # 지점
               'ODER_QTY',  # 주문수량
               'ACNT_NAME',  # 계좌명
               'ORD_COND_PRC',  # 호가조건가격 (스톱지정가 시 표시)
               'ORD_EXG_GB',  # 주문거래소 구분 (1:KRX, 2:NXT, 3:SOR-KRX, 4:SOR-NXT)
               'POPUP_YN',  # 실시간체결창 표시여부 (Y/N)
               'FILLER',  # 필러
               'CRDT_CLS',  # 신용구분
               'CRDT_LOAN_DATE',  # 신용대출일자
               'CNTG_ISNM40',  # 체결종목명40
               'ODER_PRC'  # 주문가격
               ]


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
    df3['STCK_PRPR'] = pd.to_numeric(df3['STCK_PRPR'], errors='coerce').convert_dtypes()
    df3 = df3['STCK_PRPR'].resample(bar_sz).ohlc()

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
        elif tr_id == KIS_WSReq.BID_ASK: # 실시간호가
            hcols = bid_ask_cols
        elif tr_id == KIS_WSReq.NOTICE:  # 계좌체결통보
            hcols = notice_cols
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

            if __DEBUG__: print(f'***EXECUTED NOTICE [{dp_.to_string(header=False, index=False)}]')

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

            val1 =  dp_['STCK_PRPR'].tolist()[0]
            tr_plans[stock_code].push(int(val1))  # 이동평균값 활용
            # tr_plans[stock_code].eval()         # RSI(Relative Strength Index, 상대강도지수)라는 주가 지표 계산 활용

            # [국내주식] 주문/계좌 > 매수가능조회 (종목번호 5자리 + 종목단가) REST API
            rt_data = kb.get_inquire_psbl_order(pdno=stock_code, ord_unpr=val1)
            ord_qty = rt_data.loc[0, 'nrcvb_buy_qty']  # nrcvb_buy_qty	미수없는매수수량
            print("[미수없는매수주문가능수량!] : " + ord_qty)

            # 국내주식 현금 주문
            # rt_data = kb.get_order_cash(ord_dv="buy",itm_no=stock_code, qty=ord_qty, unpr=val1)
            # print(rt_data.KRX_FWDG_ORD_ORGNO + "+" + rt_data.ODNO + "+" + rt_data.ORD_TMD) # 주문접수조직번호+주문접수번호+주문시각
            print("매수/매도 조건 주문 : " + val1)

            #########################################################

        elif tr_id == KIS_WSReq.NOTICE:  # 체결통보의 경우, 일단 executed_df 에만 저장해 둠
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
    stocks = ('009540', '012630', '052300', '089860', '218410', '330590', '357550', '419080', '348370')
    for scode in stocks:
        subscribe(ws, KIS_WSReq.BID_ASK, _connect_key, scode)       # 실시간 호가
        subscribe(ws, KIS_WSReq.CONTRACT, _connect_key, scode)      # 실시간 체결

    # unsubscribe(ws, KIS_WSReq.CONTRACT, _connect_key, "005930")   #실시간 체결 해제
    # subscribe(ws, KIS_WSReq.BID_ASK, _connect_key, "005930")      #실시간 호가
    # 실시간 계좌체결발생통보를 등록한다. 계좌체결발생통보 결과는 executed_df 에 저장된다.
    subscribe(ws, KIS_WSReq.NOTICE, _connect_key, "HTS ID 입력") # HTS ID 입력


ws = websocket.WebSocketApp("ws://ops.koreainvestment.com:21000/tryitout",
                            on_open=on_open, on_message=on_message, on_error=on_error, on_data=on_data)

ws.run_forever() # 실시간 웹소켓 연결 작동
