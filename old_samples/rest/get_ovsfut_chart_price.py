## 해외선물분봉조회: 해외선물 상품의 특정 기간동안의 분봉을 받아서 엑셀로 저장하는 파이썬 샘플코드
## config.yaml 파일을 설정한 뒤 get_ovsfut_chart_price.py를 실행해서 분봉 데이터 저장 가능
## 해외선물 종목정보 마스터파일 다운로드 : https://new.real.download.dws.co.kr/common/master/ffcode.mst.zip

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
def get_access_token():
    """ OAuth 인증 > 접근토큰발급 """
    headers = {"content-type": "application/json"}
    body = {"grant_type": "client_credentials",
            "appkey": APP_KEY,
            "appsecret": APP_SECRET}
    PATH = "oauth2/tokenP"
    URL = f"{URL_BASE}/{PATH}"
    res = requests.post(URL, headers=headers, data=json.dumps(body))
    time.sleep(0.1)
    try:
        ACCESS_TOKEN = res.json()["access_token"]
        ACCESS_TOKEN_EXPIRED = res.json()["access_token_token_expired"]
        return ACCESS_TOKEN, ACCESS_TOKEN_EXPIRED
    except:
        print("접근 토큰 발급이 불가능합니다")
        print(res.json())

        
def get_overseas_future_time_price(SRS="6AZ23", EXCH="CME", STRT_DT="",END_DT="", CNT="100", GAP="1", dataframe=None, file_name=None): # 해외선물옵션시세 > 해외선물 분봉조회
    """
    해외선물옵션시세 > 해외선물 분봉조회를 위한 함수

    Parameters:
    - SRS: 종목 코드
    - EXCH: 거래소 코드
    - STRT_DT: 조회 시작일
    - END_DT: 조회 종료일
    - CNT: 호출건당 조회 갯수
    - GAP: 조회 간격
    - dataframe: 초기 데이터프레임
    - file_name: 저장할 파일 이름

    Returns"":
    - 최종 데이터프레임
    """
    PATH = "/uapi/overseas-futureoption/v1/quotations/inquire-time-futurechartprice"
    URL = f"{URL_BASE}/{PATH}"
    headers = {"Content-Type":"application/json",
        "authorization":f"Bearer {ACCESS_TOKEN}",
        "appKey":APP_KEY,
        "appSecret":APP_SECRET,
        "tr_id":"HHDFC55020400", # 실전투자
        "custtype":"P"
    }
    params = {
        "SRS_CD": SRS,
        "EXCH_CD": EXCH,
        "START_DATE_TIME": "",
        "CLOSE_DATE_TIME": END_DT,
        "QRY_TP": "",
        "QRY_CNT": CNT,
        "QRY_GAP": GAP,
        "INDEX_KEY": ""
    }    
    res = requests.get(URL, headers=headers, params=params)
    time.sleep(0.1) # 유량제한 예방 (REST: 1초당 20건 제한)
    output = res.json()['output1']
    
    # 파일 이름이 제공되지 않은 경우에만 생성
    if file_name is None:
        file_name = f"{SRS}_{EXCH}_{STRT_DT}_{END_DT}"
    
    # 초기 dataframe 생성
    if dataframe is None:
        dataframe = pd.DataFrame()  
    
    current_dataframe = pd.DataFrame(output)
    
    # 이전 응답값이 존재하고, 이전 응답값과 현재 응답값이 동일하면
    if not dataframe.empty and dataframe.iloc[-1,0] == current_dataframe.iloc[-1,0] and dataframe.iloc[-1,1] == current_dataframe.iloc[-1,1]:
        
        # 이전 데이터프레임에 현재 데이터프레임 추가
        dataframe = pd.concat([dataframe, current_dataframe], ignore_index=True)
        
        # STRT_DT와 END_DT가 같은 경우 현재 dataframe을 return
        if STRT_DT == END_DT:
            dataframe = dataframe.drop_duplicates(ignore_index=True)
            
            # 최종 데이터프레임 정제 작업(이상치 삭제 및 date, time으로 정렬)
            ## 'data_date'와 'data_time'을 문자열로 변환하여 문자열을 합쳐 datetime 형식으로 만들기
            dataframe['datetime'] = pd.to_datetime(dataframe['data_date'].astype(str) + dataframe['data_time'].astype(str).str.zfill(6), errors='coerce', format='%Y%m%d%H%M%S')
            ## 유효한 datetime이 아닌 행 삭제
            dataframe = dataframe.dropna(subset=['datetime'])
            ## 'datetime'을 기준으로 정렬 후 'datetime' 열 삭제
            dataframe = dataframe.sort_values(by=['datetime']).drop(columns=['datetime']).reset_index(drop=True)
            
            # 현재 위치에 엑셀파일로 저장
            dataframe.to_excel(f"{file_name}.xlsx",index=False)
            print("File Saved")
            
            # 최종 데이터프레임 return
            return dataframe
            
        else:
            # END_DT를 하루 이전으로 설정하고 재귀호출
            END_DT = pd.to_datetime(END_DT) - pd.DateOffset(days=1)
            END_DT = END_DT.strftime("%Y%m%d")
            return get_overseas_future_time_price(SRS, EXCH, STRT_DT, END_DT, "100", GAP, dataframe, file_name)
    else:
        # 이전 데이터프레임에 현재 데이터프레임 추가
        dataframe = pd.concat([dataframe, current_dataframe], ignore_index=True)
        
        # 이전 응답값과 현재 응답값이 다르면 CNT를 100늘려서 재호출
        CNT = str(int(CNT) + 100)
        # print(SRS, EXCH, STRT_DT, END_DT, CNT, GAP)
        return get_overseas_future_time_price(SRS, EXCH, STRT_DT, END_DT, CNT, GAP, dataframe, file_name)

    
# (3) 함수 실행
# 접근토큰 발급
ACCESS_TOKEN, ACCESS_TOKEN_EXPIRED = get_access_token()

# 사용자 입력 받기
SRS = input("종목 코드를 입력하세요(ex. 6AZ23): ")
EXCH = input("거래소 코드를 입력하세요(ex. CME): ")
STRT_DT = input("조회 시작일을 입력하세요 (YYYYMMDD 형식): ")
END_DT = input("조회 종료일을 입력하세요 (YYYYMMDD 형식): ")
GAP = input("조회 간격(분)을 입력하세요 (ex. 1) : ")

# 해외선물분봉조회 호출
print("Downloading...")
result_dataframe = get_overseas_future_time_price(SRS=SRS, EXCH=EXCH, STRT_DT=STRT_DT, END_DT=END_DT, CNT="100", GAP=GAP)
result_dataframe[:3]