# 삼성 자동 거래 시스템

Korea Investment & Securities Open API를 사용하여 삼성전자(005930)를 자동으로 거래하는 Python 시스템입니다.

## 특징

- **모의 거래 환경** - 안전한 테스트 환경에서 실행
- **REST API만 사용** - WebSocket 미포함
- **토큰 캐싱** - 같은 날 내에 토큰 재사용하여 API 호출 최소화
- **자동 거래 시간** - 09:10 ~ 15:30만 자동 거래
- **폴링 기반** - 30초 간격으로 가격 및 계좌 조회
- **완전 로깅** - 모든 주요 행동 기록

## 프로젝트 구조

```
samsung_auto_trader/
├── main.py              # 진입점 및 거래 루프
├── config.py            # API 설정 및 상수
├── auth.py              # 인증 및 토큰 캐싱
├── api_client.py        # HTTP 클라이언트 래퍼
├── market_data.py       # 현재 주가 조회
├── account.py           # 계좌 정보 조회
├── orders.py            # 주문 실행 및 상태 확인
├── trader.py            # 거래 로직 조직화
├── logger.py            # 로깅 설정
├── requirements.txt     # Python 의존성
├── token_cache.json     # 토큰 캐시 (자동 생성)
└── README.md            # 이 파일
```

## 필수 요구사항

- Python 3.8 이상
- Korea Investment & Securities Open API 계정
- 모의 거래 계정 활성화
- 필요한 환경 변수

## 설치

### 1단계: 프로젝트 폴더로 이동

```bash
cd samsung_auto_trader
```

### 2단계: Python 의존성 설치

```bash
pip install -r requirements.txt
```

## 🚀 빠른 시작 (GitHub Codespaces 권장)

### Codespaces에서 시작하기

**1단계: 시크릿 등록**
- https://github.com/settings/codespaces 접속
- "Secrets and variables" > "Codespaces" 클릭
- "New secret" 버튼으로 3개 생성:
  - `GH_ACCOUNT`: 계좌번호
  - `GH_APPKEY`: 앱키
  - `GH_APPSECRET`: 앱시크릿

**2단계: Codespaces 재시작**
- Codespaces를 중지 후 재시작 (시크릿이 자동 주입됨)

**3단계: 실행**
```bash
python main.py
```

## 환경 변수 설정

### 방법 1: GitHub Codespaces User Secrets (최권장) ⭐

가장 안전하고 권장되는 방법입니다.

1. https://github.com/settings/codespaces 접속
2. "Secrets and variables" > "Codespaces" > "New secret" 클릭
3. 아래 3개 시크릿 생성 (각각 별도로):
   ```
   GH_ACCOUNT = <계좌번호>
   GH_APPKEY = <앱키>
   GH_APPSECRET = <앱시크릿>
   ```
4. Codespaces 재시작 (Stop & Start)

### 방법 2: .env 파일 사용 (로컬 개발용)

로컬 환경이나 선호하는 경우:

```bash
cp .env.example .env  # 템플릿 복사
# 텍스트 에디터로 .env 파일 열어서 자격증명 입력
```

### 방법 3: 셸 환경 변수 사용

```bash
export GH_ACCOUNT=<계좌번호>
export GH_APPKEY=<앱키>
export GH_APPSECRET=<앱시크릿>
```

### 추가 커스터마이징 (선택사항)

`config.py` 파일을 열어 다음 설정을 필요에 따라 조정할 수 있습니다:

- `BUY_OFFSET` - 매수 오프셋 (기본값: 2000 KRW)
- `SELL_OFFSET` - 매도 오프셋 (기본값: 2000 KRW)
- `POLLING_INTERVAL_SECONDS` - 폴링 간격 (기본값: 30초)
- `TRADING_START_HOUR` / `TRADING_START_MINUTE` - 거래 시작
- `TRADING_END_HOUR` / `TRADING_END_MINUTE` - 거래 종료

## 실행

```bash
python main.py
```

**백그라운드 실행 (Linux/Mac):**
```bash
nohup python main.py > trading.log 2>&1 &
```

**VS Code에서 실행:**
- `main.py` 우측 상단 "Run" 버튼 또는 `Ctrl+F5`

## 거래 로직

프로그램은 다음 순서로 거래합니다:

1. **주가 확인** - 삼성전자(005930)의 현재 주가를 조회
2. **계좌 확인 (거래 전)** - 현금 잔액 및 보유 주식 확인
3. **매수 주문** - 현재가에서 2,000 KRW을 내린 가격으로 1주 매수
4. **계좌 확인 (매수 후)** - 거래 결과 확인
5. **매도 주문** - 현재가에서 2,000 KRW을 올린 가격으로 1주 매도
6. **계좌 확인 (매도 후)** - 완료 후 최종 상태 확인
7. **주문 상태 확인** - 최근 주문 상태 조회

