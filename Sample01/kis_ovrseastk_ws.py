# 해외주식 실시간 websocket sample
import websocket

import kis_auth as ka
import kis_ovrseastk as kb

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
    BID_USA = 'HDFSASP0'   # 해외주식 실시간지연호가(미국)
    BID_ASA = 'HDFSASP1'   # 해외주식 실시간지연호가(아시아)
    CONTRACT = 'HDFSCNT0'  # 해외주식 실시간지연 체결가
    NOTICE = 'H0GSCNI0'    # 실시간 해외주식 체결통보

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
        dftt['LAST'] = pd.to_numeric(dftt['LAST'], errors='coerce').convert_dtypes()
        np_closes = np.array(dftt['LAST'], dtype=np.float64)
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
reserved_cols = ['TICK_HOUR', 'LAST']  # 실시간 해외주식 체결 중 사용할 column 만 추출하기 위한 column 정의

# 해외주식 실시간지연체결가 column header
contract_cols = ['RSYM',	# 실시간종목코드
                'SYMB',	# 종목코드
                'ZDIV',	# 수수점자리수
                'TYMD',	# 현지영업일자
                'XYMD',	# 현지일자
                'XHMS',	# 현지시간
                'KYMD',	# 한국일자
                'TICK_HOUR',  # pandas time conversion 편의를 위해 이 필드만 이름을 통일한다 'KHMS' 한국시간
                'OPEN',	# 시가
                'HIGH',	# 고가
                'LOW',	# 저가
                'LAST',	# 현재가
                'SIGN',	# 대비구분
                'DIFF',	# 전일대비
                'RATE',	# 등락율
                'PBID',	# 매수호가
                'PASK',	# 매도호가
                'VBID',	# 매수잔량
                'VASK',	# 매도잔량
                'EVOL',	# 체결량
                'TVOL',	# 거래량
                'TAMT',	# 거래대금
                'BIVL',	# 매도체결량
                'ASVL',	# 매수체결량
                'STRN',	# 체결강도
                'MTYP']	# 시장구분 1:장중,2:장전,3:장후

# 실시간 해외주식호가(미국) column eader
bid_usa_cols = ['RSYM',	 #실시간종목코드
                'SYMB',	 # 종목코드
                'ZDIV',	 # 소숫점자리수
                'XYMD',	 # 현지일자
                'XHMS',	 # 현지시간
                'KYMD',	 # 한국일자
                'TICK_HOUR',  # pandas time conversion 편의를 위해 이 필드만 이름을 통일한다 'KHMS' 한국시간
                'BVOL',	 # 매수총잔량
                'AVOL',	 # 매도총잔량
                'BDVL',	 # 매수총잔량대비
                'ADVL',	 # 매도총잔량대비
                'PBID1', # 매수호가1
                'PASK1', # 매도호가1
                'VBID1', # 매수잔량1
                'VASK1', # 매도잔량1
                'DBID1', # 매수잔량대비1
                'DASK1' ] # 매도잔량대비1

# 실시간 해외주식호가(아시아) column eader
bid_asa_cols = ['RSYM',	#실시간종목코드
                'SYMB',	#종목코드
                'ZDIV',	#소수점자리수
                'XYMD',	#현지일자
                'XHMS',	#현지시간
                'KYMD',	#한국일자
                'TICK_HOUR',  # pandas time conversion 편의를 위해 이 필드만 이름을 통일한다 'KHMS' 한국시간
                'BVOL',	#매수총잔량
                'AVOL',	#매도총잔량
                'BDVL',	#매수총잔량대비
                'ADVL',	#매도총잔량대비
                'PBID1',	#매수호가1
                'PASK1',	#매도호가1
                'VBID1',	#매수잔량1
                'VASK1',	#매도잔량1
                'DBID1',	#매수잔량대비1
                'DASK1']	#매도잔량대비1


