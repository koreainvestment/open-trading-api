![header](https://capsule-render.vercel.app/api?type=waving&color=gradient&height=300&section=header&text=한국투자증권%20KIS%20Developers&fontSize=50&animation=fadeIn&fontAlignY=38&desc=Open%20Trading%20API%20Postman%20Sample%20Code&descAlignY=51&descAlign=62)


## 1. Postman이란

[포스트맨(Postman)](https://www.postman.com/)은 개발자들이 API를 디자인하고 빌드하고 테스트하고 반복하기 위한 API 플랫폼입니다. 2022년 4월 기준으로 포스트맨의 등록 사용자는 20,000,000명 이상, 개방 API 수는 75,000개로 보고되었으며, 세계 최대의 공개 API 허브입니다. (출처 : [위키백과-포스트맨](https://ko.wikipedia.org/wiki/포스트맨_(소프트웨어)))


## 2. 사전 준비 사항
1.  [한국투자증권 홈페이지](https://securities.koreainvestment.com/main/A_CO_10004.jsp) 혹은 [가까운 영업점](https://securities.koreainvestment.com/main/customer/guide/branch/branch.jsp)에서 계좌 개설(모의계좌 or 실전계좌) → **계좌번호 준비**
2.  [KIS Developers 홈페이지](https://apiportal.koreainvestment.com/)에서 API신청 - 사용할 계좌번호로 API신청 → **APP KEY & APP SECRET 준비**
3.  [Postman](https://www.postman.com/downloads/) 설치


## 3. Postman을 활용한 API 호출 방법
### 3.1. Postman 실행 및 json 파일 Import
Postman 실행 후 아래 4개의 json 파일들을 Import 해주세요. Import하는 방법은 Postman 좌측 상단의 Import 버튼을 누르시고 File 탭에 파일을 끌어다 놓아주세요. 파일이 정상적으로 끌어와지면 아래 이미지와 같이 파일들이 식별되며, 이후 Import 버튼을 누르시면 됩니다.
* 모의계좌만을 사용하시는 경우 1,2번 파일을, 실전계좌만을 사용하시는 경우 3,4번 파일만 Import하셔도 됩니다.

|순번 |파일명 |파일 상세 |
|--|--|--|
|1|모의계좌_POSTMAN_샘플코드_v1.2.json|postman collections json file(모의계좌용)|
|2|모의계좌_POSTMAN_환경변수.json|postman environments json file(모의계좌용)|
|3|실전계좌_POSTMAN_샘플코드_v1.2.json|postman collections json file(실전계좌용)|
|4|실전계좌_POSTMAN_환경변수.json|postman environments json file(실전계좌용)|

![pm_image01](https://user-images.githubusercontent.com/87407853/185285464-84554b6c-2ed6-47da-86c4-7e73197ae26f.png)

### 3.2. 환경변수 설정
Import가 완료되면 환경변수 설정을 해줍니다. 모의계좌를 활용하여 API테스트를 하실 경우 왼쪽 바의 Environments의 모의Env를, 실전계좌를 활용하여 API테스트를 하실 경우 실전 Env를 환경변수로 사용합니다. 따라서 사용하실 환경변수 값들을 채워주어야 합니다. 아래 설명대로 값들을 전부 채워 넣어주세요. 값을 채워 넣을 때는 Initial Value, Current Value 모두 값을 넣어주셔야 합니다. (VTS, PROD는 이미 값이 채워져 있으니 수정하지 말아주세요.)

* 아직 다중계좌 지원 전이어서, 실전계좌와 모의계좌 모두 하나의 계좌(주식 or 선물옵션)만 API 신청이 가능합니다. 따라서 API 신청한 계좌번호와 해당 계좌의 APPKEY, APPSECRET 값만 채워주시면 됩니다. 
* 예를 들어, 주식계좌로 API 신청하셨으면 아래 각 표의 1,3,4번만을 채워주시면 되고, 선물옵션계좌로 API신청하셨으면 아래 각 표의 2,5,6번만을 채워주시면 됩니다. (9월 말 다중계좌 오픈 예정, 업데이트 사항 KIS Developers - 공지사항 참고)

#### 3.2.1. 모의Env의 경우 아래의 값들을 각각 채워 넣어줍니다.
|순번 |환경변수명 |값(Initial Value, Current Value) |값 예시 |
|--|--|--|--|
|1|CANO|본인의 모의계좌 종합계좌번호 8자리(주식)|ex.50012345|
|2|CANO_T|본인의 모의계좌 종합계좌번호 8자리(선물옵션)|ex.60012345|
|3|VTS_APPKEY|홈페이지에서 발급 받은 계좌번호(주식) APP KEY|ex.PSabcmEJH4U9dfewefwJdfsa4P5qewrPdf4n|
|4|VTS_APPSECRET|홈페이지에서 발급 받은 계좌번호(주식) APP SECRET|ex.FoB6uLRLw5o0Ozxsdfkejklskjkr...uFg9Ya0=|
|5|VTT_APPKEY|홈페이지에서 발급 받은 계좌번호(선물옵션) APP KEY|ex.PSabcmEJH4U9dfewefwJdfsa4P5qewrPdf4n|
|6|VTT_APPSECRET|홈페이지에서 발급 받은 계좌번호(선물옵션) APP SECRET|ex.FoB6uLRLw5o0Ozxsdfkejklskjkr...uFg9Ya0=|

#### 3.2.2. 실전Env의 경우 아래의 값들을 각각 채워 넣어줍니다.
|순번 |환경변수명 |값(Initial Value, Current Value) |값 예시 |
|--|--|--|--|
|1|CANO_REAL|본인의 실전계좌 종합계좌번호(주식)|ex.50012345|
|2|CANO_REAL_T|본인의 실전계좌 종합계좌번호(선물옵션)|ex.60012345|
|3|PROD_APPKEY|홈페이지에서 발급 받은 계좌번호(주식) APP KEY|ex.PSabcmEJH4U9dfewefwJdfsa4P5qewrPdf4n|
|4|PROD_APPSECRET|홈페이지에서 발급 받은 계좌번호(주식) APP SECRET|ex.FoB6uLRLw5o0Ozxsdfkejklskjkr...uFg9Ya0=|
|5|PROT_APPKEY|홈페이지에서 발급 받은 계좌번호(선물옵션) APP KEY|ex.PSabcmEJH4U9dfewefwJdfsa4P5qewrPdf4n|
|6|PROT_APPSECRET|홈페이지에서 발급 받은 계좌번호(선물옵션) APP SECRET|ex.FoB6uLRLw5o0Ozxsdfkejklskjkr...uFg9Ya0=|


### 3.3. 환경변수 선택
모의계좌를 활용하여 API테스트를 하실 경우 왼쪽 바의 Collections에서 모의투자(모의Env)를, 실전계좌를 활용하여 API테스트를 하실 경우 실전투자(실전Env)를 선택합니다.


### 3.4. API 호출
호출하고 싶은 API를 각 폴더에서 찾아 header값, body값을 변경하시면서 사용하시면 됩니다.
* 각 API 이름 앞에 V는 모의계좌를, J는 실전계좌를 의미합니다.
* **(중요)** GET 요청의 경우, 계좌번호 환경변수가 불러와져 그대로 사용하시면 되지만, POST 요청의 경우 계좌번호(CANO)를 BODY값에 직접 입력하셔야 하는 점 유의 부탁드립니다. **따라서 POST API 호출 테스트하실 때는 반드시 Body 값의 계좌번호(CANO)를 본인의 종합계좌번호 8자리로 수정 후 호출하셔야 합니다.**


## 4. Postman 샘플코드 목록

|구분 |API명 |모의투자 제공 여부 |실전투자 제공 여부 |
|--|--|--|--|
|OAuth인증|접근토큰발급|⭕|⭕|
|OAuth인증|접근토큰폐기|⭕|⭕|
|OAuth인증|Hashkey|⭕|⭕|
|국내주식주문|주식주문(현금)|⭕|⭕|
|국내주식주문|주식주문(신용)| |⭕|
|국내주식주문|주식주문(정정취소)|⭕|⭕|
|국내주식주문|주식정정취소가능주문조회| |⭕|
|국내주식주문|주식일별주문체결조회|⭕|⭕|
|국내주식주문|주식잔고조회|⭕|⭕|
|국내주식주문|매수가능조회|⭕|⭕|
|국내주식주문|주식예약주문| |⭕|
|국내주식주문|주식예약주문정정취소| |⭕|
|국내주식주문|주식예약주문조회| |⭕|
|국내주식시세|주식현재가 시세|⭕|⭕|
|국내주식시세|주식현재가 체결|⭕|⭕|
|국내주식시세|주식현재가 일자별|⭕|⭕|
|국내주식시세|주식현재가 호가 예상체결|⭕|⭕|
|국내주식시세|주식현재가 투자자|⭕|⭕|
|국내주식시세|주식현재가 회원사|⭕|⭕|
|국내주식시세|ELW현재가 시세|⭕|⭕|
|국내주식시세|국내주식기간별시세(일/주/월/년)|⭕|⭕|
|국내주식시세|국내주식업종기간별시세(일/주/월/년)|⭕|⭕|
|국내주식시세|주식현재가 당일시간대별체결|⭕|⭕|
|국내주식시세|주식현재가 시간외시간별체결|⭕|⭕|
|국내주식시세|주식현재가 시간외일자별주가|⭕|⭕|
|국내주식실시간|주식현재가 실시간주식체결가|⭕|⭕|
|국내주식실시간|주식현재가 실시간주식호가|⭕|⭕|
|국내주식실시간|주식현재가 실시간주식체결통보|⭕|⭕|
|국내선물옵션주문|선물옵션 주문|⭕|⭕|
|국내선물옵션주문|선물옵션 정정취소주문|⭕|⭕|
|국내선물옵션주문|선물옵션 주문체결내역조회|⭕|⭕|
|국내선물옵션주문|선물옵션 잔고현황|⭕|⭕|
|국내선물옵션주문|선물옵션 주문가능|⭕|⭕|
|국내선물옵션시세|선물옵션 시세|⭕|⭕|
|국내선물옵션시세|선물옵션 시세호가|⭕|⭕|
|국내선물옵션시세|선물옵션기간별시세(일/주/월/년)|⭕|⭕|
|해외주식주문|해외주식 주문|⭕|⭕|
|해외주식주문|해외주식 정정취소주문|⭕|⭕|
|해외주식주문|해외주식 예약주문접수|⭕|⭕|
|해외주식주문|해외주식 예약주문접수취소|⭕|⭕|
|해외주식주문|해외주식 미체결내역|⭕|⭕|
|해외주식주문|해외주식 잔고|⭕|⭕|
|해외주식주문|해외주식 주문체결내역|⭕|⭕|
|해외주식주문|해외주식 체결기준현재잔고|⭕|⭕|
|해외주식주문|해외주식 주야간원장구분조회|⭕|⭕|
|해외주식주문|해외주식 예약주문조회| |⭕|
|해외주식주문|해외주식 매수가능금액조회| |⭕|
|해외주식현재가|해외주식 현재체결가|⭕|⭕|
|해외주식현재가|해외주식 기간별시세|⭕|⭕|
|해외주식현재가|해외주식 종목/지수/환율기간별시세(일/주/월/년)|⭕|⭕|
|해외주식현재가|해외주식 조건검색|⭕|⭕|


**사용하시면서 어려운 점이 생기면 KIS Developers - Q&A 게시판에 문의 부탁드립니다 :)**


![Footer](https://capsule-render.vercel.app/api?type=waving&color=gradient&height=200&section=footer)
