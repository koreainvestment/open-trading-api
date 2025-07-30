# -*- coding: utf-8 -*-
# ====|  (REST) 접근 토큰 / (Websocket) 웹소켓 접속키 발급 에 필요한 API 호출 샘플 아래 참고하시기 바랍니다.  |=====================
# ====|  API 호출 공통 함수 포함                                  |=====================

import asyncio
import copy
import json
import logging
import os
import time
from base64 import b64decode
from collections import namedtuple
from collections.abc import Callable
from datetime import datetime
from io import StringIO

import pandas as pd

# pip install requests (패키지설치)
import requests

# 웹 소켓 모듈을 선언한다.
import websockets

# pip install PyYAML (패키지설치)
import yaml
from Crypto.Cipher import AES

# pip install pycryptodome
from Crypto.Util.Padding import unpad

clearConsole = lambda: os.system("cls" if os.name in ("nt", "dos") else "clear")

key_bytes = 32
config_root = os.path.join(os.path.expanduser("~"), "KIS", "config")
# config_root = "$HOME/KIS/config/"  # 토큰 파일이 저장될 폴더, 제3자가 찾기 어렵도록 경로 설정하시기 바랍니다.
# token_tmp = config_root + 'KIS000000'  # 토큰 로컬저장시 파일 이름 지정, 파일이름을 토큰값이 유추가능한 파일명은 삼가바랍니다.
# token_tmp = config_root + 'KIS' + datetime.today().strftime("%Y%m%d%H%M%S")  # 토큰 로컬저장시 파일명 년월일시분초
token_tmp = os.path.join(
    config_root, f"KIS{datetime.today().strftime("%Y%m%d")}"
)  # 토큰 로컬저장시 파일명 년월일

# 접근토큰 관리하는 파일 존재여부 체크, 없으면 생성
if os.path.exists(token_tmp) == False:
    f = open(token_tmp, "w+")

# 앱키, 앱시크리트, 토큰, 계좌번호 등 저장관리, 자신만의 경로와 파일명으로 설정하시기 바랍니다.
# pip install PyYAML (패키지설치)
with open(os.path.join(config_root, "kis_devlp.yaml"), encoding="UTF-8") as f:
    _cfg = yaml.load(f, Loader=yaml.FullLoader)

_TRENV = tuple()
_last_auth_time = datetime.now()
_autoReAuth = False
_DEBUG = False
_isPaper = False
_smartSleep = 0.1

# 기본 헤더값 정의
_base_headers = {
    "Content-Type": "application/json",
    "Accept": "text/plain",
    "charset": "UTF-8",
    "User-Agent": _cfg["my_agent"],
}


# 토큰 발급 받아 저장 (토큰값, 토큰 유효시간,1일, 6시간 이내 발급신청시는 기존 토큰값과 동일, 발급시 알림톡 발송)
def save_token(my_token, my_expired):
    # print(type(my_expired), my_expired)
    valid_date = datetime.strptime(my_expired, "%Y-%m-%d %H:%M:%S")
    # print('Save token date: ', valid_date)
    with open(token_tmp, "w", encoding="utf-8") as f:
        f.write(f"token: {my_token}\n")
        f.write(f"valid-date: {valid_date}\n")


# 토큰 확인 (토큰값, 토큰 유효시간_1일, 6시간 이내 발급신청시는 기존 토큰값과 동일, 발급시 알림톡 발송)
def read_token():
    try:
        # 토큰이 저장된 파일 읽기
        with open(token_tmp, encoding="UTF-8") as f:
            tkg_tmp = yaml.load(f, Loader=yaml.FullLoader)

        # 토큰 만료 일,시간
        exp_dt = datetime.strftime(tkg_tmp["valid-date"], "%Y-%m-%d %H:%M:%S")
        # 현재일자,시간
        now_dt = datetime.today().strftime("%Y-%m-%d %H:%M:%S")

        # print('expire dt: ', exp_dt, ' vs now dt:', now_dt)
        # 저장된 토큰 만료일자 체크 (만료일시 > 현재일시 인경우 보관 토큰 리턴)
        if exp_dt > now_dt:
            return tkg_tmp["token"]
        else:
            # print('Need new token: ', tkg_tmp['valid-date'])
            return None
    except Exception:
        # print('read token error: ', e)
        return None


