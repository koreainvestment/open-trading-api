# ECO4126 Final Project: Samsung Auto Trader

한국투자증권 Open API REST를 이용한 삼성전자(005930) 모의투자 자동매매 시스템 구현 프로젝트 보고서입니다.

## 1. 프로젝트 개요
이 프로젝트는 한국투자증권(KIS) Open API REST 방식만을 사용하여 삼성전자 005930 종목의 모의투자 자동매매를 수행하는 Python 시스템을 구현합니다. 목표는 모의투자 환경에서 안전하게 지정가 매수/매도 주문을 제출하고 주문 전후 계좌 상태를 확인하는 것입니다.

## 2. 개발 목표
- `REST API only` 기반으로 구현
- `websocket` 미사용
- `requests` 라이브러리 사용
- `DRY_RUN=true` 기본 실행
- `PAPER_TRADING=true` 기본 설정
- `GH_ACCOUNT`, `GH_APPKEY`, `GH_APPSECRET` 환경변수로 인증 정보 로드
- `GH_PRODUCT_CODE` 기본값 `01`
- 한 사이클 실행 후 종료하는 `--once` 옵션 지원

## 3. 시스템 구성
- `samsung_auto_trader/config.py`: 환경변수 및 기본값 관리
- `samsung_auto_trader/auth.py`: OAuth 토큰 획득 및 동일일 캐싱
- `samsung_auto_trader/api_client.py`: REST 공통 요청 처리, 재시도, 토큰 재발급
- `samsung_auto_trader/market_data.py`: 현재가 조회 기능
- `samsung_auto_trader/account.py`: 계좌 잔고 및 보유 종목 조회
- `samsung_auto_trader/orders.py`: 매수/매도 주문 실행
- `samsung_auto_trader/trader.py`: 거래 루프 및 실행 제어
- `samsung_auto_trader/logger.py`: 일관된 로그 출력

## 4. 인증 흐름
1. 환경변수 `GH_ACCOUNT`, `GH_APPKEY`, `GH_APPSECRET` 로드
2. `auth.py`가 KIS OAuth 토큰 발급 요청 수행
3. 발급된 토큰을 `token_cache.json`에 저장
4. 동일한 날짜에는 저장된 토큰을 재사용하여 인증 호출 최소화
5. `401` 오류 발생 시 자동 재인증으로 토큰 갱신

## 5. 모의투자 및 안전 전략
- 기본 모드는 `DRY_RUN=true`로 실제 주문을 전송하지 않습니다.
- 기본 `PAPER_TRADING=true`로 모의투자 TR ID를 사용합니다.
- `place_order()`는 `paper_trading` 플래그에 따라 모의투자용 TR ID(`VTTC0802U`, `VTTC0801U`) 또는 실거래용 TR ID(`TTTC0802U`, `TTTC0801U`)를 선택합니다.
- `--no-dry-run`을 사용해야 실제 주문 요청이 전송됩니다.
- `--once` 옵션으로 한 사이클만 실행하여 테스트에 안전합니다.
- 거래 시간 외 실행 시 루프를 종료하도록 되어 있습니다.

## 6. 삼성전자 005930 매매 로직
1. 현재가 조회
2. 계좌 현금 및 보유 종목 조회
3. 매수 지정가 = 현재가 - `ORDER_OFFSET_KRW`
4. 매도 지정가 = 현재가 + `ORDER_OFFSET_KRW`
5. 매수 가능 수량을 현재가와 현금으로 계산
6. `DRY_RUN`이 해제된 경우에만 매수/매도 주문 제출
7. 주문 후 30초 대기 후 계좌 상태 재조회
8. `--once` 모드로 한 사이클 종료

## 7. 실행 방법
### 필수 환경변수
- `GH_ACCOUNT`
- `GH_APPKEY`
- `GH_APPSECRET`

### 선택 환경변수
- `GH_PRODUCT_CODE` (기본값 `01`)

### 실행 예시
- 한 사이클 dry-run 테스트:
  - `python -m samsung_auto_trader.main --once --dry-run`
- 모의투자 주문 요청:
  - `python -m samsung_auto_trader.main --once --no-dry-run`
- 지속 실행 모드:
  - `python -m samsung_auto_trader.main`

## 8. 폴더 구조
```
open-trading-api/
  samsung_auto_trader/
    main.py
    config.py
    auth.py
    api_client.py
    market_data.py
    account.py
    orders.py
    trader.py
    logger.py
    requirements.txt
    README.md
  .env.example
  docs/
    assets/.gitkeep
  outputs/.gitkeep
```

## 9. 안전 설계 요약
- 기본 `DRY_RUN=true`로 실제 주문 차단
- 기본 `PAPER_TRADING=true`로 모의투자용 TR ID 사용
- 동일일 토큰 캐시로 인증 호출 최소화
- 30초 간격으로 주문 후 계좌 재확인
- `--once` 옵션으로 안전한 테스트 모드

## 10. 검증 및 테스트 계획
- `python -m compileall samsung_auto_trader`로 문법 검사
- `python -m samsung_auto_trader.main --once --dry-run`로 한 사이클 실행 검증
- `GH_*` 환경변수를 설정하여 실제 KIS REST 요청 흐름 확인
