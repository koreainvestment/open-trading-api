"""
해당 접근토큰발급관리 파일을 그대로 사용하시면 오류 발생할 수 있습니다.
토큰저장 및 발급 함수 등을 참고하시되 본인 환경에 맞게 코드 수정하셔서 사용하시기 바랍니다.

Created on Wed Feb 15 16:57:19 2023

@author: Administrator
"""

import time, copy
import hashlib
import yaml
import requests
import json

import os
import re
import tempfile

import pandas as pd

from collections import namedtuple
from datetime import datetime

config_root = os.environ.get('KIS_CONFIG_DIR', os.getcwd() + '\\')
if not config_root.endswith(('\\', '/')):
    config_root += os.sep
# config_root = 'd:\\KIS\\config\\'  # 토큰 파일이 저장될 폴더, 제3자가 찾지 어렵도록 경로 설정하시기 바랍니다.
#token_tmp = config_root + 'KIS000000'  # 토큰 로컬저장시 파일 이름 지정, 파일이름을 토큰값이 유추가능한 파일명은 삼가바랍니다.
#token_tmp = config_root + 'KIS' + datetime.today().strftime("%Y%m%d%H%M%S")  # 토큰 로컬저장시 파일명 년월일시분초
token_tmp = config_root + 'KIS' + datetime.today().strftime("%Y%m%d")  # 토큰 로컬저장시 파일명 년월일

if os.path.exists(token_tmp) == False:
    with open(token_tmp, 'a', encoding='utf-8'):
        pass
    try:
        os.chmod(token_tmp, 0o600)
    except OSError:
        pass

# 앱키, 앱시크리트, 토큰, 계좌번호 등 저장관리, 자신만의 경로와 파일명으로 설정하시기 바랍니다.
# pip install PyYAML (패키지설치)
with open(config_root + 'kis_devlp.yaml', encoding='UTF-8') as f:
    _cfg = yaml.safe_load(f)

_TRENV = tuple()
REQ_TIMEOUT = (5.0, 30.0)  # 모든 KIS HTTP 호출의 (connect, read) 타임아웃
_last_auth_time = datetime.now()
_autoReAuth = False
_last_svr = None  # 마지막으로 auth()를 호출한 서버 구분 (prod:실전, vps:모의)
_last_product = None  # 마지막으로 auth()에 넘긴 상품코드
_reauth_running = False  # 재인증 재진입 차단용
_DEBUG = False
_isPaper = False

# 기본 헤더값 정의
_base_headers = {
    "Content-Type": "application/json",
    "Accept": "text/plain",
    "charset": "UTF-8",
    'User-Agent': _cfg['my_agent']
}

_SECRET_KEYS = ('authorization', 'appsecret', 'appkey', 'approval_key', 'key', 'iv', 'token', 'secretkey')
_MASKED = '***'

def _redact(obj):
    if isinstance(obj, dict):
        return {k: (_MASKED if isinstance(k, str) and k.lower() in _SECRET_KEYS else _redact(v)) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_redact(v) for v in obj]
    return obj

def _redacted_headers(headers):
    return _redact(dict(headers))

def _masked_json(payload):
    try:
        if isinstance(payload, str):
            try:
                payload = json.loads(payload)
            except (ValueError, TypeError):
                return re.sub(r'("(?:approval_key|authorization|appsecret|appkey|secretkey|token|key|iv)"\s*:\s*")[^"]*(")', r'\1***\2', payload)
        return json.dumps(_redact(payload))
    except (ValueError, TypeError):
        return '***'

def _mask_ws_raw(raw):
    if isinstance(raw, (bytes, bytearray)):
        try:
            raw = bytes(raw).decode('utf-8', 'replace')
        except Exception:
            return '***'
    if not isinstance(raw, str):
        return '***'
    s = raw.strip()
    if s.startswith('{'):
        try:
            return json.dumps(_redact(json.loads(s)))
        except (ValueError, TypeError):
            pass
    return re.sub(r'("(?:approval_key|authorization|appsecret|appkey|secretkey|token|key|iv)"\s*:\s*")[^"]*(")', r'\1***\2', raw)

# 토큰 발급 받아 저장 (토큰값, 토큰 유효시간,1일, 6시간 이내 발급신청시는 기존 토큰값과 동일, 발급시 알림톡 발송)
def _token_path(svr):
    return f"{token_tmp}_{svr}"


def _appkey_fingerprint(svr):
    """토큰 파일 귀속용 앱키 지문(sha256 앞 16자). 앱키가 바뀌면 기존 토큰을 폐기한다."""
    try:
        key = _cfg['my_app'] if svr == 'prod' else _cfg['paper_app']
    except (KeyError, TypeError):
        return ""
    return hashlib.sha256(key.encode('utf-8')).hexdigest()[:16]


