**[당사에서 제공하는 샘플코드에 대한 유의사항]**

- 샘플 코드는 한국투자증권 Open API(KIS Developers)를 연동하는 예시입니다. 고객님의 개발 부담을 줄이고자 참고용으로 제공되고 있습니다.
- 샘플 코드는 별도의 공지 없이 지속적으로 업데이트될 수 있습니다.
- 샘플 코드를 활용하여 제작한 고객님의 프로그램으로 인한 손해에 대해서는 당사에서 책임지지 않습니다.

# KIS Open API 샘플 코드 저장소

한국투자증권(Korea Investment & Securities)의 Open API를 쉽게 이해하고 활용할 수 있도록 실용적인 샘플 코드를 제공합니다.

## 1. 제작 의도 및 대상

### 🎯 제작 의도

- **KIS Open API를 쉽게 이해하고 활용**할 수 있도록 실용적인 샘플 코드 제공
- **초보자도 쉽게 접근**할 수 있는 Procedural 스타일의 코드 작성
- **복사-붙여넣기**만으로 바로 사용 가능한 실용적 예제 제공
- **실전투자**와 **모의투자** 환경 모두 지원

### 👤 대상 사용자

- 한국투자증권 Open API를 처음 사용하는 개발자
- 기존 Open API 사용자
- Python 기반의 자동매매 시스템을 구축하려는 사용자

## 2. 사전 환경설정 안내

### 2.1. Python 환경 요구사항

- **Python 3.9 이상** 필요
- **uv** **패키지 매니저 사용** 권장 (빠르고 간편한 의존성 관리)

### 2.2. uv 설치 방법

- 간편 설정을 위해 uv를 권장합니다

```bash
# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# 설치 확인
uv --version
# uv 0.x.x ... -> 설치 완료
```

### 2.3. KIS Open API 계정 설정

