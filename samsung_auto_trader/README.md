# Samsung Auto Trader

삼성전자(005930)를 대상으로 하는 KIS Open API 모의투자 전용 REST 폴링형 자동매매 예제입니다.

## 폴더 구조

```text
samsung_auto_trader/
  main.py          # 실행 엔트리포인트
  config.py        # 환경변수, 계좌 파싱, 실행 설정
  auth.py          # 토큰 발급 및 same-day 캐시
  api_client.py    # 공통 HTTP 클라이언트, retry, hashkey
  market_data.py   # 현재가 조회
  account.py       # 잔고/보유종목 조회
  orders.py        # 매수/매도 주문
  trader.py        # trading window loop
  logger.py        # 로깅 설정
  trader.log       # 실행 로그 파일
  token_cache.json # 오늘 발급한 토큰 캐시
  requirements.txt # requests 의존성
```

## 역할

`config.py`는 `GH_ACCOUNT`, `GH_APPKEY`, `GH_APPSECRET`를 읽고, 계좌번호를 8-2 형식으로 분리합니다. `auth.py`는 모의투자 토큰을 오늘 날짜 기준으로 캐시하고, `api_client.py`는 KIS REST 호출과 주문용 hashkey 발급을 담당합니다.

`market_data.py`, `account.py`, `orders.py`는 각각 시세, 잔고, 주문만 책임집니다. `trader.py`는 09:10~15:30 사이에서만 반복 실행되며, 현재가 조회 후 매수/매도 지정가 주문을 넣고 각 주문 뒤에 다시 잔고를 확인합니다.

로그는 터미널과 함께 [trader.log](trader.log) 파일에도 저장됩니다.

## 환경 변수

필수:

- `GH_ACCOUNT` - KIS 계좌번호 8-2 형식. 예: `12345678-01` 또는 `1234567801`
- `GH_APPKEY` - 모의투자 App Key
- `GH_APPSECRET` - 모의투자 App Secret

선택:

- `KIS_BASE_URL` - 기본값 `https://openapivts.koreainvestment.com:29443`
- `TRADING_SYMBOL` - 기본값 `005930`
- `TRADING_ORDER_QTY` - 기본값 `1`
- `TRADING_PRICE_OFFSET_KRW` - 기본값 `1000`
- `TRADING_POLL_SECONDS` - 기본값 `180`
- `TRADING_VERIFY_DELAY_SECONDS` - 기본값 `5`
- `TRADING_REQUEST_TIMEOUT_SECONDS` - 기본값 `10`
- `TRADING_RETRY_COUNT` - 기본값 `2`
- `TRADING_RETRY_BACKOFF_SECONDS` - 기본값 `2`

## 설치

```bash
cd samsung_auto_trader
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 실행

```bash
export GH_ACCOUNT="12345678-01"
export GH_APPKEY="..."
export GH_APPSECRET="..."

python main.py
```

원하면 인자만 덮어쓸 수 있습니다.

```bash
python main.py --poll-seconds 180 --offset-krw 1000 --quantity 1
```

## 동작 방식

1. 토큰을 발급하거나 `token_cache.json`의 당일 토큰을 재사용합니다.
2. 삼성전자 현재가를 1회 조회합니다.
3. 잔고/보유종목을 1회 조회합니다.
4. 현재가 기준으로 매수 지정가와 매도 지정가를 계산해 주문합니다.
5. 각 주문 뒤에 잔고/보유종목을 다시 조회해 체결 여부를 추정합니다.
6. 09:10~15:30 사이에만 반복하고, 15:30 이후 자동 종료합니다.

## 주의

이 코드는 모의투자 전용 예제입니다. 실제 운용 전에 반드시 계좌 환경과 주문 가능 여부를 확인하고, 요청 제한이 낮다는 점을 고려해 폴링 간격을 충분히 길게 유지하세요.
