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

## config.py: 환경변수 
# 설정 모듈 README

이 문서는 환경변수에서 한국투자증권 KIS API 및 자동매매 프로그램 실행에 필요한 설정값을 읽어오는 코드에 대한 설명입니다.

이 코드는 크게 다음 세 부분으로 구성됩니다.

1. 필수 환경변수를 읽는 `_env()` 함수
2. 계좌번호 문자열을 파싱하는 `parse_account()` 함수
3. 전체 설정값을 관리하는 `Settings` 데이터 클래스

이 모듈의 목적은 프로그램 곳곳에서 환경변수를 직접 읽지 않고, 한 번에 설정값을 읽어 `Settings` 객체로 정리하여 사용하는 것입니다.

---

# 1. 전체 코드의 역할

이 코드는 자동매매 프로그램이 실행될 때 필요한 설정값을 환경변수에서 읽어옵니다.

---

# 2. `_env()` 함수

```python
def _env(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)
    if value is None or value == "":
        raise ValueError(f"Missing required environment variable: {name}")
    return value
```

`_env()` 함수는 환경변수 값을 읽어오는 함수입니다.

단순히 `os.getenv()`를 사용하는 것과 달리, 환경변수가 없거나 빈 문자열이면 오류를 발생시킵니다.

즉, 반드시 필요한 환경변수를 안전하게 읽기 위한 함수입니다.

`os.getenv()`는 운영체제 환경변수 값을 읽는 함수입니다.

환경변수가 없을 경우 `default` 값이 사용됩니다.

환경변수가 없거나 빈 문자열이면 `ValueError`를 발생시킵니다.

환경변수가 정상적으로 존재하면 문자열 값을 반환합니다.

반환 타입은 `str`입니다.

이 함수는 필수 설정값이 빠진 상태로 프로그램이 실행되는 것을 막습니다.

 `_env()`를 사용하면 프로그램 시작 단계에서 명확한 오류를 볼 수 있어 어떤 설정이 빠졌는지 쉽게 확인할 수 있습니다.

---

# 3. `parse_account()` 함수

```python
def parse_account(account_value: str) -> tuple[str, str]:
    cleaned = re.sub(r"\s+", "", account_value)
    if "-" in cleaned:
        front, back = cleaned.split("-", 1)
        if len(front) == 8 and len(back) == 2 and front.isdigit() and back.isdigit():
            return front, back

    digits = re.sub(r"\D", "", cleaned)
    if len(digits) == 10:
        return digits[:8], digits[8:]

    raise ValueError(
        "GH_ACCOUNT must contain the KIS account number in 8-2 format, for example '12345678-01' or '1234567801'."
    )
```

`parse_account()` 함수는 계좌번호 문자열을 한국투자증권 KIS API에서 사용할 수 있는 형태로 나누어주는 함수입니다.

```python
cleaned = re.sub(r"\s+", "", account_value)
```

이 코드는 계좌번호 문자열에서 모든 공백을 제거합니다.

---

```python
if "-" in cleaned:
    front, back = cleaned.split("-", 1)
    if len(front) == 8 and len(back) == 2 and front.isdigit() and back.isdigit():
        return front, back
```

계좌번호에 하이픈이 포함되어 있으면 하이픈을 기준으로 앞부분과 뒷부분을 나눕니다.

그리고 다음 조건을 검사합니다.

```python
len(front) == 8
```

앞부분이 8자리인지 확인합니다.

```python
len(back) == 2
```

뒷부분이 2자리인지 확인합니다.

```python
front.isdigit()
```

앞부분이 숫자로만 이루어져 있는지 확인합니다.

```python
back.isdigit()
```

뒷부분이 숫자로만 이루어져 있는지 확인합니다.

모든 조건을 만족하면 다음 값을 반환합니다.

```python
return front, back
```

```python
digits = re.sub(r"\D", "", cleaned)
if len(digits) == 10:
    return digits[:8], digits[8:]
```

계좌번호가 하이픈 없이 입력될 수도 있습니다.

먼저 숫자가 아닌 문자를 모두 제거합니다.

그리고 숫자만 남긴 결과가 10자리이면 앞 8자리와 뒤 2자리로 나눕니다.

```python
return digits[:8], digits[8:]
```