# 토큰 유효시간 체크해서 만료된 토큰이면 재발급처리
def _getBaseHeader():
    if _autoReAuth:
        reAuth()
    return copy.deepcopy(_base_headers)


# 가져오기 : 앱키, 앱시크리트, 종합계좌번호(계좌번호 중 숫자8자리), 계좌상품코드(계좌번호 중 숫자2자리), 토큰, 도메인
def _setTRENV(cfg):
    nt1 = namedtuple(
        "KISEnv",
        ["my_app", "my_sec", "my_acct", "my_prod", "my_htsid", "my_token", "my_url", "my_url_ws"],
    )
    d = {
        "my_app": cfg["my_app"],  # 앱키
        "my_sec": cfg["my_sec"],  # 앱시크리트
        "my_acct": cfg["my_acct"],  # 종합계좌번호(8자리)
        "my_prod": cfg["my_prod"],  # 계좌상품코드(2자리)
        "my_htsid": cfg["my_htsid"],  # HTS ID
        "my_token": cfg["my_token"],  # 토큰
        "my_url": cfg[
            "my_url"
        ],  # 실전 도메인 (https://openapi.koreainvestment.com:9443)
        "my_url_ws": cfg["my_url_ws"],
    }  # 모의 도메인 (https://openapivts.koreainvestment.com:29443)

    # print(cfg['my_app'])
    global _TRENV
    _TRENV = nt1(**d)


def isPaperTrading():  # 모의투자 매매
    return _isPaper


# 실전투자면 'prod', 모의투자면 'vps'를 셋팅 하시기 바랍니다.
def changeTREnv(token_key, svr="prod", product=_cfg["my_prod"]):
    cfg = dict()

    global _isPaper
    if svr == "prod":  # 실전투자
        ak1 = "my_app"  # 실전투자용 앱키
        ak2 = "my_sec"  # 실전투자용 앱시크리트
        _isPaper = False
        _smartSleep = 0.05
    elif svr == "vps":  # 모의투자
        ak1 = "paper_app"  # 모의투자용 앱키
        ak2 = "paper_sec"  # 모의투자용 앱시크리트
        _isPaper = True
        _smartSleep = 0.5

    cfg["my_app"] = _cfg[ak1]
    cfg["my_sec"] = _cfg[ak2]

    if svr == "prod" and product == "01":  # 실전투자 주식투자, 위탁계좌, 투자계좌
        cfg["my_acct"] = _cfg["my_acct_stock"]
    elif svr == "prod" and product == "03":  # 실전투자 선물옵션(파생)
        cfg["my_acct"] = _cfg["my_acct_future"]
    elif svr == "prod" and product == "08":  # 실전투자 해외선물옵션(파생)
        cfg["my_acct"] = _cfg["my_acct_future"]
    elif svr == "prod" and product == "22":  # 실전투자 개인연금저축계좌
        cfg["my_acct"] = _cfg["my_acct_stock"]
    elif svr == "prod" and product == "29":  # 실전투자 퇴직연금계좌
        cfg["my_acct"] = _cfg["my_acct_stock"]
    elif svr == "vps" and product == "01":  # 모의투자 주식투자, 위탁계좌, 투자계좌
        cfg["my_acct"] = _cfg["my_paper_stock"]
    elif svr == "vps" and product == "03":  # 모의투자 선물옵션(파생)
        cfg["my_acct"] = _cfg["my_paper_future"]

    cfg["my_prod"] = product
    cfg["my_htsid"] = _cfg["my_htsid"]
    cfg["my_url"] = _cfg[svr]

    try:
        my_token = _TRENV.my_token
    except AttributeError:
        my_token = ""
    cfg["my_token"] = my_token if token_key else token_key
    cfg["my_url_ws"] = _cfg["ops" if svr == "prod" else "vops"]

    # print(cfg)
    _setTRENV(cfg)


def _getResultObject(json_data):
    _tc_ = namedtuple("res", json_data.keys())

    return _tc_(**json_data)


