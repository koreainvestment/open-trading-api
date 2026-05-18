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

~~~text
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
~~~

---

## 2. Requirements

- Python 3.10 이상 권장
- `requests` 패키지 필요
- 한국투자증권 Open API 모의투자 계정 필요
- GitHub Codespaces 또는 로컬 Python 실행 환경 필요

필요 패키지 설치:

~~~bash
pip install -r requirements.txt
~~~

---

## 3. Run

프로젝트 폴더로 이동한 뒤 실행합니다.

~~~bash
cd /workspaces/open-trading-api/samsung_auto_trader
python main.py
~~~

실행 중인 프로그램을 멈추려면 터미널에서 `Ctrl + C`를 누릅니다.

다른 터미널에서 강제 종료하려면 아래 명령어를 사용합니다.

~~~bash
pkill -f main.py
~~~

---

## 4. Trading Logic

이 시스템은 한 사이클마다 현재가 조회, 잔고 조회, 주문 판단, 주문 요청, 사후 잔고 확인을 수행합니다.

기본 흐름은 다음과 같습니다.

~~~text
1. 삼성전자 현재가를 조회한다.
2. 계좌의 주문 가능 현금과 보유 수량을 조회한다.
3. 현재가를 기준으로 매수 가격과 매도 가격을 계산한다.
4. 매수 가능 여부와 매도 가능 여부를 판단한다.
5. 조건이 맞으면 한 사이클 안에서 매수 주문 최대 1번, 매도 주문 최대 1번을 시도한다.
6. 주문 후 계좌 상태를 다시 조회한다.
7. 다음 사이클까지 대기한다.
~~~

### Buy Logic

매수 로직은 다음과 같습니다.

~~~text
매수 가격 = 현재가 - 1,000원
매수 수량 = 1주
~~~

계좌의 주문 가능 현금이 `매수 가격 × 1주` 이상이면 삼성전자 1주를 지정가 매수 주문으로 제출합니다.

### Sell Logic

매도 로직은 다음과 같습니다.

~~~text
매도 가격 = 현재가 + 1,000원
매도 수량 = 1주
~~~

계좌에 삼성전자 보유 수량이 1주 이상 있으면 삼성전자 1주를 지정가 매도 주문으로 제출합니다.

---

## 5. Repeated Execution

이 시스템은 한 번 실행하고 끝나는 프로그램이 아니라, 일정 시간마다 반복 실행되는 구조입니다.

~~~text
현재가 조회
→ 잔고 조회
→ 주문 판단
→ 주문 요청
→ 주문 후 잔고 확인
→ 대기
→ 다시 반복
~~~

반복 주기는 `config.py`의 `polling_interval_seconds` 값으로 조정할 수 있습니다.

예시:

~~~python
polling_interval_seconds = 60
~~~

위 설정은 60초마다 한 번씩 매매 사이클을 실행한다는 뜻입니다.

---

## 6. Log Example

실행하면 다음과 같은 요약 로그가 출력됩니다.

~~~text
[CYCLE_START] symbol=005930
[MARKET] symbol=005930 current_price=281000
[ACCOUNT_BEFORE] cash=9820053 holding_qty=1
[STRATEGY] buy_price=280000 sell_price=282000 order_qty=1 can_buy=True can_sell=True
[ORDER_RESULT] side=buy success=False order_id=None msg=모의투자 장종료 입니다.
[ORDER_RESULT] side=sell success=False order_id=None msg=모의투자 장종료 입니다.
[ACCOUNT_AFTER] cash=9820053 holding_qty=1
[EXECUTION_CHECK] result=No clear execution change was detected.
[CYCLE_END] symbol=005930 buy_orders=1 sell_orders=1
[SLEEP] next_cycle_after_seconds=60
~~~

---

## 7. Common Messages

### `모의투자 장종료 입니다.`

주문 요청은 정상적으로 전송되었지만, 모의투자 서버에서 주문 가능 시간이 아니라고 판단한 경우입니다.

이는 코드 오류가 아니라 API 업무상 거절입니다.

### `EGW00201`

초당 거래건수를 초과했다는 의미입니다.

이 시스템은 API 호출 사이에 대기 시간을 두어 해당 오류 가능성을 줄입니다.

---

## 8. Notes

- 이 프로젝트는 학습 및 데모용 모의투자 시스템입니다.
- 실제 투자 수익을 보장하지 않습니다.
- 지정가 주문이므로 주문이 제출되어도 바로 체결되지 않을 수 있습니다.
- 현재 코드는 미체결 주문을 다음 사이클까지 추적하지 않습니다.
- 주문 후 잔고를 다시 조회하여 체결 여부를 간단히 추정합니다.
- `token_cache.json`에는 접근 토큰이 저장될 수 있으므로 GitHub에 올리지 않는 것이 좋습니다.
- API Key와 App Secret은 코드에 직접 작성하지 말고 환경변수 또는 Codespaces Secrets로 관리해야 합니다.