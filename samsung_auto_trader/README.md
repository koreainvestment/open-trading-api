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

# config.py: 환경변수 

이 문서는 환경변수에서 한국투자증권 KIS API 및 자동매매 프로그램 실행에 필요한 설정값을 읽어오는 코드에 대한 설명입니다.

이 코드는 크게 다음 세 부분으로 구성됩니다.

1. 필수 환경변수를 읽는 `_env()` 함수
2. 계좌번호 문자열을 파싱하는 `parse_account()` 함수
3. 전체 설정값을 관리하는 `Settings` 데이터 클래스

이 모듈의 목적은 프로그램 곳곳에서 환경변수를 직접 읽지 않고, 한 번에 설정값을 읽어 `Settings` 객체로 정리하여 사용하는 것입니다.

---

## 1. 전체 코드의 역할

이 코드는 자동매매 프로그램이 실행될 때 필요한 설정값을 환경변수에서 읽어옵니다.

---

## 2. `_env()` 함수

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

## 3. `parse_account()` 함수

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

## 4. `Settings` 데이터 클래스

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

## 5. `Settings` 필드 설명

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

## 6. `from_env()` 클래스 메서드

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

## 7. 필수 환경변수 읽기

```python
account_number, account_product_code = parse_account(_env("GH_ACCOUNT"))
appkey = _env("GH_APPKEY")
appsecret = _env("GH_APPSECRET")
```

이 세 환경변수는 필수입니다.

이 값들은 `_env()`로 읽기 때문에, 누락되면 프로그램이 바로 오류를 발생시킵니다.

필수 환경변수와 달리, 다른 값들은 환경변수가 없으면 기본값을 사용합니다.

---

## 8. `Settings` 객체 생성

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

## 9. 환경변수 목록

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

# 10. `.env` 파일 예시

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

# 11. 사용 예시

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

# 12. 실행 흐름 요약

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

# auth.py: 토큰 발급과 관리

한국투자증권 KIS API 접근 토큰을 발급받고, 발급받은 토큰을 파일에 캐시하여 재사용하는 인증 관리 코드에 대한 설명입니다.

---

## 1. 전체 코드의 역할

KIS API를 사용하려면 API 요청마다 접근 토큰이 필요합니다.

접근 토큰은 `appkey`와 `appsecret`을 사용해 발급받으며, 이후 API 요청의 `Authorization` 헤더에 사용됩니다.

하지만 API 요청을 보낼 때마다 새 토큰을 발급받는 것은 비효율적이므로 이 코드는 한 번 발급받은 토큰을 파일에 저장해두고, 같은 날짜 안에서는 저장된 토큰을 재사용합니다.

전체 흐름은 다음과 같습니다.

```text
AuthManager 생성
  ↓
토큰 캐시 파일 읽기
  ↓
get_token() 호출
  ↓
오늘 발급된 캐시 토큰이 있으면 재사용
  ↓
없으면 새 토큰 발급
  ↓
새 토큰을 파일에 저장
  ↓
토큰 반환
```

---

# 3. `TokenCache` 데이터 클래스

```python
@dataclass
class TokenCache:
    token: str
    issued_date: str
```

`TokenCache`는 발급받은 접근 토큰과 해당 토큰을 발급받은 날짜를 저장하는 클래스입니다.

이 클래스는 파일에 저장된 토큰 정보를 읽어오거나, 현재 토큰 정보를 파일에 저장하는 역할을 합니다.

`TokenCache`는 두 개의 필드를 가집니다.

| 필드            | 타입    | 설명                       |
| ------------- | ----- | ------------------------ |
| `token`       | `str` | KIS API에서 발급받은 접근 토큰입니다. |
| `issued_date` | `str` | 토큰을 발급받은 날짜입니다.          |

---

# 4. `TokenCache.from_file()`

```python
@classmethod
def from_file(cls, path: Path) -> "TokenCache | None":
```

`from_file()`은 토큰 캐시 파일에서 기존 토큰 정보를 읽어오는 클래스 메서드입니다.

파일에 유효한 토큰 정보가 있으면 `TokenCache` 객체를 반환하고, 없거나 사용할 수 없는 상태이면 `None`을 반환합니다.

---

## 4.3 파일 존재 여부 확인

```python
if not path.exists():
    return None
```

먼저 토큰 캐시 파일이 존재하는지 확인합니다.

파일이 없으면 읽을 수 있는 캐시 토큰도 없으므로 `None`을 반환합니다.

이 경우 이후 `AuthManager.get_token()`에서 새 토큰을 발급받게 됩니다.

---

## 4.4 JSON 파일 읽기

```python
try:
    payload = json.loads(path.read_text(encoding="utf-8"))
except json.JSONDecodeError:
    return None
```

파일이 존재하면 파일 내용을 읽고 JSON으로 변환합니다.

```python
path.read_text(encoding="utf-8")
```

이 코드는 캐시 파일의 내용을 UTF-8 인코딩으로 읽습니다.

```python
json.loads(...)
```

이 코드는 읽어온 문자열을 Python 객체로 변환합니다.

만약 파일 내용이 올바른 JSON 형식이 아니면 `json.JSONDecodeError`가 발생합니다.

이 경우 캐시 파일을 사용할 수 없다고 판단하고 `None`을 반환합니다.

---

## 4.5 토큰과 발급일 추출

```python
token = str(payload.get("token", "")).strip()
issued_date = str(payload.get("issued_date", "")).strip()
```

JSON 데이터에서 `token`과 `issued_date` 값을 꺼냅니다.

```python
payload.get("token", "")
```

`token` 키가 있으면 해당 값을 가져오고, 없으면 빈 문자열을 사용합니다.

```python
payload.get("issued_date", "")
```

`issued_date` 키가 있으면 해당 값을 가져오고, 없으면 빈 문자열을 사용합니다.

각 값은 `str()`로 문자열화한 뒤 `strip()`으로 앞뒤 공백을 제거합니다.

---

## 4.6 유효성 확인

```python
if not token or not issued_date:
    return None
```

토큰이나 발급일 중 하나라도 비어 있으면 캐시 정보를 사용할 수 없습니다.

따라서 `None`을 반환합니다.

---

## 4.7 `TokenCache` 객체 생성

```python
return cls(token=token, issued_date=issued_date)
```

캐시 파일에서 유효한 토큰과 발급일을 읽어왔다면 `TokenCache` 객체를 생성해 반환합니다.

여기서 `cls`는 `TokenCache` 클래스를 의미합니다.

---

# 5. `TokenCache.save()`

```python
def save(self, path: Path) -> None:
```

`save()` 메서드는 현재 `TokenCache` 객체의 내용을 파일에 저장합니다.

새 토큰을 발급받은 뒤, 다음 실행에서도 재사용할 수 있도록 캐시 파일을 갱신하는 역할을 합니다.

이 메서드는 파일 저장만 수행하고 별도의 값을 반환하지 않습니다.

---

## 5.3 JSON 파일 저장

```python
path.write_text(
    json.dumps({"token": self.token, "issued_date": self.issued_date}, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
```

현재 객체의 `token`과 `issued_date`를 JSON 문자열로 변환한 뒤 파일에 저장합니다.

`json.dumps()`는 Python 객체를 JSON 문자열로 변환합니다.

여기서는 딕셔너리를 JSON 문자열로 변환합니다.

이 딕셔너리는 현재 캐시 객체가 가진 토큰과 발급일을 담고 있습니다.

---

# 6. `AuthManager` 클래스

```python
class AuthManager:
```

`AuthManager`는 KIS API 접근 토큰을 관리하는 클래스입니다.

주요 역할은 다음과 같습니다.

1. 캐시 파일에서 기존 토큰을 읽어온다.
2. 오늘 발급된 토큰이 있으면 재사용한다.
3. 오늘 발급된 토큰이 없으면 새 토큰을 요청한다.
4. 새 토큰을 캐시 파일에 저장한다.
5. API 클라이언트가 사용할 수 있도록 토큰 문자열을 반환한다.

---

# 7. `AuthManager.__init__()`

```python
def __init__(
    self,
    base_url: str,
    appkey: str,
    appsecret: str,
    cache_path: Path,
    logger,
    timeout_seconds: int = 10,
) -> None:
```

`AuthManager` 객체를 초기화하는 생성자입니다.

KIS API 인증에 필요한 기본 정보와 토큰 캐시 경로를 저장합니다.

## 7.2 `base_url` 저장

```python
self.base_url = base_url.rstrip("/")
```

`base_url` 끝에 `/`가 있으면 제거합니다.

나중에 API 경로를 붙일 때 슬래시가 중복되는 것을 막기 위해서입니다.

---

## 7.3 인증 정보 저장

```python
self.appkey = appkey
self.appsecret = appsecret
```

KIS API 토큰 발급에 필요한 앱키와 앱시크릿을 객체 내부에 저장합니다.

---

## 7.4 캐시 경로 저장

```python
self.cache_path = cache_path
```

토큰 캐시 파일 경로를 저장합니다.

---

## 7.5 로거 저장

```python
self.logger = logger
```

로그를 기록하기 위한 객체를 저장합니다.

---

## 7.6 타임아웃 설정 저장

```python
self.timeout_seconds = timeout_seconds
```

토큰 발급 요청의 최대 대기 시간을 저장합니다.

---

## 7.7 HTTP 세션 생성

```python
self._session = requests.Session()
```

`requests.Session()` 객체를 생성합니다.

