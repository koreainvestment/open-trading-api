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

### 1-1. 국내주식 ###

# 국내주식호가 출력라이브러리
def stockhoka_domestic(data):
    """ 넘겨받는데이터가 정상인지 확인
    print("stockhoka[%s]"%(data))
    """
    recvvalue = data.split('^')  # 수신데이터를 split '^'

    print("유가증권 단축 종목코드 [" + recvvalue[0] + "]")
    print("영업시간 [" + recvvalue[1] + "]" + "시간구분코드 [" + recvvalue[2] + "]")
    print("======================================")
    print("매도호가10 [%s]    잔량10 [%s]" % (recvvalue[12], recvvalue[32]))
    print("매도호가09 [%s]    잔량09 [%s]" % (recvvalue[11], recvvalue[31]))
    print("매도호가08 [%s]    잔량08 [%s]" % (recvvalue[10], recvvalue[30]))
    print("매도호가07 [%s]    잔량07 [%s]" % (recvvalue[9], recvvalue[29]))
    print("매도호가06 [%s]    잔량06 [%s]" % (recvvalue[8], recvvalue[28]))
    print("매도호가05 [%s]    잔량05 [%s]" % (recvvalue[7], recvvalue[27]))
    print("매도호가04 [%s]    잔량04 [%s]" % (recvvalue[6], recvvalue[26]))
    print("매도호가03 [%s]    잔량03 [%s]" % (recvvalue[5], recvvalue[25]))
    print("매도호가02 [%s]    잔량02 [%s]" % (recvvalue[4], recvvalue[24]))
    print("매도호가01 [%s]    잔량01 [%s]" % (recvvalue[3], recvvalue[23]))
    print("--------------------------------------")
    print("매수호가01 [%s]    잔량01 [%s]" % (recvvalue[13], recvvalue[33]))
    print("매수호가02 [%s]    잔량02 [%s]" % (recvvalue[14], recvvalue[34]))
    print("매수호가03 [%s]    잔량03 [%s]" % (recvvalue[15], recvvalue[35]))
    print("매수호가04 [%s]    잔량04 [%s]" % (recvvalue[16], recvvalue[36]))
    print("매수호가05 [%s]    잔량05 [%s]" % (recvvalue[17], recvvalue[37]))
    print("매수호가06 [%s]    잔량06 [%s]" % (recvvalue[18], recvvalue[38]))
    print("매수호가07 [%s]    잔량07 [%s]" % (recvvalue[19], recvvalue[39]))
    print("매수호가08 [%s]    잔량08 [%s]" % (recvvalue[20], recvvalue[40]))
    print("매수호가09 [%s]    잔량09 [%s]" % (recvvalue[21], recvvalue[41]))
    print("매수호가10 [%s]    잔량10 [%s]" % (recvvalue[22], recvvalue[42]))
    print("======================================")
    print("총매도호가 잔량        [%s]" % (recvvalue[43]))
    print("총매도호가 잔량 증감   [%s]" % (recvvalue[54]))
    print("총매수호가 잔량        [%s]" % (recvvalue[44]))
    print("총매수호가 잔량 증감   [%s]" % (recvvalue[55]))
    print("시간외 총매도호가 잔량 [%s]" % (recvvalue[45]))
    print("시간외 총매수호가 증감 [%s]" % (recvvalue[46]))
    print("시간외 총매도호가 잔량 [%s]" % (recvvalue[56]))
    print("시간외 총매수호가 증감 [%s]" % (recvvalue[57]))
    print("예상 체결가            [%s]" % (recvvalue[47]))
    print("예상 체결량            [%s]" % (recvvalue[48]))
    print("예상 거래량            [%s]" % (recvvalue[49]))
    print("예상체결 대비          [%s]" % (recvvalue[50]))
    print("부호                   [%s]" % (recvvalue[51]))
    print("예상체결 전일대비율    [%s]" % (recvvalue[52]))
    print("누적거래량             [%s]" % (recvvalue[53]))
    print("주식매매 구분코드      [%s]" % (recvvalue[58]))

    
# 국내주식체결처리 출력라이브러리
def stockspurchase_domestic(data_cnt, data):
    print("============================================")
    menulist = "유가증권단축종목코드|주식체결시간|주식현재가|전일대비부호|전일대비|전일대비율|가중평균주식가격|주식시가|주식최고가|주식최저가|매도호가1|매수호가1|체결거래량|누적거래량|누적거래대금|매도체결건수|매수체결건수|순매수체결건수|체결강도|총매도수량|총매수수량|체결구분|매수비율|전일거래량대비등락율|시가시간|시가대비구분|시가대비|최고가시간|고가대비구분|고가대비|최저가시간|저가대비구분|저가대비|영업일자|신장운영구분코드|거래정지여부|매도호가잔량|매수호가잔량|총매도호가잔량|총매수호가잔량|거래량회전율|전일동시간누적거래량|전일동시간누적거래량비율|시간구분코드|임의종료구분코드|정적VI발동기준가"
    menustr = menulist.split('|')
    pValue = data.split('^')
    i = 0
    for cnt in range(data_cnt):  # 넘겨받은 체결데이터 개수만큼 print 한다
        print("### [%d / %d]" % (cnt + 1, data_cnt))
        for menu in menustr:
            print("%-13s[%s]" % (menu, pValue[i]))
            i += 1

            
# 국내주식예상체결 출력라이브러리
def stockexppurchase_domestic(data_cnt, data):
    print("============================================")
    menulist = "유가증권단축종목코드|주식체결시간|주식현재가|전일대비구분|전일대비|등락율|가중평균주식가격|시가|고가|저가|매도호가|매수호가|거래량|누적거래량|누적거래대금|매도체결건수|매수체결건수|순매수체결건수|체결강도|총매도수량|총매수수량|체결구분|매수비율|전일거래량대비등락율|시가시간|시가대비구분|시가대비|최고가시간|고가대비구분|고가대비|최저가시간|저가대비구분|저가대비|영업일자|신장운영구분코드|거래정지여부|매도호가잔량1|매수호가잔량1|총매도호가잔량|총매수호가잔량|거래량회전율|전일동시간누적거래량|전일동시간누적거래량비율|시간구분코드|임의종료구분코드"
    menustr = menulist.split('|')
    pValue = data.split('^')
    i = 0
    for cnt in range(data_cnt):  # 넘겨받은 체결데이터 개수만큼 print 한다
        print("### [%d / %d]" % (cnt + 1, data_cnt))
        for menu in menustr:
            print("%-13s[%s]" % (menu, pValue[i]))
            i += 1

            
# 국내주식체결통보 출력라이브러리
def stocksigningnotice_domestic(data, key, iv):
    
    # AES256 처리 단계
    aes_dec_str = aes_cbc_base64_dec(key, iv, data)
    pValue = aes_dec_str.split('^')

    if pValue[13] == '2': # 체결통보
        print("#### 국내주식 체결 통보 ####")
        menulist = "고객ID|계좌번호|주문번호|원주문번호|매도매수구분|정정구분|주문종류|주문조건|주식단축종목코드|체결수량|체결단가|주식체결시간|거부여부|체결여부|접수여부|지점번호|주문수량|계좌명|체결종목명|신용구분|신용대출일자|체결종목명40|주문가격"
        menustr1 = menulist.split('|')
    else:
        print("#### 국내주식 주문·정정·취소·거부 접수 통보 ####")
        menulist = "고객ID|계좌번호|주문번호|원주문번호|매도매수구분|정정구분|주문종류|주문조건|주식단축종목코드|주문수량|주문가격|주식체결시간|거부여부|체결여부|접수여부|지점번호|주문수량|계좌명|주문종목명|신용구분|신용대출일자|체결종목명40|체결단가"
        menustr1 = menulist.split('|')
    
    i = 0
    for menu in menustr1:
        print("%s  [%s]" % (menu, pValue[i]))
        i += 1