# Token 발급, 유효기간 1일, 6시간 이내 발급시 기존 token값 유지, 발급시 알림톡 무조건 발송
# 모의투자인 경우  svr='vps', 투자계좌(01)이 아닌경우 product='XX' 변경하세요 (계좌번호 뒤 2자리)
def auth(svr="prod", product=_cfg["my_prod"], url=None):
    p = {
        "grant_type": "client_credentials",
    }
    # 개인 환경파일 "kis_devlp.yaml" 파일을 참조하여 앱키, 앱시크리트 정보 가져오기
    # 개인 환경파일명과 위치는 고객님만 아는 위치로 설정 바랍니다.
    if svr == "prod":  # 실전투자
        ak1 = "my_app"  # 앱키 (실전투자용)
        ak2 = "my_sec"  # 앱시크리트 (실전투자용)
    elif svr == "vps":  # 모의투자
        ak1 = "paper_app"  # 앱키 (모의투자용)
        ak2 = "paper_sec"  # 앱시크리트 (모의투자용)

    # 앱키, 앱시크리트 가져오기
    p["appkey"] = _cfg[ak1]
    p["appsecret"] = _cfg[ak2]

    # 기존 발급된 토큰이 있는지 확인
    saved_token = read_token()  # 기존 발급 토큰 확인
    # print("saved_token: ", saved_token)
    if saved_token is None:  # 기존 발급 토큰 확인이 안되면 발급처리
        url = f"{_cfg[svr]}/oauth2/tokenP"
        res = requests.post(
            url, data=json.dumps(p), headers=_getBaseHeader()
        )  # 토큰 발급
        rescode = res.status_code
        if rescode == 200:  # 토큰 정상 발급
            my_token = _getResultObject(res.json()).access_token  # 토큰값 가져오기
            my_expired = _getResultObject(
                res.json()
            ).access_token_token_expired  # 토큰값 만료일시 가져오기
            save_token(my_token, my_expired)  # 새로 발급 받은 토큰 저장
        else:
            print("Get Authentification token fail!\nYou have to restart your app!!!")
            return
    else:
        my_token = saved_token  # 기존 발급 토큰 확인되어 기존 토큰 사용

    # 발급토큰 정보 포함해서 헤더값 저장 관리, API 호출시 필요
    changeTREnv(my_token, svr, product)

    _base_headers["authorization"] = f"Bearer {my_token}"
    _base_headers["appkey"] = _TRENV.my_app
    _base_headers["appsecret"] = _TRENV.my_sec

    global _last_auth_time
    _last_auth_time = datetime.now()

    if _DEBUG:
        print(f"[{_last_auth_time}] => get AUTH Key completed!")


# end of initialize, 토큰 재발급, 토큰 발급시 유효시간 1일
# 프로그램 실행시 _last_auth_time에 저장하여 유효시간 체크, 유효시간 만료시 토큰 발급 처리
def reAuth(svr="prod", product=_cfg["my_prod"]):
    n2 = datetime.now()
    if (n2 - _last_auth_time).seconds >= 86400:  # 유효시간 1일
        auth(svr, product)


def getEnv():
    return _cfg


def smart_sleep():
    if _DEBUG:
        print(f"[RateLimit] Sleeping {_smartSleep}s ")

    time.sleep(_smartSleep)


def getTREnv():
    return _TRENV


# 주문 API에서 사용할 hash key값을 받아 header에 설정해 주는 함수
# 현재는 hash key 필수 사항아님, 생략가능, API 호출과정에서 변조 우려를 하는 경우 사용
# Input: HTTP Header, HTTP post param
# Output: None
def set_order_hash_key(h, p):
    url = f"{getTREnv().my_url}/uapi/hashkey"  # hashkey 발급 API URL

    res = requests.post(url, data=json.dumps(p), headers=h)
    rescode = res.status_code
    if rescode == 200:
        h["hashkey"] = _getResultObject(res.json()).HASH
    else:
        print("Error:", rescode)


