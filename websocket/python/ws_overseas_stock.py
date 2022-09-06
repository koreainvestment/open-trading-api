# 웹 소켓 모듈을 선언한다.
import websockets
import json
import os
import asyncio
import time

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from base64 import b64decode

clearConsole = lambda: os.system('cls' if os.name in ('nt', 'dos') else 'clear')

key_bytes = 32


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


# 해외주식체결 출력라이브러리
def stockhoka(data):
    """ 넘겨받는데이터가 정상인지 확인
    print("stockhoka[%s]"%(data))
    """
    recvvalue = data.split('^')  # 수신데이터를 split '^'

    print("실시간종목코드 [" + recvvalue[0] + "]" + ", 종목코드 [" + recvvalue[1] + "]")
    print("소숫점자리수 [" + recvvalue[2] + "]")
    print("현지일자 [" + recvvalue[3] + "]" + ", 현지시간 [" + recvvalue[4] + "]")
    print("한국일자 [" + recvvalue[5] + "]" + ", 한국시간 [" + recvvalue[6] + "]")
    print("======================================")
    print("매수총 잔량        [%s]" % (recvvalue[7]))
    print("매수총잔량대비      [%s]" % (recvvalue[9]))
    print("매도총 잔량        [%s]" % (recvvalue[8]))
    print("매도총잔략대비      [%s]" % (recvvalue[10]))
    print("매수호가           [%s]" % (recvvalue[11]))
    print("매도호가           [%s]" % (recvvalue[12]))
    print("매수잔량           [%s]" % (recvvalue[13]))
    print("매도잔량           [%s]" % (recvvalue[14]))
    print("매수잔량대비        [%s]" % (recvvalue[15]))
    print("매도잔량대비        [%s]" % (recvvalue[16]))


# 해외주식체결처리 출력라이브러리
def stockspurchase(data_cnt, data):
    print("============================================")
    menulist = "실시간종목코드|종목코드|수수점자리수|현지영업일자|현지일자|현지시간|한국일자|한국시간|시가|고가|저가|현재가|대비구분|전일대비|등락율|매수호가|매도호가|매수잔량|매도잔량|체결량|거래량|거래대금|매도체결량|매수체결량|체결강도|시장구분"
    menustr = menulist.split('|')
    pValue = data.split('^')
    i = 0
    for cnt in range(data_cnt):  # 넘겨받은 체결데이터 개수만큼 print 한다
        print("### [%d / %d]" % (cnt + 1, data_cnt))
        for menu in menustr:
            print("%-13s[%s]" % (menu, pValue[i]))
            i += 1


# 해외주식체결통보 출력라이브러리
def stocksigningnotice(data, key, iv):
    menulist = "고객 ID|계좌번호|주문번호|원주문번호|매도매수구분|정정구분|주문종류2|주식단축종목코드|체결 수량|체결단가|주식체결시간|거부여부|체결여부|접수여부|지점번호|주문수량|계좌명|체결종목명|해외종목구분|담보유형코드|담보대출일자"
    menustr1 = menulist.split('|')

    # AES256 처리 단계
    aes_dec_str = aes_cbc_base64_dec(key, iv, data)
    pValue = aes_dec_str.split('^')

    i = 0
    for menu in menustr1:
        print("%s  [%s]" % (menu, pValue[i]))
        i += 1