세션을 사용하면 HTTP 연결을 재사용할 수 있어 여러 요청을 보낼 때 더 효율적으로 동작할 수 있습니다.

---

## 7.8 캐시 토큰 로드

```python
self._cached_token = TokenCache.from_file(cache_path)
```

객체가 생성될 때 토큰 캐시 파일을 읽어옵니다.

캐시 파일에서 유효한 토큰 정보를 읽으면 `_cached_token`에는 `TokenCache` 객체가 저장됩니다.

캐시 파일이 없거나, 파일 형식이 잘못되었거나, 필요한 값이 비어 있으면 `_cached_token`에는 `None`이 저장됩니다.

---

# 8. `AuthManager.get_token()`

```python
def get_token(self) -> str:
```

`get_token()`은 API 요청에 사용할 접근 토큰을 반환하는 메서드입니다.

이 메서드는 먼저 캐시된 토큰을 확인하고, 사용할 수 있으면 재사용합니다.

사용할 수 있는 토큰이 없으면 새 토큰을 발급받아 캐시에 저장한 뒤 반환합니다.

---

## 8.2 오늘 날짜 구하기

```python
today = date.today().isoformat()
```

현재 날짜를 구해 문자열로 변환합니다.

---

## 8.3 캐시 토큰 재사용 조건

```python
if self._cached_token and self._cached_token.issued_date == today:
```

캐시 토큰을 재사용하려면 두 조건을 만족해야 합니다.

첫 번째 조건은 캐시 파일에서 유효한 토큰을 읽어왔는지 확인합니다.

두 번째 조건은 그 토큰이 오늘 발급된 토큰인지 확인합니다.

---

## 8.4 캐시 토큰 재사용

```python
self.logger.info("token reuse: cached token reused for %s", today)
return self._cached_token.token
```

오늘 발급된 캐시 토큰이 있으면 새 토큰을 요청하지 않고 저장된 토큰을 반환합니다.

이때 로거에 토큰을 재사용했다는 정보를 남깁니다.

---

## 8.5 새 토큰 발급 요청

```python
self.logger.info("token refresh: requesting a new mock-trading token")
token = self._request_new_token()
```

캐시 토큰이 없거나, 캐시 토큰의 발급일이 오늘이 아니면 새 토큰을 요청합니다.

새 토큰 발급은 `_request_new_token()` 메서드가 담당합니다.

---

## 8.6 새 캐시 객체 생성

```python
self._cached_token = TokenCache(token=token, issued_date=today)
```

새로 발급받은 토큰과 오늘 날짜를 사용해 `TokenCache` 객체를 만듭니다.

---

## 8.7 캐시 파일 저장

```python
self._cached_token.save(self.cache_path)
```

같은 날짜에는 토큰을 재사용할 수 있도록 새로 발급받은 토큰 정보를 파일에 저장합니다.

---

## 8.8 토큰 갱신 로그 기록

```python
self.logger.info("token refresh: token cached at %s", self.cache_path)
```

토큰이 캐시 파일에 저장되었음을 로그로 기록합니다.

---

## 8.9 토큰 반환

```python
return token
```

최종적으로 새로 발급받은 토큰 문자열을 반환합니다.

---

# 9. `AuthManager._request_new_token()`

```python
def _request_new_token(self) -> str:
```

`_request_new_token()`은 KIS API 서버에 새 접근 토큰 발급을 요청하는 내부 메서드입니다.

메서드 이름 앞에 밑줄 `_`이 붙어 있으므로, 클래스 외부에서 직접 호출하기보다는 `get_token()`을 통해 간접적으로 사용하는 것을 의도한 메서드입니다.

---

## 9.2 토큰 발급 URL 생성

```python
url = f"{self.base_url}/oauth2/tokenP"
```

토큰 발급 API의 URL을 생성합니다.

`base_url` 뒤에 `/oauth2/tokenP` 경로를 붙입니다.

이 URL로 POST 요청을 보내 새 접근 토큰을 발급받습니다.

---

## 9.3 요청 본문 생성

```python
payload: dict[str, Any] = {
    "grant_type": "client_credentials",
    "appkey": self.appkey,
    "appsecret": self.appsecret,
}
```

토큰 발급 요청에 사용할 JSON 본문입니다.

`grant_type`은 `"client_credentials"`로 설정되어 있습니다.

이는 애플리케이션의 키와 시크릿을 사용해 토큰을 발급받는 방식입니다.

---

## 9.4 요청 헤더 생성

```python
headers = {
    "content-type": "application/json",
    "accept": "text/plain",
    "charset": "UTF-8",
}
```

토큰 발급 요청에 사용할 HTTP 헤더입니다.

각 헤더의 의미는 다음과 같습니다.

| 헤더             | 설명                      |
| -------------- | ----------------------- |
| `content-type` | 요청 본문이 JSON 형식임을 의미합니다. |
| `accept`       | 응답 형식과 관련된 헤더입니다.       |
| `charset`      | 문자 인코딩을 UTF-8로 지정합니다.   |

---

## 9.5 POST 요청 전송

```python
response = self._session.post(url, json=payload, headers=headers, timeout=self.timeout_seconds)
```

KIS API 서버에 토큰 발급 요청을 보냅니다.

요청 방식은 POST입니다.

각 인자의 역할은 다음과 같습니다.

| 인자                             | 설명                   |
| ------------------------------ | -------------------- |
| `url`                          | 토큰 발급 API 주소입니다.     |
| `json=payload`                 | 요청 본문을 JSON으로 전송합니다. |
| `headers=headers`              | 요청 헤더를 함께 전송합니다.     |
| `timeout=self.timeout_seconds` | 응답을 기다릴 최대 시간입니다.    |

---

## 9.6 HTTP 오류 확인

```python
response.raise_for_status()
```

HTTP 응답 상태 코드가 오류인지 확인합니다.

상태 코드가 정상 범위가 아니면 `requests.HTTPError`가 발생합니다.

---

## 9.7 응답 JSON 변환

```python
data = response.json()
```

응답 본문을 JSON으로 해석하여 Python 객체로 변환합니다.


---

## 9.8 접근 토큰 추출

```python
token = str(data.get("access_token", "")).strip()
```

응답 JSON에서 `access_token` 값을 꺼냅니다.

`access_token` 키가 없으면 빈 문자열을 사용합니다.

꺼낸 값은 문자열로 변환한 뒤 앞뒤 공백을 제거합니다.

---

## 9.9 접근 토큰 유효성 확인

```python
if not token:
    raise RuntimeError(f"Token response did not include access_token: {data}")
```

응답에 `access_token`이 없거나 빈 문자열이면 정상적인 토큰 발급 응답이 아니라고 판단합니다.

이 경우 `RuntimeError`를 발생시킵니다.

---

## 9.10 새 토큰 반환

```python
return token
```

응답에서 정상적으로 추출한 접근 토큰 문자열을 반환합니다.

---

# 14. 전체 실행 흐름

`AuthManager.get_token()`을 기준으로 전체 실행 흐름을 정리하면 다음과 같습니다.

```text
get_token()
  ↓
오늘 날짜를 YYYY-MM-DD 형식으로 구함
  ↓
메모리에 저장된 캐시 토큰 확인
  ↓
캐시 토큰이 있고 issued_date가 오늘이면 token 반환
  ↓
캐시 토큰이 없거나 오늘 날짜가 아니면 새 토큰 요청
  ↓
/oauth2/tokenP에 POST 요청
  ↓
응답 JSON에서 access_token 추출
  ↓
TokenCache 객체 생성
  ↓
토큰 캐시 파일 저장
  ↓
새 토큰 반환
```

---

# api_client.py: 공통 HTTP 클라이언트

한국투자증권 KIS API에 HTTP 요청을 보내기 위한 클라이언트 코드에 대한 설명입니다.

이 모듈의 목적은 KIS API를 사용할 때 필요한 공통 요청 로직을 하나의 클래스로 묶어 관리하는 것입니다.

---

# 1. 전체 코드의 역할

KIS API를 사용하려면 요청마다 여러 정보가 필요합니다.

이 코드의 `KISApiClient`는 이러한 작업을 한 곳에서 처리합니다.

프로그램의 다른 모듈은 복잡한 인증 헤더 생성이나 오류 처리 과정을 직접 반복하지 않고, `get()` 또는 `post()` 메서드를 호출하여 KIS API에 요청을 보낼 수 있습니다.

전체 흐름은 다음과 같습니다.

```text
KISApiClient 생성
  ↓
get() 또는 post() 호출
  ↓
_request()에서 공통 요청 처리
  ↓
AuthManager에서 접근 토큰 가져오기
  ↓
요청 헤더 생성
  ↓
GET이면 params 전송
  ↓
POST이면 json body 전송
  ↓
필요하면 hashkey 생성
  ↓
HTTP 요청 실행
  ↓
응답 상태 코드 확인
  ↓
KIS API 응답 코드 확인
  ↓
성공 시 payload 반환
  ↓
실패 시 재시도 또는 최종 예외 발생
```

---

# 3. `KISResult` 데이터 클래스

```python
@dataclass
class KISResult:
    status_code: int
    data: dict[str, Any]
```

`KISResult`는 KIS API 응답 결과를 표현하기 위한 데이터 클래스입니다.

이 클래스는 HTTP 상태 코드와 응답 데이터를 함께 담습니다.

`status_code`는 HTTP 응답 상태 코드입니다.