# 국내주식 실시간회원사 출력라이브러리
def stocksmember_domestic(data_cnt, data):
    print("============================================")
    print(data)
    menulist = "유가증권단축종목코드|매도2회원사명1|매도2회원사명2|매도2회원사명3|매도2회원사명4|매도2회원사명5|매수회원사명1|매수회원사명2|매수회원사명3|매수회원사명4|매수회원사명5|총매도수량1|총매도수량2|총매도수량3|총매도수량4|총매도수량5|총매수2수량1|총매수2수량2|총매수2수량3|총매수2수량4|총매수2수량5|매도거래원구분1|매도거래원구분2|매도거래원구분3|매도거래원구분4|매도거래원구분5|매수거래원구분1|매수거래원구분2|매수거래원구분3|매수거래원구분4|매수거래원구분5|매도거래원코드1|매도거래원코드2|매도거래원코드3|매도거래원코드4|매도거래원코드5|매수거래원코드1|매수거래원코드2|매수거래원코드3|매수거래원코드4|매수거래원코드5|매도회원사비중1|매도회원사비중2|매도회원사비중3|매도회원사비중4|매도회원사비중5|매수2회원사비중1|매수2회원사비중2|매수2회원사비중3|매수2회원사비중4|매수2회원사비중5|매도수량증감1|매도수량증감2|매도수량증감3|매도수량증감4|매도수량증감5|매수2수량증감1|매수2수량증감2|매수2수량증감3|매수2수량증감4|매수2수량증감5|외국계총매도수량|외국계총매수2수량|외국계총매도수량증감|외국계총매수2수량증감|외국계순매수수량|외국계매도비중|외국계매수2비중|매도2영문회원사명1|매도2영문회원사명2|매도2영문회원사명3|매도2영문회원사명4|매도2영문회원사명5|매수영문회원사명1|매수영문회원사명2|매수영문회원사명3|매수영문회원사명4|매수영문회원사명5"
    menustr = menulist.split('|')
    pValue = data.split('^')
    i = 0
    for cnt in range(data_cnt):  # 넘겨받은 체결데이터 개수만큼 print 한다
        print("### [%d / %d]" % (cnt + 1, data_cnt))
        for menu in menustr:
            print("%-13s[%s]" % (menu, pValue[i]))
            i += 1              
            
            
# 국내주식 실시간프로그램매매 출력라이브러리
def stocksprogramtrade_domestic(data_cnt, data):
    print("============================================")
    menulist = "유가증권단축종목코드|주식체결시간|매도체결량|매도거래대금|매수2체결량|매수2거래대금|순매수체결량|순매수거래대금|매도호가잔량|매수호가잔량|전체순매수호가잔량"
    menustr = menulist.split('|')
    pValue = data.split('^')
    i = 0
    for cnt in range(data_cnt):  # 넘겨받은 체결데이터 개수만큼 print 한다
        print("### [%d / %d]" % (cnt + 1, data_cnt))
        for menu in menustr:
            print("%-13s[%s]" % (menu, pValue[i]))
            i += 1
            
            
# 국내주식 장운영정보 출력라이브러리
def stocksmarketinfo_domestic(data_cnt, data):
    print("============================================")
    print(data)
    menulist = "유가증권단축종목코드|거래정지여부|거래정지사유내용|장운영구분코드|예상장운영구분코드|임의연장구분코드|동시호가배분처리구분코드|종목상태구분코드|VI적용구분코드|시간외단일가VI적용구분코드"
    menustr = menulist.split('|')
    pValue = data.split('^')
    i = 0
    for cnt in range(data_cnt):  # 넘겨받은 체결데이터 개수만큼 print 한다
        print("### [%d / %d]" % (cnt + 1, data_cnt))
        for menu in menustr:
            print("%-13s[%s]" % (menu, pValue[i]))
            i += 1                  

# 국내주식시간외체결 출력라이브러리
def stockoverpurchase_domestic(data_cnt, data):
    print("============================================")
    menulist = "유가증권단축종목코드|주식체결시간|주식현재가|전일대비구분|전일대비|등락율|가중평균주식가격|시가|고가|저가|매도호가|매수호가|거래량|누적거래량|누적거래대금|매도체결건수|매수체결건수|순매수체결건수|체결강도|총매도수량|총매수수량|체결구분|매수비율|전일거래량대비등락율|시가시간|시가대비구분|시가대비|최고가시간|고가대비구분|고가대비|최저가시간|저가대비구분|저가대비|영업일자|신장운영구분코드|거래정지여부|매도호가잔량1|매수호가잔량1|총매도호가잔량|총매수호가잔량|거래량회전율|전일동시간누적거래량|전일동시간누적거래량비율"
    menustr = menulist.split('|')
    pValue = data.split('^')
    i = 0
    for cnt in range(data_cnt):  # 넘겨받은 체결데이터 개수만큼 print 한다
        print("### [%d / %d]" % (cnt + 1, data_cnt))
        for menu in menustr:
            print("%-13s[%s]" % (menu, pValue[i]))
            i += 1

            
# 국내주식시간외예상체결 출력라이브러리
def stockoverexppurchase_domestic(data_cnt, data):
    print("============================================")
    menulist = "유가증권단축종목코드|주식체결시간|주식현재가|전일대비구분|전일대비|등락율|가중평균주식가격|시가|고가|저가|매도호가|매수호가|거래량|누적거래량|누적거래대금|매도체결건수|매수체결건수|순매수체결건수|체결강도|총매도수량|총매수수량|체결구분|매수비율|전일거래량대비등락율|시가시간|시가대비구분|시가대비|최고가시간|고가대비구분|고가대비|최저가시간|저가대비구분|저가대비|영업일자|신장운영구분코드|거래정지여부|매도호가잔량1|매수호가잔량1|총매도호가잔량|총매수호가잔량|거래량회전율|전일동시간누적거래량|전일동시간누적거래량비율"
    menustr = menulist.split('|')
    pValue = data.split('^')
    i = 0
    for cnt in range(data_cnt):  # 넘겨받은 체결데이터 개수만큼 print 한다
        print("### [%d / %d]" % (cnt + 1, data_cnt))
        for menu in menustr:
            print("%-13s[%s]" % (menu, pValue[i]))
            i += 1
            
            