async def connect():
    # 웹 소켓에 접속.( 주석은 koreainvest test server for websocket)
    ## 시세데이터를 받기위한 데이터를 미리 할당해서 사용한다.

    g_appkey = '앱키를 입력하세요'
    g_appsceret = '앱시크리트를 입력하세요'
    g_personalsecKey = ''

    stockcode = '종목코드입력하세요'  #  D+시장구분(3자리)+종목코드
                                   # 예) DNASAAPL : D+NAS(나스닥)+AAPL(애플)
    htsid = 'HTS ID를 입력하세요'  # 체결통보용 htsid 입력
    custtype = 'P'  # customer type, 개인:'P' 법인 'B'
    url = 'ws://ops.koreainvestment.com:21000'
    async with websockets.connect(url, ping_interval=None) as websocket:

        """" 주석처리는 더블쿼트 3개로 처리
        """
        while True:
            print("1.해외주식호가, 2.해외주식호가해제, 3.해외주식체결, 4.해외주식체결해제, 5.해외주식체결통보(고객), 6.해외주식체결통보해제(고객), 7.해외주식체결통보(모의), 8.해외주식체결통보해제(모의)")
            print("Input Command :")
            cmd = input()

            # 입력값 체크 step
            if cmd < '0' or cmd > '9':
                print("> Wrong Input Data", cmd)
                continue
            elif cmd == '0':
                print("Exit!!")
                break

            # 입력값에 따라 전송 데이터셋 구분 처리
            if cmd == '1':  # 해외주식호가 등록
                tr_id = 'HDFSASP1'
                tr_type = '1'
            elif cmd == '2':  # 해외주식호가 등록해제
                tr_id = 'HDFSASP1'
                tr_type = '2'
            elif cmd == '3':  # 해외주식체결 등록
                tr_id = 'HDFSCNT0'
                tr_type = '1'
            elif cmd == '4':  # 해외주식체결 등록해제
                tr_id = 'HDFSCNT0'
                tr_type = '2'
            elif cmd == '5':  # 해외주식체결통보 등록(고객용)
                tr_id = 'H0GSCNI0'  # 고객체결통보
                tr_type = '1'
            elif cmd == '6':  # 해외주식체결통보 등록해제(고객용)
                tr_id = 'H0GSCNI0'  # 고객체결통보
                tr_type = '2'
            elif cmd == '7':  # 해외주식체결통보 등록(모의)
                tr_id = 'H0GSCNI9'  # 테스트용 직원체결통보
                tr_type = '1'
            elif cmd == '8':  # 해외주식체결통보 등록해제(모의)
                tr_id = 'H0GSCNI9'  # 테스트용 직원체결통보
                tr_type = '2'
            else:
                senddata = 'wrong inert data'

            # send json, 체결통보는 tr_key 입력항목이 상이하므로 분리를 한다.
            if cmd == '5' or cmd == '6' or cmd == '7' or cmd == '8':
                senddata = '{"header":{"appkey":"' + g_appkey + '","appsecret":"' + g_appsceret + '","personalseckey":"' + g_personalsecKey + '","custtype":"' + custtype + '","tr_type":"' + tr_type + '","content-type":"utf-8"},"body":{"input":{"tr_id":"' + tr_id + '","tr_key":"' + htsid + '"}}}'
            else:
                senddata = '{"header":{"appkey":"' + g_appkey + '","appsecret":"' + g_appsceret + '","personalseckey":"' + g_personalsecKey + '","custtype":"' + custtype + '","tr_type":"' + tr_type + '","content-type":"utf-8"},"body":{"input":{"tr_id":"' + tr_id + '","tr_key":"' + stockcode + '"}}}'

            print('Input Command is :', senddata)

            await websocket.send(senddata)
            time.sleep(1)

            # 데이터가 오기만 기다린다.
            while True:
                data = await websocket.recv()
                print("Recev Command is :", data)
                if data[0] == '0' or data[0] == '1':  # 실시간 데이터일 경우
                    trid = jsonObject["header"]["tr_id"]

                    if data[0] == '0':
                        recvstr = data.split('|')  # 수신데이터가 실데이터 이전은 '|'로 나뉘어져있어 split
                        trid0 = recvstr[1]
                        if trid0 == "HDFSASP1":  # 해외주식호가tr 일경우의 처리 단계
                            print("#### 해외주식호가 ####")
                            stockhoka(recvstr[3])
                            time.sleep(1)

                        elif trid0 == "HDFSCNT0":  # 주식체결 데이터 처리
                            print("#### 해외주식체결 ####")
                            data_cnt = int(recvstr[2])  # 체결데이터 개수
                            stockspurchase(data_cnt, recvstr[3])

                    elif data[0] == '1':
                        recvstr = data.split('|')  # 수신데이터가 실데이터 이전은 '|'로 나뉘어져있어 split
                        trid0 = recvstr[1]
                        if trid0 == "H0GSCNI0" or trid0 == "H0GSCNI9" or trid0 == "H0GSCNI0" or trid0 == "H0GSCNI9":  # 해외주실체결 통보 처리
                            print("#### 해외주식체결통보 ####")
                            stocksigningnotice(recvstr[3], aes_key, aes_iv)
                            await websocket.send(senddata)

                    # clearConsole()
                    # break;
                else:
                    jsonObject = json.loads(data)
                    trid = jsonObject["header"]["tr_id"]

                    if trid != "PINGPONG":
                        rt_cd = jsonObject["body"]["rt_cd"]
                        if rt_cd == '1':  # 에러일 경우 처리
                            print("### ERROR RETURN CODE [ %s ][ %s ] MSG [ %s ]" % (jsonObject["header"]["tr_key"], rt_cd, jsonObject["body"]["msg1"]))
                            #break
                        elif rt_cd == '0':  # 정상일 경우 처리
                            print("### RETURN CODE [ %s ][ %s ] MSG [ %s ]" % (jsonObject["header"]["tr_key"], rt_cd, jsonObject["body"]["msg1"]))
                            # 체결통보 처리를 위한 AES256 KEY, IV 처리 단계
                            if trid == "H0GSCNI0" or trid == "H0GSCNI9" or trid == "H0GSCNI0" or trid == "H0GSCNI9":
                                aes_key = jsonObject["body"]["output"]["key"]
                                aes_iv = jsonObject["body"]["output"]["iv"]
                                print("### TRID [%s] KEY[%s] IV[%s]" % (trid, aes_key, aes_iv))

                    elif trid == "PINGPONG":
                        print("### RECV [PINGPONG] [%s]" % (data))
                        await websocket.send(data)
                        print("### SEND [PINGPONG] [%s]" % (data))


# 비동기로 서버에 접속한다.
asyncio.get_event_loop().run_until_complete(connect())
asyncio.get_event_loop().close()