요청 자체가 서버와 정상적으로 통신되었는지를 나타냅니다.

대표적으로 `200`은 HTTP 요청이 성공했다는 뜻입니다.

`data`는 KIS API 서버에서 반환한 JSON 응답을 딕셔너리 형태로 저장하는 필드입니다.

---

# 4. `KISResult.ok` 속성

```python
@property
def ok(self) -> bool:
    rt_cd = str(self.data.get("rt_cd", "0"))
    return self.status_code == 200 and rt_cd == "0"
```

`ok`는 응답이 성공인지 확인하는 읽기 전용 속성입니다.

`@property`가 붙어 있기 때문에 메서드처럼 호출하지 않고 속성처럼 사용할 수 있습니다.

---

## 4.2 `rt_cd` 확인

```python
rt_cd = str(self.data.get("rt_cd", "0"))
```

KIS API 응답 데이터에서 `rt_cd` 값을 꺼냅니다.

`rt_cd`는 KIS API의 처리 결과 코드를 의미합니다.

이 코드에서는 `rt_cd`가 `"0"`이면 KIS API 내부 처리가 성공한 것으로 판단합니다.

`data`에 `rt_cd` 키가 없으면 기본값 `"0"`을 사용합니다.

또한 `str()`로 감싸서 숫자 형태로 들어온 값도 문자열로 비교할 수 있게 합니다.

---

## 4.3 성공 조건

```python
return self.status_code == 200 and rt_cd == "0"
```

`ok`가 `True`가 되려면 두 조건을 모두 만족해야 합니다.

1. HTTP 상태 코드가 `200`이어야 한다.
2. KIS API 응답 코드인 `rt_cd`가 `"0"`이어야 한다.

---

# 5. `KISApiClient` 클래스

```python
class KISApiClient:
```

`KISApiClient`는 KIS API 요청을 처리하는 클라이언트 클래스입니다.

이 클래스는 다음 기능을 담당합니다.

1. GET 요청 전송
2. POST 요청 전송
3. 접근 토큰을 포함한 요청 헤더 생성
4. Hashkey 생성
5. 응답 상태 코드 확인
6. KIS API 응답 코드 확인
7. 일시적 오류에 대한 재시도
8. 오류 로그 기록

---

# 6. `KISApiClient.__init__()`

```python
def __init__(
    self,
    base_url: str,
    appkey: str,
    appsecret: str,
    auth_manager: AuthManager,
    logger,
    timeout_seconds: int = 10,
    retry_count: int = 2,
    retry_backoff_seconds: float = 2.0,
) -> None:
```

`KISApiClient` 객체를 초기화하는 생성자입니다.

KIS API 요청에 필요한 기본 정보들을 객체 내부에 저장합니다.

| 매개변수                    | 타입            | 설명                                 |
| ----------------------- | ------------- | ---------------------------------- |
| `base_url`              | `str`         | KIS API 서버의 기본 주소입니다.              |
| `appkey`                | `str`         | KIS API 앱키입니다.                     |
| `appsecret`             | `str`         | KIS API 앱시크릿입니다.                   |
| `auth_manager`          | `AuthManager` | 접근 토큰을 관리하는 인증 관리자입니다.             |
| `logger`                | 명시된 타입 없음     | 오류와 요청 실패를 기록하기 위한 로거입니다.          |
| `timeout_seconds`       | `int`         | API 요청의 최대 대기 시간입니다. 기본값은 10초입니다.  |
| `retry_count`           | `int`         | 요청 실패 시 재시도할 횟수입니다. 기본값은 2입니다.     |
| `retry_backoff_seconds` | `float`       | 재시도 전 대기 시간의 기준값입니다. 기본값은 2.0초입니다. |

---

# 7. `get()` 메서드

```python
def get(self, path: str, tr_id: str, params: dict[str, Any], tr_cont: str = "") -> dict[str, Any]:
    return self._request("GET", path, tr_id, params=params, tr_cont=tr_cont)
```

`get()`은 KIS API에 GET 요청을 보내는 공개 메서드입니다.

GET 요청은 보통 서버에서 데이터를 조회할 때 사용됩니다.

`get()`은 `_request()`에 다음 정보를 전달합니다.

* 요청 방식: `"GET"`
* API 경로: `path`
* 거래 ID: `tr_id`
* 조회 조건: `params`
* 연속 조회 값: `tr_cont`

즉, `get()`은 GET 요청에 필요한 값을 정리해서 공통 요청 메서드인 `_request()`로 넘겨주는 역할을 합니다.

---

# 8. `post()` 메서드

```python
def post(
    self,
    path: str,
    tr_id: str,
    body: dict[str, Any],
    tr_cont: str = "",
    use_hashkey: bool = True,
) -> dict[str, Any]:
    return self._request("POST", path, tr_id, body=body, tr_cont=tr_cont, use_hashkey=use_hashkey)
```

`post()`는 KIS API에 POST 요청을 보내는 공개 메서드입니다.

POST 요청은 보통 서버에 데이터를 전달하여 어떤 동작을 수행할 때 사용됩니다.

이 메서드도 직접 요청을 처리하지 않고 `_request()`에 요청 처리를 위임합니다.

`post()`는 `_request()`에 다음 정보를 전달합니다.

* 요청 방식: `"POST"`
* API 경로: `path`
* 거래 ID: `tr_id`
* 요청 본문: `body`
* 연속 조회 값: `tr_cont`
* Hashkey 사용 여부: `use_hashkey`

---

# 9. `get_hashkey()` 메서드

```python
def get_hashkey(self, body: dict[str, Any]) -> str:
```

`get_hashkey()`는 KIS API의 Hashkey를 발급받는 메서드입니다.

일부 POST 요청에서는 요청 본문에 대한 Hashkey를 헤더에 포함해야 합니다.

이 메서드는 `/uapi/hashkey` API에 요청 본문을 보내고, 응답으로 받은 Hashkey 값을 반환합니다.

---

## 9.3 Hashkey URL 생성

```python
url = f"{self.base_url}/uapi/hashkey"
```

Hashkey 발급 API의 URL을 생성합니다.

`base_url` 뒤에 `/uapi/hashkey` 경로를 붙입니다.

---

## 9.4 Hashkey 요청 헤더 생성

```python
headers = {
    "content-type": "application/json",
    "accept": "text/plain",
    "charset": "UTF-8",
    "appkey": self.appkey,
    "appsecret": self.appsecret,
}
```

Hashkey 요청에 필요한 헤더를 생성합니다.

각 헤더의 의미는 다음과 같습니다.

| 헤더             | 설명                      |
| -------------- | ----------------------- |
| `content-type` | 요청 본문이 JSON 형식임을 의미합니다. |
| `accept`       | 응답 형식과 관련된 헤더입니다.       |
| `charset`      | 문자 인코딩을 UTF-8로 지정합니다.   |
| `appkey`       | KIS API 앱키입니다.          |
| `appsecret`    | KIS API 앱시크릿입니다.        |

---

## 9.5 Hashkey 요청 전송

```python
response = self._session.post(url, json=body, headers=headers, timeout=self.timeout_seconds)
```

Hashkey 발급 API에 POST 요청을 보냅니다.

요청 본문은 `json=body`로 전달됩니다.

요청이 응답을 기다리는 최대 시간은 `self.timeout_seconds`입니다.

---

## 9.6 HTTP 오류 확인

```python
response.raise_for_status()
```

Hashkey 요청의 HTTP 상태 코드가 오류인지 확인합니다.

상태 코드가 오류이면 `requests.HTTPError`가 발생합니다.

---

## 9.7 응답 JSON 변환

```python
payload = response.json()
```

Hashkey API의 응답 본문을 JSON으로 변환합니다.

---

## 9.8 Hashkey 추출

```python
hashkey = str(payload.get("HASH", "")).strip()
```

응답 JSON에서 `HASH` 값을 꺼냅니다.

`HASH` 키가 없으면 빈 문자열을 사용합니다.

꺼낸 값은 문자열로 변환한 뒤 앞뒤 공백을 제거합니다.

---

## 9.9 Hashkey 유효성 확인

```python
if not hashkey:
    raise RuntimeError(f"Hashkey response did not include HASH: {payload}")
```

응답에서 Hashkey를 찾을 수 없거나 값이 비어 있으면 `RuntimeError`를 발생시킵니다.

즉, HTTP 요청이 성공했더라도 응답 안에 `HASH` 값이 없으면 정상적인 Hashkey 발급 응답으로 보지 않습니다.

---

## 9.10 Hashkey 반환

```python
return hashkey
```

정상적으로 추출한 Hashkey 문자열을 반환합니다.

---

# 10. `_request()` 메서드

```python
def _request(
    self,
    method: str,
    path: str,
    tr_id: str,
    params: dict[str, Any] | None = None,
    body: dict[str, Any] | None = None,
    tr_cont: str = "",
    use_hashkey: bool = False,
) -> dict[str, Any]:
```

`_request()`는 실제 API 요청을 처리하는 핵심 메서드입니다.

`get()`과 `post()`는 모두 내부적으로 이 메서드를 호출합니다.

메서드 이름 앞에 밑줄 `_`이 붙어 있으므로, 클래스 외부에서 직접 호출하기보다는 `get()`과 `post()`를 통해 사용하는 것을 의도한 내부 메서드입니다.

