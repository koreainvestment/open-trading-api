삼성전자 자동화 모의투자 시스템<br>
<br>
Trading logic:<br>
1. Check the current market price of Samsung Electronics<br>
2. Check account balance / holdings<br>
3. Place a buy order at 2,000 KRW below the currently checked price<br>
4. Place a sell order at 2,000 KRW above the currently checked price<br>
5. After placing orders, check balance/holdings again to confirm whether execution actually happened<br>
6. Repeat this process continuously during the trading window only<br>
<br>
Trading window:<br>

- Start: 09:10 AM<br>
- End: 03:30 PM<br>
- Outside this window, do not place orders<br>
- The program should stop trading automatically after 03:30 PM<br>
<br>
samsung_auto_trader 폴더는 README.md, account.py, api_client.py, auth.py, config.py, logger.py, main.py, market_data.py, orders.py, requirements.txt, token_cache.json, trader.py 으로 이루어져 있다.<br>
<br>
main.py가 프로그램을 시작하고,<br>
auth.py가 토큰을 준비하고,<br>
api_client.py가 API 요청을 보내고,<br>
market_data.py/account.py/orders.py가 각각 현재가/잔고/주문 기능을 담당하고,<br>
trader.py가 이 기능들을 조합해서 자동매매 로직을 실행한다.<br>
<br>
requirements는 필요한 파이썬 패키지 목록으로 구성<br>
config.py는 APP_KEY, APP_SECRET, ACCOUNT와 같은 설정값들 한 곳에 모아둔 곳이다.<br>
logger.py는 logger를 만들고 INFO의 로그를 출력한다.<br>
token_cache.json는 토큰을 저장하는 곳이다.<br>
<br>
<br>
자동화 모의 투자 구조 : 현재가 조회 → 잔고 확인 → 매수 주문 → 체결 추정 → 매도 주문 → 반복<br>
<br>
<br>
<br>
<br>
<br>
사전 환경설정 안내<br>
KIS Open API 신청 및 설정<br>
https://apiportal.koreainvestment.com/intro     <br>
한국투자증권 계좌 개설 및 ID 연결<br>
한국투자증권 홈페이지 or 앱에서 Open API 서비스 신청<br>
앱키(App Key), 앱시크릿(App Secret) 발급<br>
모의투자 및 실전투자 앱키 각각 준비<br>
<br>
<br>
APP_KEY, APP_SECRET, ACCOUNT를 시크릿 만들기<br>
<img width="1758" height="851" alt="image" src="https://github.com/user-attachments/assets/11dea30a-1f80-40f2-a26e-c86144225e6f" /><br>
<br>
<br>

코드 실행하는 법<br>
패키지 설치<br>
cd samsung_auto_trader<br>
pip install -r requirements.txt<br>
<img width="355" height="227" alt="image" src="https://github.com/user-attachments/assets/759895f4-0cab-4198-8232-5b197fa52c6f" /> <br>
<br>
<br>
자동 모의 투자 실행<br>
python main.py<br>
<br>
<img width="868" height="244" alt="image" src="https://github.com/user-attachments/assets/ab2d97e4-30fc-47d8-9174-a4d58eed5c38" /><br>

<img width="911" height="222" alt="image" src="https://github.com/user-attachments/assets/5f894641-59b8-4618-a5fc-7997a056a335" /><br>

<br>
<br>
09:10 ~ 15:30이 아닐 경우<br>
<img width="907" height="145" alt="image" src="https://github.com/user-attachments/assets/ddfe3eed-04f4-4cd6-b234-a0ffb5d1c867" /><br>
<br>
<br>
<br>
<br>
만약 다른 거래 종목으로 자동화 투자를 하고 싶다면 cofig.py에서 SYMBOL의 값을 바꿔주고 지정가를 바꾸고 싶다면 ORDER_PRICE_GAP을 바꿔주면 된다.<br>
<br>
하이닉스를 현재 확인 가격보다 1,000원 ​​낮은 가격에 매수 주문을 내고 1,000원 ​​높은 가격에 매도 주문을 내는 자동 모의투자하고 싶다면 <br>
먼저 한국거래소 정보데이터시스템에서 하이닉스 종목코드를 조회한다.<br>
<img width="516" height="53" alt="image" src="https://github.com/user-attachments/assets/015329eb-d58b-4418-b2f7-e8ec32d3ab23" /><br>
<br>
config.py를 열어 SYMBOL 값을 000660으로 바꿔주고 ORDER_PRICE_GAP를 1000으로 바꿔준다.<br>
<br>
config.py<br>
SYMBOL = "000660"<br>
ORDER_PRICE_GAP = 1000<br>
<img width="865" height="267" alt="image" src="https://github.com/user-attachments/assets/5360f9c6-bc36-4e15-ac81-b0d26b2956dc" /><br>
<img width="927" height="241" alt="image" src="https://github.com/user-attachments/assets/0391b3db-19e4-4777-926d-f4d1583230f5" /><br>
<img width="929" height="238" alt="image" src="https://github.com/user-attachments/assets/27afcae6-948b-4e88-af59-9f71cec4e66a" /><br>



