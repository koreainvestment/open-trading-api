# Samsung Electronics Auto Trader

이 프로젝트는 한국투자증권(KIS) Open API를 이용하여 삼성전자(005930) 주식을 모의투자 환경에서 자동 주문하는 Python 시스템입니다.

## 프로젝트 개요
- 대상 종목: 삼성전자 005930
- API 방식: REST API만 사용
- 환경: 모의투자(mock trading)
- 주문 방식: 지정가 매수 및 지정가 매도
- 실행 방식: polling 기반, websocket 미사용

## 한국투자증권 Open API 사용 이유
- 한국 증권사의 실거래와 동일한 주문 인터페이스 제공
- REST API로 간단하고 명시적인 요청/응답 구조 지원
- 모의투자를 통해 안전하게 자동매매 로직을 검증 가능

## REST API와 모의투자 사용 이유
- 과제 요구사항에서 REST API만 허용됨
- websocket을 사용하지 않고 polling으로 안정적인 API 호출
- 모의투자는 실제 자금이 아닌 시뮬레이션이므로 안전

## 모의투자와 실거래 차이
- 모의투자는 실제 자금이 사용되지 않음
- 주문 체결 및 잔고 변화가 모의계좌에 반영됨
- 실거래에 비해 위험이 낮고 연습/테스트 목적에 적합

## 인증 흐름 및 동일일 토큰 재사용
- `auth.py`가 환경변수 `GH_APPKEY`, `GH_APPSECRET`으로 토큰 발급
- 발급된 토큰은 `token_cache.json`에 저장
- 저장된 토큰은 당일 내 재사용되어 불필요한 재발급 회피

## 환경변수 및 Codespaces Secrets
- 필수 환경변수
  - `GH_ACCOUNT`
  - `GH_APPKEY`
  - `GH_APPSECRET`
- 선택 환경변수
  - `GH_PRODUCT_CODE` (기본값 `01`)

### GitHub Codespaces Secrets 설정
1. `Settings` > `Secrets` > `Codespaces`로 이동
2. `GH_ACCOUNT`, `GH_APPKEY`, `GH_APPSECRET`, `GH_PRODUCT_CODE`를 등록
3. Codespace에서 환경변수가 자동 적용됨

## 전체 폴더 구조
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
  docs/
    assets/.gitkeep
  outputs/.gitkeep
```

## 실행 명령
- 기본 dry-run 테스트
  - `python -m samsung_auto_trader.main --once --dry-run`
- 실제 주문 확인용(모의투자)
  - `python -m samsung_auto_trader.main --once --no-dry-run`
- 반복 실행 모드
  - `python -m samsung_auto_trader.main`

## 삼성전자 005930 자동매매 로직
1. 현재가 조회
2. 계좌 현금/보유 종목 조회
3. `current_price - ORDER_OFFSET_KRW`로 매수 지정가 주문
4. `current_price + ORDER_OFFSET_KRW`로 매도 지정가 주문
5. 주문 후 다시 계좌 상태를 확인하여 실행 여부 추정
6. 09:10~15:30 KST 사이에만 주문 수행

## ORDER_OFFSET_KRW 설명
- 기본값: `2000`
- 매수 주문은 현재가에서 2000원 낮은 가격으로 지정가 제출
- 매도 주문은 현재가에서 2000원 높은 가격으로 지정가 제출
- 이 값은 `--offset` 옵션으로 조정 가능

## 요청 최소화 및 안전 설계
- 당일 토큰을 재사용하여 불필요한 인증 호출 감소
- polling 간격 30초로 과도한 반복 호출 방지
- `dry_run` 기본 활성화로 실주문 테스트 시 안전성 확보
- `paper_trading` 기본 활성화로 모의투자 전용 주문 사용

## DRY_RUN / PAPER_TRADING 설명
- `DRY_RUN=true`는 주문을 실제로 전송하지 않음
- `PAPER_TRADING=true`는 모의투자 TR ID를 사용하여 모의주문 모드로 작동
- 과제 기본 설정은 안전한 테스트를 위해 두 모드 모두 활성화

## 로깅 설명
- 토큰 재사용 여부
- 현재가 조회
- 주문 전 잔고/보유 종목
- 매수/매도 주문 요청
- 주문 후 잔고/보유 종목
- 실행 여부 추정 결과
- API 오류/타임아웃/재시도
- 거래창 시작 및 종료

## 증빙 섹션
- 실제 모의투자 주문 로그
- 계좌 잔고 조회 결과
- 매수/매도 주문 요청 화면
