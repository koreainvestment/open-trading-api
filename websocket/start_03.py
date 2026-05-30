from dotenv import load_dotenv
import os
import json
import time
import requests
import websocket

load_dotenv()
appkey = os.getenv("appkey_01")
appsecret = os.getenv("appsecret_01")

def get_approval(key, secret):

    url = "https://openapivts.koreainvestment.com:29443"  # 모의투자계좌

    headers = {"content-type": "application/json"}

    body = {
        "grant_type": "client_credentials",
        "appkey": key,
        "secretkey": secret
    }

    PATH = "oauth2/Approval"
    URL = f"{url}/{PATH}"

    time.sleep(0.05)

    res = requests.post(
        URL,
        headers=headers,
        data=json.dumps(body)
    )

    approval_key = res.json()["approval_key"]

    return approval_key

approval_key = get_approval(appkey, appsecret)

def wsdataf(approval_key, tr_id, tr_key):
    wsdata = {
        "header": {
            "approval_key": approval_key,
            "custtype": "P",
            "tr_type": "1",
            "content-type": "utf-8"
        },
        "body":
            {
                "input": {
                    "tr_id": tr_id,
                    "tr_key": tr_key
                }
            }
        }
    return wsdata

if __name__ == "__main__":

    def on_message(ws, message):
        print(f"Received message: {message}")

    def on_open(ws):
        print("Connection opened")
        ws.send(json.dumps(wsdataf(approval_key, "H0STCNT0", "101V09")))
    
    websocket.enableTrace(False)
    ws = websocket.WebSocketApp("ws://ops.koreainvestment.com:21000",
                                on_open=on_open,
                                on_message=on_message)
    ws.run_forever()
