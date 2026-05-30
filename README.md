한국투자증권 open api trading system

1. 프로젝트 설명

본 프로젝트는 한국투자증권의 open ai를 활용하여 자동 모의투자 시스템을 구현하는 것을 목표로 합니다. 먼저 삼성전자(005930)으로 모의투자 시스템을 구현한 후, 두산에너빌리티(034020)으로 진행하는 시스템도 구현을 해보았습니다. 
본 프로그램은 실시간으로 데이터를 조회하고, 전일 종가 대비 등락을 계산하여 사전에 정의된 매매 전략에 따라 자동으로 매수 및 매도를 진행하도록 설계되었습니다. 
또한 backtester를 활용하여 모의투자를 진행하기 전, backtesting도 진행하였습니다.

___

2. Postman

<img width="691" height="147" alt="image" src="https://github.com/user-attachments/assets/0efcf61b-195c-470c-b4e6-322aad81e8e4" />

우선, postman의 모의env에 계좌번호와 appkey, appsecret을 기입하였습니다.

2.1. 토큰발급

<img width="719" height="763" alt="image" src="https://github.com/user-attachments/assets/6e25fbd5-2285-4506-a1bd-032e1b37ad46" />

토큰발급을 send한 결과, 결과값이 나온 것으로 보아 지금 api 시스템에서의 appkey와 appsecret은 정상 작동하고 있으며, 토큰이 정상 발급됨을 확인할 수 있습니다. 

2.2. 주식현재가 조회

<img width="725" height="813" alt="image" src="https://github.com/user-attachments/assets/d8301228-946a-4074-89fb-86e50c314ee1" />

또한 주식현재가 조회가 되는 것으로 보아 코딩환경에 있어서의 오류가 없음을 확인할 수 있습니다. 

2.3. 웹소켓접속키 발급

<img width="723" height="745" alt="image" src="https://github.com/user-attachments/assets/76584c09-6e62-4ea6-967c-96623c9de971" />
<img width="678" height="255" alt="image" src="https://github.com/user-attachments/assets/b87fbb61-b045-451f-955f-bafc567cfda4" />

웹소켓접속키 또한 정상 발급 되고 있으며 codespace에서도 제대로 구현되고 있음을 확인할 수 있습니다. 
___

3. 주요파일 설명

3.1. kis_devlp.yaml

<img width="710" height="723" alt="image" src="https://github.com/user-attachments/assets/3c3429cf-b7f2-41dc-bf5b-150521025d53" />

kis_devlp.yaml 파일에 앱키와 앱시크릿, 모의투자 계좌를 기입하여 이 파일이 구동될 수 있도록 했습니다. 

3.2. kis_auth.py

<img width="601" height="101" alt="image" src="https://github.com/user-attachments/assets/e2102c81-ef74-4524-9d0e-aaa9613adb38" />

kis_auth에서는 kis_devlp.yml에서 저장했던 앱키와 앱시크릿 정보, 계좌번호 등을 불러와서 읽습니다. 

<img width="603" height="409" alt="image" src="https://github.com/user-attachments/assets/f4d0b00f-68a2-442f-aefa-ffece8645f29" />

또한 해당 앱키와 앱시크릿으로 발급받은 토큰을 불러와 저장합니다. 

<img width="583" height="364" alt="image" src="https://github.com/user-attachments/assets/3c3d4036-7f98-468b-95cd-acdd1eb85c87" />

yaml에 저장한 정보에 따라, 현재 프로그램을 실전투자로 할지 모의투자로 할지의 결정 또한 이 파일에서 이루어집니다. 

3.3. domestic_stock_functions.py

꽤 방대한 크기의 파일이어서, 필요한 부분만 설명하겠습니다. 우선, 이 파일은 국내주식을 기준으로 주식을 매매할 때 필요한 함수들을 모아놓은 것입니다. 

<img width="474" height="199" alt="image" src="https://github.com/user-attachments/assets/08b52f9a-2909-45fc-9920-0b11d533378c" />

예를 들어 def after_hour_balance는 입력된 종목의 장후 가격과 거래량 등의 정보를 나타내줍니다. 이런 함수는 def bulk_trans_num (대량체결주식 정보), def capture_uplowprice (상한가, 하한가 정보) 등 여러가지가 있습니다. 저는 모의투자를 진행하는 auto_paper_trading.py 파일에서 전일종가 대비 등락을 기준으로 코딩을 했으므로, 전일종가나 현재가(def inquire_price)를 불러오는 함수를 사용했습니다. 

3.4. auto_paperr_trading.py

실제 자동 매매를 수행하는 프로그램입니다. 
