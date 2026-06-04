삼성전자 자동화 모의투자 시스템

Trading logic:

1. Check the current market price of Samsung Electronics
2. Check account balance / holdings
3. Place a buy order at 2,000 KRW below the currently checked price
4. Place a sell order at 2,000 KRW above the currently checked price
5. After placing orders, check balance/holdings again to confirm whether execution actually happened
6. Repeat this process continuously during the trading window only

Trading window:

- Start: 09:10 AM
- End: 03:30 PM
- Outside this window, do not place orders
- The program should stop trading automatically after 03:30 PM

samsung_auto_trader 폴더는 README.md, account.py, api_client.py, auth.py, config.py, logger.py, main.py, market_data.py, orders.py, requirements.txt, token_cache.json, trader.py 으로 이루어져 있다.

main.py가 프로그램을 시작하고,
auth.py가 토큰을 준비하고,
api_client.py가 API 요청을 보내고,
market_data.py/account.py/orders.py가 각각 현재가/잔고/주문 기능을 담당하고,
trader.py가 이 기능들을 조합해서 자동매매 로직을 실행한다.

requirements는 필요한 파이썬 패키지 목록으로 구성
config.py는 APP_KEY, APP_SECRET, ACCOUNT와 같은 설정값들 한 곳에 모아둔 곳이다.
logger.py는 logger를 만들고 INFO의 로그를 출력한다.
token_cache.json는 토큰을 저장하는 곳이다.

cd samsung_auto_trader
pip install -r requirements.txt
<img width="355" height="227" alt="image" src="https://github.com/user-attachments/assets/759895f4-0cab-4198-8232-5b197fa52c6f" />



python main.py

<img width="1299" height="730" alt="image" src="https://github.com/user-attachments/assets/fc35d437-1159-459a-b062-23a5241e52b2" />
<img width="1300" height="507" alt="image" src="https://github.com/user-attachments/assets/7bcf98a6-f952-4c79-aecc-411a3714e6c3" />


09:10 ~ 15:30이 아닐 경우
<img width="907" height="145" alt="image" src="https://github.com/user-attachments/assets/ddfe3eed-04f4-4cd6-b234-a0ffb5d1c867" />