# 실시간 계좌체결발생통보 column header
notice_cols = ['CUST_ID',  # HTS ID
               'ACNT_NO',
               'ODER_NO',  # 주문번호
               'OODER_NO',  # 원주문번호
               'SELN_BYOV_CLS',  # 매도매수구분
               'RCTF_CLS',  # 정정구분
               'ODER_KIND2',  # 주문종류2(1:시장가 2:지정자 6:단주시장가 7:단주지정가 A:MOO B:LOO C:MOC D:LOC)
               'STCK_SHRN_ISCD',  # 주식 단축 종목코드
               'CNTG_QTY',  # 체결 수량   - 주문통보의 경우 해당 위치에 주문수량이 출력, - 체결통보인 경우 해당 위치에 체결수량이 출력
               'CNTG_UNPR',  # 체결단가  ※ 주문통보 시에는 주문단가가, 체결통보 시에는 체결단가가 수신 됩니다. ※ 체결단가의 경우, 국가에 따라 소수점 생략 위치가 상이합니다.
                             # 미국 4 일본 1 중국 3 홍콩 3 베트남 0 EX) 미국 AAPL(현재가 : 148.0100)의 경우 001480100으로 체결단가가 오는데, 4번째 자리에 소수점을 찍어 148.01로 해석하시면 됩니다.
               'STCK_CNTG_HOUR',  # 주식 체결 시간
               'RFUS_YN',  # 거부여부(0 : 승인, 1 : 거부)
               'CNTG_YN',  # 체결여부(1 : 주문,정정,취소,거부,, 2 : 체결 (★ 체결만 볼 경우 2번만 ))
               'ACPT_YN',  # 접수여부(1:주문접수 2:확인 3:취소(FOK/IOC))
               'BRNC_NO',  # 지점
               'ODER_QTY',  # 주문수량  - 주문통보인 경우 해당 위치 미출력 (주문통보의 주문수량은 CNTG_QTY 위치에 출력) - 체결통보인 경우 해당 위치에 주문수량이 출력
               'ACNT_NAME',  # 계좌명
               'CNTG_ISNM',  # 체결종목명
               'ODER_COND',	# 해외종목구분
               'DEBT_GB',  # 담보유형코드  10:현금 15:해외주식담보대출
               'DEBT_DATE']  # 담보대출일자  대출일(YYYYMMDD)


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
    df3['LAST'] = pd.to_numeric(df3['LAST'], errors='coerce').convert_dtypes()
    df3 = df3['LAST'].resample(bar_sz).ohlc()

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
        elif tr_id == KIS_WSReq.BID_USA: # 해외주식 실시간지연호가(미국)
            hcols = bid_usa_cols
        elif tr_id == KIS_WSReq.BID_ASA: # 해외주식 실시간지연호가(아시아)
            hcols = bid_asa_cols
        elif tr_id == KIS_WSReq.NOTICE:  # 계좌체결통보
            hcols = notice_cols
        else:
            pass

        if tr_id in (KIS_WSReq.CONTRACT, KIS_WSReq.BID_USA, KIS_WSReq.BID_ASA):  # 실시간체결, 실시간지연호가(미국), 실시간지연호가(아시아)
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

            val1 =  dp_['LAST'].tolist()[0]
            tr_plans[stock_code].push(float(val1))  # 이동평균값 활용
            # tr_plans[stock_code].eval()         # RSI(Relative Strength Index, 상대강도지수)라는 주가 지표 계산 활용

            excg_df = excg_dict[stock_code[1:4]]  # 해외거래소코드(3자리) 주문API 사용가능 해외거래소코드(4자리) 변환
            stock_df =  dp_['SYMB'].tolist()[0]   # 종목코드
            # [국내주식] 주문/계좌 > 매수가능조회 (종목번호 5자리 + 종목단가) REST API
            #rt_data = kb.get_inquire_psbl_order(pdno=stock_code, ord_unpr=val1, itm_no="TSLA")
            rt_data = kb.get_overseas_inquire_psamount(excg=excg_df, itm_no=stock_df)
            ord_qty = rt_data.loc[0, 'ord_psbl_qty']  # ord_psbl_qty	주문가능수량 또는 외화인 경우 max_ord_psbl_qty	최대주문가능수량
            print("[주문가능수량!] : " + ord_qty)

            ###########################################################
            # 해외주식(미국) 현금 주문
            # rt_data = kb.get_overseas_order(ord_dv="buy", excg_cd=excg_df, itm_no=stock_df, qty=1, unpr=123.3)
            # print(rt_data.KRX_FWDG_ORD_ORGNO + "+" + rt_data.ODNO + "+" + rt_data.ORD_TMD) # 주문접수조직번호+주문접수번호+주문시각
            # 해외주식(미국) 현금 주문(주간)
            # rt_data = kb.get_overseas_daytime_order(ord_dv="buy", excg_cd=excg_df, itm_no=stock_df, qty=1, unpr=123.3)
            # print(rt_data.KRX_FWDG_ORD_ORGNO + "+" + rt_data.ODNO + "+" + rt_data.ORD_TMD) # 주문접수조직번호+주문접수번호+주문시각
            print("매수/매도 조건 주문 : " + val1)
            ###########################################################

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
    stocks = ('RBAQAAPL', 'RBAQTSLA', 'RBAQAMZN', 'RBAQNVDA', 'RBAQINTC', 'RBAQMSFT')   # 미국주식 주간거래
    #stocks = ('DNASAAPL', 'DNASTSLA', 'DNASAMZN', 'DNASNVDA', 'DNASINTC', 'DNASMSFT')  # 미국주식 야간거래(정규시장)
    for scode in stocks:
        subscribe(ws, KIS_WSReq.BID_USA, _connect_key, scode)       # 실시간 호가(미국)
        #subscribe(ws, KIS_WSReq.BID_USA, _connect_key, scode)      # 실시간 호가(아시아)
        subscribe(ws, KIS_WSReq.CONTRACT, _connect_key, scode)      # 실시간 체결

    # unsubscribe(ws, KIS_WSReq.CONTRACT, _connect_key, "RBAQAAPL")   #실시간 체결 연결해제
    # subscribe(ws, KIS_WSReq.CONTRACT, _connect_key, "RBAQAAPL")     #실시간 체결 연결등록
    # unsubscribe(ws, KIS_WSReq.BID_USA, _connect_key, "RBAQAAPL")    #실시간 호가(미국) 연결해제
    # subscribe(ws, KIS_WSReq.BID_USA, _connect_key, "RBAQAAPL")      #실시간 호가(미국) 연결등록
    # 실시간 계좌체결발생통보를 등록한다. 계좌체결발생통보 결과는 executed_df 에 저장된다.
    subscribe(ws, KIS_WSReq.NOTICE, _connect_key, "HTS ID 입력") # HTS ID 입력 계좌체결발생통보


ws = websocket.WebSocketApp("ws://ops.koreainvestment.com:21000/tryitout",
                            on_open=on_open, on_message=on_message, on_error=on_error, on_data=on_data)

ws.run_forever() # 실시간 웹소켓 연결 작동