def save_token(my_token, my_expired, svr=None):
    valid_date = datetime.strptime(my_expired, '%Y-%m-%d %H:%M:%S')
    svr = svr or _last_svr
    path = _token_path(svr) if svr else token_tmp
    content = f'token: {my_token}\nvalid-date: {valid_date}\n'
    if svr:
        content += f'appkey-sha: {_appkey_fingerprint(svr)}\n'
    d = os.path.dirname(path) or '.'
    try:
        os.makedirs(d, exist_ok=True)
    except OSError:
        pass
    fd, tmp = tempfile.mkstemp(dir=d, prefix='.kis_token_')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(content)
        os.chmod(tmp, 0o600)
        os.replace(tmp, path)
        try:
            os.chmod(path, 0o600)
        except OSError:
            pass
    except BaseException:
        try:
            os.remove(tmp)
        except OSError:
            pass
        raise

# 토큰 확인 (토큰값, 토큰 유효시간_1일, 6시간 이내 발급신청시는 기존 토큰값과 동일, 발급시 알림톡 발송)
# svr 지정 시 해당 서버의 토큰 파일만 확인
def read_token(svr=None):
    svr = svr or _last_svr
    paths = [_token_path(svr)] if svr else [token_tmp]
    for path in paths:
        token = _read_token_file(path, svr)
        if token:
            return token
    return None


def _read_token_file(path, svr=None):
    try:
        # 토큰이 저장된 파일 읽기
        with open(path, encoding='UTF-8') as f:
            tkg_tmp = yaml.safe_load(f)

        if svr:
            expected = _appkey_fingerprint(svr)
            actual = (tkg_tmp.get('appkey-sha') or '') if isinstance(tkg_tmp, dict) else ''
            if expected and actual and expected != actual:
                return None  # 다른 앱키의 토큰은 폐기

        # 토큰 만료 일,시간
        exp_dt = datetime.strftime(tkg_tmp['valid-date'], '%Y-%m-%d %H:%M:%S')
        # 현재일자,시간
        now_dt = datetime.today().strftime("%Y-%m-%d %H:%M:%S")

        # print('expire dt: ', exp_dt, ' vs now dt:', now_dt)
        # 저장된 토큰 만료일자 체크 (만료일시 > 현재일시 인경우 보관 토큰 리턴)
        if exp_dt > now_dt:
            return tkg_tmp['token']
        else:
            # print('Need new token: ', tkg_tmp['valid-date'])
            return None
    except Exception as e:
        # print('read token error: ', e)
        return None


# 토큰 유효시간 체크해서 만료된 토큰이면 재발급처리
def clear_saved_tokens():
    """저장된 토큰 파일(당일 + prod/vps 분리본)을 모두 삭제한다. 삭제된 개수를 반환."""
    removed = 0
    for path in (token_tmp, f"{token_tmp}_prod", f"{token_tmp}_vps"):
        try:
            if os.path.exists(path):
                os.remove(path)
                removed += 1
        except OSError:
            pass
    return removed


def _getBaseHeader():
    if _autoReAuth and not _reauth_running: reAuth()
    return copy.deepcopy(_base_headers)


# 가져오기 : 앱키, 앱시크리트, 종합계좌번호(계좌번호 중 숫자8자리), 계좌상품코드(계좌번호 중 숫자2자리), 토큰, 도메인
def _setTRENV(cfg):
    nt1 = namedtuple('KISEnv', ['my_app', 'my_sec', 'my_acct', 'my_prod', 'my_token', 'my_url'])
    d = {
        'my_app': cfg['my_app'],  # 앱키
        'my_sec': cfg['my_sec'],  # 앱시크리트
        'my_acct': cfg['my_acct'],  # 종합계좌번호(8자리)
        'my_prod': cfg['my_prod'],  # 계좌상품코드(2자리)
        'my_token': cfg['my_token'],  # 토큰
        'my_url': cfg['my_url']  # 실전 도메인 (https://openapi.koreainvestment.com:9443)
    }  # 모의 도메인 (https://openapivts.koreainvestment.com:29443)

    global _TRENV
    _TRENV = nt1(**d)


def isPaperTrading():  # 모의투자 매매
    return _isPaper