# 국내주식시간외호가 출력라이브러리
def stockoverhoka_domestic(data):
    """ 넘겨받는데이터가 정상인지 확인
    print("stockoverhoka_domestic[%s]"%(data))
    """
    recvvalue = data.split('^')  # 수신데이터를 split '^'

    print("유가증권 단축 종목코드 [" + recvvalue[0] + "]")
    print("영업시간 [" + recvvalue[1] + "]" + "시간구분코드 [" + recvvalue[2] + "]")
    print("======================================")
    print("매도호가10 [%s]    잔량10 [%s]" % (recvvalue[12], recvvalue[32]))
    print("매도호가09 [%s]    잔량09 [%s]" % (recvvalue[11], recvvalue[31]))
    print("매도호가08 [%s]    잔량08 [%s]" % (recvvalue[10], recvvalue[30]))
    print("매도호가07 [%s]    잔량07 [%s]" % (recvvalue[9], recvvalue[29]))
    print("매도호가06 [%s]    잔량06 [%s]" % (recvvalue[8], recvvalue[28]))
    print("매도호가05 [%s]    잔량05 [%s]" % (recvvalue[7], recvvalue[27]))
    print("매도호가04 [%s]    잔량04 [%s]" % (recvvalue[6], recvvalue[26]))
    print("매도호가03 [%s]    잔량03 [%s]" % (recvvalue[5], recvvalue[25]))
    print("매도호가02 [%s]    잔량02 [%s]" % (recvvalue[4], recvvalue[24]))
    print("매도호가01 [%s]    잔량01 [%s]" % (recvvalue[3], recvvalue[23]))
    print("--------------------------------------")
    print("매수호가01 [%s]    잔량01 [%s]" % (recvvalue[13], recvvalue[33]))
    print("매수호가02 [%s]    잔량02 [%s]" % (recvvalue[14], recvvalue[34]))
    print("매수호가03 [%s]    잔량03 [%s]" % (recvvalue[15], recvvalue[35]))
    print("매수호가04 [%s]    잔량04 [%s]" % (recvvalue[16], recvvalue[36]))
    print("매수호가05 [%s]    잔량05 [%s]" % (recvvalue[17], recvvalue[37]))
    print("매수호가06 [%s]    잔량06 [%s]" % (recvvalue[18], recvvalue[38]))
    print("매수호가07 [%s]    잔량07 [%s]" % (recvvalue[19], recvvalue[39]))
    print("매수호가08 [%s]    잔량08 [%s]" % (recvvalue[20], recvvalue[40]))
    print("매수호가09 [%s]    잔량09 [%s]" % (recvvalue[21], recvvalue[41]))
    print("매수호가10 [%s]    잔량10 [%s]" % (recvvalue[22], recvvalue[42]))
    print("======================================")
    print("총매도호가 잔량        [%s]" % (recvvalue[43]))
    print("총매도호가 잔량 증감   [%s]" % (recvvalue[54]))
    print("총매수호가 잔량        [%s]" % (recvvalue[44]))
    print("총매수호가 잔량 증감   [%s]" % (recvvalue[55]))
    print("시간외 총매도호가 잔량 [%s]" % (recvvalue[45]))
    print("시간외 총매수호가 증감 [%s]" % (recvvalue[46]))
    print("시간외 총매도호가 잔량 [%s]" % (recvvalue[56]))
    print("시간외 총매수호가 증감 [%s]" % (recvvalue[57]))
    print("예상 체결가            [%s]" % (recvvalue[47]))
    print("예상 체결량            [%s]" % (recvvalue[48]))
    print("예상 거래량            [%s]" % (recvvalue[49]))
    print("예상체결 대비          [%s]" % (recvvalue[50]))
    print("부호                   [%s]" % (recvvalue[51]))
    print("예상체결 전일대비율    [%s]" % (recvvalue[52]))
    print("누적거래량             [%s]" % (recvvalue[53]))

### 1-2. 국내지수 ###

# 국내지수체결 출력라이브러리
def indexpurchase_domestic(data_cnt, data):
    print("============================================")
    menulist = "업종구분코드|영업시간|현재가지수|전일대비부호|업종지수전일대비|누적거래량|누적거래대금|건별거래량|건별거래대금|전일대비율|시가지수|지수최고가|지수최저가|시가대비지수현재가|시가대비지수부호|최고가대비지수현재가|최고가대비지수부호|최저가대비지수현재가|최저가대비지수부호|전일종가대비시가2비율|전일종가대비최고가비율|전일종가대비최저가비율|상한종목수|상승종목수|보합종목수|하락종목수|하한종목수|기세상승종목수|기세하락종목수|TICK대비"
    menustr = menulist.split('|')
    pValue = data.split('^')
    i = 0
    for cnt in range(data_cnt):  # 넘겨받은 체결데이터 개수만큼 print 한다
        print("### [%d / %d]" % (cnt + 1, data_cnt))
        for menu in menustr:
            print("%-13s[%s]" % (menu, pValue[i]))
            i += 1

# 국내지수예상체결 출력라이브러리
def indexexppurchase_domestic(data_cnt, data):
    print("============================================")
    menulist = "업종구분코드|영업시간|현재가지수|전일대비부호|업종지수전일대비|누적거래량|누적거래대금|건별거래량|건별거래대금|전일대비율|상한종목수|상승종목수|보합종목수|하락종목수|하한종목수"
    menustr = menulist.split('|')
    pValue = data.split('^')
    i = 0
    for cnt in range(data_cnt):  # 넘겨받은 체결데이터 개수만큼 print 한다
        print("### [%d / %d]" % (cnt + 1, data_cnt))
        for menu in menustr:
            print("%-13s[%s]" % (menu, pValue[i]))
            i += 1

# 국내지수 실시간프로그램매매 출력라이브러리
def indexprogramtrade_domestic(data_cnt, data):
    print("============================================")
    menulist = "업종구분코드|영업시간|차익매도위탁체결량|차익매도자기체결량|차익매수2위탁체결량|차익매수2자기체결량|비차익매도위탁체결량|비차익매도자기체결량|비차익매수2위탁체결량|비차익매수2자기체결량|차익매도위탁체결금액|차익매도자기체결금액|차익매수2위탁체결금액|차익매수2자기체결금액|비차익매도위탁체결금액|비차익매도자기체결금액|비차익매수2위탁체결금액|비차익매수2자기체결금액|차익합계매도거래량|차익합계매도거래량비율|차익합계매도거래대금|차익합계매도거래대금비율|차익합계매수2거래량|차익합계매수거래량비율|차익합계매수2거래대금|차익합계매수거래대금비율|차익합계순매수수량|차익합계순매수수량비율|차익합계순매수거래대금|차익합계순매수거래대금비율|비차익합계매도거래량|비차익합계매도거래량비율|비차익합계매도거래대금|비차익합계매도거래대금비율|비차익합계매수2거래량|비차익합계매수거래량비율|비차익합계매수2거래대금|비차익합계매수거래대금비율|비차익합계순매수수량|비차익합계순매수수량비율|비차익합계순매수거래대금|비차익합계순매수거래대금비|전체위탁매도거래량|위탁매도거래량비율|전체위탁매도거래대금|위탁매도거래대금비율|전체위탁매수2거래량|위탁매수거래량비율|전체위탁매수2거래대금|위탁매수거래대금비율|전체위탁순매수수량|위탁순매수수량비율|전체위탁순매수거래대금|위탁순매수금액비율|전체자기매도거래량|자기매도거래량비율|전체자기매도거래대금|자기매도거래대금비율|전체자기매수2거래량|자기매수거래량비율|전체자기매수2거래대금|자기매수거래대금비율|전체자기순매수수량|자기순매수량비율|전체자기순매수거래대금|자기순매수대금비율|총매도수량|전체매도거래량비율|총매도거래대금|전체매도거래대금비율|총매수수량|전체매수거래량비율|총매수2거래대금|전체매수거래대금비율|전체순매수수량|전체합계순매수수량비율|전체순매수거래대금|전체순매수거래대금비율|차익위탁순매수수량|차익위탁순매수거래대금|차익자기순매수수량|차익자기순매수거래대금|비차익위탁순매수수량|비차익위탁순매수거래대금|비차익자기순매수수량|비차익자기순매수거래대금|누적거래량|누적거래대금"
    menustr = menulist.split('|')
    pValue = data.split('^')
    i = 0
    for cnt in range(data_cnt):  # 넘겨받은 체결데이터 개수만큼 print 한다
        print("### [%d / %d]" % (cnt + 1, data_cnt))
        for menu in menustr:
            print("%-13s[%s]" % (menu, pValue[i]))
            i += 1            

### 1-3. ELW ###            
            
