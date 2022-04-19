![header](https://capsule-render.vercel.app/api?type=waving&color=auto&height=300&section=header&text=capsule%20render&fontSize=90&animation=fadeIn&fontAlignY=38&desc=Decorate%20GitHub%20Profile%20or%20any%20Repo%20like%20me!&descAlignY=51&descAlign=62)
<p align='center'> 한국투자증권 KIS Developers </p>
<p align='center'>
  <a href="https://apiportal.koreainvestment.com/intro">
    <img src="https://img.shields.io/badge/IDEA%20ISSUE%20-%23F7DF1E.svg?&style=for-the-badge&&logoColor=white"/>
  </a>
  <a href="#apiList">
    <img src="https://img.shields.io/badge/DEMO%20-%234FC08D.svg?&style=for-the-badge&&logoColor=white"/>
  </a>
</p>

## 1. KIS Developers 개발자 센터 소개
[KIS Developers](https://apiportal.koreainvestment.com/)는 한국투자증권의 트레이딩 서비스를 오픈API로 제공하여 개발자들이 다양한 금융서비스를 만들 수 있도록 지원하는 개발자 센터입니다. KIS Developers에서는 개발자의 금융 서비스 개발을 지원하기 위해 API 문서 메뉴 내 API에 대한 상세한 설명과 예제를 제공합니다. 전문 개발자가 아닌 일반인들도 쉽게 금융 서비스를 만들 수 있습니다.

* 제휴 문의는 [제휴안내 페이지](https://apiportal.koreainvestment.com/howto-register)에서 제휴 신청 부탁드립니다.
* API 사용 관련 문의는 [Q&A 페이지](https://apiportal.koreainvestment.com/community/10000000-0000-0011-0000-000000000003)에서 문의 부탁드립니다.

## 2. 이용 안내
### 2.1. 사전 준비
KIS Developers 서비스는 한국투자증권 홈페이지에서 신청하실 수 있습니다. 신청을 위해서는 2가지 사전 준비물이 필요합니다. 첫 번째로는 한국투자증권 계좌가 개설되어있어야 하며, 두 번째로는 한국투자증권 ID 등록이 필요합니다. 만약 계좌가 없으시다면 한국투자증권 앱을 통해 비대면 개설을 진행하거나, 가까운 영업점을 방문해주시길 바랍니다.

-   한국투자증권 앱 :  [https://securities.koreainvestment.com/main/A_CO_10004.jsp](https://securities.koreainvestment.com/main/A_CO_10004.jsp)
-   가까운 영업점 찾기 :  [https://securities.koreainvestment.com/main/customer/guide/branch/branch.jsp](https://securities.koreainvestment.com/main/customer/guide/branch/branch.jsp)
### 2.2. 서비스 신청
![enter image description here](https://wikidocs.net/images/page/159333/KIS_Developers_%EC%84%9C%EB%B9%84%EC%8A%A4_%EC%8B%A0%EC%B2%AD%ED%95%98%EA%B8%B0.png)

서비스 신청 페이지까지 2가지 경로로 접속 가능합니다. 
* [KIS Developers](https://apiportal.koreainvestment.com/) 우상단 API신청 버튼 클릭
* 한국투자증권 홈페이지 [서비스신청 > Open API > KIS Developers > KIS Developers 서비스 신청하기]

위 그림과 같은 서비스신청 페이지에서 등록하신 휴대폰 인증을 통해 본인 인증을 완료합니다.

### 2.3.유의사항 확인
![enter image description here](https://wikidocs.net/images/page/159301/%EC%9C%A0%EC%9D%98%EC%82%AC%ED%95%AD%ED%99%95%EC%9D%B8.JPG)

다음으로는 유의사항확인입니다. 서비스 사용에 관한 유의사항을 정독하여 충분하게 숙지하신 뒤, 동의를 진행합니다. 개인정보 처리와 서비스 이용약관에 대해 미동의 시, 서비스 이용이 불가합니다.

### 2.4. 신청정보 확인
![enter image description here](https://wikidocs.net/images/page/159301/%EC%8B%A0%EC%B2%AD%EC%A0%95%EB%B3%B4.JPG)

해당 화면에서는 서비스 신청 정보를 확인하실 수 있습니다. 주요하게 확인할 사항 3가지를 소개해드리겠습니다. 첫 번째로 상단 테이블에 위치한 **이메일**은 사전에 등록한 이메일로 향후 KIS Developers ID/PW 찾기에 활용되니 꼭 기억하시길 바랍니다. 다음으로 하단 테이블에 위치한 **계좌정보**에서 종합계좌, 모의계좌 각각 한 계좌씩 총 두 개의 계좌를 신청할 수 있습니다. 만약 종합계좌, 모의계좌 중 하나만 선택하신 뒤 완료하셨다면 나중에 추가 혹은 변경이 가능한 점 참고하시길 바랍니다. 마지막으로 KIS Developers **사용자 ID**는 향후 KIS Developers 포탈에서 사용되는 ID로 기존 등록된 HTS ID와 동일합니다.

이 외에 최하단에 위치한 문자메시지 설정을 통해 서비스 만료 1개월 전 메시지를 받을 수 있으니 참고하시길 바랍니다.

### 2.5. 신청 완료
![enter image description here](https://wikidocs.net/images/page/159301/%EC%84%9C%EB%B9%84%EC%8A%A4%EC%8B%A0%EC%B2%AD%EC%99%84%EB%A3%8C.JPG)
신청한 계좌의 App Key와 App Secret을 확인합니다. 두 암호키를 통해 계좌에 접근할 수 있는 토큰을 발급받을 수 있어, 타인에게 유출을 금하며 관리에 유의해야합니다. 유출시 즉시 홈페이지에서 재발급 하시기 바랍니다.

## 3. API 제공 목록 <a id="apiList">

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

## 4. API 예제 목록

|구분|예제명|지원언어|
|--|--|--|
|rest|kis_api.py|python|
|websocket|ops_ws_sample.jar|java|
|websocket|ops_ws_sample.html|js|
|websocket|ops_ws_sample.py|python|
|websocket|ws_realstkprice.py|python|
|websocket|ws_realstkquote.py|python|

![Footer](https://capsule-render.vercel.app/api?type=waving&color=gradient&height=200&section=footer)