| 매개변수          | 타입                       | 설명                                         |
| ------------- | ------------------------ | ------------------------------------------ |
| `method`      | `str`                    | HTTP 요청 방식입니다. `"GET"` 또는 `"POST"`가 사용됩니다. |
| `path`        | `str`                    | API 경로입니다.                                 |
| `tr_id`       | `str`                    | KIS API에서 요구하는 거래 ID입니다.                   |
| `params`      | `dict[str, Any] \| None` | GET 요청에서 사용할 조회 조건입니다.                     |
| `body`        | `dict[str, Any] \| None` | POST 요청에서 사용할 요청 본문입니다.                    |
| `tr_cont`     | `str`                    | 연속 조회 여부를 나타내는 값입니다.                       |
| `use_hashkey` | `bool`                   | Hashkey 사용 여부입니다.                          |

반환값은 KIS API 서버에서 받은 JSON 응답 데이터입니다.

요청이 성공하고, KIS API 응답 코드가 정상일 때만 반환됩니다.

---

# 11. 요청 URL 생성

```python
url = f"{self.base_url}{path}"
```

`base_url`과 `path`를 합쳐 최종 요청 URL을 생성합니다.

`base_url`은 생성자에서 끝의 `/`가 제거된 상태로 저장되어 있으므로, `path`가 `/`로 시작하면 정상적인 URL 구조가 됩니다.

---

# 12. 접근 토큰 가져오기

```python
token = self.auth_manager.get_token()
```

API 요청을 보내기 전에 인증 관리자에서 접근 토큰을 가져옵니다.

KIS API의 일반 요청은 접근 토큰을 필요로 하므로, 이 토큰은 요청 헤더의 `authorization` 값에 포함됩니다.

---

# 13. 요청 헤더 생성

```python
headers: dict[str, str] = {
    "content-type": "application/json",
    "accept": "text/plain",
    "charset": "UTF-8",
    "authorization": f"Bearer {token}",
    "appkey": self.appkey,
    "appsecret": self.appsecret,
    "tr_id": tr_id,
    "custtype": "P",
    "tr_cont": tr_cont,
}
```

KIS API 요청에 필요한 공통 헤더를 생성합니다.

각 헤더의 의미는 다음과 같습니다.

| 헤더              | 설명                             |
| --------------- | ------------------------------ |
| `content-type`  | 요청 본문 형식이 JSON임을 나타냅니다.        |
| `accept`        | 응답 형식과 관련된 헤더입니다.              |
| `charset`       | 문자 인코딩을 UTF-8로 지정합니다.          |
| `authorization` | 접근 토큰을 담는 인증 헤더입니다.            |
| `appkey`        | KIS API 앱키입니다.                 |
| `appsecret`     | KIS API 앱시크릿입니다.               |
| `tr_id`         | KIS API 거래 ID입니다.              |
| `custtype`      | 고객 타입입니다. `"P"`는 개인 고객을 의미합니다. |
| `tr_cont`       | 연속 조회 여부를 나타내는 값입니다.           |

---

# 14. 요청 옵션 생성

```python
request_kwargs: dict[str, Any] = {"headers": headers, "timeout": self.timeout_seconds}
```

실제 HTTP 요청에 전달할 공통 옵션을 만듭니다.

모든 요청에는 다음 값이 포함됩니다.

| 옵션        | 설명                |
| --------- | ----------------- |
| `headers` | 요청 헤더입니다.         |
| `timeout` | 응답을 기다릴 최대 시간입니다. |

---

# 15. GET 요청 처리

```python
if method == "GET":
    request_kwargs["params"] = params or {}
```

요청 방식이 GET이면 `params`를 요청 옵션에 추가합니다.

GET 요청에서 `params`는 URL 쿼리 파라미터로 전송됩니다.

즉, 조회 조건은 요청 본문이 아니라 URL 뒤에 붙는 방식으로 서버에 전달됩니다.

`params`가 `None`이면 빈 딕셔너리 `{}`를 사용합니다.

---

# 16. POST 요청 처리

```python
else:
    request_kwargs["json"] = body or {}
    if use_hashkey:
        headers["hashkey"] = self.get_hashkey(body or {})
```

요청 방식이 GET이 아니면 POST 요청으로 처리합니다.

POST 요청에서는 `body`를 JSON 본문으로 전송합니다.

---

## 16.1 JSON 본문 설정

```python
request_kwargs["json"] = body or {}
```

`body` 값이 있으면 그 값을 JSON 본문으로 설정합니다.

`body`가 `None`이면 빈 딕셔너리 `{}`를 사용합니다.

---

## 16.2 Hashkey 추가

```python
if use_hashkey:
    headers["hashkey"] = self.get_hashkey(body or {})
```

`use_hashkey`가 `True`이면 `get_hashkey()`를 호출해 Hashkey를 생성합니다.

생성된 Hashkey는 요청 헤더에 추가됩니다.

---

# 17. 재시도 준비

```python
last_error: Exception | None = None
```

마지막으로 발생한 오류를 저장하기 위한 변수입니다.

요청이 최종적으로 실패했을 때, 마지막 오류를 원인으로 연결하기 위해 사용됩니다.

---

# 18. 재시도 반복문

```python
for attempt in range(self.retry_count + 1):
```

API 요청을 실행하는 반복문입니다.

`retry_count`는 재시도 횟수입니다.

---

# 19. 실제 HTTP 요청 실행

```python
response = self._session.request(method, url, **request_kwargs)
```

`requests.Session`을 사용해 실제 HTTP 요청을 보냅니다.

각 값의 의미는 다음과 같습니다.

| 값                | 설명                                     |
| ---------------- | -------------------------------------- |
| `method`         | 요청 방식입니다.                              |
| `url`            | 최종 요청 URL입니다.                          |
| `request_kwargs` | 헤더, 타임아웃, GET 파라미터 또는 POST JSON 본문입니다. |

---

# 20. 재시도 가능한 HTTP 상태 코드 확인

```python
if response.status_code == 429 or response.status_code >= 500:
    raise requests.HTTPError(f"retryable HTTP {response.status_code}", response=response)
```

응답 상태 코드가 `429`이거나 `500` 이상이면 재시도 가능한 HTTP 오류로 처리합니다.

이 경우 즉시 `requests.HTTPError`를 발생시켜 예외 처리 구간으로 이동합니다.

---

# 21. 일반 HTTP 오류 확인

```python
response.raise_for_status()
```

HTTP 응답 상태 코드가 오류인지 확인합니다.

`400`번대나 `500`번대 상태 코드가 있으면 `requests.HTTPError`가 발생합니다.

---

# 22. 응답 JSON 변환

```python
payload = response.json()
```

응답 본문을 JSON으로 변환합니다.

변환에 실패하면 `json.JSONDecodeError`가 발생할 수 있습니다.

---

# 23. KIS API 응답 코드 확인

```python
if str(payload.get("rt_cd", "0")) != "0":
    raise RuntimeError(
        f"KIS API error: rt_cd={payload.get('rt_cd')} msg_cd={payload.get('msg_cd')} msg1={payload.get('msg1')}"
    )
```

HTTP 요청 자체가 성공했더라도 KIS API 내부 처리 결과가 실패일 수 있습니다.

KIS API 응답의 `rt_cd` 값이 `"0"`이 아니면 API 오류로 판단합니다.

이 경우 `RuntimeError`를 발생시킵니다.

오류 메시지에는 다음 값들이 포함됩니다.

| 값        | 설명                   |
| -------- | -------------------- |
| `rt_cd`  | KIS API 처리 결과 코드입니다. |
| `msg_cd` | KIS API 메시지 코드입니다.   |
| `msg1`   | KIS API 메시지 내용입니다.   |

---

# 24. 정상 응답 반환

```python
return payload
```

HTTP 요청이 성공하고, KIS API 응답 코드도 정상이라면 응답 JSON 전체를 반환합니다.

이 시점에서 `_request()`는 종료됩니다.

---

# 25. 예외 처리

```python
except (requests.Timeout, requests.ConnectionError, json.JSONDecodeError, RuntimeError, requests.HTTPError) as exc:
```

요청 처리 중 발생할 수 있는 주요 예외를 처리합니다.

처리 대상은 다음과 같습니다.

| 예외                         | 설명                                 |
| -------------------------- | ---------------------------------- |
| `requests.Timeout`         | 요청 시간이 초과된 경우입니다.                  |
| `requests.ConnectionError` | 네트워크 연결 문제가 발생한 경우입니다.             |
| `json.JSONDecodeError`     | 응답을 JSON으로 해석하지 못한 경우입니다.          |
| `RuntimeError`             | KIS API 응답 오류 또는 직접 발생시킨 실행 오류입니다. |
| `requests.HTTPError`       | HTTP 상태 코드 오류입니다.                  |

---

## 25.1 마지막 오류 저장

```python
last_error = exc
```

현재 발생한 예외를 `last_error`에 저장합니다.

이 값은 모든 재시도가 실패했을 때 최종 예외의 원인으로 연결됩니다.

---

## 25.2 상태 코드 추출

```python
status_code = getattr(getattr(exc, "response", None), "status_code", None)
```

예외 객체에서 HTTP 응답 상태 코드를 추출합니다.

일부 예외는 `response` 속성을 가지고 있지 않을 수 있으므로 `getattr()`을 사용해 안전하게 접근합니다.

먼저 `exc.response`를 가져오고, 그 결과에서 다시 `status_code`를 가져옵니다.

값을 가져올 수 없으면 `None`이 됩니다.

---