# ELW호가 출력라이브러리
def elwhoka_domestic(data):
    """ 넘겨받는데이터가 정상인지 확인
    print("elwhoka_domestic[%s]"%(data))
    """
    recvvalue = data.split('^')  # 수신데이터를 split '^'

    print("ELW 종목코드 [" + recvvalue[0] + "]")
    print("영업시간 [" + recvvalue[1] + "]" + "시간구분코드 [" + recvvalue[2] + "]")
    print("======================================")
    print("매도호가10 [%s]    잔량10 [%s]    LP매도호가잔량10 [%s]" % (recvvalue[12], recvvalue[32], recvvalue[59]))
    print("매도호가09 [%s]    잔량09 [%s]    LP매도호가잔량09 [%s]" % (recvvalue[11], recvvalue[31], recvvalue[58]))
    print("매도호가08 [%s]    잔량08 [%s]    LP매도호가잔량08 [%s]" % (recvvalue[10], recvvalue[30], recvvalue[57]))
    print("매도호가07 [%s]    잔량07 [%s]    LP매도호가잔량07 [%s]" % (recvvalue[9], recvvalue[29], recvvalue[56]))
    print("매도호가06 [%s]    잔량06 [%s]    LP매도호가잔량06 [%s]" % (recvvalue[8], recvvalue[28], recvvalue[55]))
    print("매도호가05 [%s]    잔량05 [%s]    LP매도호가잔량05 [%s]" % (recvvalue[7], recvvalue[27], recvvalue[54]))
    print("매도호가04 [%s]    잔량04 [%s]    LP매도호가잔량04 [%s]" % (recvvalue[6], recvvalue[26], recvvalue[53]))
    print("매도호가03 [%s]    잔량03 [%s]    LP매도호가잔량03 [%s]" % (recvvalue[5], recvvalue[25], recvvalue[52]))
    print("매도호가02 [%s]    잔량02 [%s]    LP매도호가잔량02 [%s]" % (recvvalue[4], recvvalue[24], recvvalue[51]))
    print("매도호가01 [%s]    잔량01 [%s]    LP매도호가잔량01 [%s]" % (recvvalue[3], recvvalue[23], recvvalue[50]))
    print("--------------------------------------")
    print("매수호가01 [%s]    잔량01 [%s]    LP매수호가잔량01 [%s]" % (recvvalue[13], recvvalue[33], recvvalue[60]))
    print("매수호가02 [%s]    잔량02 [%s]    LP매수호가잔량02 [%s]" % (recvvalue[14], recvvalue[34], recvvalue[61]))
    print("매수호가03 [%s]    잔량03 [%s]    LP매수호가잔량03 [%s]" % (recvvalue[15], recvvalue[35], recvvalue[62]))
    print("매수호가04 [%s]    잔량04 [%s]    LP매수호가잔량04 [%s]" % (recvvalue[16], recvvalue[36], recvvalue[63]))
    print("매수호가05 [%s]    잔량05 [%s]    LP매수호가잔량05 [%s]" % (recvvalue[17], recvvalue[37], recvvalue[64]))
    print("매수호가06 [%s]    잔량06 [%s]    LP매수호가잔량06 [%s]" % (recvvalue[18], recvvalue[38], recvvalue[65]))
    print("매수호가07 [%s]    잔량07 [%s]    LP매수호가잔량07 [%s]" % (recvvalue[19], recvvalue[39], recvvalue[66]))
    print("매수호가08 [%s]    잔량08 [%s]    LP매수호가잔량08 [%s]" % (recvvalue[20], recvvalue[40], recvvalue[67]))
    print("매수호가09 [%s]    잔량09 [%s]    LP매수호가잔량09 [%s]" % (recvvalue[21], recvvalue[41], recvvalue[68]))
    print("매수호가10 [%s]    잔량10 [%s]    LP매수호가잔량10 [%s]" % (recvvalue[22], recvvalue[42], recvvalue[69]))
    print("======================================")
    print("총매도호가 잔량        [%s]" % (recvvalue[43]))
    print("총매수호가 잔량        [%s]" % (recvvalue[44]))
    print("LP총매도호가잔량       [%s]" % (recvvalue[70]))
    print("LP총매수호가잔량       [%s]" % (recvvalue[71]))
    print("예상 체결가            [%s]" % (recvvalue[45]))
    print("예상 체결량            [%s]" % (recvvalue[46]))
    print("예상 체결대비부호      [%s]" % (recvvalue[47]))
    print("예상 체결대비          [%s]" % (recvvalue[48]))
    print("예상 체결전일대비율    [%s]" % (recvvalue[48]))
    print("예상 거래량            [%s]" % (recvvalue[72]))

    
# ELW체결처리 출력라이브러리
def elwpurchase_domestic(data_cnt, data):
    print("============================================")
    menulist = "유가증권단축종목코드|주식체결시간|주식현재가|전일대비부호|전일대비|전일대비율|가중평균주식가격|주식시가2|주식최고가|주식최저가|매도호가1|매수호가1|체결거래량|누적거래량|누적거래대금|매도체결건수|매수체결건수|순매수체결건수|체결강도|총매도수량|총매수수량|체결구분코드|매수2비율|전일거래량대비등락율|시가시간|시가2대비현재가부호|시가2대비현재가|최고가시간|최고가대비현재가부호|최고가대비현재가|최저가시간|최저가대비현재가부호|최저가대비현재가|영업일자|신장운영구분코드|거래정지여부|매도호가잔량1|매수호가잔량1|총매도호가잔량|총매수호가잔량|시간가치값|패리티|프리미엄값|기어링|손익분기비율|내재가치값|프리미엄비율|자본지지점|레버리지값|델타|감마|베가|세타|로우|HTS내재변동성|HTS이론가|거래량회전율|전일동시간누적거래량|전일동시간누적거래량비율|접근도|LP보유량|LP보유비율|LP순매도량"
    menustr = menulist.split('|')
    pValue = data.split('^')
    i = 0
    for cnt in range(data_cnt):  # 넘겨받은 체결데이터 개수만큼 print 한다
        print("### [%d / %d]" % (cnt + 1, data_cnt))
        for menu in menustr:
            print("%-13s[%s]" % (menu, pValue[i]))
            i += 1
            
            
### 2. 해외주식 ###
            
# 해외주식(아시아)호가 출력라이브러리
def stockhoka_overseas_asia(data):
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

          
# 해외주식(미국)호가 출력라이브러리
def stockhoka_overseas_usa(data):
    """ 넘겨받는데이터가 정상인지 확인
    print("stockhoka[%s]"%(data))
    """
    recvvalue = data.split('^')  # 수신데이터를 split '^'

    print("실시간종목코드 [" + recvvalue[0] + "]" + ", 종목코드 [" + recvvalue[1] + "]")
    print("소숫점자리수 [" + recvvalue[2] + "]")
    print("현지일자 [" + recvvalue[3] + "]" + ", 현지시간 [" + recvvalue[4] + "]")
    print("한국일자 [" + recvvalue[5] + "]" + ", 한국시간 [" + recvvalue[6] + "]")
    print("======================================")    
    print("매도호가10 [%s]    잔량10 [%s]" % (recvvalue[66], recvvalue[68]))
    print("매도호가09 [%s]    잔량09 [%s]" % (recvvalue[60], recvvalue[62]))
    print("매도호가08 [%s]    잔량08 [%s]" % (recvvalue[54], recvvalue[56]))
    print("매도호가07 [%s]    잔량07 [%s]" % (recvvalue[48], recvvalue[50]))
    print("매도호가06 [%s]    잔량06 [%s]" % (recvvalue[42], recvvalue[44]))
    print("매도호가05 [%s]    잔량05 [%s]" % (recvvalue[36], recvvalue[38]))
    print("매도호가04 [%s]    잔량04 [%s]" % (recvvalue[30], recvvalue[32]))
    print("매도호가03 [%s]    잔량03 [%s]" % (recvvalue[24], recvvalue[26]))
    print("매도호가02 [%s]    잔량02 [%s]" % (recvvalue[18], recvvalue[20]))
    print("매도호가01 [%s]    잔량01 [%s]" % (recvvalue[12], recvvalue[14]))
    print("--------------------------------------")
    print("매수호가01 [%s]    잔량01 [%s]" % (recvvalue[11], recvvalue[13]))
    print("매수호가02 [%s]    잔량02 [%s]" % (recvvalue[17], recvvalue[19]))
    print("매수호가03 [%s]    잔량03 [%s]" % (recvvalue[23], recvvalue[25]))
    print("매수호가04 [%s]    잔량04 [%s]" % (recvvalue[29], recvvalue[31]))
    print("매수호가05 [%s]    잔량05 [%s]" % (recvvalue[35], recvvalue[37]))
    print("매수호가06 [%s]    잔량06 [%s]" % (recvvalue[41], recvvalue[43]))
    print("매수호가07 [%s]    잔량07 [%s]" % (recvvalue[47], recvvalue[49]))
    print("매수호가08 [%s]    잔량08 [%s]" % (recvvalue[53], recvvalue[55]))
    print("매수호가09 [%s]    잔량09 [%s]" % (recvvalue[59], recvvalue[61]))
    print("매수호가10 [%s]    잔량10 [%s]" % (recvvalue[65], recvvalue[67]))
    print("======================================")
    print("매수총 잔량        [%s]" % (recvvalue[7]))
    print("매수총잔량대비      [%s]" % (recvvalue[9]))
    print("매도총 잔량        [%s]" % (recvvalue[8]))
    print("매도총잔략대비      [%s]" % (recvvalue[10]))


