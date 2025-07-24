## 관심종목 복수시세조회 파이썬 샘플코드
### config.yaml 파일을 설정한 뒤 get_interest_stocks_price.py를 실행하여
### 1) 관심종목 그룹조회 → 2) 관심종목 그룹별 종목조회 → 3) 관심종목(멀티종목) 시세조회 순서대로 호출하여 관심종목 복수시세 조회 가능

# (0) 필요 모듈 임포트
import pandas as pd
import requests
import json
import yaml
import time

# (1) 개인정보 파일 가져오기
with open('config.yaml', encoding='UTF-8') as f:
    _cfg = yaml.load(f, Loader=yaml.FullLoader)
APP_KEY = _cfg['APP_KEY']
APP_SECRET = _cfg['APP_SECRET']
ACCESS_TOKEN = ""
ACCESS_TOKEN_EXPIRED = ""
CANO = _cfg['CANO']
ACNT_PRDT_CD = _cfg['ACNT_PRDT_CD']
URL_BASE = _cfg['URL_BASE']
HTS_ID = _cfg['HTS_ID']

# (2) 함수 정의
## 1. 접근 토큰 발급
def get_access_token():
    """ OAuth 인증 > 접근토큰발급 """
    headers = {"content-type": "application/json"}
    body = {"grant_type": "client_credentials",
            "appkey": APP_KEY,
            "appsecret": APP_SECRET}
    PATH = "oauth2/tokenP"
    URL = f"{URL_BASE}/{PATH}"
    res = requests.post(URL, headers=headers, data=json.dumps(body))
    time.sleep(0.1) # 유량제한 예방 (REST: 1초당 20건 제한)
    try:
        ACCESS_TOKEN = res.json()["access_token"]
        ACCESS_TOKEN_EXPIRED = res.json()["access_token_token_expired"]
        return ACCESS_TOKEN, ACCESS_TOKEN_EXPIRED
    except:
        print("접근 토큰 발급이 불가능합니다")
        print(res.json())

## 2. 관심종목 그룹 조회
def get_interest_groups():
    PATH = "/uapi/domestic-stock/v1/quotations/intstock-grouplist"
    URL = f"{URL_BASE}/{PATH}"
    params = {
        "TYPE": "1",
        "FID_ETC_CLS_CODE": "00",
        "USER_ID": HTS_ID
    }
    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {ACCESS_TOKEN}",
        "appKey": APP_KEY,
        "appSecret": APP_SECRET,
        "tr_id": "HHKCM113004C7",  # 실전투자
        "custtype": "P"
    }
    time.sleep(0.05) # 유량제한 예방 (REST: 1초당 20건 제한)
    res = requests.get(URL, headers=headers, params=params)
    return res.json()

## 3. 관심종목 그룹별 종목 조회
def get_group_stocks(interest_group):
    PATH = "/uapi/domestic-stock/v1/quotations/intstock-stocklist-by-group"
    URL = f"{URL_BASE}/{PATH}"
    params = {
        "TYPE": "1",
        "USER_ID": HTS_ID,
        "DATA_RANK": "",
        "INTER_GRP_CODE": interest_group,
        "INTER_GRP_NAME": "",
        "HTS_KOR_ISNM": "",
        "CNTG_CLS_CODE": "",
        "FID_ETC_CLS_CODE": "4"
    }
    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {ACCESS_TOKEN}",
        "appKey": APP_KEY,
        "appSecret": APP_SECRET,
        "tr_id": "HHKCM113004C6",  # 실전투자
        "custtype": "P"
    }
    time.sleep(0.05) # 유량제한 예방 (REST: 1초당 20건 제한)
    res = requests.get(URL, headers=headers, params=params)
    return res.json()

## 4. 관심종목(멀티종목) 시세조회 (30종목까지 조회 가능)
def get_multi_stock_prices(jongs):
    PATH = "/uapi/domestic-stock/v1/quotations/intstock-multprice"
    URL = f"{URL_BASE}/{PATH}"
    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {ACCESS_TOKEN}",
        "appKey": APP_KEY,
        "appSecret": APP_SECRET,
        "tr_id": "FHKST11300006",  # 실전투자
        "custtype": "P"
    }
    time.sleep(0.05) # 유량제한 예방 (REST: 1초당 20건 제한)
    res = requests.get(URL, headers=headers, params=jongs)
    print(res.text)
    print(res.json())
    return res.json()

# (3) 함수 실행
## 1. 접근토큰 발급
ACCESS_TOKEN, ACCESS_TOKEN_EXPIRED = get_access_token()

## 2. 관심종목 그룹 조회
interest_groups = get_interest_groups()
print(interest_groups)

## 3. 사용자로부터 관심종목 그룹 선택
interest_group = str(input("관심종목 그룹 번호(inter_grp_code)를 입력하세요: "))

## 4. 선택한 관심종목 그룹별 종목 조회
group_stocks = get_group_stocks(interest_group)
print(group_stocks)
interest_mrkt_code_list = [item["fid_mrkt_cls_code"] for item in group_stocks["output2"]]
interest_jong_code_list = [item["jong_code"] for item in group_stocks["output2"]]

print(interest_mrkt_code_list)
print(interest_jong_code_list)

## 5. 관심종목 최대30종목 리스트 생성
jongs = {}
for i in range(min(len(interest_jong_code_list), 30)):  # 관심종목 (최대) 30종목 리스트 생성
    jongs[f"FID_COND_MRKT_DIV_CODE_{i}"] = interest_mrkt_code_list[i]
    jongs[f"FID_INPUT_ISCD_{i}"] = interest_jong_code_list[i]
print("jongs",jongs)
print("jongs 길이",len(jongs))
    
## 6. 관심종목 시세 조회
multi_stock_prices = get_multi_stock_prices(jongs)
print(multi_stock_prices) # 최대 30개 관심종목 데이터 출력
print(pd.DataFrame(multi_stock_prices['output'])) # 전체 데이터 데이터프레임으로 변환
print(pd.DataFrame(multi_stock_prices['output'])[['inter_kor_isnm','inter_shrn_iscd','inter2_prpr']]) #종목 한글명, 종목코드, 현재가만 출력