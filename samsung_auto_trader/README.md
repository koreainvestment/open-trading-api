# Samsung Auto Trader

삼성전자(`005930`)를 대상으로 한국투자증권 Open API를 사용해 작동하는 간단한 모의투자 자동매매 시스템입니다.

이 프로젝트는 복잡한 수익 전략보다, Open API 기반 자동매매 시스템이 정상적으로 작동하는지 보여주는 데 초점을 둡니다.

주요 기능은 다음과 같습니다.

- 접근 토큰 발급 및 캐시 재사용
- 삼성전자 현재가 조회
- 계좌 현금 및 보유 수량 조회
- 단순 매수/매도 판단
- 지정가 주문 요청
- 주문 성공/실패 메시지 처리
- 주문 후 계좌 상태 재확인
- 반복 실행 기반 자동 모니터링

---

## 1. Project Structure

```text
samsung_auto_trader/
├── main.py              # 프로그램 실행 시작점
├── config.py            # API 주소, 계좌번호, 환경변수 설정
├── auth.py              # 접근 토큰 발급 및 캐시 관리
├── api_client.py        # API 요청 공통 처리 및 실패 메시지 처리
├── market_data.py       # 삼성전자 현재가 조회
├── account.py           # 계좌 현금 및 보유 주식 조회
├── orders.py            # 매수/매도 주문 요청 및 결과 파싱
├── trader.py            # 전체 자동매매 흐름 제어
├── logger.py            # 로그 출력 설정
├── token_cache.json     # 발급받은 토큰 캐시 파일
└── requirements.txt     # 필요한 Python 패키지 목록
```

---

## 2. Requrements

-Python 3.10 이상 권장
-requests 패키지 필요
-한국투자증권 Open API 모의투자 계정 필요
-GitHub Codespaces 또는 로컬 Python 실행 환경 필요

-필요 패키지 설치: pip install -r requirements.txt

---

## 3. Run

-프로젝트 폴더로 이동한 뒤 실행합니다.
cd /workspaces/open-trading-api/samsung_auto_trader
python main.py

-다른 터미널에서 강제 종료하려면 아래 명령어를 사용합니다.
pkill -f main.py

---

## 4. 로직

```text
1. 삼성전자 현재가를 조회한다.
2. 계좌의 주문 가능 현금과 보유 수량을 조회한다.
3. 현재가를 기준으로 매수 가격과 매도 가격을 계산한다.
4. 매수 가능 여부와 매도 가능 여부를 판단한다.
5. 조건이 맞으면 한 사이클 안에서 매수 주문 최대 1번, 매도 주문 최대 1번을 시도한다.
6. 주문 후 계좌 상태를 다시 조회한다.
7. 다음 사이클까지 대기한다.

-매수로직
매수 가격 = 현재가 - 1,000원
매수 수량 = 1주

-매도로직
매도 가격 = 현재가 + 1,000원
매도 수량 = 1주
```