## 25.3 재시도 가능 여부 판단

```python
retryable = isinstance(exc, (requests.Timeout, requests.ConnectionError, json.JSONDecodeError, RuntimeError)) or status_code in {
    429,
} or (status_code is not None and status_code >= 500)
```

현재 발생한 오류가 재시도 가능한 오류인지 판단합니다.

이 코드에서 재시도 가능한 경우는 다음과 같습니다.

1. 요청 시간이 초과된 경우
2. 네트워크 연결 오류가 발생한 경우
3. JSON 파싱 오류가 발생한 경우
4. `RuntimeError`가 발생한 경우
5. HTTP 상태 코드가 `429`인 경우
6. HTTP 상태 코드가 `500` 이상인 경우

---

## 25.4 마지막 시도 여부 확인

```python
is_last_attempt = attempt >= self.retry_count
```

현재 시도가 마지막 시도인지 확인합니다.

`attempt`는 0부터 시작합니다.

따라서 `attempt >= self.retry_count`이면 더 이상 재시도하지 않습니다.

---

## 25.5 오류 로그 기록

```python
self.logger.error(
    "api error: method=%s path=%s attempt=%s/%s error=%s",
    method,
    path,
    attempt + 1,
    self.retry_count + 1,
    exc,
)
```

요청 실패 정보를 로그로 기록합니다.

로그에는 다음 정보가 포함됩니다.

| 값                      | 설명              |
| ---------------------- | --------------- |
| `method`               | 요청 방식입니다.       |
| `path`                 | API 경로입니다.      |
| `attempt + 1`          | 현재 시도 횟수입니다.    |
| `self.retry_count + 1` | 전체 최대 시도 횟수입니다. |
| `exc`                  | 발생한 오류 내용입니다.   |

이 로그를 통해 어떤 API 요청이 몇 번째 시도에서 실패했는지 확인할 수 있습니다.

---

## 25.6 반복 종료 조건

```python
if is_last_attempt or not retryable:
    break
```

다음 중 하나에 해당하면 더 이상 재시도하지 않고 반복문을 종료합니다.

1. 현재 시도가 마지막 시도인 경우
2. 발생한 오류가 재시도 가능한 오류가 아닌 경우

반복문이 종료되면 아래의 최종 실패 처리로 이동합니다.

---

## 25.7 재시도 전 대기

```python
time.sleep(self.retry_backoff_seconds * (attempt + 1))
```

재시도하기 전에 일정 시간 대기합니다.

대기 시간은 다음 방식으로 계산됩니다.

```text
retry_backoff_seconds × (attempt + 1)
```

따라서 실패 횟수가 늘어날수록 대기 시간이 길어집니다.

---

# 26. 최종 실패 처리

```python
raise RuntimeError(f"Request failed after retries: {method} {path}") from last_error
```

모든 시도가 실패하면 최종적으로 `RuntimeError`를 발생시킵니다.

오류 메시지에는 요청 방식과 API 경로가 포함됩니다.

`from last_error`를 사용했기 때문에, 최종 오류에는 마지막으로 발생한 원래 예외가 연결됩니다.

이를 통해 실제 실패 원인을 추적할 수 있습니다.

---

# 27. GET 요청 흐름

GET 요청은 다음 순서로 처리됩니다.

```text
get()
  ↓
_request("GET", ...)
  ↓
요청 URL 생성
  ↓
AuthManager에서 접근 토큰 가져오기
  ↓
공통 헤더 생성
  ↓
params를 request_kwargs에 추가
  ↓
HTTP GET 요청 실행
  ↓
HTTP 상태 코드 확인
  ↓
응답 JSON 변환
  ↓
rt_cd 확인
  ↓
정상 payload 반환
```

GET 요청에서 핵심은 `params`입니다.

`params`는 조회 조건을 담고 있으며, URL 쿼리 파라미터로 전송됩니다.

---

# 28. POST 요청 흐름

POST 요청은 다음 순서로 처리됩니다.

```text
post()
  ↓
_request("POST", ...)
  ↓
요청 URL 생성
  ↓
AuthManager에서 접근 토큰 가져오기
  ↓
공통 헤더 생성
  ↓
body를 JSON 본문으로 설정
  ↓
use_hashkey가 True이면 hashkey 생성
  ↓
hashkey를 헤더에 추가
  ↓
HTTP POST 요청 실행
  ↓
HTTP 상태 코드 확인
  ↓
응답 JSON 변환
  ↓
rt_cd 확인
  ↓
정상 payload 반환
```

POST 요청에서 핵심은 `body`입니다.

`body`는 서버에 전달할 요청 본문이며, JSON 형태로 전송됩니다.

---

# 29. Hashkey 처리 흐름

Hashkey는 다음 순서로 처리됩니다.

```text
POST 요청 시작
  ↓
use_hashkey 확인
  ↓
get_hashkey(body) 호출
  ↓
/uapi/hashkey로 POST 요청
  ↓
응답 JSON에서 HASH 추출
  ↓
hashkey 헤더에 추가
  ↓
원래 POST 요청 실행
```

Hashkey는 원래 POST 요청을 보내기 전에 먼저 생성됩니다.

그 후 생성된 Hashkey가 원래 요청의 헤더에 포함됩니다.

---

# 30. 재시도 처리 흐름

API 요청 실패 시 재시도 흐름은 다음과 같습니다.

```text
요청 실행
  ↓
예외 발생
  ↓
last_error에 예외 저장
  ↓
재시도 가능한 오류인지 판단
  ↓
오류 로그 기록
  ↓
마지막 시도이거나 재시도 불가능하면 중단
  ↓
아니면 일정 시간 대기
  ↓
다시 요청 실행
```

모든 시도가 실패하면 최종적으로 `RuntimeError`가 발생합니다.

---

# market_data.py: 현재가 조회

한국투자증권 KIS API를 사용해 국내 주식의 현재가 정보를 조회하는 시장 데이터 서비스 코드에 대한 설명입니다.

이 코드는 크게 네 부분으로 구성됩니다.

1. `KISApiClient` import 처리
2. 주식 시세 정보를 담는 `Quote` 데이터 클래스
3. 값을 정수로 변환하는 `_to_int()` 함수
4. 현재가 조회를 담당하는 `MarketDataService` 클래스

이 모듈의 목적은 KIS API의 현재가 조회 응답을 `Quote` 객체로 변환하여 프로그램의 다른 부분에서 활용할 수 있도록 하는 것입니다.

---

# 1. 전체 코드의 역할

이 코드는 특정 종목의 현재가 정보를 조회합니다.

한국투자증권 KIS API의 국내 주식 현재가 조회 API를 호출하고, 응답 데이터에서 다음 정보를 추출합니다.

* 종목 코드
* 현재가
* 시가
* 고가
* 저가
* 누적 거래량
* 원본 API 응답 데이터

API 응답은 일반적으로 문자열 형태로 들어오기 때문에, 가격이나 거래량처럼 숫자로 다뤄야 하는 값은 정수로 변환합니다.

전체 흐름은 다음과 같습니다.

```text
MarketDataService 생성
  ↓
get_current_price() 호출
  ↓
KISApiClient.get()으로 현재가 조회 API 호출
  ↓
응답 payload에서 output 추출
  ↓
현재가 stck_prpr 추출
  ↓
현재가를 정수로 변환
  ↓
현재가가 없으면 오류 발생
  ↓
시가, 고가, 저가, 거래량 변환
  ↓
Quote 객체 생성
  ↓
조회 결과 로그 기록
  ↓
Quote 객체 반환
```

---

# 2. `KISApiClient` import 처리

```python
try:
    from .api_client import KISApiClient
except ImportError:  # pragma: no cover
    from api_client import KISApiClient
```

이 부분은 `KISApiClient` 클래스를 가져오는 코드입니다.

먼저 상대 import를 시도합니다.

상대 import는 `market_data.py` 안에서 같은 패키지의 `api_client.py`를 가져올 때 `.api_client` 형식을 사용할 수 있습니다.

상대 import가 실패하면 일반 import 방식으로 다시 가져옵니다.

---

# 3. `Quote` 데이터 클래스

```python
@dataclass(frozen=True)
class Quote:
    symbol: str
    price: int
    open_price: int | None = None
    high_price: int | None = None
    low_price: int | None = None
    volume: int | None = None
    raw: dict[str, Any] | None = None
```

`Quote`는 주식 시세 정보를 담는 데이터 클래스입니다.

KIS API에서 받은 현재가 조회 응답 중 필요한 값을 정리하여 하나의 객체로 표현합니다.

---

## 4.1 `symbol`

```python
symbol: str
```

조회한 종목 코드입니다.

---

## 4.2 `price`

```python
price: int
```

현재가입니다.

KIS API 응답의 `stck_prpr` 값을 정수로 변환하여 저장합니다

---

## 4.3 `open_price`

```python
open_price: int | None = None
```

시가입니다.

시가는 장 시작 시 처음 형성된 가격을 의미합니다.

값이 없거나 변환할 수 없으면 `None`이 됩니다.

---

## 4.4 `high_price`

```python
high_price: int | None = None
```

고가입니다.

고가는 해당 거래일 중 현재까지 가장 높게 형성된 가격을 의미합니다.

값이 없거나 변환할 수 없으면 `None`이 됩니다.

---

## 4.5 `low_price`

```python
low_price: int | None = None
```

저가입니다.

저가는 해당 거래일 중 현재까지 가장 낮게 형성된 가격을 의미합니다.

