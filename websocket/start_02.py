from dotenv import load_dotenv
import os
import json
import time
import requests

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

if __name__ == "__main__":

    approval_key = get_approval(appkey, appsecret)
    print(approval_key)