# 해외주식체결처리 출력라이브러리
def stockspurchase_overseas(data_cnt, data):
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
def stocksigningnotice_overseas(data, key, iv):
    menulist = "고객 ID|계좌번호|주문번호|원주문번호|매도매수구분|정정구분|주문종류2|단축종목코드|주문수량|체결단가|체결시간|거부여부|체결여부|접수여부|지점번호|체결수량|계좌명|체결종목명|해외종목구분|담보유형코드|담보대출일자"
    menustr1 = menulist.split('|')

    # AES256 처리 단계
    aes_dec_str = aes_cbc_base64_dec(key, iv, data)
    pValue = aes_dec_str.split('^')

    if pValue[12] == '2': # 체결통보
        print("#### 해외주식 체결 통보 ####")
    else:
        print("#### 해외주식 주문·정정·취소·거부 접수 통보 ####")
    
    i = 0
    for menu in menustr1:
        print("%s  [%s]" % (menu, pValue[i]))
        i += 1

### 3. 국내선물옵션 ###
            
# 지수선물호가 출력라이브러리
def stockhoka_futs(data):

    # print(data)
    recvvalue = data.split('^')  # 수신데이터를 split '^'

    print("지수선물  ["+recvvalue[ 0]+"]")
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
    print("선물매수호가4	["+recvvalue[10 ]+"]"+",   매수호가건수4	["+recvvalue[20]+"]"+",    매수호가잔량4	["+recvvalue[30]+"]")
    print("선물매수호가5	["+recvvalue[11]+"]"+",    매수호가건수5	["+recvvalue[21]+"]"+",    매수호가잔량5	["+recvvalue[31]+"]")
    print("====================================")
    print("총매도호가건수	["+recvvalue[32]+"]"+",    총매도호가잔량	["+recvvalue[34]+"]"+",    총매도호가잔량증감	["+recvvalue[36]+"]")
    print("총매수호가건수	["+recvvalue[33]+"]"+",    총매수호가잔량	["+recvvalue[35]+"]"+",    총매수호가잔량증감	["+recvvalue[37]+"]") 
    
    
# 지수옵션호가 출력라이브러리
def stockhoka_optn(data):
    # print(data)
    recvvalue = data.split('^')  # 수신데이터를 split '^'
    
    print("지수옵션  ["+recvvalue[ 0]+"]")
    print("영업시간  ["+recvvalue[ 1]+"]")
    print("====================================")
    print("옵션매도호가1	["+recvvalue[ 2]+"]"+",    매도호가건수1	["+recvvalue[12]+"]"+",    매도호가잔량1	["+recvvalue[22]+"]")
    print("옵션매도호가2	["+recvvalue[ 3]+"]"+",    매도호가건수2	["+recvvalue[13]+"]"+",    매도호가잔량2	["+recvvalue[23]+"]")
    print("옵션매도호가3	["+recvvalue[ 4]+"]"+",    매도호가건수3	["+recvvalue[14]+"]"+",    매도호가잔량3	["+recvvalue[24]+"]")
    print("옵션매도호가4	["+recvvalue[ 5]+"]"+",    매도호가건수4	["+recvvalue[15]+"]"+",    매도호가잔량4	["+recvvalue[25]+"]")
    print("옵션매도호가5	["+recvvalue[ 6]+"]"+",    매도호가건수5	["+recvvalue[16]+"]"+",    매도호가잔량5	["+recvvalue[26]+"]")
    print("옵션매수호가1	["+recvvalue[ 7]+"]"+",    매수호가건수1	["+recvvalue[17]+"]"+",    매수호가잔량1	["+recvvalue[27]+"]")
    print("옵션매수호가2	["+recvvalue[ 8]+"]"+",    매수호가건수2	["+recvvalue[18]+"]"+",    매수호가잔량2	["+recvvalue[28]+"]")
    print("옵션매수호가3	["+recvvalue[ 9]+"]"+",    매수호가건수3	["+recvvalue[19]+"]"+",    매수호가잔량3	["+recvvalue[29]+"]")
    print("옵션매수호가4	["+recvvalue[10 ]+"]"+",   매수호가건수4	["+recvvalue[20]+"]"+",    매수호가잔량4	["+recvvalue[30]+"]")
    print("옵션매수호가5	["+recvvalue[11]+"]"+",    매수호가건수5	["+recvvalue[21]+"]"+",    매수호가잔량5	["+recvvalue[31]+"]")
    print("====================================")
    print("총매도호가건수	["+recvvalue[32]+"]"+",    총매도호가잔량	["+recvvalue[34]+"]"+",    총매도호가잔량증감	["+recvvalue[36]+"]")
    print("총매수호가건수	["+recvvalue[33]+"]"+",    총매수호가잔량	["+recvvalue[35]+"]"+",    총매수호가잔량증감	["+recvvalue[37]+"]") 
    

# 지수선물체결처리 출력라이브러리
def stockspurchase_futs(data_cnt, data):
    print("============================================")
    print(data)
    menulist = "선물단축종목코드|영업시간|선물전일대비|전일대비부호|선물전일대비율|선물현재가|선물시가|선물최고가|선물최저가|최종거래량|누적거래량|누적거래대금|HTS이론가|시장베이시스|괴리율|근월물약정가|원월물약정가|스프레드|미결제약정수량|미결제약정수량증감|시가시간|시가대비현재가부호|시가대비지수현재가|최고가시간|최고가대비현재가부호|최고가대비지수현재가|최저가시간|최저가대비현재가부호|최저가대비지수현재가|매수비율|체결강도|괴리도|미결제약정직전수량증감|이론베이시스|선물매도호가|선물매수호가|매도호가잔량|매수호가잔량|매도체결건수|매수체결건수|순매수체결건수|총매도수량|총매수수량|총매도호가잔량|총매수호가잔량|전일거래량대비등락율|협의대량거래량|실시간상한가|실시간하한가|실시간가격제한구분"
    menustr = menulist.split('|')
    pValue = data.split('^')
    i = 0
    for cnt in range(data_cnt):  # 넘겨받은 체결데이터 개수만큼 print 한다
        print("### [%d / %d]" % (cnt + 1, data_cnt))
        for menu in menustr:
            print("%-13s[%s]" % (menu, pValue[i]))
            i += 1
            
            