## 거래 시간

- **시작**: 09:10 AM
- **종료**: 03:30 PM (15:30)
- 이 시간대 외에는 거래하지 않습니다

## 로깅

프로그램은 다음 정보를 기록합니다:

- 토큰 발급/재사용
- 현재 주가
- 계좌 잔액 및 보유 주식
- 주문 요청 및 결과
- 거래 체결 확인
- API 오류 및 재시도

로그는 콘솔과 파일(`.log`)에 함께 기록됩니다.

## 안전성

이 시스템은 다음과 같이 설계되었습니다:

- **모의 거래만 사용** - 실거래 불가능
- **토큰 캐싱** - 불필요한 API 호출 최소화
- **재시도 로직** - 네트워크 오류 시 자동 재시도
- **타임아웃 처리** - API 요청 시간 초과 처리
- **안전한 환경변수** - 자격증명 하드코딩 없음

## API 필드명 확인 및 수정

Korea Investment Open API의 응답 필드명은 API 문서에 따라 다를 수 있습니다.
다음 파일들에서 필드명을 확인하고 필요시 수정하세요:

- `market_data.py` - 주가 필드명 (현재: `stck_prpr`)
- `account.py` - 계좌 필드명 (현재: `hldg_qty`, `scts_evlu_amt`)
- `orders.py` - 주문 필드명 (현재: `ODNO`, `rt_cd`)

## 문제 해결

### "환경 변수가 설정되지 않았습니다" 오류

**GitHub Codespaces 사용 시:**
```
1. https://github.com/settings/codespaces 확인
2. Secrets and variables > Codespaces에서 3개 시크릿 생성
3. GH_ACCOUNT, GH_APPKEY, GH_APPSECRET 모두 등록되었는지 확인
4. Codespaces 재시작 (Stop & Start)
5. Terminal에서 `echo $GH_ACCOUNT` 실행하여 값 확인
```

**로컬 환경 사용 시:**
```
1. .env 파일 존재 확인
2. GH_ACCOUNT, GH_APPKEY, GH_APPSECRET 확인
3. 파일 형식: KEY=VALUE (공백 없음)
4. .env 파일이 프로젝트 루트 디렉토리에 있는지 확인
```

### "토큰 발급 실패" 오류

```
해결방법:
1. 앱키(GH_APPKEY)와 앱시크릿(GH_APPSECRET) 확인
2. Korea Investment API 계정 활성화 확인
3. 네트워크 연결 확인
```

### "타임아웃" 오류

```
해결방법:
1. 네트워크 연결 확인
2. Korea Investment API 서버 상태 확인
3. 방화벽 설정 확인 (포트 9443 허용)
```

## 개발 팁

### 토큰 캐시 초기화

```bash
rm token_cache.json
```

### 디버그 로깅 활성화

`logger.py`에서 `console_handler.setLevel(logging.DEBUG)`로 변경

### 테스트 실행 (시뮬레이션)

거래 로직을 실제 실행하지 않고 테스트하려면:
- `main.py`의 거래 시간 설정을 현재 시간으로 임시 변경
- `trader.py`의 `execute_trading_cycle()` 함수에 디버그 로그 추가

## 주의사항

- **모의 거래 환경에서만 사용** - 실거래 환경에서 절대 사용 금지
- **충분한 잔액 유지** - 주문 실패를 방지하기 위해 충분한 현금 유지
- **API 호출 제한** - 모의 거래 환경은 API 호출 제한이 있습니다
- **시스템 시간 동기화** - 시스템 시간이 정확해야 거래 시간 판별이 정확합니다

## 추가 기능 (향후 개선사항)

- 실시간 주가 업데이트 (WebSocket, 현재는 미포함)
- 고급 주문 전략 (OCO, 조건부 주문 등)
- 수익/손실 분석 및 보고기
- 설정 파일 (YAML/JSON)로 전환
- 데이터베이스 통합 (거래 이력 기록)
- 텔레그램/슬랙 알림

## 라이센스

프로젝트에 따라 적절한 라이센스 추가

## 지원 및 문의

Korea Investment Open API 문서:
- https://www.koreainvestment.com/

## 면책사항

이 프로그램은 교육 및 테스트 목적으로만 제공됩니다.
실거래로 인한 손실은 사용자 본인이 책임집니다.