```python
raise ValueError(
    "GH_ACCOUNT must contain the KIS account number in 8-2 format, for example '12345678-01' or '1234567801'."
)
```

입력값이 올바른 형식이 아니면 `ValueError`를 발생시킵니다.

---

# 4. `Settings` 데이터 클래스

```python
@dataclass(frozen=True)
class Settings:
```

`Settings` 클래스는 자동매매 프로그램에서 사용하는 설정값을 하나의 객체로 묶어 관리하는 클래스입니다.

`@dataclass`를 사용하면 생성자, 출력, 비교 등의 기본 메서드를 자동으로 만들어줍니다.

`frozen=True`는 객체를 생성한 뒤 값을 수정할 수 없게 만드는 옵션입니다.

즉, `Settings` 객체는 불변 객체입니다.

---

`dataclass`를 사용하면 `__init__()` 없이 필드만 선언하면 됩니다.

```python
@dataclass
class Settings:
    account_number: str
    account_product_code: str
    appkey: str
    appsecret: str
    base_url: str
```

그러면 Python이 자동으로 `__init__()`을 만들어줍니다.

---

---

# 5. `Settings` 필드 설명

```python
class Settings:
    account_number: str
    account_product_code: str
    appkey: str
    appsecret: str
    base_url: str
    symbol: str = "005930"
    market_code: str = "J"
    order_quantity: int = 1
    price_offset_krw: int = 1000
    poll_interval_seconds: int = 180
    verify_delay_seconds: int = 5
    request_timeout_seconds: int = 10
    retry_count: int = 2
    retry_backoff_seconds: float = 2.0
    trading_start: time = time(9, 10)
    trading_end: time = time(15, 30)
    token_cache_path: Path = Path(__file__).resolve().parent / "token_cache.json"
```

각 필드는 자동매매 프로그램에서 사용하는 설정값입니다.

---

# 6. `from_env()` 클래스 메서드

```python
@classmethod
def from_env(cls) -> "Settings":
```

`from_env()`는 환경변수를 읽어서 `Settings` 객체를 생성하는 클래스 메서드입니다.

일반적으로 프로그램 시작 시 다음처럼 사용합니다.

```python
settings = Settings.from_env()
```

`@classmethod`는 메서드가 클래스 자체를 첫 번째 인자로 받도록 합니다.

여기서 `cls`는 `Settings` 클래스를 의미합니다.

그래서 마지막에 다음처럼 객체를 생성할 수 있습니다.

```python
return cls(...)
```

이 방식은 나중에 `Settings`를 상속한 클래스에서도 유연하게 사용할 수 있다는 장점이 있습니다.

---

# 7. 필수 환경변수 읽기

```python
account_number, account_product_code = parse_account(_env("GH_ACCOUNT"))
appkey = _env("GH_APPKEY")
appsecret = _env("GH_APPSECRET")
```

이 세 환경변수는 필수입니다.

이 값들은 `_env()`로 읽기 때문에, 누락되면 프로그램이 바로 오류를 발생시킵니다.

필수 환경변수와 달리, 다른 값들은 환경변수가 없으면 기본값을 사용합니다.

---

# 8. `Settings` 객체 생성

```python
return cls(
    account_number=account_number,
    account_product_code=account_product_code,
    appkey=appkey,
    appsecret=appsecret,
    base_url=base_url,
    symbol=symbol,
    market_code=market_code,
    order_quantity=order_quantity,
    price_offset_krw=price_offset_krw,
    poll_interval_seconds=poll_interval_seconds,
    verify_delay_seconds=verify_delay_seconds,
    request_timeout_seconds=request_timeout_seconds,
    retry_count=retry_count,
    retry_backoff_seconds=retry_backoff_seconds,
    token_cache_path=cache_path,
)
```

환경변수에서 읽은 값들을 사용해 `Settings` 객체를 생성합니다.

이때 `trading_start`와 `trading_end`는 별도로 넘기지 않았습니다.

따라서 클래스에 정의된 기본값이 사용됩니다.

```python
trading_start = time(9, 10)
trading_end = time(15, 30)
```

즉, 최종적으로 생성된 `Settings` 객체에는 다음과 같은 값들이 들어갑니다.

