#웹소켓 실시간 WEBSOCKET 주식현재가_실시간주식체결가[실시간-003] 엑셀연동 샘플
#Method : POST
#실전 Domain : https://openapi.koreainvestment.com:9443
#모의 Domain : https://openapivts.koreainvestment.com:29443
#URL: /tryitout/H0STASP0
#Content-Type : text/plain
#엑셀파일 실시간.xlsx 띄우고 프로그램 실행하세요
import os
import json
import requests
import pandas as pd

try:
    import xlwings as xw

except ImportError:
    print("엑셀연동 xlwings 설치중입니다.[관리자 권한필요]")
    os.system('sudo python3 -m pip3 install xlwings')

try:
    import websocket

except ImportError:
    print("websocket-client 설치중입니다.")
    os.system('python3 -m pip3 install websocket-client')

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

g_appkey = "Appkey값셋팅하세요"
g_appsecret = "Appsecret값셋팅하세요"
g_approval_key = get_approval(g_appkey, g_appsecret) 
    
    
h = {
    "appkey": g_appkey,
    "appsecret": g_appsecret
}
b = {
    "header": {
        "approval_key": g_approval_key,
        "custtype": "P",
        "tr_type": "1",
        "content-type": "utf-8"
    },
    "body":
        {
            "input": {
                "tr_id": "H0STASP0", # API명
                "tr_key": "011700"   # 종목번호
            }
    }
}

wb = xw.Book('실시간.xlsx')
wsheet = wb.sheets[0]

# Pandas DataFrame 이용
def pdbind(result):

    df = pd.DataFrame([
        ['', result[1], ''],
        [result[32], result[12], ''],
        [result[31], result[11], ''],
        [result[30], result[10], ''],
        [result[29], result[9], ''],
        [result[28], result[8], ''],
        [result[27], result[7], ''],
        [result[26], result[6], ''],
        [result[25], result[5], ''],
        [result[24], result[4], ''],
        [result[23], result[3], ''],
        ['', result[13], result[33]],
        ['', result[14], result[34]],
        ['', result[15], result[35]],
        ['', result[16], result[36]],
        ['', result[17], result[37]],
        ['', result[18], result[38]],
        ['', result[19], result[39]],
        ['', result[20], result[40]],
        ['', result[21], result[41]],
        ['', result[22], result[42]],
        [result[43], '', result[44]]  # 총매도호가, 총매수호가
    ]
    )
    wsheet.range('A4').value = df

def on_message(ws, data):
    #print('type=', type(data), '\ndata=', data)

    if data[0] in ['0', '1']:  # 시세데이터가 아닌경우
        d1 = data.split("|")
        if len(d1) >= 4:
            isEncrypt = d1[0]
            tr_id = d1[1]
            tr_cnt = d1[2]
            recvData = d1[3]
            result = recvData.split("^")
            #print("start time=", result[1])
            pdbind(result)  # pandas dataframe 이용 변경
            # xlsvalue(result)

        else:
            print('Data Size Error=', len(d1))
    else:
        recv_dic = json.loads(data)
        tr_id = recv_dic['header']['tr_id']
        # xls 바인딩
        wsheet.range('A4').value = tr_id

        if tr_id == 'PINGPONG':
            send_ping = recv_dic
            ws.send(data, websocket.ABNF.OPCODE_PING)
        else:  # parser data
            print('tr_id=', tr_id, '\nmsg=', data)


def on_error(ws, error):
    print('error=', error)


def on_close(ws, status_code, close_msg):
    print('on_close close_status_code=', status_code, " close_msg=", close_msg)


def on_open(ws):
    print('on_open send data=', json.dumps(b))
    ws.send(json.dumps(b), websocket.ABNF.OPCODE_TEXT)


# websocket.enableTrace(True)

# 모의투자
# ws = websocket.WebSocketApp("ws://ops.koreainvestment.com:31000",
#                             on_open=on_open, on_message=on_message, on_error=on_error)


ws = websocket.WebSocketApp("ws://ops.koreainvestment.com:21000",
                            on_open=on_open, on_message=on_message, on_error=on_error)

ws.run_forever()
