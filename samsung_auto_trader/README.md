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
def _env(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)
    if value is None or value == "":
        raise ValueError(f"Missing required environment variable: {name}")
    return value
API_KEY 등 환경변수를 불러오는 함수
os.getenv()는 환경변수를 읽는 함수이다. 이름에 맞는 환경변수를 가져오고, 없으면 default를 가져온다. 만약 그 값이 없으면 오류를 발생시킨다

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
계좌번호 문자열을 정해진 형식으로 정리해서 앞 8자리와 뒤 2자리로 나누는 함수
먼저 re.sub으로 계좌번호의 공백을 모두 없애준다
계좌번호 중간에 -이 있으면 -을 기준으로 계좌번호를 나눈다
앞이 8자리, 뒤가 2가지라 맞고 모두 숫자인지 확인한다
그 다음 문자가 섞여있을 가능성을 대비하여 문자를 모두 제거하고 전체가 10자리가 맞으면 앞 8자리, 뒷 2자리를 나누어 반환한다
형식이 맞지 않았으면 오류를 발생시킨다

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
한국투자증권 API에 GET/POST 요청을 보내는 공통 클라이언트 클래스
KISApiClient
│
├─ __init__()
│  └─ API 요청에 필요한 기본 정보 저장
│
├─ get()
│  └─ GET 요청을 _request()로 넘김
│
├─ post()
│  └─ POST 요청을 _request()로 넘김
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
   