# 지수옵션체결처리 출력라이브러리
def stockspurchase_optn(data_cnt, data):
    print("============================================")
    # print(data)
    menulist = "옵션단축종목코드|영업시간|옵션현재가|전일대비부호|옵션전일대비|전일대비율|옵션시가|옵션최고가|옵션최저가|최종거래량|누적거래량|누적거래대금|HTS이론가|HTS미결제약정수량|미결제약정수량증감|시가시간|시가대비현재가부호|시가대비지수현재가|최고가시간|최고가대비현재가부호|최고가대비지수현재가|최저가시간|최저가대비현재가부호|최저가대비지수현재가|매수2비율|프리미엄값|내재가치값|시간가치값|델타|감마|베가|세타|로우|HTS내재변동성|괴리도|미결제약정직전수량증감|이론베이시스|역사적변동성|체결강도|괴리율|시장베이시스|옵션매도호가1|옵션매수호가1|매도호가잔량1|매수호가잔량1|매도체결건수|매수체결건수|순매수체결건수|총매도수량|총매수수량|총매도호가잔량|총매수호가잔량|전일거래량대비등락율|평균변동성|협의대량누적거래량|실시간상한가|실시간하한가|실시간가격제한구분"  
    menustr = menulist.split('|')
    pValue = data.split('^')
    i = 0
    for cnt in range(data_cnt):  # 넘겨받은 체결데이터 개수만큼 print 한다
        print("### [%d / %d]" % (cnt + 1, data_cnt))
        for menu in menustr:
            print("%-13s[%s]" % (menu, pValue[i]))
            i += 1

            
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
        
            
# 주식선물호가 출력라이브러리
def stockhoka_stockfuts(data):

    # print(data)
    recvvalue = data.split('^')  # 수신데이터를 split '^'

    print("주식선물  ["+recvvalue[ 0]+"]")
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
    print("선물매수호가4	["+recvvalue[10 ]+"]"+",   매수호가건수4	["+recvvalue[20]+"]"+",    매수호가잔량4	["+recvvalue[30]+"]")
    print("선물매수호가5	["+recvvalue[11]+"]"+",    매수호가건수5	["+recvvalue[21]+"]"+",    매수호가잔량5	["+recvvalue[31]+"]")
    print("====================================")
    print("총매도호가건수	["+recvvalue[32]+"]"+",    총매도호가잔량	["+recvvalue[34]+"]"+",    총매도호가잔량증감	["+recvvalue[36]+"]")
    print("총매수호가건수	["+recvvalue[33]+"]"+",    총매수호가잔량	["+recvvalue[35]+"]"+",    총매수호가잔량증감	["+recvvalue[37]+"]") 
 
            
# 주식선물체결처리 출력라이브러리
def stockspurchase_stockfuts(data_cnt, data):
    print("============================================")
    print(data)
    menulist = "선물단축종목코드|영업시간|주식현재가|전일대비부호|전일대비|선물전일대비율|주식시가2|주식최고가|주식최저가|최종거래량|누적거래량|누적거래대금|HTS이론가|시장베이시스|괴리율|근월물약정가|원월물약정가|스프레드1|HTS미결제약정수량|미결제약정수량증감|시가시간|시가2대비현재가부호|시가2대비현재가|최고가시간|최고가대비현재가부호|최고가대비현재가|최저가시간|최저가대비현재가부호|최저가대비현재가|매수2비율|체결강도|괴리도|미결제약정직전수량증감|이론베이시스|매도호가1|매수호가1|매도호가잔량1|매수호가잔량1|매도체결건수|매수체결건수|순매수체결건수|총매도수량|총매수수량|총매도호가잔량|총매수호가잔량|전일거래량대비등락율|실시간상한가|실시간하한가|실시간가격제한구분"
    menustr = menulist.split('|')
    pValue = data.split('^')
    i = 0
    for cnt in range(data_cnt):  # 넘겨받은 체결데이터 개수만큼 print 한다
        print("### [%d / %d]" % (cnt + 1, data_cnt))
        for menu in menustr:
            print("%-13s[%s]" % (menu, pValue[i]))
            i += 1

            
# 주식옵션호가 출력라이브러리
def stockhoka_stockoptn(data):

    # print(data)
    recvvalue = data.split('^')  # 수신데이터를 split '^'
 
    print("주식옵션  ["+recvvalue[ 0]+"]")
    print("영업시간  ["+recvvalue[ 1]+"]")
    print("====================================")
    print("옵션매도호가1	["+recvvalue[ 2]+"]"+",    매도호가건수1	["+recvvalue[12]+"]"+",    매도호가잔량1	["+recvvalue[22]+"]")
    print("옵션매도호가2	["+recvvalue[ 3]+"]"+",    매도호가건수2	["+recvvalue[13]+"]"+",    매도호가잔량2	["+recvvalue[23]+"]")
    print("옵션매도호가3	["+recvvalue[ 4]+"]"+",    매도호가건수3	["+recvvalue[14]+"]"+",    매도호가잔량3	["+recvvalue[24]+"]")
    print("옵션매도호가4	["+recvvalue[ 5]+"]"+",    매도호가건수4	["+recvvalue[15]+"]"+",    매도호가잔량4	["+recvvalue[25]+"]")
    print("옵션매도호가5	["+recvvalue[ 6]+"]"+",    매도호가건수5	["+recvvalue[16]+"]"+",    매도호가잔량5	["+recvvalue[26]+"]")
    print("옵션매수호가1	["+recvvalue[ 7]+"]"+",    매수호가건수1	["+recvvalue[17]+"]"+",    매수호가잔량1	["+recvvalue[27]+"]")
    print("옵션매수호가2	["+recvvalue[ 8]+"]"+",    매수호가건수2	["+recvvalue[18]+"]"+",    매수호가잔량2	["+recvvalue[28]+"]")
    print("옵션매수호가3	["+recvvalue[ 9]+"]"+",    매수호가건수3	["+recvvalue[19]+"]"+",    매수호가잔량3	["+recvvalue[29]+"]")
    print("옵션매수호가4	["+recvvalue[10 ]+"]"+",   매수호가건수4	["+recvvalue[20]+"]"+",    매수호가잔량4	["+recvvalue[30]+"]")
    print("옵션매수호가5	["+recvvalue[11]+"]"+",    매수호가건수5	["+recvvalue[21]+"]"+",    매수호가잔량5	["+recvvalue[31]+"]")
    print("====================================")
    print("총매도호가건수	["+recvvalue[32]+"]"+",    총매도호가잔량	["+recvvalue[34]+"]"+",    총매도호가잔량증감	["+recvvalue[36]+"]")
    print("총매수호가건수	["+recvvalue[33]+"]"+",    총매수호가잔량	["+recvvalue[35]+"]"+",    총매수호가잔량증감	["+recvvalue[37]+"]") 
    
    
# 주식옵션체결처리 출력라이브러리
def stockspurchase_stockoptn(data_cnt, data):
    print("============================================")
    # print(data)
    menulist = "옵션단축종목코드|영업시간|옵션현재가|전일대비부호|옵션전일대비|전일대비율|옵션시가2|옵션최고가|옵션최저가|최종거래량|누적거래량|누적거래대금|HTS이론가|HTS미결제약정수량|미결제약정수량증감|시가시간|시가2대비현재가부호|시가대비지수현재가|최고가시간|최고가대비현재가부호|최고가대비지수현재가|최저가시간|최저가대비현재가부호|최저가대비지수현재가|매수2비율|프리미엄값|내재가치값|시간가치값|델타|감마|베가|세타|로우|HTS내재변동성|괴리도|미결제약정직전수량증감|이론베이시스|역사적변동성|체결강도|괴리율|시장베이시스|옵션매도호가1|옵션매수호가1|매도호가잔량1|매수호가잔량1|매도체결건수|매수체결건수|순매수체결건수|총매도수량|총매수수량|총매도호가잔량|총매수호가잔량|전일거래량대비등락율"
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
    # print(aes_dec_str)
    pValue = aes_dec_str.split('^')
    # print(pValue)

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
            print("#### 지수선물옵션 주문 접수 통보 ####")
            menulist_order = "고객ID|계좌번호|주문번호|원주문번호|매도매수구분|정정구분|주문종류|단축종목코드|주문수량|체결단가|체결시간|거부여부|체결여부|접수여부|지점번호|체결수량|계좌명|체결종목명|주문조건|주문그룹ID|주문그룹SEQ|주문가격"
            menustr = menulist_order.split('|')
            i = 0
            for menu in menustr:
                print("%s  [%s]" % (menu, pValue[i]))
                i += 1

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