# 실전투자면 'prod', 모의투자면 'vps'를 셋팅 하시기 바랍니다.
def changeTREnv(token_key, svr='prod', product='01'):
    cfg = dict()

    global _isPaper
    if svr == 'prod':  # 실전투자
        ak1 = 'my_app'  # 실전투자용 앱키
        ak2 = 'my_sec'  # 실전투자용 앱시크리트
        _isPaper = False
    elif svr == 'vps':  # 모의투자
        ak1 = 'paper_app'  # 모의투자용 앱키
        ak2 = 'paper_sec'  # 모의투자용 앱시크리트
        _isPaper = True

    cfg['my_app'] = _cfg[ak1]
    cfg['my_sec'] = _cfg[ak2]

    if svr == 'prod' and product == '01':  # 실전투자 주식투자, 위탁계좌, 투자계좌
        cfg['my_acct'] = _cfg['my_acct_stock']
    elif svr == 'prod' and product == '03':  # 실전투자 선물옵션(파생)
        cfg['my_acct'] = _cfg['my_acct_future']
    elif svr == 'vps' and product == '01':  # 모의투자 주식투자, 위탁계좌, 투자계좌
        cfg['my_acct'] = _cfg['my_paper_stock']
    elif svr == 'vps' and product == '03':  # 모의투자 선물옵션(파생)
        cfg['my_acct'] = _cfg['my_paper_future']

    cfg['my_prod'] = product
    cfg['my_token'] = token_key
    cfg['my_url'] = _cfg[svr]

    _setTRENV(cfg)


def _getResultObject(json_data):
    _tc_ = namedtuple('res', json_data.keys())

    return _tc_(**json_data)


# Token 발급, 유효기간 1일, 6시간 이내 발급시 기존 token값 유지, 발급시 알림톡 무조건 발송
def auth(svr='prod', product='01', url=None):
    global _last_svr, _last_product
    _last_svr = svr
    _last_product = product
    p = {
        "grant_type": "client_credentials",
    }
    # 개인 환경파일 "kis_devlp.yaml" 파일을 참조하여 앱키, 앱시크리트 정보 가져오기
    # 개인 환경파일명과 위치는 고객님만 아는 위치로 설정 바랍니다.
    if svr == 'prod':  # 실전투자
        ak1 = 'my_app'  # 앱키 (실전투자용)
        ak2 = 'my_sec'  # 앱시크리트 (실전투자용)
    elif svr == 'vps':  # 모의투자
        ak1 = 'paper_app'  # 앱키 (모의투자용)
        ak2 = 'paper_sec'  # 앱시크리트 (모의투자용)

    # 앱키, 앱시크리트 가져오기
    p["appkey"] = _cfg[ak1]
    p["appsecret"] = _cfg[ak2]

    # 기존 발급된 토큰이 있는지 확인
    saved_token = read_token(svr)  # 기존 발급 토큰 확인
    if saved_token is None:  # 기존 발급 토큰 확인이 안되면 발급처리
        url = f'{_cfg[svr]}/oauth2/tokenP'
        res = requests.post(url, data=json.dumps(p), headers=_getBaseHeader(), timeout=REQ_TIMEOUT)  # 토큰 발급
        rescode = res.status_code
        if rescode == 200:  # 토큰 정상 발급
            my_token = _getResultObject(res.json()).access_token  # 토큰값 가져오기
            my_expired= _getResultObject(res.json()).access_token_token_expired  # 토큰값 만료일시 가져오기
            save_token(my_token, my_expired, svr)  # 새로 발급 받은 토큰 저장
        else:
            raise RuntimeError(
                f'Get Authentification token fail! (HTTP {rescode}): {res.text[:200]}'
            )
    else:
        my_token = saved_token  # 기존 발급 토큰 확인되어 기존 토큰 사용

    # 발급토큰 정보 포함해서 헤더값 저장 관리, API 호출시 필요
    changeTREnv(f"Bearer {my_token}", svr, product)

    _base_headers["authorization"] = _TRENV.my_token
    _base_headers["appkey"] = _TRENV.my_app
    _base_headers["appsecret"] = _TRENV.my_sec

    global _last_auth_time
    _last_auth_time = datetime.now()

    if (_DEBUG):
        print(f'[{_last_auth_time}] => get AUTH Key completed!')


# end of initialize, 토큰 재발급, 토큰 발급시 유효시간 1일
# 프로그램 실행시 _last_auth_time에 저장하여 유효시간 체크, 유효시간 만료시 토큰 발급 처리
def reAuth(svr=None, product=None):
    """토큰 유효기간(24시간)이 지나면 마지막 auth() 서버·상품으로 재발급한다.

    생략된 인자는 기억한 값을 재사용하므로 모의 세션이 실전으로 바뀌지 않는다.
    재진입(헤더 생성→재인증→헤더 생성)은 1회로 차단한다.
    """
    global _reauth_running
    if _reauth_running:
        return
    svr = svr or _last_svr or "prod"
    product = product or _last_product or "01"
    n2 = datetime.now()
    if (n2 - _last_auth_time).total_seconds() >= 86400:  # 유효시간 1일
        _reauth_running = True
        try:
            auth(svr, product)
        finally:
            _reauth_running = False

# 접근토큰발급 저장 (import 시점: 실패해도 모듈 로드는 계속된다)
try:
    auth()
except RuntimeError as e:
    print(e)
# 접근토큰 조회
gettoken = read_token()
