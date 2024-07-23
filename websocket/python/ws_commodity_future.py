# -*- coding: utf-8 -*-
### 모듈 임포트 ###
import os
import sys
import json
import time
import requests
import asyncio
import traceback
import websockets

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
    time.sleep(0.05)
    res = requests.post(URL, headers=headers, data=json.dumps(body))
    approval_key = res.json()["approval_key"]
    return approval_key


# 상품선물호가 출력라이브러리
def stockhoka_productfuts(data):

    # print(data)
    recvvalue = data.split('^')  # 수신데이터를 split '^'
 
    print("상품선물  ["+recvvalue[ 0]+"]")
    print("영업시간  ["+recvvalue[ 1]+"]")
    print("====================================")
    print("선물매도호가1	["+recvvalue[ 2]+"]"+",    매도호가건수1	["+recvvalue[12]+"]"+",    매도호가잔량1	["+recvvalue[22]+"]")
    print("선물매도호가2	["+recvvalue[ 3]+"]"+",    매도호가건수2	["+recvvalue[13]+"]"+",    매도호가잔량2	["+recvvalue[23]+"]")
    print("선물매도호가3	["+recvvalue[ 4]+"]"+",    매도호가건수3	["+recvvalue[14]+"]"+",    매도호가잔량3	["+recvvalue[24]+"]")
    print("선물매도호가4	["+recvvalue[ 5]+"]"+",    매도호가건수4	["+recvvalue[15]+"]"+",    매도호가잔량4	["+recvvalue[25]+"]")
    print("선물매도호가5	["+recvvalue[ 6]+"]"+",    매도호가건수5	["+recvvalue[16]+"]"+",    매도호가잔량5	["+recvvalue[26]+"]")
    print("선물매수호가1	["+recvvalue[ 7]+"]"+",    매수호가건수1	["+recvvalue[17]+"]"+",    매수호가잔량1	["+recvvalue[27]+"]")
    print("선물매수호가2	["+recvvalue[ 8]+"]"+",    매수호가건수2	["+recvvalue[18]+"]"+",    매수호가잔량2	["+recvvalue[28]+"]")
    print("선물매수호가3	["+recvvalue[ 9]+"]"+",    매수호가건수3	["+recvvalue[19]+"]"+",    매수호가잔량3	["+recvvalue[29]+"]")
    print("선물매수호가4	["+recvvalue[10 ]+"]"+",    매수호가건수4	["+recvvalue[20]+"]"+",    매수호가잔량4	["+recvvalue[30]+"]")
    print("선물매수호가5	["+recvvalue[11]+"]"+",    매수호가건수5	["+recvvalue[21]+"]"+",    매수호가잔량5	["+recvvalue[31]+"]")
    print("====================================")
    print("총매도호가건수	["+recvvalue[32]+"]"+",    총매도호가잔량	["+recvvalue[34]+"]"+",    총매도호가잔량증감	["+recvvalue[36]+"]")
    print("총매수호가건수	["+recvvalue[33]+"]"+",    총매수호가잔량	["+recvvalue[35]+"]"+",    총매수호가잔량증감	["+recvvalue[37]+"]") 
    
    
# 상품선물체결처리 출력라이브러리
def stockspurchase_productfuts(data_cnt, data):
    print("============================================")
    # print(data)
    menulist = "선물단축종목코드|영업시간|선물전일대비|전일대비부호|선물전일대비율|선물현재가|선물시가|선물최고가|선물최저가|최종거래량|누적거래량|누적거래대금|HTS이론가|시장베이시스|괴리율|근월물약정가|원월물약정가|스프레드|미결제약정수량|미결제약정수량증감|시가시간|시가대비현재가부호|시가대비지수현재가|최고가시간|최고가대비현재가부호|최고가대비지수현재가|최저가시간|최저가대비현재가부호|최저가대비지수현재가|매수비율|체결강도|괴리도|미결제약정직전수량증감|이론베이시스|선물매도호가|선물매수호가|매도호가잔량|매수호가잔량|매도체결건수|매수체결건수|순매수체결건수|총매도수량|총매수수량|총매도호가잔량|총매수호가잔량|전일거래량대비등락율|협의대량거래량|실시간상한가|실시간하한가|실시간가격제한구분"
    menustr = menulist.split('|')
    pValue = data.split('^')
    i = 0
    for cnt in range(data_cnt):  # 넘겨받은 체결데이터 개수만큼 print 한다
        print("### [%d / %d]" % (cnt + 1, data_cnt))
        for menu in menustr:
            print("%-13s[%s]" % (menu, pValue[i]))
            i += 1

