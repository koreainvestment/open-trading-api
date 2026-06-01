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


















































