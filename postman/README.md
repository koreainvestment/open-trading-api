![header](https://capsule-render.vercel.app/api?type=waving&color=gradient&height=300&section=header&text=한국투자증권%20KIS%20Developers&fontSize=50&animation=fadeIn&fontAlignY=38&desc=Open%20Trading%20API%20Postman%20Sample%20Code&descAlignY=51&descAlign=62)


## 1. Postman이란

[포스트맨(Postman)](https://www.postman.com/)은 개발자들이 API를 디자인하고 빌드하고 테스트하고 반복하기 위한 API 플랫폼입니다. 2022년 4월 기준으로 포스트맨의 등록 사용자는 20,000,000명 이상, 개방 API 수는 75,000개로 보고되었으며, 이는 세계 최대의 공개 API 허브를 구성한 것입니다. (출처 : [위키백과-포스트맨](https://ko.wikipedia.org/wiki/포스트맨_(소프트웨어)))


## 2. 사전 준비 사항
1.  [한국투자증권 홈페이지](https://securities.koreainvestment.com/main/A_CO_10004.jsp) 혹은 [가까운 영업점](https://securities.koreainvestment.com/main/customer/guide/branch/branch.jsp)에서 계좌 개설(모의계좌 or 실전계좌) → **계좌번호 준비**
2.  [KIS Developers 홈페이지](https://apiportal.koreainvestment.com/)에서 API신청 - 사용할 계좌번호로 API신청 → **APP KEY & APP SECRET 준비**
3.  [Postman](https://www.postman.com/downloads/) 설치


## 3. Postman을 활용한 API 호출 방법
### 3.1. Postman 실행 및 json 파일 Import
Postman 실행 후 아래 4개의 json 파일들을 Import 해주세요.
* 모의계좌만을 사용하시는 경우 1,2번 파일을, 실전계좌만을 사용하시는 경우 3,4번 파일만 Import하셔도 됩니다.

|순번 |파일명 |파일 상세 |
|--|--|--|
|1|모의계좌_POSTMAN_샘플코드.json|postman collections json file(모의계좌용)|
|2|모의계좌_POSTMAN_환경변수.json|postman environments json file(모의계좌용)|
|3|실전계좌_POSTMAN_샘플코드.json|postman collections json file(실전계좌용)|
|4|실전계좌_POSTMAN_환경변수.json|postman environments json file(실전계좌용)|

### 3.2. 환경변수 설정
Import가 완료되면 환경변수 설정을 해줍니다. 모의계좌를 활용하여 API테스트를 하실 경우 왼쪽 바의 Environments의 모의Env를, 실전계좌를 활용하여 API테스트를 하실 경우 실전 Env를 환경변수로 사용합니다. 따라서 사용하실 환경변수 값들을 채워주어야 합니다. 아래 설명대로 값들을 전부 채워 넣어주세요. 값을 채워 넣을 때는 Initial Value, Current Value 모두 값을 넣어주셔야 합니다. (VTS, PROD는 이미 값이 채워져 있으니 수정하지 말아주세요.)

#### 3.2.1. 모의Env의 경우 아래의 값들을 각각 채워 넣어줍니다.
|순번 |환경변수명 |값 |
|--|--|--|
|1|CANO|계좌번호(주식)|
|2|CANO_T|계좌번호(선물옵션)|
|3|VTS_APPKEY|홈페이지에서 발급 받은 계좌번호(주식) APP KEY|
|4|VTS_APPSECRET|홈페이지에서 발급 받은 계좌번호(주식) APP SECRET|
|5|VTT_APPKEY|홈페이지에서 발급 받은 계좌번호(선물옵션) APP KEY|
|6|VTT_APPSECRET|홈페이지에서 발급 받은 계좌번호(선물옵션) APP SECRET|


#### 3.2.2. 실전Env의 경우 아래의 값들을 각각 채워 넣어줍니다.
|순번 |환경변수명 |값 |
|--|--|--|
|1|CANO_REAL|계좌번호(주식)|
|2|CANO_REAL_T|계좌번호(선물옵션)|
|3|PROD_APPKEY|홈페이지에서 발급 받은 계좌번호(주식) APP KEY|
|4|PROD_APPSECRET|홈페이지에서 발급 받은 계좌번호(주식) APP SECRET|
|5|PROT_APPKEY|홈페이지에서 발급 받은 계좌번호(선물옵션) APP KEY|
|6|PROT_APPSECRET|홈페이지에서 발급 받은 계좌번호(선물옵션) APP SECRET|


### 3.3. 환경변수 선택
모의계좌를 활용하여 API테스트를 하실 경우 왼쪽 바의 Collections에서 모의투자(모의Env)를, 실전계좌를 활용하여 API테스트를 하실 경우 실전투자(실전Env)를 선택합니다.


### 3.4. API 호출
호출하고 싶은 API를 각 폴더에서 찾아 header값, body값을 변경하시면서 사용하시면 됩니다.
* 각 API 이름 앞에 V는 모의계좌를, J는 실전계좌를, T는 선물옵션계좌(모의/실전 공통)를 의미합니다.
* GET 요청의 경우, 계좌번호 환경변수가 불러와져 그대로 사용하시면 되지만, POST 요청의 경우 계좌번호를 BODY값에 직접 입력하셔야 하는 점 유의 부탁드립니다.


## 3.5. Postman 샘플코드 목록

|구분 |API명 |모의투자 제공 여부|
|--|--|--|
|OAuth인증|접근토큰발급|⭕|
|OAuth인증|접근토큰폐기|⭕|
|OAuth인증|Hashkey|⭕|
|국내주식주문|주식주문(현금)|⭕|
|국내주식주문|주식주문(신용)| |
|국내주식주문|주식주문(정정취소)|⭕|
|국내주식주문|주식정정취소가능주문조회| |
|국내주식주문|주식일별주문체결조회|⭕|
|국내주식주문|주식잔고조회|⭕|
|국내주식주문|매수가능조회|⭕|
|국내주식시세|주식현재가 시세|⭕|
|국내주식시세|주식현재가 체결|⭕|
|국내주식시세|주식현재가 일자별|⭕|
|국내주식시세|주식현재가 호가 예상체결|⭕|
|국내주식시세|주식현재가 투자자|⭕|
|국내주식시세|주식현재가 회원사|⭕|
|국내주식시세|ELW현재가 시세|⭕|
|국내주식실시간|주식현재가 실시간주식체결가|⭕|
|국내주식실시간|주식현재가 실시간주식호가|⭕|
|국내주식실시간|주식현재가 실시간주식체결통보|⭕|
|국재선물옵션주문|선물옵션 주문|⭕|
|국재선물옵션주문|선물옵션 정정취소주문|⭕|
|국재선물옵션주문|선물옵션 주문체결내역조회|⭕|
|국재선물옵션주문|선물옵션 잔고현황|⭕|
|국재선물옵션주문|선물옵션 주문가능| |
|국재선물옵션시세|선물옵션 시세| |
|국재선물옵션시세|선물옵션 시세호가| |
|해외주식주문|해외주식 주문|⭕|
|해외주식주문|해외주식 예약주문접수|⭕|
|해외주식주문|해외주식 정정취소주문|⭕|
|해외주식주문|해외주식 예약주문접수취소|⭕|
|해외주식주문|해외주식 미체결내역|⭕|
|해외주식주문|해외주식 잔고|⭕|
|해외주식주문|해외주식 주문체결내역|⭕|
|해외주식주문|해외주식 체결기준현재잔고|⭕|
|해외주식현재가|해외주식 현재체결가| |
|해외주식현재가|해외주식 기간별시세| |


**사용하시면서 어려운 점이 생기면 KIS Developers - Q&A 게시판에 문의 부탁드립니다 :)**


![Footer](https://capsule-render.vercel.app/api?type=waving&color=gradient&height=200&section=footer)
