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

3. 