# API 호출 응답에 필요한 처리 공통 함수
class APIResp:
    def __init__(self, resp):
        self._rescode = resp.status_code
        self._resp = resp
        self._header = self._setHeader()
        self._body = self._setBody()
        self._err_code = self._body.msg_cd
        self._err_message = self._body.msg1

    def getResCode(self):
        return self._rescode

    def _setHeader(self):
        fld = dict()
        for x in self._resp.headers.keys():
            if x.islower():
                fld[x] = self._resp.headers.get(x)
        _th_ = namedtuple("header", fld.keys())

        return _th_(**fld)

    def _setBody(self):
        _tb_ = namedtuple("body", self._resp.json().keys())

        return _tb_(**self._resp.json())

    def getHeader(self):
        return self._header

    def getBody(self):
        return self._body

    def getResponse(self):
        return self._resp

    def isOK(self):
        try:
            if self.getBody().rt_cd == "0":
                return True
            else:
                return False
        except:
            return False

    def getErrorCode(self):
        return self._err_code

    def getErrorMessage(self):
        return self._err_message

    def printAll(self):
        print("<Header>")
        for x in self.getHeader()._fields:
            print(f"\t-{x}: {getattr(self.getHeader(), x)}")
        print("<Body>")
        for x in self.getBody()._fields:
            print(f"\t-{x}: {getattr(self.getBody(), x)}")

    def printError(self, url):
        print(
            "-------------------------------\nError in response: ",
            self.getResCode(),
            " url=",
            url,
        )
        print(
            "rt_cd : ",
            self.getBody().rt_cd,
            "/ msg_cd : ",
            self.getErrorCode(),
            "/ msg1 : ",
            self.getErrorMessage(),
        )
        print("-------------------------------")

    # end of class APIResp


class APIRespError(APIResp):
    def __init__(self, status_code, error_text):
        # 부모 생성자 호출하지 않고 직접 초기화
        self.status_code = status_code
        self.error_text = error_text
        self._error_code = str(status_code)
        self._error_message = error_text

    def isOK(self):
        return False

    def getErrorCode(self):
        return self._error_code

    def getErrorMessage(self):
        return self._error_message

    def getBody(self):
        # 빈 객체 리턴 (속성 접근 시 AttributeError 방지)
        class EmptyBody:
            def __getattr__(self, name):
                return None

        return EmptyBody()

    def getHeader(self):
        # 빈 객체 리턴
        class EmptyHeader:
            tr_cont = ""

            def __getattr__(self, name):
                return ""

        return EmptyHeader()

    def printAll(self):
        print(f"=== ERROR RESPONSE ===")
        print(f"Status Code: {self.status_code}")
        print(f"Error Message: {self.error_text}")
        print(f"======================")

    def printError(self, url=""):
        print(f"Error Code : {self.status_code} | {self.error_text}")
        if url:
            print(f"URL: {url}")


########### API call wrapping : API 호출 공통


def _url_fetch(
        api_url, ptr_id, tr_cont, params, appendHeaders=None, postFlag=False, hashFlag=True
):
    url = f"{getTREnv().my_url}{api_url}"

    headers = _getBaseHeader()  # 기본 header 값 정리

    # 추가 Header 설정
    tr_id = ptr_id
    if ptr_id[0] in ("T", "J", "C"):  # 실전투자용 TR id 체크
        if isPaperTrading():  # 모의투자용 TR id 식별
            tr_id = "V" + ptr_id[1:]

    headers["tr_id"] = tr_id  # 트랜젝션 TR id
    headers["custtype"] = "P"  # 일반(개인고객,법인고객) "P", 제휴사 "B"
    headers["tr_cont"] = tr_cont  # 트랜젝션 TR id

    if appendHeaders is not None:
        if len(appendHeaders) > 0:
            for x in appendHeaders.keys():
                headers[x] = appendHeaders.get(x)

    if _DEBUG:
        print("< Sending Info >")
        print(f"URL: {url}, TR: {tr_id}")
        print(f"<header>\n{headers}")
        print(f"<body>\n{params}")

    if postFlag:
        # if (hashFlag): set_order_hash_key(headers, params)
        res = requests.post(url, headers=headers, data=json.dumps(params))
    else:
        res = requests.get(url, headers=headers, params=params)

    if res.status_code == 200:
        ar = APIResp(res)
        if _DEBUG:
            ar.printAll()
        return ar
    else:
        print("Error Code : " + str(res.status_code) + " | " + res.text)
        return APIRespError(res.status_code, res.text)


# auth()
# print("Pass through the end of the line")


########### New - websocket 대응

_base_headers_ws = {
    "content-type": "utf-8",
}


def _getBaseHeader_ws():
    if _autoReAuth:
        reAuth_ws()

    return copy.deepcopy(_base_headers_ws)


