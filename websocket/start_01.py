from dotenv import load_dotenv
import os

load_dotenv()
appkey = os.getenv("appkey_01")
appsecret = os.getenv("appsecret_01")

if __name__ == "__main__":

    print(appkey)
    print(appsecret)
    