# 선물옵션 체결통보 출력라이브러리
def stocksigningnotice_futsoptn(data, key, iv):
    
    # AES256 처리 단계
    aes_dec_str = aes_cbc_base64_dec(key, iv, data)
    print(aes_dec_str)
    pValue = aes_dec_str.split('^')
    print(pValue)

    if pValue[6] == '0': # 체결통보
        print("#### 지수선물옵션 체결 통보 ####")
        menulist_sign = "고객ID|계좌번호|주문번호|원주문번호|매도매수구분|정정구분|주문종류|단축종목코드|체결수량|체결단가|체결시간|거부여부|체결여부|접수여부|지점번호|주문수량|계좌명|체결종목명|주문조건|주문그룹ID|주문그룹SEQ|주문가격"
        menustr = menulist_sign.split('|')
        i = 0
        for menu in menustr:
            print("%s  [%s]" % (menu, pValue[i]))
            i += 1

    else: # pValue[6] == 'L', 주문·정정·취소·거부 접수 통보
        
        if pValue[5] == '1': # 정정 접수 통보 (정정구분이 1일 경우)
            print("#### 지수선물옵션 정정 접수 통보 ####")
            menulist_revise = "고객ID|계좌번호|주문번호|원주문번호|매도매수구분|정정구분|주문종류|단축종목코드|정정수량|정정단가|체결시간|거부여부|체결여부|접수여부|지점번호|체결수량|계좌명|체결종목명|주문조건|주문그룹ID|주문그룹SEQ|주문가격"
            menustr = menulist_revise.split('|')
            i = 0
            for menu in menustr:
                print("%s  [%s]" % (menu, pValue[i]))
                i += 1
                
        elif pValue[5] == '2': # 취소 접수 통보 (정정구분이 2일 경우)
            print("#### 지수선물옵션 취소 접수 통보 ####")
            menulist_cancel = "고객ID|계좌번호|주문번호|원주문번호|매도매수구분|정정구분|주문종류|단축종목코드|취소수량|주문단가|체결시간|거부여부|체결여부|접수여부|지점번호|체결수량|계좌명|체결종목명|주문조건|주문그룹ID|주문그룹SEQ|주문가격"
            menustr = menulist_cancel.split('|')
            i = 0
            for menu in menustr:
                print("%s  [%s]" % (menu, pValue[i]))
                i += 1
        
        elif pValue[11] == '1': # 거부 접수 통보 (거부여부가 1일 경우)
            print("#### 지수선물옵션 거부 접수 통보 ####")
            menulist_refuse = "고객ID|계좌번호|주문번호|원주문번호|매도매수구분|정정구분|주문종류|단축종목코드|주문수량|주문단가|주문시간|거부여부|체결여부|접수여부|지점번호|체결수량|계좌명|체결종목명|주문조건|주문그룹ID|주문그룹SEQ|주문가격"
            menustr = menulist_refuse.split('|')
            i = 0
            for menu in menustr:
                print("%s  [%s]" % (menu, pValue[i]))
                i += 1
        
        else: # 주문 접수 통보 
            print("#### 지수선물옵션 주문접수 통보 ####")
            menulist_order = "고객ID|계좌번호|주문번호|원주문번호|매도매수구분|정정구분|주문종류|단축종목코드|주문수량|체결단가|체결시간|거부여부|체결여부|접수여부|지점번호|체결수량|계좌명|체결종목명|주문조건|주문그룹ID|주문그룹SEQ|주문가격"
            menustr = menulist_order.split('|')
            i = 0
            for menu in menustr:
                print("%s  [%s]" % (menu, pValue[i]))
                i += 1

        
### 앱키 정의 ###