def auth_ws(svr="prod", product=_cfg["my_prod"]):
    p = {"grant_type": "client_credentials"}
    if svr == "prod":
        ak1 = "my_app"
        ak2 = "my_sec"
    elif svr == "vps":
        ak1 = "paper_app"
        ak2 = "paper_sec"

    p["appkey"] = _cfg[ak1]
    p["secretkey"] = _cfg[ak2]

    url = f"{_cfg[svr]}/oauth2/Approval"
    res = requests.post(url, data=json.dumps(p), headers=_getBaseHeader())  # 토큰 발급
    rescode = res.status_code
    if rescode == 200:  # 토큰 정상 발급
        approval_key = _getResultObject(res.json()).approval_key
    else:
        print("Get Approval token fail!\nYou have to restart your app!!!")
        return

    changeTREnv(None, svr, product)

    _base_headers_ws["approval_key"] = approval_key

    global _last_auth_time
    _last_auth_time = datetime.now()

    if _DEBUG:
        print(f"[{_last_auth_time}] => get AUTH Key completed!")


def reAuth_ws(svr="prod", product=_cfg["my_prod"]):
    n2 = datetime.now()
    if (n2 - _last_auth_time).seconds >= 86400:
        auth_ws(svr, product)


def data_fetch(tr_id, tr_type, params, appendHeaders=None) -> dict:
    headers = _getBaseHeader_ws()  # 기본 header 값 정리

    headers["tr_type"] = tr_type
    headers["custtype"] = "P"

    if appendHeaders is not None:
        if len(appendHeaders) > 0:
            for x in appendHeaders.keys():
                headers[x] = appendHeaders.get(x)

    if _DEBUG:
        print("< Sending Info >")
        print(f"TR: {tr_id}")
        print(f"<header>\n{headers}")

    inp = {
        "tr_id": tr_id,
    }
    inp.update(params)

    return {"header": headers, "body": {"input": inp}}


# iv, ekey, encrypt 는 각 기능 메소드 파일에 저장할 수 있도록 dict에서 return 하도록
def system_resp(data):
    isPingPong = False
    isUnSub = False
    isOk = False
    tr_msg = None
    tr_key = None
    encrypt, iv, ekey = None, None, None

    rdic = json.loads(data)

    tr_id = rdic["header"]["tr_id"]
    if tr_id != "PINGPONG":
        tr_key = rdic["header"]["tr_key"]
        encrypt = rdic["header"]["encrypt"]
    if rdic.get("body", None) is not None:
        isOk = True if rdic["body"]["rt_cd"] == "0" else False
        tr_msg = rdic["body"]["msg1"]
        # 복호화를 위한 key 를 추출
        if "output" in rdic["body"]:
            iv = rdic["body"]["output"]["iv"]
            ekey = rdic["body"]["output"]["key"]
        isUnSub = True if tr_msg[:5] == "UNSUB" else False
    else:
        isPingPong = True if tr_id == "PINGPONG" else False

    nt2 = namedtuple(
        "SysMsg",
        [
            "isOk",
            "tr_id",
            "tr_key",
            "isUnSub",
            "isPingPong",
            "tr_msg",
            "iv",
            "ekey",
            "encrypt",
        ],
    )
    d = {
        "isOk": isOk,
        "tr_id": tr_id,
        "tr_key": tr_key,
        "tr_msg": tr_msg,
        "isUnSub": isUnSub,
        "isPingPong": isPingPong,
        "iv": iv,
        "ekey": ekey,
        "encrypt": encrypt,
    }

    return nt2(**d)


def aes_cbc_base64_dec(key, iv, cipher_text):
    if key is None or iv is None:
        raise AttributeError("key and iv cannot be None")

    cipher = AES.new(key.encode("utf-8"), AES.MODE_CBC, iv.encode("utf-8"))
    return bytes.decode(unpad(cipher.decrypt(b64decode(cipher_text)), AES.block_size))


#####
open_map: dict = {}


def add_open_map(
        name: str,
        request: Callable[[str, str, ...], (dict, list[str])],
        data: str | list[str],
        kwargs: dict = None,
):
    if open_map.get(name, None) is None:
        open_map[name] = {
            "func": request,
            "items": [],
            "kwargs": kwargs,
        }

    if type(data) is list:
        open_map[name]["items"] += data
    elif type(data) is str:
        open_map[name]["items"].append(data)


data_map: dict = {}


def add_data_map(
        tr_id: str,
        columns: list = None,
        encrypt: str = None,
        key: str = None,
        iv: str = None,
):
    if data_map.get(tr_id, None) is None:
        data_map[tr_id] = {"columns": [], "encrypt": False, "key": None, "iv": None}

    if columns is not None:
        data_map[tr_id]["columns"] = columns

    if encrypt is not None:
        data_map[tr_id]["encrypt"] = encrypt

    if key is not None:
        data_map[tr_id]["key"] = key

    if iv is not None:
        data_map[tr_id]["iv"] = iv


