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

<img width="493" height="289" alt="image" src="https://github.com/user-attachments/assets/f3f4a120-e693-4b0b-b4b7-dfc391b86e28" />

종목은 삼성전자로 설정하였고, 매도전략과 매수전략 모두 전일 종가 기준으로 일정 비율 이상 변동할 경우, 보유 수량의 일정 비율을 매도하는 방식으로 하였고, 매도비율을 더 높게 함으로써 이익을 더 많이 내도록 설정하였습니다. 매매는 30분 기준으로 행동하도록 설정하였습니다. 매매가는 시장가 기준으로 설정했습니다.

<img width="502" height="333" alt="image" src="https://github.com/user-attachments/assets/0b89483c-93d0-40b4-a342-94290c7a0e38" />
<img width="473" height="303" alt="image" src="https://github.com/user-attachments/assets/e25440d0-854a-4c84-9ee3-95c6c2e8b03e" />
<img width="529" height="429" alt="image" src="https://github.com/user-attachments/assets/39a89eb9-4493-466e-8d8c-3fbe3c92c6f1" />
<img width="650" height="412" alt="image" src="https://github.com/user-attachments/assets/ad7b5177-84a4-4f42-a58b-6c454bb93cb3" />

get current holding과 get available cash를 통해 현재 보유하고 있는 삼성전자 주식 수와 현금을 계산하도록 만들었습니다. get action and qty를 통해 실제 매수와 매도를 실행하도록 하였고, 조건 충족 여부에 따라 매매가 계속 이어지도록 설정했습니다. 

4. Backtesting

<img width="713" height="490" alt="image" src="https://github.com/user-attachments/assets/548c85c4-7fa3-4f80-86c6-9703276c628f" />
<img width="739" height="254" alt="image" src="https://github.com/user-attachments/assets/b6077160-1268-4bf6-aee2-d9da6c031ca4" />

auto_paper_trading.py 파일과 같은 내용의 simple_backtest_samsung.py를 만들었고, 4월 16일부터 5월 29일까지의 주가를 기반으로 backtest를 진행하였습니다. 그 결과 9%의 수익률을 낸 것을 볼 수 있습니다. 

6. auto_paper_trading2 (두산에너빌리티, 034020)

<img width="580" height="435" alt="image" src="https://github.com/user-attachments/assets/6bad9339-3b49-4a0d-a5b5-2107de97b18f" />

삼성전자의 수익률이 기대에 못미치는 점에 기반하여 10분단위로 매매를 진행하고, 조금더 공격적인 매매를 진행하는 코드를 만들었습니다. 삼성전자 코드는 최대 5%와 7%의 주가변동만을 고려했지만, 현재 KOSPI시장의 변동성이 큰 점을 감안하여 상한가와 하한가까지의 가격변동을 고려하는 코드로 만들었습니다. 가격이 많이 내려갈 수록 많이 매수하는 전략이 아니라 가격이 많이 내려갈 수록 적개 매수하는 방향으로 전략을 수정했습니다. 

6.1. backtesting

<img width="638" height="125" alt="image" src="https://github.com/user-attachments/assets/64cd384b-b995-40ef-9c19-385d710a1cf0" />

그 결과 15%로 수익률이 개선된 것을 볼 수 있었습니다. 

7. 실제 모의투자 (삼성전자, 두산)

<img width="845" height="337" alt="image" src="https://github.com/user-attachments/assets/923f38aa-0cad-4090-861d-0a01099d2d99" />

<img width="513" height="453" alt="image" src="https://github.com/user-attachments/assets/f52e4b37-86d7-4e19-a844-df8e80ed8a19" />
<img width="501" height="214" alt="image" src="https://github.com/user-attachments/assets/35f845c9-d8d1-4885-a9ef-efdd891ce5f3" />

두산의 백테스팅 결과를 반영하여 삼성전자의 실제 모의투자 파일(auto_paper_trading.py)의 매매 공식도 업데이트 하였습니다. 또한 현재 코스피가 상승장임을 반영하여, 주가가 하락해야 매도하는 코딩의 특성을 반영하여 초기 매수 코딩도 작성하였습니다. 

<img width="845" height="337" alt="image" src="https://github.com/user-attachments/assets/1b01bbfe-8e97-4a58-9e93-f29e742fc459" />
<img width="480" height="209" alt="image" src="https://github.com/user-attachments/assets/d3135e8a-8f17-4615-863a-f431e9108102" />

<img width="1069" height="339" alt="image" src="https://github.com/user-attachments/assets/71824a1f-35ee-43fd-9aea-dd5c11c1297c" />
<img width="445" height="204" alt="image" src="https://github.com/user-attachments/assets/1ffd4672-0388-4bad-8905-e17df2d452cf" />

그 결과 삼성전자와 두산 모두 초기 매매 및 이후 매수매도 주문이 성립하는 것을 볼 수 있습니다. 