async def connect():
    
    try:
        g_appkey = "앱키를 입력하세요"
        g_appsecret = "앱 시크릿키를 입력하세요" 

        g_approval_key = get_approval(g_appkey, g_appsecret)
        print("approval_key [%s]" % (g_approval_key))

        # url = 'ws://ops.koreainvestment.com:31000' # 모의투자계좌
        url = 'ws://ops.koreainvestment.com:21000' # 실전투자계좌

        # 원하는 호출을 [tr_type, tr_id, tr_key] 순서대로 리스트 만들기
        code_list = [['1','H0CFASP0','175V08'],['1','H0CFCNT0','175T11'], # 상품선물호가, 체결가
                     ['1','H0IFCNI0','HTS ID를 입력하세요']] # 선물옵션체결통보

        senddata_list=[]

        for i,j,k in code_list:
            temp = '{"header":{"approval_key": "%s","custtype":"P","tr_type":"%s","content-type":"utf-8"},"body":{"input":{"tr_id":"%s","tr_key":"%s"}}}'%(g_approval_key,i,j,k)         
            senddata_list.append(temp)


        async with websockets.connect(url, ping_interval=None) as websocket:

            for senddata in senddata_list:
                await websocket.send(senddata)
                await asyncio.sleep(0.5)
                print(f"Input Command is :{senddata}")

            while True:
                data = await websocket.recv()
                # await asyncio.sleep(0.5)
                # print(f"Recev Command is :{data}")  # 정제되지 않은 Request / Response 출력

                if data[0] == '0':
                    recvstr = data.split('|')  # 수신데이터가 실데이터 이전은 '|'로 나뉘어져있어 split
                    trid0 = recvstr[1]

                    if trid0 == "H0CFASP0":  # 상품선물호가 tr 일경우의 처리 단계
                        print("#### 상품선물호가 ####")
                        stockhoka_productfuts(recvstr[3])

                    elif trid0 == "H0CFCNT0":  # 상품선물체결 데이터 처리
                        print("#### 상품선물체결 ####")
                        data_cnt = int(recvstr[2])  # 체결데이터 개수
                        stockspurchase_productfuts(data_cnt, recvstr[3])          

                elif data[0] == '1':

                    recvstr = data.split('|')  # 수신데이터가 실데이터 이전은 '|'로 나뉘어져있어 split
                    trid0 = recvstr[1]

                    if trid0 == "H0IFCNI0":  # 선물옵션체결 통보 처리
                        print("#### 선물옵션 통보 처리 ####")
                        stocksigningnotice_futsoptn(recvstr[3], aes_key, aes_iv)

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
                            if trid == "H0IFCNI0": 
                                aes_key = jsonObject["body"]["output"]["key"]
                                aes_iv = jsonObject["body"]["output"]["iv"]
                                print("### TRID [%s] KEY[%s] IV[%s]" % (trid, aes_key, aes_iv))

                    elif trid == "PINGPONG":
                        print("### RECV [PINGPONG] [%s]" % (data))
                        await websocket.pong(data)
                        print("### SEND [PINGPONG] [%s]" % (data))

    # ----------------------------------------
    # 모든 함수의 공통 부분(Exception 처리)
    # ----------------------------------------
    except Exception as e:
        print('Exception Raised!')
        print(e)
        print('Connect Again!')
        time.sleep(0.1)

        # 웹소켓 다시 시작
        await connect()     
                    
                    
# # 비동기로 서버에 접속한다.
# asyncio.get_event_loop().run_until_complete(connect())
# asyncio.get_event_loop().close()

# -----------------------------------------------------------------------------
# - Name : main
# - Desc : 메인
# -----------------------------------------------------------------------------
async def main():
    try:
        # 웹소켓 시작
        await connect()

    except Exception as e:
        print('Exception Raised!')
        print(e)

        
if __name__ == "__main__":

    # noinspection PyBroadException
    try:
        # ---------------------------------------------------------------------
        # Logic Start!
        # ---------------------------------------------------------------------
        # 웹소켓 시작
        asyncio.run(main())

    except KeyboardInterrupt:
        print("KeyboardInterrupt Exception 발생!")
        print(traceback.format_exc())
        sys.exit(-100)

    except Exception:
        print("Exception 발생!")
        print(traceback.format_exc())
        sys.exit(-200)