```python
Settings(
    account_number="12345678",
    account_product_code="01",
    appkey="...",
    appsecret="...",
    base_url="https://openapivts.koreainvestment.com:29443",
    symbol="005930",
    market_code="J",
    order_quantity=1,
    price_offset_krw=1000,
    poll_interval_seconds=180,
    verify_delay_seconds=5,
    request_timeout_seconds=10,
    retry_count=2,
    retry_backoff_seconds=2.0,
    trading_start=time(9, 10),
    trading_end=time(15, 30),
    token_cache_path=Path(".../token_cache.json"),
)
```

---

# 11. 환경변수 목록

아래는 이 코드에서 사용하는 환경변수 전체 목록입니다.

| 환경변수                              | 필수 여부 | 기본값                                            | 설명            |
| --------------------------------- | ----- | ---------------------------------------------- | ------------- |
| `GH_ACCOUNT`                      | 필수    | 없음                                             | KIS 계좌번호      |
| `GH_APPKEY`                       | 필수    | 없음                                             | KIS API 앱키    |
| `GH_APPSECRET`                    | 필수    | 없음                                             | KIS API 앱시크릿  |
| `KIS_BASE_URL`                    | 선택    | `https://openapivts.koreainvestment.com:29443` | KIS API 서버 주소 |
| `TRADING_SYMBOL`                  | 선택    | `005930`                                       | 매매 대상 종목 코드   |
| `TRADING_MARKET_CODE`             | 선택    | `J`                                            | 시장 구분 코드      |
| `TRADING_ORDER_QTY`               | 선택    | `1`                                            | 주문 수량         |
| `TRADING_PRICE_OFFSET_KRW`        | 선택    | `1000`                                         | 주문 가격 조정 폭    |
| `TRADING_POLL_SECONDS`            | 선택    | `180`                                          | 시세 조회 주기      |
| `TRADING_VERIFY_DELAY_SECONDS`    | 선택    | `5`                                            | 주문 확인 전 대기 시간 |
| `TRADING_REQUEST_TIMEOUT_SECONDS` | 선택    | `10`                                           | API 요청 타임아웃   |
| `TRADING_RETRY_COUNT`             | 선택    | `2`                                            | API 요청 재시도 횟수 |
| `TRADING_RETRY_BACKOFF_SECONDS`   | 선택    | `2`                                            | 재시도 대기 시간 기준값 |
| `TRADING_TOKEN_CACHE_PATH`        | 선택    | `token_cache.json`                             | 토큰 캐시 파일 경로   |

---

# 12. `.env` 파일 예시

로컬 환경에서 실행한다면 다음처럼 `.env` 파일을 만들 수 있습니다.

```env
GH_ACCOUNT=12345678-01
GH_APPKEY=your_app_key
GH_APPSECRET=your_app_secret

KIS_BASE_URL=https://openapivts.koreainvestment.com:29443
TRADING_SYMBOL=005930
TRADING_MARKET_CODE=J
TRADING_ORDER_QTY=1
TRADING_PRICE_OFFSET_KRW=1000
TRADING_POLL_SECONDS=180
TRADING_VERIFY_DELAY_SECONDS=5
TRADING_REQUEST_TIMEOUT_SECONDS=10
TRADING_RETRY_COUNT=2
TRADING_RETRY_BACKOFF_SECONDS=2
TRADING_TOKEN_CACHE_PATH=./token_cache.json
```

주의할 점은 `.env` 파일에 API 키와 계좌번호가 포함되므로 GitHub에 올리면 안 된다는 것입니다.

반드시 `.gitignore`에 `.env`를 추가해야 합니다.

```gitignore
.env
token_cache.json
```

---

# 13. 사용 예시

프로그램에서는 일반적으로 다음처럼 사용합니다.

```python
settings = Settings.from_env()
```

그 후 다른 객체를 만들 때 설정값을 전달합니다.

예시:

```python
settings = Settings.from_env()

client = KISApiClient(
    base_url=settings.base_url,
    appkey=settings.appkey,
    appsecret=settings.appsecret,
    auth_manager=auth_manager,
    logger=logger,
    timeout_seconds=settings.request_timeout_seconds,
    retry_count=settings.retry_count,
    retry_backoff_seconds=settings.retry_backoff_seconds,
)
```

주문 모듈에서는 다음 값을 사용할 수 있습니다.