값이 없거나 변환할 수 없으면 `None`이 됩니다.

---

## 4.6 `volume`

```python
volume: int | None = None
```

누적 거래량입니다.

값이 없거나 변환할 수 없으면 `None`이 됩니다.

---

## 4.7 `raw`

```python
raw: dict[str, Any] | None = None
```

KIS API 응답의 원본 `output` 데이터입니다.

이 필드는 현재 코드에서 별도로 추출하지 않은 API 응답 항목까지 보존하기 위해 사용됩니다.

---

# 5. `_to_int()` 함수

```python
def _to_int(value: Any, default: int | None = None) -> int | None:
    if value is None:
        return default
    try:
        text = str(value).replace(",", "").strip()
        if text == "":
            return default
        return int(float(text))
    except (TypeError, ValueError):
        return default
```

`_to_int()` 함수는 다양한 형태의 값을 정수로 변환하는 보조 함수입니다.

---

## 5.1 함수 매개변수

```python
def _to_int(value: Any, default: int | None = None) -> int | None:
```

변환에 성공하면 `int` 값을 반환합니다.

변환할 수 없으면 `default` 값을 반환합니다.

기본적으로 `default`는 `None`이므로, 변환 실패 시 `None`이 반환됩니다.

---

## 5.3 `None` 처리

```python
if value is None:
    return default
```

입력값이 `None`이면 변환을 시도하지 않고 바로 `default`를 반환합니다.

---

## 5.4 문자열 변환과 쉼표 제거

```python
text = str(value).replace(",", "").strip()
```

입력값을 먼저 문자열로 변환합니다.

그 다음 쉼표를 제거합니다.

```python
replace(",", "")
```

```python
strip()
```

---

## 5.5 빈 문자열 처리

```python
if text == "":
    return default
```

문자열로 변환하고 공백을 제거한 결과가 빈 문자열이면 숫자로 변환할 수 없습니다.

따라서 `default`를 반환합니다.

---

## 5.6 정수 변환

```python
return int(float(text))
```

이 코드는 문자열을 먼저 `float`으로 변환한 뒤, 다시 `int`로 변환합니다.

예를 들어 `"70000.0"`을 바로 `int()`로 변환하면 오류가 발생합니다.

따라서 이 함수는 정수 문자열뿐 아니라 소수점이 포함된 숫자 문자열도 처리할 수 있습니다.

---

## 5.7 변환 실패 처리

```python
except (TypeError, ValueError):
    return default
```

정수 변환 과정에서 오류가 발생하면 `default`를 반환합니다.

처리하는 오류는 다음 두 가지입니다.

| 예외           | 발생 상황                    |
| ------------ | ------------------------ |
| `TypeError`  | 변환할 수 없는 타입이 들어온 경우      |
| `ValueError` | 숫자로 해석할 수 없는 문자열이 들어온 경우 |

---

# 6. `MarketDataService` 클래스

```python
class MarketDataService:
```

`MarketDataService`는 시장 데이터 조회 기능을 제공하는 클래스입니다.

---

# 7. `MarketDataService.__init__()`

```python
def __init__(self, client: KISApiClient, logger) -> None:
    self.client = client
    self.logger = logger
```

`MarketDataService` 객체를 초기화하는 생성자입니다.

현재가 조회에 사용할 API 클라이언트와 로그 기록용 로거를 저장합니다.

| 매개변수     | 타입             | 설명                           |
| -------- | -------------- | ---------------------------- |
| `client` | `KISApiClient` | KIS API 요청을 보내는 클라이언트 객체입니다. |
| `logger` | 명시된 타입 없음      | 현재가 조회 결과를 기록하는 로거입니다.       |

`KISApiClient` 객체를 저장합니다.

로그를 기록하기 위한 객체를 저장합니다.

---

# 8. `get_current_price()` 메서드

```python
def get_current_price(self, symbol: str, market_code: str = "J") -> Quote:
```

`get_current_price()`는 특정 종목의 현재가를 조회하는 메서드입니다.

KIS API의 국내 주식 현재가 조회 API를 호출하고, 응답을 `Quote` 객체로 변환하여 반환합니다.

| 매개변수          | 타입    | 설명                          |
| ------------- | ----- | --------------------------- |
| `symbol`      | `str` | 조회할 종목 코드입니다.               |
| `market_code` | `str` | 시장 구분 코드입니다. 기본값은 `"J"`입니다. |

`Quote` 객체에는 현재가, 시가, 고가, 저가, 거래량, 원본 응답 데이터가 담깁니다.

---

# 9. 현재가 조회 API 호출

```python
payload = self.client.get(
    "/uapi/domestic-stock/v1/quotations/inquire-price",
    tr_id="FHKST01010100",
    params={
        "FID_COND_MRKT_DIV_CODE": market_code,
        "FID_INPUT_ISCD": symbol,
    },
)
```

이 코드는 `KISApiClient`의 `get()` 메서드를 사용하여 국내 주식 현재가 조회 API를 호출합니다.


```python
"/uapi/domestic-stock/v1/quotations/inquire-price"
```

이 경로는 국내 주식 현재가 조회 API의 경로입니다.

`KISApiClient`는 이 경로를 `base_url`과 합쳐 최종 요청 URL을 만듭니다.

```python
tr_id="FHKST01010100"
```

`tr_id`는 KIS API에서 요청 종류를 구분하기 위해 사용하는 거래 ID입니다.

이 값은 현재가 조회 API에 해당하는 거래 ID로 사용됩니다.

```python
params={
    "FID_COND_MRKT_DIV_CODE": market_code,
    "FID_INPUT_ISCD": symbol,
}
```

GET 요청에 전달할 조회 조건입니다.

이 파라미터는 URL 쿼리 파라미터로 전송됩니다.

각 값의 의미는 다음과 같습니다.

| 파라미터                     | 설명            |
| ------------------------ | ------------- |
| `FID_COND_MRKT_DIV_CODE` | 시장 구분 코드입니다.  |
| `FID_INPUT_ISCD`         | 조회할 종목 코드입니다. |

---

# 10. 응답 `output` 추출

```python
output = payload.get("output", {})
```

KIS API 응답에서 `output` 값을 꺼냅니다.

`output` 키가 없으면 빈 딕셔너리 `{}`를 사용합니다.

---

# 11. 현재가 추출 및 변환

```python
price = _to_int(output.get("stck_prpr"))
```

`output`에서 현재가 값을 꺼내 정수로 변환합니다.

---

## 11.1 현재가 누락 검사

```python
if price is None:
    raise RuntimeError(f"Current price was missing from API response: {payload}")
```

현재가는 `Quote` 객체를 만들기 위한 필수 값입니다.

따라서 현재가가 없거나 정수로 변환할 수 없으면 오류를 발생시킵니다.

이 경우 API 응답 전체인 `payload`를 오류 메시지에 포함하여 어떤 응답이 들어왔는지 확인할 수 있게 합니다.

---

# 12. `Quote` 객체 생성

```python
quote = Quote(
    symbol=symbol,
    price=price,
    open_price=_to_int(output.get("stck_oprc")),
    high_price=_to_int(output.get("stck_hgpr")),
    low_price=_to_int(output.get("stck_lwpr")),
    volume=_to_int(output.get("acml_vol")),
    raw=output,
)
```

현재가 조회 결과를 `Quote` 객체로 변환합니다.

---

# 13. 조회 결과 로그 기록

```python
self.logger.info("current price: symbol=%s price=%s", symbol, f"{quote.price:,}")
```

현재가 조회가 성공하면 로그를 남깁니다.

로그에는 다음 정보가 포함됩니다.

* 종목 코드
* 현재가

`f"{quote.price:,}"`는 현재가에 천 단위 쉼표를 넣어 문자열로 만드는 표현입니다.

---

# 14. `Quote` 객체 반환

```python
return quote
```

최종적으로 생성된 `Quote` 객체를 반환합니다.

이 객체는 프로그램의 다른 모듈에서 현재가 판단, 주문 가격 계산, 로그 기록 등에 사용할 수 있습니다.

---

# 15. 실행 흐름 요약

`get_current_price()`를 기준으로 전체 실행 흐름을 정리하면 다음과 같습니다.

```text
get_current_price(symbol, market_code)
  ↓
KISApiClient.get() 호출
  ↓
국내 주식 현재가 조회 API 요청
  ↓
payload에서 output 추출
  ↓
output["stck_prpr"]를 현재가로 사용
  ↓
현재가를 정수로 변환
  ↓
현재가가 없으면 RuntimeError 발생
  ↓
시가, 고가, 저가, 거래량을 정수로 변환
  ↓
Quote 객체 생성
  ↓
현재가 조회 성공 로그 기록
  ↓
Quote 반환
```

---

# account.py: 잔고/보유종목 조회

한국투자증권 KIS API를 사용해 계좌 잔고와 보유 종목 정보를 조회하는 코드에 대한 설명입니다.

이 코드는 크게 다섯 부분으로 구성됩니다.

1. `KISApiClient` import 처리
2. 응답 데이터에서 첫 번째 유효 값을 찾는 `_first_value()` 함수
3. 값을 정수로 변환하는 `_to_int()` 함수
4. 보유 종목 정보를 표현하는 `Holding` 데이터 클래스
5. 계좌 전체 상태를 표현하는 `AccountSnapshot` 데이터 클래스
6. 계좌 잔고 조회를 담당하는 `AccountService` 클래스