class KISWebSocket:
    api_url: str = ""
    on_result: Callable[
        [websockets.ClientConnection, str, pd.DataFrame, dict], None
    ] = None
    result_all_data: bool = False

    retry_count: int = 0
    amx_retries: int = 0

    # init
    def __init__(self, api_url: str, max_retries: int = 3):
        self.api_url = api_url
        self.max_retries = max_retries

    # private
    async def __subscriber(self, ws: websockets.ClientConnection):
        async for raw in ws:
            logging.info("received message >> %s" % raw)
            show_result = False

            df = pd.DataFrame()

            if raw[0] in ["0", "1"]:
                d1 = raw.split("|")
                if len(d1) < 4:
                    raise ValueError("data not found...")

                tr_id = d1[1]

                dm = data_map[tr_id]
                d = d1[3]
                if dm.get("encrypt", None) == "Y":
                    d = aes_cbc_base64_dec(dm["key"], dm["iv"], d)

                df = pd.read_csv(
                    StringIO(d), header=None, sep="^", names=dm["columns"], dtype=object
                )

                show_result = True

            else:
                rsp = system_resp(raw)

                tr_id = rsp.tr_id
                add_data_map(
                    tr_id=rsp.tr_id, encrypt=rsp.encrypt, key=rsp.ekey, iv=rsp.iv
                )

                if rsp.isPingPong:
                    print(f"### RECV [PINGPONG] [{raw}]")
                    await ws.pong(raw)
                    print(f"### SEND [PINGPONG] [{raw}]")

                if self.result_all_data:
                    show_result = True

            if show_result is True and self.on_result is not None:
                self.on_result(ws, tr_id, df, data_map[tr_id])

    async def __runner(self):
        if len(open_map.keys()) > 40:
            raise ValueError("Subscription's max is 40")

        url = f"{getTREnv().my_url_ws}{self.api_url}"

        while self.retry_count < self.max_retries:
            try:
                async with websockets.connect(url) as ws:
                    # request subscribe
                    for name, obj in open_map.items():
                        await self.send_multiple(
                            ws, obj["func"], "1", obj["items"], obj["kwargs"]
                        )

                    # subscriber
                    await asyncio.gather(
                        self.__subscriber(ws),
                    )
            except Exception as e:
                print("Connection exception >> ", e)
                self.retry_count += 1
                await asyncio.sleep(1)

    # func
    @classmethod
    async def send(
            cls,
            ws: websockets.ClientConnection,
            request: Callable[[str, str, ...], (dict, list[str])],
            tr_type: str,
            data: str,
            kwargs: dict = None,
    ):
        k = {} if kwargs is None else kwargs
        msg, columns = request(tr_type, data, **k)

        add_data_map(tr_id=msg["body"]["input"]["tr_id"], columns=columns)

        logging.info("send message >> %s" % json.dumps(msg))

        await ws.send(json.dumps(msg))
        smart_sleep()

    async def send_multiple(
            self,
            ws: websockets.ClientConnection,
            request: Callable[[str, str, ...], (dict, list[str])],
            tr_type: str,
            data: list | str,
            kwargs: dict = None,
    ):
        if type(data) is str:
            await self.send(ws, request, tr_type, data, kwargs)
        elif type(data) is list:
            for d in data:
                await self.send(ws, request, tr_type, d, kwargs)
        else:
            raise ValueError("data must be str or list")

    @classmethod
    def subscribe(
            cls,
            request: Callable[[str, str, ...], (dict, list[str])],
            data: list | str,
            kwargs: dict = None,
    ):
        add_open_map(request.__name__, request, data, kwargs)

    def unsubscribe(
            self,
            ws: websockets.ClientConnection,
            request: Callable[[str, str, ...], (dict, list[str])],
            data: list | str,
    ):
        self.send_multiple(ws, request, "2", data)

    # start
    def start(
            self,
            on_result: Callable[
                [websockets.ClientConnection, str, pd.DataFrame, dict], None
            ],
            result_all_data: bool = False,
    ):
        self.on_result = on_result
        self.result_all_data = result_all_data
        try:
            asyncio.run(self.__runner())
        except KeyboardInterrupt:
            print("Closing by KeyboardInterrupt")
