# -*- coding: utf-8 -*-
### 모듈 임포트 ###
import websockets
import json
import requests
import os
import asyncio
import time

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from base64 import b64decode

clearConsole = lambda: os.system('cls' if os.name in ('nt', 'dos') else 'clear')

key_bytes = 32


### 함수 정의 ###

# AES256 DECODE
def aes_cbc_base64_dec(key, iv, cipher_text):
    """
    :param key:  str type AES256 secret key value
    :param iv: str type AES256 Initialize Vector
    :param cipher_text: Base64 encoded AES256 str
    :return: Base64-AES256 decodec str
    """
    cipher = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv.encode('utf-8'))
    return bytes.decode(unpad(cipher.decrypt(b64decode(cipher_text)), AES.block_size))


# 웹소켓 접속키 발급
def get_approval(key, secret):
    # url = https://openapivts.koreainvestment.com:29443' # 모의투자계좌     
    url = 'https://openapi.koreainvestment.com:9443' # 실전투자계좌
    headers = {"content-type": "application/json"}
    body = {"grant_type": "client_credentials",
            "appkey": key,
            "secretkey": secret}
    PATH = "oauth2/Approval"
    URL = f"{url}/{PATH}"
    res = requests.post(URL, headers=headers, data=json.dumps(body))
    approval_key = res.json()["approval_key"]
    return approval_key

### 4. 해외선물옵션 ###                
                
# 해외선물옵션호가 출력라이브러리
def stockhoka_overseafut(data):
    print(data)
    recvvalue = data.split('^')  # 수신데이터를 split '^'
    
    print("종목코드	 ["+recvvalue[ 0]+"]")
    print("수신일자	 ["+recvvalue[ 1]+"]")
    print("수신시각	 ["+recvvalue[ 2]+"]")
    print("전일종가	 ["+recvvalue[ 3]+"]")
    print("====================================")
    print("매수1수량 	["+recvvalue[ 4]+"]"+",    매수1번호 	["+recvvalue[ 5]+"]"+",    매수1호가 	["+recvvalue[ 6]+"]")
    print("매도1수량 	["+recvvalue[ 7]+"]"+",    매도1번호 	["+recvvalue[ 8]+"]"+",    매도1호가 	["+recvvalue[ 9]+"]")
    print("매수2수량 	["+recvvalue[10]+"]"+",    매수2번호 	["+recvvalue[11]+"]"+",    매수2호가 	["+recvvalue[12]+"]")
    print("매도2수량 	["+recvvalue[13]+"]"+",    매도2번호 	["+recvvalue[14]+"]"+",    매도2호가 	["+recvvalue[15]+"]")
    print("매수3수량 	["+recvvalue[16]+"]"+",    매수3번호  	["+recvvalue[17]+"]"+",    매수3호가  	["+recvvalue[18]+"]")
    print("매도3수량 	["+recvvalue[19]+"]"+",    매도3번호 	["+recvvalue[20]+"]"+",    매도3호가 	["+recvvalue[21]+"]")
    print("매수4수량 	["+recvvalue[22]+"]"+",    매수4번호 	["+recvvalue[23]+"]"+",    매수4호가 	["+recvvalue[24]+"]")
    print("매도4수량 	["+recvvalue[25]+"]"+",    매도4번호 	["+recvvalue[26]+"]"+",    매도4호가 	["+recvvalue[27]+"]")
    print("매수5수량 	["+recvvalue[28 ]+"]"+",   매수5번호 	["+recvvalue[29]+"]"+",    매수5호가 	["+recvvalue[30]+"]")
    print("매도5수량 	["+recvvalue[31]+"]"+",    매도5번호 	["+recvvalue[32]+"]"+",    매도5호가 	["+recvvalue[33]+"]")
    print("====================================")
    print("전일정산가 	["+recvvalue[32]+"]")


# 해외선물옵션체결처리 출력라이브러리
def stockspurchase_overseafut(data_cnt, data):
    print("============================================")
    menulist = "종목코드|영업일자|장개시일자|장개시시각|장종료일자|장종료시각|전일종가|수신일자|수신시각|본장_전산장구분|체결가격|체결수량|전일대비가|등락률|시가|고가|저가|누적거래량|전일대비부호|체결구분|수신시각2만분의일초|전일정산가|전일정산가대비|전일정산가대비가격|전일정산가대비율"  
    menustr = menulist.split('|')
    pValue = data.split('^')
    print(pValue)
    i = 0
    for cnt in range(data_cnt):  # 넘겨받은 체결데이터 개수만큼 print 한다
        print("### [%d / %d]" % (cnt + 1, data_cnt))
        for menu in menustr:
            print("%-13s[%s]" % (menu, pValue[i]))
            i += 1


# 해외선물옵션 체결통보 출력라이브러리
def stocksigningnotice_overseafut(data, key, iv):
    menulist = "유저ID|계좌번호|주문일자|주문번호|원주문일자|원주문번호|종목명|정정취소구분코드|매도매수구분코드|복합주문구분코드|가격구분코드|FM거래소접수구분코드|주문수량|FMLIMIT가격|FMSTOP주문가격|총체결수량|총체결단가|잔량|FM주문그룹일자|주문그룹번호|주문상세일시|조작상세일시|주문자|체결일자|체결번호|API체결번호|체결수량|FM체결가격|통화코드|위탁수수료|주문매체온라인여부|FM체결금액|선물옵션종목구분코드"
    menustr1 = menulist.split('|')

    # AES256 처리 단계
    aes_dec_str = aes_cbc_base64_dec(key, iv, data)
    print(aes_dec_str)
    pValue = aes_dec_str.split('^')
    print(pValue)
    print("#### 해외선물옵션 체결통보 처리 ####")

    i = 0
    for menu in menustr1:
        print("%s  [%s]" % (menu, pValue[i]))
        i += 1