이 모듈의 목적은 KIS API의 계좌 잔고 조회 응답을 프로그램에서 사용하기 쉬운 형태로 변환하는 것입니다.

---

# 1. 전체 코드의 역할

이 코드는 사용자의 국내 주식 계좌 상태를 조회합니다.

한국투자증권 KIS API의 잔고 조회 API를 호출하고, 응답 데이터에서 다음 정보를 추출합니다.

* 현금 잔고
* 주문 가능 현금
* 총 평가 금액
* 보유 종목 목록
* 각 보유 종목의 종목 코드
* 각 보유 종목의 종목명
* 보유 수량
* 평균 매입가
* 현재가
* 평가 손익
* 원본 API 응답 데이터

KIS API 응답은 문자열 형태의 숫자를 많이 포함합니다.

따라서 이 코드는 API 응답에서 필요한 값을 꺼낸 뒤 정수로 변환하여 `Holding` 객체와 `AccountSnapshot` 객체로 정리합니다.

전체 흐름은 다음과 같습니다.

```text
AccountService 생성
  ↓
get_snapshot() 호출
  ↓
KISApiClient.get()으로 잔고 조회 API 호출
  ↓
payload에서 output1, output2 추출
  ↓
output1에서 보유 종목 목록 생성
  ↓
output2에서 계좌 요약 정보 추출
  ↓
Holding 객체 목록 생성
  ↓
AccountSnapshot 객체 생성
  ↓
계좌 스냅샷 로그 기록
  ↓
AccountSnapshot 반환
```

---

# 2. `KISApiClient` import 처리

```python
try:
    from .api_client import KISApiClient
except ImportError:  # pragma: no cover
    from api_client import KISApiClient
```

이 코드는 `KISApiClient` 클래스를 가져오는 부분입니다.

먼저 상대 import를 시도합니다.

상대 import는 이 파일이 패키지 내부 모듈로 실행될 때 사용됩니다.

예를 들어 같은 패키지 안에 `api_client.py`와 `account.py`가 있다면, `.api_client`를 통해 같은 패키지의 API 클라이언트를 가져올 수 있습니다.

상대 import가 실패하면 일반 import 방식으로 다시 가져옵니다.

---

# 3. `_first_value()` 함수

```python
def _first_value(mapping: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in mapping and mapping[key] not in (None, ""):
            return mapping[key]
    return None
```

`_first_value()` 함수는 딕셔너리에서 여러 후보 키를 순서대로 확인하고, 가장 먼저 발견되는 유효한 값을 반환하는 보조 함수입니다.

KIS API 응답 필드명은 API 종류나 환경에 따라 조금씩 다르게 들어올 수 있습니다.

이 함수는 이런 여러 후보 키 중 실제 응답에 존재하는 값을 찾아줍니다.

| 매개변수      | 타입               | 설명                   |
| --------- | ---------------- | -------------------- |
| `mapping` | `dict[str, Any]` | 값을 찾을 대상 딕셔너리입니다.    |
| `*keys`   | `str`            | 순서대로 확인할 후보 키 목록입니다. |

`*keys`는 여러 개의 문자열 인자를 받을 수 있다는 뜻입니다.

각 키에 대해 두 가지 조건을 확인합니다.

1. 해당 키가 딕셔너리에 존재해야 한다.
2. 해당 키의 값이 `None` 또는 빈 문자열 `""`이 아니어야 한다.

두 조건을 모두 만족하면 해당 값을 반환합니다.

모든 후보 키를 확인했는데 사용할 수 있는 값이 없으면 `None`을 반환합니다.

---

# 4. `_to_int()` 함수

```python
def _to_int(value: Any) -> int:
    try:
        return int(float(str(value).replace(",", "").strip()))
    except (TypeError, ValueError):
        return 0
```

`_to_int()` 함수는 API 응답 값을 정수로 변환하는 보조 함수입니다.

변환할 수 없는 경우에는 `0`을 반환합니다.

처리하는 오류는 다음과 같습니다.

| 예외           | 발생 상황                    |
| ------------ | ------------------------ |
| `TypeError`  | 변환할 수 없는 타입이 들어온 경우      |
| `ValueError` | 숫자로 해석할 수 없는 문자열이 들어온 경우 |

---

# 5. `Holding` 데이터 클래스

```python
@dataclass(frozen=True)
class Holding:
    symbol: str
    name: str
    quantity: int
    average_price: int
    current_price: int
    evaluation_profit_loss: int
    raw: dict[str, Any]
```

`Holding`은 계좌가 보유한 개별 종목 정보를 표현하는 데이터 클래스입니다.

보유 종목 하나당 하나의 `Holding` 객체가 생성됩니다.

| 필드                       | 타입               | 설명                          |
| ------------------------ | ---------------- | --------------------------- |
| `symbol`                 | `str`            | 종목 코드입니다.                   |
| `name`                   | `str`            | 종목명입니다.                     |
| `quantity`               | `int`            | 보유 수량입니다.                   |
| `average_price`          | `int`            | 평균 매입가입니다.                  |
| `current_price`          | `int`            | 현재가입니다.                     |
| `evaluation_profit_loss` | `int`            | 평가 손익 금액입니다.                |
| `raw`                    | `dict[str, Any]` | 해당 보유 종목의 원본 API 응답 데이터입니다. |

---

# 6. `AccountSnapshot` 데이터 클래스

```python
@dataclass(frozen=True)
class AccountSnapshot:
    cash: int
    available_cash: int
    total_value: int
    holdings: list[Holding]
    raw_summary: dict[str, Any]
    raw_holdings: list[dict[str, Any]]
```

`AccountSnapshot`은 특정 시점의 계좌 전체 상태를 표현하는 데이터 클래스입니다.

| 필드               | 타입                     | 설명                 |
| ---------------- | ---------------------- | ------------------ |
| `cash`           | `int`                  | 계좌의 현금 금액입니다.      |
| `available_cash` | `int`                  | 주문 가능 현금입니다.       |
| `total_value`    | `int`                  | 계좌 총 평가 금액입니다.     |
| `holdings`       | `list[Holding]`        | 보유 종목 목록입니다.       |
| `raw_summary`    | `dict[str, Any]`       | 계좌 요약 정보 원본 응답입니다. |
| `raw_holdings`   | `list[dict[str, Any]]` | 보유 종목 목록 원본 응답입니다. |


# 7. `AccountService` 클래스

```python
class AccountService:
```

`AccountService`는 `KISApiClient`를 통해 계좌 정보를 조회하는 서비스 클래스입니다.

---

# 8. `AccountService.__init__()`

```python
class AccountService:
    def __init__(self, client: KISApiClient, logger, account_number: str, account_product_code: str) -> None:
        self.client = client
        self.logger = logger
        self.account_number = account_number
        self.account_product_code = account_product_code
```

`AccountService` 객체를 초기화하는 생성자입니다.

| 매개변수                   | 타입             | 설명                           |
| ---------------------- | -------------- | ---------------------------- |
| `client`               | `KISApiClient` | KIS API 요청을 보내는 클라이언트 객체입니다. |
| `logger`               | 명시된 타입 없음      | 계좌 조회 결과를 기록하는 로거입니다.        |
| `account_number`       | `str`          | 계좌번호 앞 8자리입니다.               |
| `account_product_code` | `str`          | 계좌상품코드 2자리입니다.               |

---


# 9. `get_snapshot()` 메서드

```python
def get_snapshot(self) -> AccountSnapshot:
```

`get_snapshot()`은 현재 계좌 상태를 조회하는 메서드입니다.

KIS API의 국내 주식 잔고 조회 API를 호출하고, 응답을 `AccountSnapshot` 객체로 변환하여 반환합니다.

```python
payload = self.client.get(
    "/uapi/domestic-stock/v1/trading/inquire-balance",
    tr_id="VTTC8434R",
    params={
        "CANO": self.account_number,
        "ACNT_PRDT_CD": self.account_product_code,
        "AFHR_FLPR_YN": "N",
        "OFL_YN": "",
        "INQR_DVSN": "02",
        "UNPR_DVSN": "01",
        "FUND_STTL_ICLD_YN": "N",
        "FNCG_AMT_AUTO_RDPT_YN": "N",
        "PRCS_DVSN": "00",
        "CTX_AREA_FK100": "",
        "CTX_AREA_NK100": "",
    },
)
```

`KISApiClient`의 `get()` 메서드를 사용하여 국내 주식 잔고 조회 API를 호출합니다.

---

## 10.1 API 경로

```python
"/uapi/domestic-stock/v1/trading/inquire-balance"
```

이 경로는 국내 주식 잔고 조회 API의 경로입니다.

`KISApiClient`는 이 경로를 `base_url`과 합쳐 최종 요청 URL을 만듭니다.

---

## 10.2 거래 ID

```python
tr_id="VTTC8434R"
```

`tr_id`는 KIS API에서 요청 종류를 구분하기 위해 사용하는 거래 ID입니다.

이 값은 잔고 조회 API에 해당하는 거래 ID로 사용됩니다.

---

## 10.3 요청 파라미터

```python
params={
    "CANO": self.account_number,
    "ACNT_PRDT_CD": self.account_product_code,
    "AFHR_FLPR_YN": "N",
    "OFL_YN": "",
    "INQR_DVSN": "02",
    "UNPR_DVSN": "01",
    "FUND_STTL_ICLD_YN": "N",
    "FNCG_AMT_AUTO_RDPT_YN": "N",
    "PRCS_DVSN": "00",
    "CTX_AREA_FK100": "",
    "CTX_AREA_NK100": "",
}
```

