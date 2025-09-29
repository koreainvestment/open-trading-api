# MCP를 AI 도구에 연결하는 방법

### 한국투자증권 Open API를 활용하는 KIS Trade MCP와 KIS Code Assistant MCP를 AI 도구(Claude Desktop | Cursor)에 연결하는 설정 방법을 단계별로 안내합니다.

---

# 공통사항

한국투자증권 계좌와 한국투자증권 OpenAPI 홈페이지에서 인증정보(App Key, App Secret)를 준비해 주세요.

개발 환경 : Python 3.13 이상 권장

Claude Desktop 또는 Cursor와 같은 한국투자증권 MCP를 연결할 AI 도구를 설치해 주세요.

## **KIS Open API 신청 및 설정**

1. 한국투자증권 **계좌 개설 및 ID 연결**
2. 한국투자증권 홈페이지 or 앱에서 **Open API 서비스 신청**
3. **앱키(App Key)**, **앱시크릿(App Secret)** 발급
4. **모의투자** 및 **실전투자** 앱키 각각 준비

🍀 [서비스 신청 안내 바로가기](https://apiportal.koreainvestment.com/about-howto)

# 🔗 MCP(Model Context Protocol)란?

MCP는 Claude를 개발한 Anthropic에서 만든 프로토콜로, AI 모델이 외부 도구와 데이터에 안전하고 효율적으로 접근할 수 있게 해주는 표준화된 인터페이스입니다.
이제 한국투자증권이 만든 2개의 MCP를 통해 한국투자증권 Open API를 자연어로 쉽게 활용할 수 있습니다.

# 한국투자증권 MCP 소개

## KIS Trade MCP

### **특징 및 용도**

국내/해외주식, 선물·옵션, 채권, ETF/ETN, 인증 등 한국투자증권의 다양한 Open API를 **MCP 서버의 "도구"**로 래핑하였습니다. LLM이 바로 사용할 수 있도록 *API 스키마·파라미터*를 리소스로 제공하고, *모의/실전 환경*을 구분하여 안전하게 실행합니다.

### 설정 방법

(9월 중 공개 예정)

## KIS Code Assistant MCP

### 특징 및 용도

한국투자증권의 많은 Open API 중에서 **자연어 검색으로 관련 API를 찾고**, **호출 예제(파라미터 포함)까지 자동 구성**해주는 MCP 서버입니다. "무엇을 하고 싶은지"만 말하면, 관련 API를 추천하고 예시 호출 코드를 만들어 드립니다.

### 설정 방법

1. Claude Desktop
    
    Link : [https://smithery.ai/server/@KISOpenAPI/kis-code-assistant-mcp](https://smithery.ai/server/@KISOpenAPI/kis-code-assistant-mcp)
    
    <img width="2048" height="958" alt="image" src="https://github.com/user-attachments/assets/82aa8bc4-b112-482c-8e8d-34c41fb0ed76" />

    <img width="2048" height="816" alt="image 1" src="https://github.com/user-attachments/assets/3404acc4-058a-4b41-a4d4-0d5aa62ddd3b" />
    
    **AUTO / Claude Desktop** 선택 → Terminal 명령어 Copy 클릭
    
    <img width="2048" height="884" alt="image 2" src="https://github.com/user-attachments/assets/a5852435-baa9-4fe0-a5e6-41929552b900" />
    
    터미널에 명령어 붙여넣기하고 엔터 → 설치 완료 메시지 후 Claude 재시작 질문에는 Y 입력 후 엔터를 누르면 Claude Desktop 재시작
    
    <img width="2048" height="1000" alt="image 3" src="https://github.com/user-attachments/assets/911b7818-bedf-4d04-8721-09cc4cf5409d" />

    
    홈 화면 대화창 하단 **검색 및 도구** 버튼에서 설치 및 추가 확인 가능, `설정 → 개발자`에서도 확인 할 수 있습니다.
    
2. Cursor
    
    Link : [https://smithery.ai/server/@KISOpenAPI/kis-code-assistant-mcp](https://smithery.ai/server/@KISOpenAPI/kis-code-assistant-mcp)
    
    <img width="2048" height="988" alt="image 4" src="https://github.com/user-attachments/assets/5058bc1d-8046-47e4-9962-f7f1a5f3bcba" />

    <img width="2048" height="988" alt="image 5" src="https://github.com/user-attachments/assets/6bb863b7-a8de-4435-8bdd-ef1deece02f0" />

    
    **AUTO / Cursor** 선택 → **One-Click Install** 클릭
    
   <img width="2048" height="958" alt="image 6" src="https://github.com/user-attachments/assets/f3e2f17b-f1b6-4b8f-a388-2990ef6f2a0e" />
    
    Cursor에서 **Install** 클릭하면 완료
    
   <img width="2048" height="958" alt="image 7" src="https://github.com/user-attachments/assets/a4fcdcdc-d83b-4187-946d-28160d7f65bf" />

    KIS Code Assistant MCP가 연결되었는지 확인 (경로 :  `Settings` > `MCP Servers`)
    

# 🚀 MCP기반 트레이딩 시스템 개발을 위한 환경 설정

트레이딩 시스템 개발을 시작하기 전에 필요한 Python 환경 구성부터 API 연결 테스트까지 개발 환경 설정 과정을 안내합니다.

### 1. 폴더 생성 및 파일 다운로드

트레이딩 시스템 개발을 위해 필요한 파일을 다운로드하고 폴더를 생성하고 경로를 지정하세요.

### **1-1. 보안 폴더 생성**

중요 정보를 저장하는 폴더와 실행 코드를 저장하는 폴더를 각각 생성합니다. 

**맥/리눅스**:

```bash
mkdir -p ~/KIS/config
cd ~/KIS/config
```

**윈도우 PowerShell**:

```powershell
mkdir "$HOME\KIS\config"
cd "$HOME\KIS\config"
```

### **1-2. 프로젝트 폴더 생성**

**맥/리눅스**:

```bash
mkdir -p ~/자동매매
cd ~/자동매매
```

**윈도우 PowerShell**:

```powershell
mkdir "$HOME\자동매매"
cd "$HOME\자동매매"
```

### **1-3. GitHub에서 파일 다운로드**

한국투자증권 GitHub에서 세개 파일을 다운로드 받으세요.

**GitHub 링크**: https://github.com/koreainvestment/open-trading-api

1. **kis_devlp.yaml** → `~/kis/config` 폴더에 저장 **(보안 정보로 별도 관리)**
    
    https://github.com/koreainvestment/open-trading-api/blob/main/kis_devlp.yaml
    
2. **kis_auth.py** → `~/자동매매/` 폴더에 저장
    
    https://github.com/koreainvestment/open-trading-api/blob/main/examples_llm/kis_auth.py
    
3. **pyproject.toml** → `~/자동매매/` 폴더에 저장
    
    https://github.com/koreainvestment/open-trading-api/blob/main/pyproject.toml
    

> 경로 표기 안내
문서에서 `~`는 **내 사용자 폴더(홈)**를 뜻합니다.
`~/{폴더명}`은 그 안의 `{폴더명}` 폴더라는 의미이며, 실제 입력은 `~/kis/config`처럼 중괄호 없이 적습니다.
(Windows PowerShell: `~` → `C:\Users\내이름`)
> 

### **1-4. `중요`kis_devlp.yaml 설정**

`~/KIS/kis_devlp.yaml` 파일에 발급받은 App key, App Secret, 계좌정보 (실전, 모의)를 입력하세요

```yaml
#홈페이지에서 API서비스 신청시 발급 AppKey, AppSecret 값 설정
#실전투자
my_app: "발급받은_실제_APP_KEY"      # 한국투자증권에서 발급받은 APP KEY 입력
my_sec: "발급받은_실제_APP_SECRET"   # 한국투자증권에서 발급받은 APP SECRET 입력

#모의투자  
paper_app: "발급받은_실제_APP_KEY"      # 모의투자용 APP KEY (실전과 동일)
paper_sec: "발급받은_실제_APP_SECRET"   # 모의투자용 APP SECRET (실전과 동일)

# HTS ID
my_htsid: "실제_HTS_ID"              # 한국투자증권 HTS ID 입력

#계좌번호 및 8자리
my_acct_stock: "실제_계좌번호"        # 주식 계좌번호 (예: 50068418)  
my_acct_future: "실제_계좌번호"       # 선물옵션 계좌번호 (주식과 동일 가능)
my_paper_stock: "모의투자_계좌번호"    # 모의투자 주식 계좌번호
my_paper_future: "모의투자_계좌번호"   # 모의투자 선물옵션 계좌번호 (주식과 동일 가능)

#계좌번호 뒤 2자리
my_prod: "01"   # 01(종합계좌), 03(국내선물옵션), 08(해외선물옵션), 22(개인연금), 29(퇴직연금)
```

> **⚠️ 보안 주의사항:**
> 
> - App Key/App Secret과 계좌번호는 절대 타인과 공유하지 마세요.
> - GitHub 공개 저장소와 같이 외부에 공개된 저장소에는 절대 업로드하지 마세요.
> - 트레이딩 시스템 폴더와 별도의 경로(~/KIS/config)에 보관하세요.
> - 정기적으로 API Key를 재발급하여 보안을 강화하세요

## 2. uv 설치 및 가상환경 설정

### **2-1. uv 설치**

**맥/리눅스**:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**윈도우**:

```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### **2-2. 가상환경 설정**

프로젝트 폴더로 이동 후 가상환경 생성:

```bash
cd ~/자동매매
uv sync
```

### **2-3. 가상환경 활성화**

**맥/리눅스**:

```bash
source .venv/bin/activate
```

**윈도우**:

```bash
.venv\Scripts\activate
```

## 3. 연결 테스트 (필수 검증)

### 3-1. 기본 연결 테스트

`~/자동매매/test_connection.py` 파일을 생성하고 해당 코드를 복사/붙여넣기 합니다.

(모의투자로 세팅되어 있습니다.)

```python
# test_connection.py
# KIS Open API 연결 테스트 및 기본 정보 확인 스크립트
import sys
import os

try:
    from kis_auth import auth, getTREnv, getEnv, read_token
    import kis_auth
    
    # 설정 파일 확인
    print("설정 파일 확인 중...")
    cfg = getEnv()
    print(f"앱키: {cfg.get('my_app', 'None')[:10]}...")
    print(f"서버 URL: {cfg.get('prod', 'None')}")
    
    # 인증 토큰 발급 테스트
    print("토큰 발급 시도 중...")
    try:
        # 디버그 모드 활성화
        kis_auth._DEBUG = True
        
        auth(svr="vps")  # 모의투자 토큰 발급 및 저장
        print("토큰 발급 완료")
        
        # 토큰이 제대로 설정되지 않은 경우 수동으로 설정
        env = getTREnv()
        if not env.my_token:
            print("토큰이 환경에 설정되지 않음. 저장된 토큰을 확인합니다...")
            saved_token = read_token()
            if saved_token:
                print("저장된 토큰을 찾았습니다. 환경에 설정합니다...")
                # 토큰을 직접 설정
                kis_auth._TRENV = kis_auth._TRENV._replace(my_token=saved_token)
                kis_auth._base_headers["authorization"] = f"Bearer {saved_token}"
                print("토큰 설정 완료")
            else:
                print("저장된 토큰도 없습니다.")
        
    except Exception as auth_error:
        print(f"토큰 발급 중 오류: {auth_error}")
        import traceback
        traceback.print_exc()
    
    # 환경 정보 확인
    env = getTREnv()
    
    if hasattr(env, 'my_token') and env.my_token:
        print("✅ API 연결 성공!")
        print(f"토큰 앞 10자리: {env.my_token[:10]}...")
        print(f"계좌번호: {env.my_acct}")
        print(f"서버: {'모의투자' if env.my_url.find('vts') > 0 else '실전투자'}")
    else:
        print("❌ API 연결 실패 - 토큰이 없습니다")
        print(f"토큰 속성 존재: {hasattr(env, 'my_token')}")
        if hasattr(env, 'my_token'):
            print(f"토큰 값: {env.my_token}")
            print(f"토큰 길이: {len(env.my_token) if env.my_token else 0}")

except Exception as e:
    print(f"❌ 오류 발생: {e}")
    print("devlp.yaml 파일 경로와 설정을 확인해주세요")
```

### 3-2. 테스트 실행

테스트를 실행하고 결과를 확인하세요.

```bash
# 실행
cd ~/자동매매
python test_connection.py

# 결과
✅ API 연결 성공!
토큰 앞 10자리: asdfasdfas...
계좌번호: 12345678
서버: 모의투자
```

### 🛠️ 자주 발생하는 문제와 해결방법

1. MCP 연결 실패 시
    - Claude Desktop/Cursor 재시작
    - MCP 서버 URL 확인 ([https://smithery.ai/server/@KISOpenAPI/kis-code-assistant-mcp](https://smithery.ai/server/@KISOpenAPI/kis-code-assistant-mcp))
    - 방화벽 설정 확인
    - 인터넷 연결 확인
2. API 연결 오류 시
    - App Key와 Secret이 발급 받은 것과 동일한지 확인
    - kis_auth.py 의 내용이 다운로드 받은 파일과 동일한지 확인
    - kis_devlp.yaml 파일이 “~/KIS/config/” 혹은 “$HOME/KIS/config”에 있는지 확인
    - kis_devlp.yaml 파일에 작성한 개인정보가 정확한지 확인 (App Key/Secret, HTS ID, 계좌번호, 상품코드)
    - kis_devlp.yaml 파일의 문법이 올바른지 확인 (YAML 문법, 들여쓰기 주의)
3. 가상환경 문제 시
    - uv 버전 확인: `uv --version`
    - pyproject.toml 의 내용이 다운로드 받은 파일과 동일한지 확인
    - 프로그램 실행에 필요한 전체 패키지 재설치:  `uv sync`
    - 가상환경 재생성: `uv venv --force`
4. Python 모듈 import 오류 시
    - 가상환경 활성화 확인
    - 필요 패키지 설치: `uv add {패키지명}`

---

## 4. 최종 폴더 구조 확인

설정이 성공적으로 완료되면 폴더 구조는 다음과 같습니다.

```
~/KIS/
└── config/
    └── devlp.yaml (보안 정보)

~/자동매매/
├── kis_auth.py
├── pyproject.toml
├── test_connection.py
├── .venv/ (uv sync 후 자동 생성)
└── uv.lock (uv sync 후 자동 생성)
```

---

## Next Step

설정이 완료되셨다면 이제 투자를 위한 전략를 구현하세요.

1. 🎯 MCP를 활용하여 개발 시작하기
    - Cursor에서 KIS Code Assistant MCP를 활용하여 자동매매 시스템 개발
    - 자연어로 '주식 현재가 조회 코드 보여줘' 같은 질문하기
2. 📊 모의투자 환경에서 충분한 테스트 진행
    - 실제 거래 전 반드시 모의투자로 검증
    - 손절/익절 로직 구현 및 테스트
3. 🔒 실전 투자 적용 시 보안과 리스크 관리 강화
    - 포트폴리오 분산 투자 권장
    - 정기적인 API 키 교체

🚀 고급 활용 팁

- 백테스팅을 통한 전략 검증
- 실시간 알림 시스템 구축
- 리스크 관리 자동화

---

한국투자증권은 기술을 통해 투자의 진입장벽을 낮추고, 투자자들이 더 나은 투자 경험을 할 수 있도록 MCP를 통해 복잡한 API 연동 등 개발환경을 개선하여 투자 전략 본질에 집중할 수 있도록 지원합니다.

AI와 함께하는 새로운 투자 시대, 여러분만의 성공 투자 스토리에 한국투자증권 MCP가 든든한 파트너가 되겠습니다.