```python
account_number = settings.account_number
account_product_code = settings.account_product_code
symbol = settings.symbol
quantity = settings.order_quantity
```

시세 조회 모듈에서는 다음 값을 사용할 수 있습니다.

```python
symbol = settings.symbol
market_code = settings.market_code
```

자동매매 루프에서는 다음 값을 사용할 수 있습니다.

```python
poll_interval = settings.poll_interval_seconds
trading_start = settings.trading_start
trading_end = settings.trading_end
```

---

# 14. 실행 흐름 요약

`Settings.from_env()`가 호출되면 전체 흐름은 다음과 같습니다.

```text
Settings.from_env()
  ↓

GH_ACCOUNT 환경변수 읽기
  ↓
parse_account()로 계좌번호 분리
  ↓
GH_APPKEY 환경변수 읽기
  ↓
GH_APPSECRET 환경변수 읽기
  ↓
선택 환경변수 읽기
  ↓
숫자 설정값 int 또는 float로 변환
  ↓
토큰 캐시 경로를 Path 객체로 변환
  ↓
Settings 객체 생성
  ↓
Settings 객체 반환
```

---

## auth.py: 토큰 발급

@dataclass(frozen=True)
class Settings:
    @classmethod
    def from_env(cls) -> "Settings":
                return cls()

Settings는 프로그램 실행에 필요한 설정값을 저장하는 클래스
계좌정보, API 키, 종목코드, 주문 수량, 요청 시간 제한 등을 관리한다
@dataclass(frozen=True)는 __init__을 대신해주고 설정값을 고정한다
@classmethod
def from_env(cls)는 Settings 클래스를 환경변수와 설정값에서 필요한 값들을 자동으로 읽어 Settings 객체로 반환한다
settings.account_number처럼 설정값을 사용할 수 있다

class TokenCache:

API 토큰을 파일에 저장하고, 나중에 다시 불러오기 위한 TokenCache 클래스
TokenCache
│
├─ token
│  └─ API 접근 토큰 저장
│
├─ issued_date
│  └─ 토큰 발급 날짜 저장
│
├─ from_file(path)
│  └─ 파일에서 토큰 캐시를 읽어 TokenCache 객체 생성
│
└─ save(path)
   └─ 현재 토큰 캐시를 JSON 파일로 저장
토큰과 날짜가 있는 파일을 저장한다. 만약 파일이 없다면 None을 반환한다
파일을 읽어 json형식으로 만들고, 다시 딕셔너리 형식으로 변환한다
파일이 깨져 있거나 JSON 형식이 아니면 None을 반환한다
파일에서 token과 issued_date를 꺼내고, 없으면 ""을 불러온다
token이나 issued_date 값이 비어 있으면 None을 반환한다
모든 과정이 정상적으로 진행되면, TokenCache에 token과 issued_date가 저장되어 반환된다
저장된 token과 issued_date는 딕셔너리 형식으로 만들고 다시 json형식으로 변환한다
새로 발급받는 토큰을 저장할 때도 save를 사용한다

class AuthManager:

이미 저장된 토큰이 오늘 발급된 토큰이면 그대로 재사용하고, 저장된 토큰이 없거나 오래된 토큰이면 API 서버에 새 토큰을 요청하고, 그 토큰을 파일에 저장하는 클래스
AuthManager
│
├─ TokenCache.from_file()
│  └─ 기존 토큰 파일 읽기
│
├─ get_token()
│  ├─ 오늘 발급된 토큰이 있으면 재사용
│  └─ 없으면 새 토큰 요청
│
└─ _request_new_token()
   └─ API 서버에 토큰 발급 요청
init에서 필요한 정보 저장
self._cached_token은 TokenCache 클래스를 사용하여 cache_path에 저장된 토큰 파일이 있으면 읽어오고, 없거나 잘못된 파일이면 None을 반환한다
get_token은 토큰을 가져오는 함수
오늘 날짜를 저장된 토큰과 비교하여 토큰의 발급일이 오늘이면 새 토큰을 요청하지 않고 기존 토큰을 반환한다
저장된 토큰이 없거나, 발급일이 오늘이 아니면 새 토큰을 요청한다
새로 토큰을 받으면 TokenCache 객체로 만들고, 파일에 저장하여 재사용할 수 있게 만든다
request_new_token은 실제 토큰을 발급받는 함수
API 서버 주소로 토큰 발급 주소를 만들고 서버에 grant_type(토큰 발급 방식), appkey와 appsecret(인증에 필요), content-type(토큰 형식)을 보내 토큰 발급 요청을 보낸다. 
post는 서버에 데이터를 보내서 어떤 결과를 받아오는 HTTP 요청 방식
raise_for_status()는 서버 응답이 실패 상태이면 오류를 발생시킨다
서버가 응답하면 json 형태로 바꾼 후 access token을 꺼낸다
없으면 오류를 발생시키고 있으면 토큰 반환