# 해외선물옵션 체결처리 출력라이브러리
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
    
    ### 1-1. 국내주식 호가, 체결가, 예상체결, 체결통보 ### # 모의투자 국내주식 체결통보: H0STCNI9
    # code_list = [['1','H0STASP0','005930'],['1','H0STCNT0','005930'],['1', 'H0STANC0', '005930'],['1','H0STCNI0','HTS ID를 입력하세요']]
    
    ### 1-2. 국내주식 실시간회원사, 실시간프로그램매매, 장운영정보 ###
    # code_list = [['1', 'H0STMBC0', '005930'], ['1', 'H0STPGM0', '005930'], ['1', 'H0STMKO0', '005930']]
    
    ### 1-3. 국내주식 시간외 호가, 체결가, 예상체결 ###
    # code_list = [['1','H0STOAA0','005930'],['1','H0STOUP0','005930'],['1', 'H0STOAC0', '005930']]
    
    ### 1-4. 국내지수 체결, 예상체결, 실시간프로그램매매 ###
    # code_list = [['1', 'H0UPCNT0', '0001'], ['1', 'H0UPANC0', '0001'], ['1', 'H0UPPGM0', '0001']]
    
    ### 1-5. ELW 호가, 체결가 ###
    # code_list = [['1', 'H0EWASP0', '58J297'],['1', 'H0EWCNT0', '58J297']]
    
    ### 2-1. 해외주식(미국) 호가, 체결가, 체결통보 ###
    # code_list = [['1','HDFSASP0','DNASAAPL'],['1','HDFSCNT0','DNASAAPL'],['1','H0GSCNI0','HTS ID를 입력하세요']]
    
    ### 2-2.해외주식(아시아) 호가, 체결가, 체결통보 ###
    # code_list = [['1','HDFSASP1','DHKS00003'],['1','HDFSCNT0','DHKS00003'],['1','H0GSCNI0','HTS ID를 입력하세요']]
    
    ### 3-1. 국내 지수선물옵션 호가, 체결가, 체결통보 ###
    # code_list = [['1','H0IFASP0','101T12'],['1','H0IFCNT0','101T12'], # 지수선물호가, 체결가
    #              ['1','H0IOASP0','201T11317'],['1','H0IOCNT0','201T11317'], # 지수옵션호가, 체결가
    #              ['1','H0IFCNI0','HTS ID를 입력하세요']] # 선물옵션체결통보
    
    ### 3-2. 국내 상품선물 호가, 체결가, 체결통보 ###
    # code_list = [['1','H0CFASP0','175T11'],['1','H0CFCNT0','175T11'], # 상품선물호가, 체결가
    #              ['1','H0IFCNI0','HTS ID를 입력하세요']] # 선물옵션체결통보
    
    ### 3-3. 국내 주식선물옵션 호가, 체결가, 체결통보 ###
    # code_list = [['1', 'H0ZFCNT0', '111V06'], ['1', 'H0ZFASP0', '111V06'], # 주식선물호가, 체결가
    #              ['1', 'H0ZOCNT0', '211V05059'], ['1', 'H0ZOASP0', '211V05059'], # 주식옵션호가, 체결가
    #              ['1','H0IFCNI0','HTS ID를 입력하세요']] # 선물옵션체결통보
        
    ### 4. 해외선물옵션 호가, 체결가, 체결통보 ###
    # code_list = [['1','HDFFF020','FCAZ22'],['1','HDFFF010','FCAZ22'], # 해외선물 체결가, 호가
    #              ['1','HDFFF020','OESH23 C3900'],['1','HDFFF010','OESH23 C3900'], # 해외옵션 체결가, 호가
    #              ['1','HDFFF2C0','HTS ID를 입력하세요']] # 해외선물옵션 체결통보
    
    ### 1+2+3+4. 국내주식, 해외주식(미국), 해외주식(아시아), 국내 지수선물옵션, 국내 상품선물, 국내 주식선물옵션, 해외선물옵션 호가, 체결가, 체결통보 ###
    code_list = [['1','H0STASP0','005930'],['1','H0STCNT0','005930'],['1', 'H0STANC0', '005930'],['1','H0STCNI0','HTS ID를 입력하세요'],
                 ['1','HDFSASP0','DNASAAPL'],['1','HDFSCNT0','DNASAAPL'],
                 ['1','HDFSASP1','DHKS00003'],['1','HDFSCNT0','DHKS00003'],['1','H0GSCNI0','HTS ID를 입력하세요'],
                 ['1','H0IFASP0','101T12'],['1','H0IFCNT0','101T12'],['1','H0IOASP0','201T11317'],['1','H0IOCNT0','201T11317'], ['1','H0CFASP0','175T11'],['1','H0CFCNT0','175T11'],['1', 'H0ZFCNT0', '111V06'], ['1', 'H0ZFASP0', '111V06'],['1', 'H0ZOCNT0', '211V05059'], ['1', 'H0ZOASP0', '211V05059'],['1','H0IFCNI0','HTS ID를 입력하세요'],
                 ['1','HDFFF020','FCAZ22'],['1','HDFFF010','FCAZ22'],['1','HDFFF020','OESH23 C3900'],['1','HDFFF010','OESH23 C3900'],['1','HDFFF2C0','HTS ID를 입력하세요']]
    

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

            try:

                data = await websocket.recv()
                # await asyncio.sleep(0.5)
                # print(f"Recev Command is :{data}")  # 정제되지 않은 Request / Response 출력

                if data[0] == '0':
                    recvstr = data.split('|')  # 수신데이터가 실데이터 이전은 '|'로 나뉘어져있어 split
                    trid0 = recvstr[1]

                    if trid0 == "H0STASP0":  # 주식호가tr 일경우의 처리 단계
                        print("#### 국내주식 호가 ####")
                        stockhoka_domestic(recvstr[3])
                        # await asyncio.sleep(0.2)

                    elif trid0 == "H0STCNT0":  # 주식체결 데이터 처리
                        print("#### 국내주식 체결 ####")
                        data_cnt = int(recvstr[2])  # 체결데이터 개수
                        stockspurchase_domestic(data_cnt, recvstr[3])
                        # await asyncio.sleep(0.2)
                    
                    elif trid0 == "H0STANC0":  # 국내주식 예상체결 데이터 처리
                        print("#### 국내주식 예상체결 ####")
                        data_cnt = int(recvstr[2])  # 체결데이터 개수
                        stockexppurchase_domestic(data_cnt, recvstr[3])
                        # await asyncio.sleep(0.2)  
                    
                    elif trid0 == "H0STOUP0":  # 국내주식 시간외체결 데이터 처리
                        print("#### 국내주식 시간외체결 ####")
                        data_cnt = int(recvstr[2])  # 체결데이터 개수
                        stockoverpurchase_domestic(data_cnt, recvstr[3])
                        # await asyncio.sleep(0.2) 

                    elif trid0 == "H0STOAA0":  # 국내주식 시간외호가 데이터 처리
                        print("#### 국내주식 시간외호가 ####")
                        stockoverhoka_domestic(recvstr[3])
                        # await asyncio.sleep(0.2)                        
                        
                    elif trid0 == "H0STOAC0":  # 국내주식 시간외예상체결데이터 처리
                        print("#### 국내주식 시간외예상체결 ####")
                        data_cnt = int(recvstr[2])  # 체결데이터 개수
                        stockoverexppurchase_domestic(data_cnt, recvstr[3])
                        
                    elif trid0 == "H0STMBC0":  # 국내주식 실시간회원사 데이터 처리
                        print("#### 국내주식 실시간회원사 ####")
                        data_cnt = int(recvstr[2])  # 데이터 개수
                        stocksmember_domestic(data_cnt, recvstr[3])
                        # await asyncio.sleep(0.2) 

                    elif trid0 == "H0STPGM0":  # 국내주식 실시간프로그램매매 데이터 처리
                        print("#### 국내주식 실시간프로그램매매 ####")
                        data_cnt = int(recvstr[2])  # 데이터 개수
                        stocksprogramtrade_domestic(data_cnt, recvstr[3])
                        # await asyncio.sleep(0.2)                        
                        
                    elif trid0 == "H0STMKO0":  # 국내주식 장운영정보 데이터 처리
                        print("#### 국내주식 장운영정보 ####")
                        data_cnt = int(recvstr[2])  # 데이터 개수
                        stocksmarketinfo_domestic(data_cnt, recvstr[3])  
                        
                    elif trid0 == "H0UPCNT0":  # 국내지수 체결 데이터 처리
                        print("#### 국내지수 체결 ####")
                        data_cnt = int(recvstr[2])  # 체결데이터 개수
                        indexpurchase_domestic(data_cnt, recvstr[3])
                        # await asyncio.sleep(0.2) 
                        
                    elif trid0 == "H0UPANC0":  # 국내지수 예상체결 데이터 처리
                        print("#### 국내지수 예상체결 ####")
                        data_cnt = int(recvstr[2])  # 체결데이터 개수
                        indexexppurchase_domestic(data_cnt, recvstr[3])
                        # await asyncio.sleep(0.2) 
                        
                    elif trid0 == "H0UPPGM0":  # 국내지수 예상체결 데이터 처리
                        print("#### 국내지수 실시간프로그램매매 ####")
                        data_cnt = int(recvstr[2])  # 체결데이터 개수
                        indexprogramtrade_domestic(data_cnt, recvstr[3])
                        # await asyncio.sleep(0.2)    
                    
                    elif trid0 == "H0EWCNT0":  # 주식옵션 체결 데이터 처리
                        print("#### ELW 체결 ####")
                        data_cnt = int(recvstr[2])  # 체결데이터 개수
                        elwpurchase_domestic(data_cnt, recvstr[3])
                        # await asyncio.sleep(0.2) 

                    elif trid0 == "H0EWASP0":  # 주식옵션 호가 데이터 처리
                        print("#### ELW 호가 ####")
                        elwhoka_domestic(recvstr[3])
                        # await asyncio.sleep(0.2)   

                    elif trid0 == "HDFSASP0":  # 해외주식호가tr 일경우의 처리 단계
                        print("#### 해외(미국)주식호가 ####")
                        stockhoka_overseas_usa(recvstr[3])
                        # await asyncio.sleep(0.2)

                    elif trid0 == "HDFSASP1":  # 해외주식호가tr 일경우의 처리 단계
                        print("#### 해외(아시아)주식호가 ####")
                        stockhoka_overseas_asia(recvstr[3])
                        # await asyncio.sleep(0.2)

                    elif trid0 == "HDFSCNT0":  # 해외주식체결 데이터 처리
                        print("#### 해외주식체결 ####")
                        data_cnt = int(recvstr[2])  # 체결데이터 개수
                        stockspurchase_overseas(data_cnt, recvstr[3])
                        # await asyncio.sleep(0.2)

                    elif trid0 == "H0IFASP0":  # 지수선물호가 tr 일경우의 처리 단계
                        print("#### 지수선물호가 ####")
                        stockhoka_futs(recvstr[3])
                        # await asyncio.sleep(0.2)

                    elif trid0 == "H0IFCNT0":  # 지수선물체결 데이터 처리
                        print("#### 지수선물체결 ####")
                        data_cnt = int(recvstr[2])  # 체결데이터 개수
                        stockspurchase_futs(data_cnt, recvstr[3])
                        # await asyncio.sleep(0.2)

                    elif trid0 == "H0IOASP0":  # 지수옵션호가 tr 일경우의 처리 단계
                        print("#### 지수옵션호가 ####")
                        stockhoka_optn(recvstr[3])
                        # await asyncio.sleep(0.2)

                    elif trid0 == "H0IOCNT0":  # 지수옵션체결 데이터 처리
                        print("#### 지수옵션체결 ####")
                        data_cnt = int(recvstr[2])  # 체결데이터 개수
                        stockspurchase_optn(data_cnt, recvstr[3])
                        # await asyncio.sleep(0.2)
                    
                    elif trid0 == "H0CFASP0":  # 상품선물호가 tr 일경우의 처리 단계
                        print("#### 상품선물호가 ####")
                        stockhoka_productfuts(recvstr[3])
                        # await asyncio.sleep(0.2)

                    elif trid0 == "H0CFCNT0":  # 상품선물체결 데이터 처리
                        print("#### 상품선물체결 ####")
                        data_cnt = int(recvstr[2])  # 체결데이터 개수
                        stockspurchase_productfuts(data_cnt, recvstr[3])
                        # await asyncio.sleep(0.2)
                        
                    elif trid0 == "H0ZFCNT0":  # 주식선물 체결 데이터 처리
                        print("#### 주식선물 체결 ####")
                        data_cnt = int(recvstr[2])  # 체결데이터 개수
                        stockspurchase_stockfuts(data_cnt, recvstr[3])
                        # await asyncio.sleep(0.2) 

                    elif trid0 == "H0ZFASP0":  # 주식선물 호가 데이터 처리
                        print("#### 주식선물 호가 ####")
                        stockhoka_stockfuts(recvstr[3])
                        # await asyncio.sleep(0.2)
                        
                    elif trid0 == "H0ZOCNT0":  # 주식옵션 체결 데이터 처리
                        print("#### 주식옵션 체결 ####")
                        data_cnt = int(recvstr[2])  # 체결데이터 개수
                        stockspurchase_stockoptn(data_cnt, recvstr[3])
                        # await asyncio.sleep(0.2) 

                    elif trid0 == "H0ZOASP0":  # 주식옵션 호가 데이터 처리
                        print("#### 주식옵션 호가 ####")
                        stockhoka_stockoptn(recvstr[3])
                        # await asyncio.sleep(0.2)     

                    elif trid0 == "HDFFF010":  # 해외선물옵션호가 tr 일경우의 처리 단계
                        print("#### 해외선물옵션호가 ####")
                        stockhoka_overseafut(recvstr[3])
                        # await asyncio.sleep(0.2)

                    elif trid0 == "HDFFF020":  # 해외선물옵션체결 데이터 처리
                        print("#### 해외선물옵션체결 ####")
                        data_cnt = int(recvstr[2])  # 체결데이터 개수
                        stockspurchase_overseafut(data_cnt, recvstr[3])
                        # await asyncio.sleep(0.2)

                elif data[0] == '1':

                    recvstr = data.split('|')  # 수신데이터가 실데이터 이전은 '|'로 나뉘어져있어 split
                    trid0 = recvstr[1]

                    if trid0 == "H0STCNI0" or trid0 == "H0STCNI9":  # 주실체결 통보 처리
                        stocksigningnotice_domestic(recvstr[3], aes_key, aes_iv)
                        # await asyncio.sleep(0.2)

                    elif trid0 == "H0GSCNI0":  # 해외주실체결 통보 처리
                        stocksigningnotice_overseas(recvstr[3], aes_key, aes_iv)
                        # await asyncio.sleep(0.2)

                    elif trid0 == "H0IFCNI0":  # 지수/상품/주식 선물옵션체결 통보 처리
                        stocksigningnotice_futsoptn(recvstr[3], aes_key, aes_iv)
                        # await asyncio.sleep(0.2)

                    elif trid0 == "HDFFF2C0":  # 해외선물옵션체결 통보 처리
                        stocksigningnotice_overseafut(recvstr[3], aes_key, aes_iv)
                        # await asyncio.sleep(0.2)

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
                            if trid == "H0STCNI0" or trid == "H0STCNI9": # 국내주식
                                aes_key = jsonObject["body"]["output"]["key"]
                                aes_iv = jsonObject["body"]["output"]["iv"]
                                print("### TRID [%s] KEY[%s] IV[%s]" % (trid, aes_key, aes_iv))

                            elif trid == "H0GSCNI0": # 해외주식
                                aes_key = jsonObject["body"]["output"]["key"]
                                aes_iv = jsonObject["body"]["output"]["iv"]
                                print("### TRID [%s] KEY[%s] IV[%s]" % (trid, aes_key, aes_iv))

                            elif trid == "H0IFCNI0": # 지수/상품 선물옵션
                                aes_key = jsonObject["body"]["output"]["key"]
                                aes_iv = jsonObject["body"]["output"]["iv"]
                                print("### TRID [%s] KEY[%s] IV[%s]" % (trid, aes_key, aes_iv))

                            elif trid == "HDFFF2C0": # 해외선물옵션
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