🍀 [서비스 신청 안내 바로가기](https://apiportal.koreainvestment.com/about-howto)
1. 한국투자증권 **계좌 개설 및 ID 연결**
2. 한국투자증권 홈페이지 or 앱에서 **Open API 서비스 신청**
3. **앱키(App Key)**, **앱시크릿(App Secret)** 발급
4. **모의투자** 및 **실전투자** 앱키 각각 준비

### 2.4. 설정 파일 준비

`kis_devlp.yaml` 파일을 열어 아래 항목을 수정합니다.

```yaml
# 실전투자
my_app: "여기에 실전투자 앱키 입력"
my_sec: "여기에 실전투자 앱시크릿 입력"

# 모의투자
paper_app: "여기에 모의투자 앱키 입력"
paper_sec: "여기에 모의투자 앱시크릿 입력"

# HTS ID(KIS Developers 고객 ID) - 체결통보, 나의 조건 목록 확인 등에 사용됩니다.
my_htsid: "사용자 HTS ID"

# 계좌번호 앞 8자리
my_acct_stock: "증권계좌 8자리"
my_acct_future: "선물옵션계좌 8자리"
my_paper_stock: "모의투자 증권계좌 8자리"
my_paper_future: "모의투자 선물옵션계좌 8자리"

# 계좌번호 뒤 2자리
my_prod: "01" # 종합계좌
# my_prod: "03" # 국내선물옵션 계좌
# my_prod: "08" # 해외선물옵션 계좌
# my_prod: "22" # 연금저축 계좌
# my_prod: "29" # 퇴직연금 계좌

# User-Agent(기본값 사용 권장, 변경 불필요)
my_agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
```

## 3. 폴더 구조 및 주요 파일 설명

### 3.1. 폴더 구조

```
# 프로젝트 구조
.
├── README.md                    # 프로젝트 설명서
├── conventions
│   └── convention.md            # 코딩 컨벤션 가이드
├── llm_samples                  # LLM용 샘플 코드
│   ├── domestic_bond            # 국내채권
│   ├── domestic_futureoption    # 국내선물옵션
│   ├── domestic_stock           # 국내주식
│   ├── elw                      # ELW
│   ├── etfetn                   # ETF/ETN
│   ├── kis_auth.py              # 인증 공통 함수
│   ├── overseas_futureoption    # 해외선물옵션
│   ├── overseas_price           # 해외시세
│   └── overseas_stock           # 해외주식
├── kis_devlp.yaml               # API 설정 파일 (개인정보 입력 필요)
├── pyproject.toml               # (uv)프로젝트 의존성 관리
├── user_samples                 # user용 실제 사용 예제
│   ├── domestic_bond            # 국내채권
│   ├── domestic_futureoption    # 국내선물옵션
│   ├── domestic_stock           # 국내주식
│   ├── elw                      # ELW
│   ├── etfetn                   # ETF/ETN
│   ├── kis_auth.py              # 인증 공통 함수
│   ├── overseas_futureoption    # 해외선물옵션
│   ├── overseas_price           # 해외시세
│   └── overseas_stock           # 해외주식
└── uv.lock                      # (uv)의존성 락 파일
```

### 3.2. 주요 파일 설명

### `llm_samples/` - llm용 샘플 코드

- **개별 API별 폴더 구조**: 각 API마다 독립적인 폴더로 구성, llm이 쉽게 관련 코드를 찾도록 구성
- **한줄 호출 파일**: `[함수명].py` (예: `inquire_price.py`)
- **테스트 파일**: `chk_[함수명].py` (예: `chk_inquire_price.py`)

### `user_samples/` - user용 실제 사용 예제

- **통합 함수 파일**: `[카테고리]_functions.py` - 모든 API 함수가 통합된 파일
- **실행 예제 파일**: `[카테고리]_examples.py` - 실제 사용 방법 예제
- **웹소켓 통합파일 및 실행 예제 파일**: `[카테고리]_functions_ws.py`, `[카테고리]_examples_ws.py`

### `kis_auth.py` - 인증 및 공통 기능

- 접근토큰 발급 및 관리
- API 호출 공통 함수
- 실전투자/모의투자 환경 전환
- 웹소켓 지원

## 4. 샘플 코드 실행 방법

### 4.1. 프로젝트 클론 및 환경 설정

```bash
# 저장소 클론
git clone https://github.com/koreainvestment/open-trading-api
cd open-trading-api/kis_github

# uv를 사용한 의존성 설치 - 한줄로 끝
uv sync
```

### 4.2. 설정 파일 수정

- 본인의 계정 설정을 위해 `kis_devlp.yaml` 파일을 다음과 같이 수정합니다. 이미 [2.4단계](#24-설정-파일-준비)를 완료하셨으면 `kis_devlp.yaml` 설정은 건너뛰셔도 됩니다.
    1. **프로젝트 루트에 위치한** `kis_devlp.yaml` 파일 열기
    2. **앱키와 앱시크릿** 정보 입력
    3. **HTS ID** 정보 입력
    4. **계좌번호** 정보 입력 (앞 8자리와 뒤 2자리 구분)
    5. **저장** 후 닫기
- `kis_auth.py`의 config_root 경로를 본인 환경에 맞게 수정해줍니다. 발급된 토큰 파일이 저장될 경로로, 제3자가 찾기 어렵도록 설정하는것을 권장합니다.

```yaml
# kis_auth.py 39번째 줄
# windows - C:\Users\사용자이름\KIS\config
# Linux/macOS - /home/사용자이름/KIS/config
# config_root = os.path.join(os.path.expanduser("~"), "KIS", "config")
config_root = os.path.join(os.path.expanduser("~"), "폴더 경로", "config")
```

- 실행함수에서 인증 관련 설정을 검토 혹은 변경해줍니다. 국내주식 기능 전체를 이용하시려면, `domestic_stock/domestic_stock_examples.py` 파일을 확인해주세요. 
ka.auth() 함수의 svr, product 매개변수를 아래와 같이 수정하면 실전환경(prod)에서 위탁계좌(-01)로 매매 테스트가 가능합니다.

```python
import kis_auth as ka

# 실전투자 인증
ka.auth(svr="prod", product="01") # 모의투자: svr="vps"
```

### 4.3. 샘플 코드 실행

- **user_samples 기준**

```bash
# 국내주식 샘플 코드 실행 (user_samples/domestic_stock/)
python domestic_stock_examples.py # REST 방식
python domestic_stock_examples_ws.py  # Websocket 방식 
```

domestic_stock_examples.py에는 여러 함수가 포함되어 있으므로, 사용하려는 함수만 남기고 나머지는 주석 처리한 후, 입력값을 수정하여 호출해 주세요.

- **llm_samples 기준**

```bash
# 국내주식 > 주식현재가 시세 샘플 코드 실행 (llm_samples/domestic_stock/inquire_price/)
python chk_inquire_price.py
```

llm_samples는 각 기능별로 개별 실행 파일(chk_*.py)이 분리되어 있어, 특정 기능만 테스트하고자 할 때 유용합니다.

### 4.4. 예제 코드 샘플

```python
# REST API 호출 예제 - domestic_stock_examples.py
import sys
import logging
import pandas as pd
sys.path.extend(['..', '.'])

import kis_auth as ka
from domestic_stock_functions import *

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 인증
ka.auth()
trenv = ka.getTREnv()

# 삼성전자 현재가 시세 조회
result = inquire_price(env_dv="real", fid_cond_mrkt_div_code="J", fid_input_iscd="005930")
print(result)
```

```python
# 웹소켓 호출 예제 - domestic_stock_examples_ws.py
import sys
import logging
import pandas as pd
sys.path.extend(['..', '.'])

import kis_auth as ka
from domestic_stock_functions_ws import *

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 인증
ka.auth()
ka.auth_ws()
trenv = ka.getTREnv()

# 웹소켓 선언
kws = ka.KISWebSocket(api_url="/tryitout")

# 삼성전자, sk하이닉스 실시간 호가 구독
kws.subscribe(request=asking_price_krx, data=["005930", "000660"])
```

## 5. 지원되는 주요 API 카테고리

| 카테고리 | 설명 | 폴더명 |
| --- | --- | --- |
| 국내주식 | 국내 주식 시세, 주문, 잔고 등 | `domestic_stock` |
| 국내채권 | 국내 채권 시세, 주문 등 | `domestic_bond` |
| 국내선물옵션 | 국내 파생상품 관련 | `domestic_futureoption` |
| 해외주식 | 해외 주식 시세, 주문 등 | `overseas_stock` |
| 해외선물옵션 | 해외 파생상품 관련 | `overseas_futureoption` |
| ELW | ELW 시세 API | `elw` |
| ETF/ETN | ETF, ETN 시세 API | `etfetn` |

## 6. 문제 해결 가이드

### 토큰 오류 시

```python
import kis_auth as ka

# 토큰 재발급 - 1분당 1회 발급됩니다.
ka.auth(svr="prod")  # 또는 "vps"
```

### 설정 파일 오류 시

- `kis_devlp.yaml` 파일의 앱키, 앱시크릿이 올바른지 확인
- 계좌번호 형식이 맞는지 확인 (앞 8자리 + 뒤 2자리)
- 실시간 시세(WebSocket) 이용 중 ‘No close frame received’ 오류가 발생하는 경우, `kis_devlp.yaml`에 입력하신 HTS ID가 정확한지 확인

### 의존성 오류 시

```bash
# 의존성 재설치
uv sync --reinstall
```

---

# 📧 문의사항

- [한국투자증권 고객의 소리](https://securities.koreainvestment.com/main/customer/support/Support.jsp?cmd=agree_3) > 홈페이지 로그인 후 이용해주세요