## api_client.py: 공통 HTTP 클라이언트

class KISResult:
한국투자증권 API 요청결과와 성공 여부를 확인하는 클래스
KISResult
│
├─ status_code
│  └─ HTTP 응답 코드
│
├─ data
│  └─ API 응답 본문
│
└─ ok
   └─ 요청 성공 여부를 True/False로 판단
HTTP 상태 코드와 API 서버가 보내준 응답을 받고 응답 데이터를 딕셔너리에 저장
ok 함수는 성공 여부를 판단
@property로 함수 대신 변수처럼 사용 가능
HTTP 요청 자체가 성공하고(self.status_code == 200), 한국투자증권 API 내부 응답 코드가 성공(rt_cd == "0")하면 성공한 것

class KISApiClient:
발급받은 토큰으로 한국투자증권 API에 GET/POST 요청을 보내는 공통 클라이언트 클래스
KISApiClient
│
├─ __init__()
│  └─ API 요청에 필요한 기본 정보 저장
│
├─ get()
│  └─ 서버에서 정보를 불러옴
│
├─ post()
│  └─ 서버에 데이터를 보냄
│
├─ get_hashkey()
│  └─ POST 요청 본문에 대한 hashkey 발급
│
└─ _request()
   ├─ URL 생성
   ├─ AuthManager에서 토큰 가져오기
   ├─ 공통 헤더 생성
   ├─ GET/POST에 맞게 요청 데이터 설정
   ├─ 필요 시 hashkey 추가
   ├─ API 요청 실행
   ├─ HTTP 오류 확인
   ├─ KIS 응답 rt_cd 확인
   ├─ 실패 시 재시도
   └─ 성공 시 payload 반환
   
init()에서 API 요청을 보내기 위해 필요한 정보를 저장한다
get()에서 서버에서 정보를 가져오는 함수. 실제 작동은 _request()에서
post()는 서버에 데이터를 보내는 함수 
body에 서버에 보낼 주문 정보를 넣음
use_hashkey=True이면 요청 본문에 대해 hashkey를 발급받아 헤더에 추가
get_hashkey()는 hashkey를 발급받는 함수
hashkey는 내가 보내는 요청 본문이 변조되지 않았다는 것을 증명하기 위한 값이다
먼저 hashkey 발급 전용 URL을 만들다
서버에 body를 보내고, 그 body에 대한 hashkey를 요청한다
응답에서 HASH값을 꺼내고, 없으면 오류를 발생시킨다
_request()는 실제로 API 요청을 처리하는 함수
API 서버 주소와 API 경로를 합쳐 최종 요청 주소를 만든다
AuthManager으로 토큰을 요청하여 받는다
header를 토큰, appkey, appsecret, tr_id(거래 요청 종류 ID) 등을 넣어 만든다
request_kwargs로 공통 요청 요소를 만들고, get요청인지 post요청인지에 따라 다르게 처리한다
get요청의 경우 조회조건이 params에 들어간다
post요청의 경우 body 데이터가 json 본문에 들어간다. use_hashkey가 True이면 get_hashkey()로 hashkey를 발급받아 헤더에 추가한다
요청이 실패할 경우 retry_count번 재시도한다
요청의 종류에 따라 앞 request_kwargs가 작동
오류의 종류에 따라 재시도 대상 오류와 예외 오류로 구별하여 작동한다
서버가 응답하면 응답을 json형태로 변환한다
API 내부 처리에서 실패한 경우에는 RuntimeError를 발생시킨다
성공적으로 진행되면 최종적으로는 API 응답 데이터를 반환한다
오류가 발생하면 last_error에 저장하고, 최종 실패했을 때 원래 오류를 함께 보여준다


















































