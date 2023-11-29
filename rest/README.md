![header](https://capsule-render.vercel.app/api?type=waving&color=gradient&height=300&section=header&text=한국투자증권%20KIS%20Developers&fontSize=50&animation=fadeIn&fontAlignY=38&desc=개발%20환경%20준비%20(파이썬%20세팅하기)&descAlignY=51&descAlign=62)

## 1. 개발 환경 준비 (파이썬 세팅하기)

### **1.1. 아나콘다(파이썬) 설치**

① 아나콘다 홈페이지([https://www.anaconda.com/download#downloads](https://www.anaconda.com/download#downloads))에서 본인 OS에 맞는 인스톨러를 다운로드 

![image](https://github.com/koreainvestment/open-trading-api/assets/87407853/7c3fdfe0-24b3-4dae-80ae-9c3eb83b1ba2)

② 설치파일 관리자 권한으로 실행 > Next 클릭 > 라이선스 화면 I Agree 클릭 > 설치타입 ‘All Users’ 클릭 > 설치 경로 C:\Anaconda3 으로 변경 & Next 클릭 > Advanced Options 화면에서 기본 값 그대로 Install 클릭

③ 설치 완료

### **1.2. 가상환경 생성 + 모듈 설치**

① Windows 로고 키 클릭 > Anaconda prompt 클릭 

![image](https://github.com/koreainvestment/open-trading-api/assets/87407853/8ae27b27-3990-4a70-b98d-41e2e6457440)

② prompt 창에서 아래 명령어를 순서대로 입력

**- (가상환경 생성 명령어) conda create –n koreainvest python=3.8**

**- (가상환경 실행 명령어) conda activate koreainvest**

**- (모듈 설치 명령어) pip install websockets pycryptodome requests pyyaml**
   
![image](https://github.com/koreainvestment/open-trading-api/assets/87407853/2a6651cf-25be-45fd-bd7e-5634cf3866fe)

- python websocket 사용을 위해 websockets 라이브러리를 설치하며, 주식체결통보 AES256 복호화 사용을 위한 pycrypodome 를 설치합니다.
- REST api 호출을 위해 requests 라이브러리를 설치하며, 개인정보(appkey, appsecret 등) 파일을 읽어들이기 위해 pyyaml 라이브러리를 설치합니다.

### **1.3. Pycharm 설치**

Pycharm은 파이썬 개발에 가장 널리 사용되는 통합 개발 환경으로 community 버전은 무료로 설치 가능합니다. 

① Jetbrain 홈페이지(https://www.jetbrains.com/ko-kr/pycharm/download) 에서 Pycharm 인스톨러를 다운로드

![image](https://github.com/koreainvestment/open-trading-api/assets/87407853/0a816854-f748-4778-aeca-5f8cf66fc118)

② 인스톨러 실행 > Next 클릭 > 설치 완료 시 Finish 클릭 > Pycharm 실행

![image](https://github.com/koreainvestment/open-trading-api/assets/87407853/c368369d-ea00-470e-92bc-c2d7bde015f1)

### **1.4. Project 생성 및 Python Interpreter 설정하기**

① New Project 클릭 > 하단에 Previously configured Interpreter 클릭 > 우측의 Add Interpreter – Add Local Interpreter 클릭 

![image](https://github.com/koreainvestment/open-trading-api/assets/87407853/2e90ce4b-c7d8-4b41-a2f2-9fce45660a83)

② 새 창이 뜨면 좌측의 Conda Environment 클릭 > Use existing environment - koreainvest 선택 > OK 클릭 > Create 클릭

![image](https://github.com/koreainvestment/open-trading-api/assets/87407853/4bbf7777-6d23-46ed-8914-ba294bd708c7)

### **1.5. (option) Postman 설치 및 사용하기**

포스트맨(Postman)은 개발자들이 API를 디자인하고 빌드하고 테스트하고 반복하기 위한 API 플랫폼입니다. 

Postman는 테스트베드 기능을 효율적으로 제공하여, 코드를 작성하기 전 API를 호출해보고 응답값을 확인해볼 수 있는 테스트해볼 수 있으며, 여러 언어(C, Java, Python 등)로 샘플코드를 자동으로 생성해주는 기능을 제공합니다.

![image](https://github.com/koreainvestment/open-trading-api/assets/87407853/dcfea9fb-5a95-49a9-86f2-f333b5b2f067)

 - 진행방법: 한국투자 Github ([https://github.com/koreainvestment/open-trading-api/tree/main/postman](https://github.com/koreainvestment/open-trading-api/tree/main/postman)) 의 순서대로 진행