### 앱키 정의 ###

async def connect():

    g_appkey = "앱키를 입력하세요"
    g_appsceret = "앱 시크릿키를 입력하세요"
    g_approval_key = get_approval(g_appkey, g_appsceret)
    print("approval_key [%s]" % (g_approval_key))

    # url = 'ws://ops.koreainvestment.com:31000' # 모의투자계좌
    url = 'ws://ops.koreainvestment.com:21000' # 실전투자계좌
    
    # 원하는 호출을 [tr_type, tr_id, tr_key] 순서대로 리스트 만들기
    
    ### 4. 해외선물옵션 호가, 체결가, 체결통보 ###
    # code_list = [['1','HDFFF020','FCAZ22']] # 해외선물체결
    # code_list = [['1','HDFFF010','FCAZ22']] # 해외선물호가
    # code_list = [['1','HDFFF020','OESH23 C3900']] # 해외옵션체결
    # code_list = [['1','HDFFF010','OESH23 C3900']] # 해외옵션호가
    # code_list = [['1','HDFFF2C0','HTS ID를 입력하세요']] # 해외선물옵션체결통보
    code_list = [['1','HDFFF020','FCAZ22'],['1','HDFFF010','FCAZ22'],['1','HDFFF020','OESH23 C3900'],['1','HDFFF010','OESH23 C3900'],['1','HDFFF2C0','HTS ID를 입력하세요']]
    
    senddata_list=[]
    
    for i,j,k in code_list:
        temp = '{"header":{"approval_key": "%s","custtype":"P","tr_type":"%s","content-type":"utf-8"},"body":{"input":{"tr_id":"%s","tr_key":"%s"}}}'%(g_approval_key,i,j,k)
        senddata_list.append(temp)
        
    async with websockets.connect(url, ping_interval=30) as websocket:

        for senddata in senddata_list:
            await websocket.send(senddata)
            await asyncio.sleep(0.5)
            print(f"Input Command is :{senddata}")

        while True:

            try:

                data = await websocket.recv()
                await asyncio.sleep(0.5)
                # print(f"Recev Command is :{data}")  # 정제되지 않은 Request / Response 출력

                if data[0] == '0':
                    recvstr = data.split('|')  # 수신데이터가 실데이터 이전은 '|'로 나뉘어져있어 split
                    trid0 = recvstr[1]

                    if trid0 == "HDFFF010":  # 해외선물옵션호가 tr 일경우의 처리 단계
                        print("#### 해외선물옵션호가 ####")
                        stockhoka_overseafut(recvstr[3])
                        await asyncio.sleep(0.5)

                    elif trid0 == "HDFFF020":  # 해외선물옵션체결 데이터 처리
                        print("#### 해외선물옵션체결 ####")
                        data_cnt = int(recvstr[2])  # 체결데이터 개수
                        stockspurchase_overseafut(data_cnt, recvstr[3])
                        await asyncio.sleep(0.5)

                elif data[0] == '1':

                    recvstr = data.split('|')  # 수신데이터가 실데이터 이전은 '|'로 나뉘어져있어 split
                    trid0 = recvstr[1]

                    if trid0 == "HDFFF2C0":  # 해외선물옵션체결 통보 처리
                        stocksigningnotice_overseafut(recvstr[3], aes_key, aes_iv)

                else:

                    jsonObject = json.loads(data)
                    trid = jsonObject["header"]["tr_id"]

                    if trid != "PINGPONG":
                        rt_cd = jsonObject["body"]["rt_cd"]

                        if rt_cd == '1':  # 에러일 경우 처리

                            if jsonObject["body"]["msg1"] != 'ALREADY IN SUBSCRIBE':
                                print("### ERROR RETURN CODE [ %s ][ %s ] MSG [ %s ]" % (jsonObject["header"]["tr_key"], rt_cd, jsonObject["body"]["msg1"]))
                            break

                        elif rt_cd == '0':  # 정상일 경우 처리
                            print("### RETURN CODE [ %s ][ %s ] MSG [ %s ]" % (jsonObject["header"]["tr_key"], rt_cd, jsonObject["body"]["msg1"]))

                            # 체결통보 처리를 위한 AES256 KEY, IV 처리 단계
                            if trid == "HDFFF2C0": # 해외선물옵션
                                aes_key = jsonObject["body"]["output"]["key"]
                                aes_iv = jsonObject["body"]["output"]["iv"]
                                print("### TRID [%s] KEY[%s] IV[%s]" % (trid, aes_key, aes_iv))  

                    elif trid == "PINGPONG":
                        print("### RECV [PINGPONG] [%s]" % (data))
                        await websocket.pong(data)
                        print("### SEND [PINGPONG] [%s]" % (data))

            except websockets.ConnectionClosed:
                continue
                    
                    
# 비동기로 서버에 접속한다.
asyncio.get_event_loop().run_until_complete(connect())
asyncio.get_event_loop().close()