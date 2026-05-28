# Auto Trading System

## 1. `presen` branch의 구조

`presen` 브랜치는 발표 및 제출용으로 정리한 브랜치입니다.

기존 한국투자증권 Open API 샘플 저장소에서 자동매매 시스템 실행에 필요한 부분만 남기고, 불필요한 샘플 코드와 보조 폴더는 제거했습니다.

```text
open-trading-api/
├── README.md
├── images/
│   ├── execution_log.png
│   └── account_status.png
├── .gitignore
└── samsung_auto_trader/
    ├── main.py
    ├── config.py
    ├── auth.py
    ├── api_client.py
    ├── market_data.py
    ├── account.py
    ├── orders.py
    ├── trader.py
    ├── logger.py
    └── requirements.txt
```

각 항목의 역할은 다음과 같습니다.

| 항목 | 설명 |
|---|---|
| `README.md` | 제출을 위해 작성한 시스템의 구조 |
| `images/` | 결과 이미지 저장 폴더 |
| `.gitignore` | 토큰, 캐시, 환경변수, Python 임시파일 등이 GitHub에 올라가지 않도록 관리하는 파일 |
| `samsung_auto_trader/` | 실제 자동매매 시스템 코드가 들어 있는 폴더 |

`token_cache.json`은 실행 중 생성될 수 있는 접근 토큰 캐시 파일입니다.  
보안상 업로드하지 않고 `.gitignore`를 통해 숨겼습니다.

---

## 2. `samsung_auto_trader` 폴더 구조

```text
samsung_auto_trader/
├── main.py              # 프로그램 실행 시작점
├── config.py            # API 주소, 계좌번호, 환경변수 설정
├── auth.py              # 접근 토큰 발급 및 캐시 관리
├── api_client.py        # API 요청 공통 처리 및 오류 메시지 처리
├── market_data.py       # 삼성전자 현재가 조회
├── account.py           # 계좌 현금 및 보유 주식 조회
├── orders.py            # 매수/매도 주문 요청
├── trader.py            # 전체 자동매매 흐름 제어
├── logger.py            # 로그 출력 설정
└── requirements.txt     # 필요한 Python 패키지 목록
```

실제 자동매매 흐름은 `trader.py`가 중심이 되어 다른 파일들의 기능을 순서대로 호출하는 방식으로 작동합니다.

---

## 3. `samsung_auto_trader` 코드 설명 및 역할

---

## 4. 실행 방법

프로젝트 루트에서 `samsung_auto_trader` 폴더로 이동합니다.

```bash
cd samsung_auto_trader
```

필요한 패키지를 설치합니다.

```bash
pip install -r requirements.txt
```

프로그램을 실행합니다.

```bash
python main.py
```

실행 중인 프로그램을 멈추려면 터미널에서 `Ctrl + C`를 누릅니다.

실행 후 자동매매 프로그램은 다음 순서로 작동합니다.

---

## 5. 매수·매도 로직

기본 설정

```text
대상 종목 = 삼성전자
종목 코드 = 005930
주문 수량 = 1주
매수 가격 = 현재가 - 1,000원
매도 가격 = 현재가 + 1,000원
```

이 프로젝트에서는 한 사이클 안에서 매수와 매도를 각각 최대 1번만 요청하도록 설정했습니다.

이 제한을 둔 이유는 반복 실행 중 과도한 주문 요청이 발생하는 것을 막기 위해서입니다.

한 번의 사이클은 다음 순서로 진행됩니다.

```text
1. 거래 가능 시간인지 확인
2. 삼성전자 현재가 조회
3. 계좌 현금 및 보유 수량 조회
4. 매수 가격 계산
5. 매도 가격 계산
6. 매수 가능 여부 판단
7. 매도 가능 여부 판단
8. 조건 충족 시 지정가 주문 요청
9. 주문 후 계좌 상태 재조회
10. 다음 사이클까지 대기
```

---

## 6. 실행 로그 결과 사진

아래 이미지는 자동매매 프로그램이 한 사이클 동안 실행된 결과입니다.



해당 로그에서는 현재가 조회, 계좌 조회, 매수/매도 주문 요청, 주문 후 계좌 재조회가 한 사이클 안에서 실행된 것을 확인할 수 있습니다.

아래 이미지는 계좌 현금 및 보유 수량 조회 결과입니다.

<img src="https://github.com/Kon9kongE2/open-trading-api/blob/presen/picture/execution_log.png" width="500">

<img src="https://github.com/Kon9kongE2/open-trading-api/blob/presen/picture/account.png" width="500">