GET 요청에 전달할 조회 조건입니다.

이 파라미터는 URL 쿼리 파라미터로 전송됩니다.

각 파라미터의 의미는 다음과 같습니다.

| 파라미터                    | 설명                       |
| ----------------------- | ------------------------ |
| `CANO`                  | 계좌번호 앞 8자리입니다.           |
| `ACNT_PRDT_CD`          | 계좌상품코드 2자리입니다.           |
| `AFHR_FLPR_YN`          | 시간외 단일가 여부와 관련된 값입니다.    |
| `OFL_YN`                | 오프라인 여부와 관련된 값입니다.       |
| `INQR_DVSN`             | 조회 구분 값입니다.              |
| `UNPR_DVSN`             | 단가 구분 값입니다.              |
| `FUND_STTL_ICLD_YN`     | 펀드 결제분 포함 여부와 관련된 값입니다.  |
| `FNCG_AMT_AUTO_RDPT_YN` | 융자금액 자동상환 여부와 관련된 값입니다.  |
| `PRCS_DVSN`             | 처리 구분 값입니다.              |
| `CTX_AREA_FK100`        | 연속 조회를 위한 이전 조회 키 영역입니다. |
| `CTX_AREA_NK100`        | 연속 조회를 위한 다음 조회 키 영역입니다. |

---

# 11. 응답 데이터 추출

```python
output1 = payload.get("output1", []) or []
output2 = payload.get("output2", []) or []
```

KIS API 잔고 조회 응답에서 `output1`과 `output2`를 꺼냅니다.

| 응답 필드     | 의미           |
| --------- | ------------ |
| `output1` | 보유 종목 목록입니다. |
| `output2` | 계좌 요약 정보입니다. |

키가 없을 땐 빈 리스트를 사용합니다.

뒤의 `or []`는 값이 `None`이거나 빈 값일 경우에도 빈 리스트로 처리하기 위한 코드입니다.

---

## 11.1 `output1`이 딕셔너리인 경우

```python
if isinstance(output1, dict):
    output1 = [output1]
```

보유 종목 정보인 `output1`은 보통 리스트 형태이지만, 응답 상황에 따라 딕셔너리 하나로 들어올 수도 있습니다.

이 경우 이후 코드에서 동일하게 반복 처리할 수 있도록 리스트로 감쌉니다.

---

## 11.2 `output2`가 딕셔너리인 경우

```python
if isinstance(output2, dict):
    output2 = [output2]
```

계좌 요약 정보인 `output2`도 보통 리스트 형태이지만, 딕셔너리 하나로 들어올 수 있습니다.

이 경우에도 리스트로 감싸서 이후 코드에서 일관되게 처리할 수 있도록 합니다.

---

# 12. 계좌 요약 정보 선택

```python
summary = output2[0] if output2 else {}
```

`output2`에서 첫 번째 항목을 계좌 요약 정보로 사용합니다.

`output2`가 비어 있으면 빈 딕셔너리 `{}`를 사용합니다.

이렇게 하면 계좌 요약 정보가 없더라도 이후 코드에서 오류 없이 기본값 `0`을 사용할 수 있습니다.

---

# 13. 보유 종목 목록 생성

```python
holdings: list[Holding] = []
for item in output1:
    holdings.append(
        Holding(
            symbol=str(_first_value(item, "pdno", "PDNO", "prdt_no", "shtn_pdno") or "").strip(),
            name=str(_first_value(item, "prdt_name", "PDT_NM", "hldg_item_name") or "").strip(),
            quantity=_to_int(_first_value(item, "hldg_qty", "hold_qty", "qty")),
            average_price=_to_int(_first_value(item, "pchs_avg_pric", "avg_prc", "pchs_unpr")),
            current_price=_to_int(_first_value(item, "prpr", "stck_prpr", "current_price")),
            evaluation_profit_loss=_to_int(_first_value(item, "evlu_pfls_amt", "pl_amt", "evaluation_profit_loss")),
            raw=item,
        )
    )
```

이 코드는 API 응답의 보유 종목 목록을 순회하면서 각 항목을 `Holding` 객체로 변환합니다.

## 13.1 보유 종목 리스트 초기화

```python
holdings: list[Holding] = []
```

`Holding` 객체들을 담을 빈 리스트를 만듭니다.

---

## 13.2 `output1` 순회

```python
for item in output1:
```

`output1`에 들어 있는 보유 종목 데이터를 하나씩 순회합니다.

각 `item`은 보유 종목 하나에 대한 원본 API 응답 딕셔너리입니다.

---

## 13.3 종목 코드 추출

```python
symbol=str(_first_value(item, "pdno", "PDNO", "prdt_no", "shtn_pdno") or "").strip()
```

종목 코드를 추출합니다.

여러 후보 키 중 가장 먼저 발견되는 유효 값을 사용합니다.

값이 없으면 빈 문자열을 사용합니다.

최종적으로 문자열로 변환한 뒤 앞뒤 공백을 제거합니다.

---

## 13.4 종목명 추출

```python
name=str(_first_value(item, "prdt_name", "PDT_NM", "hldg_item_name") or "").strip()
```

종목명을 추출합니다.

값이 없으면 빈 문자열을 사용합니다.

---

## 13.5 보유 수량 추출

```python
quantity=_to_int(_first_value(item, "hldg_qty", "hold_qty", "qty"))
```

보유 수량을 추출합니다.

찾은 값은 `_to_int()`를 통해 정수로 변환됩니다.

값이 없거나 변환할 수 없으면 `0`이 됩니다.

---

## 13.6 평균 매입가 추출

```python
average_price=_to_int(_first_value(item, "pchs_avg_pric", "avg_prc", "pchs_unpr"))
```

평균 매입가를 추출합니다.

찾은 값은 `_to_int()`를 통해 정수로 변환됩니다.

---

## 13.7 현재가 추출

```python
current_price=_to_int(_first_value(item, "prpr", "stck_prpr", "current_price"))
```

현재가를 추출합니다.

찾은 값은 `_to_int()`를 통해 정수로 변환됩니다.

---

## 13.8 평가 손익 추출

```python
evaluation_profit_loss=_to_int(_first_value(item, "evlu_pfls_amt", "pl_amt", "evaluation_profit_loss"))
```

평가 손익 금액을 추출합니다.

찾은 값은 `_to_int()`를 통해 정수로 변환됩니다.

---

## 13.9 원본 보유 종목 데이터 저장

```python
raw=item
```

보유 종목의 원본 API 응답 데이터를 그대로 저장합니다.

---

# 14. `AccountSnapshot` 객체 생성

```python
snapshot = AccountSnapshot(
    cash=_to_int(_first_value(summary, "dnca_tot_amt", "cash", "tot_cash_amt")),
    available_cash=_to_int(
        _first_value(summary, "prvs_rcdl_excc_amt", "available_cash", "ord_psbl_cash")
    ),
    total_value=_to_int(_first_value(summary, "tot_evlu_amt", "total_value", "evlu_amt_smtl_amt")),
    holdings=holdings,
    raw_summary=summary,
    raw_holdings=output1,
)
```

계좌 요약 정보와 보유 종목 목록을 하나로 묶어 `AccountSnapshot` 객체를 생성합니다.

---

## 14.1 현금 잔고 추출

```python
cash=_to_int(_first_value(summary, "dnca_tot_amt", "cash", "tot_cash_amt"))
```

현금 잔고를 추출합니다.

찾은 값은 `_to_int()`를 통해 정수로 변환됩니다.

---

## 14.2 주문 가능 현금 추출

```python
available_cash=_to_int(
    _first_value(summary, "prvs_rcdl_excc_amt", "available_cash", "ord_psbl_cash")
)
```

주문 가능 현금을 추출합니다.

찾은 값은 `_to_int()`를 통해 정수로 변환됩니다.

---

## 14.3 총 평가 금액 추출

```python
total_value=_to_int(_first_value(summary, "tot_evlu_amt", "total_value", "evlu_amt_smtl_amt"))
```

총 평가 금액을 추출합니다.

찾은 값은 `_to_int()`를 통해 정수로 변환됩니다.

---

## 14.4 보유 종목 목록 저장

```python
holdings=holdings
```

앞에서 생성한 `Holding` 객체 목록을 저장합니다.

---

## 14.5 원본 계좌 요약 데이터 저장

```python
raw_summary=summary
```

계좌 요약 정보의 원본 API 응답 데이터를 저장합니다.

---

## 14.6 원본 보유 종목 데이터 저장

```python
raw_holdings=output1
```

보유 종목 목록의 원본 API 응답 데이터를 저장합니다.

---

# 15. 계좌 조회 로그 기록

```python
self.logger.info(
    "holdings snapshot: cash=%s available=%s holdings=%s",
    f"{snapshot.cash:,}",
    f"{snapshot.available_cash:,}",
    len(snapshot.holdings),
)
```

계좌 스냅샷 조회가 완료되면 로그를 남깁니다.

로그에는 다음 정보가 포함됩니다.

* 현금 잔고
* 주문 가능 현금
* 보유 종목 수
* 
---

# 16. `AccountSnapshot` 반환

```python
return snapshot
```

최종적으로 생성된 `AccountSnapshot` 객체를 반환합니다.

# 

























