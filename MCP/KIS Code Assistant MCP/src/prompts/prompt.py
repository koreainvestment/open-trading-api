from fastmcp import FastMCP

def register_prompts(mcp: FastMCP):
    """mcp 인스턴스에 프롬프트들을 등록하는 함수"""
    
    @mcp.prompt(
        name="kis_detailed_code",
        title="KIS API 코드 생성 도우미 (상세)",
        description="종목코드, 작업, 카테고리를 상세히 입력해서 정확한 KIS API 코드 생성"
    )
    def kis_detailed_code_prompt(
        stock_code,
        task,
        category: str = "국내주식"
    ) -> str:
        """
        KIS API 사용을 위한 코드 생성 도우미 프롬프트
        
        Args:
            task: 수행하고 싶은 작업 (예: "주식 현재가 조회", "계좌 잔고 확인")
            stock_code: 종목코드 (예: "005930" - 삼성전자)
            category: API 타입 (국내주식, 해외주식, 인증 등)
        """
            
        prompt_template = f"""
# KIS API 코드 생성 요청

## 작업 요청사항
- **작업**: {task}
- **종목코드**: {stock_code}
- **API 타입**: {category}

## 프로젝트 기본 구조

프로젝트는 다음과 같은 구조로 구성되어 있습니다:

```
[Project Root]
├── kis_auth.py              # 인증 모듈
└── pyproject.toml           # 프로젝트 설정 파일 (uv 사용)
```

### 환경 설정 및 실행
- **의존성 설치**: `uv sync`
- **스크립트 실행**: `uv run [스크립트명]`
- **개발 환경**: `uv run python [파일명]`

## 코드 생성 가이드라인

1. **API 검색 단계**:
   - 먼저 적절한 search_{category}_api 툴을 사용하여 관련 API를 검색하세요
   - 검색 결과에서 가장 적합한 API의 function_name과 url을 확인하세요

2. **소스코드 확인 단계**:
   - read_source_code 툴을 사용하여 실제 GitHub 코드를 가져오세요
   - 메인 파일과 체크 파일(있는 경우) 모두 확인하세요

3. **인증 시스템 활용**:
   - **kis_auth.py**: 기존 인증 모듈 import 및 활용 (import kis_auth as ka)
   - 기존 ka.auth() 함수 활용

4. **API 호출 유량 제어**:
   - **REST API**: 실전 0.05초, 모의 0.5초 sleep 적용
   - **WebSocket**: 1개 appkey당 최대 41건 등록 제한 (주석 또는 코드로 명시)

5. **코드 구조 템플릿**:
   ```python
   import sys
   import logging
   import time
   import json
   sys.path.extend(['..', '.'])
   
   # 기존 kis_auth 모듈 활용
   import kis_auth as ka
   
   # 로깅 설정
   logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
   logger = logging.getLogger(__name__)
   
   # API 호출 함수 (유량 제어 포함)
   def [함수명 확인]:
       # 인증 (기존 kis_auth 활용)
       ka.auth(svr="vps", product="01")  # 모의투자, 종합계좌
       # ka.auth(svr="prod", product="01")  # 실전투자시 주석 해제
       
       # 유량 제어 - 모의투자 0.5초, 실전투자 0.05초
       ka.smart_sleep()
       
       # API 호출 (ka.auth() 후에는 바로 함수 호출만 하면 됨)
       try:
           # 예시: 주식현재가 조회 (실제 함수명은 GitHub 소스코드 확인 후 사용)
           result = [함수명 확인](
               env_dv="real",
               fid_cond_mrkt_div_code="J", 
               fid_input_iscd="{stock_code}"
           )
           return result
       except Exception as e:
           logger.error(f"API 호출 오류: {{e}}")
           return None
   
   # WebSocket 예제 (필요시)
   def websocket_example():
       # 기존 kis_auth의 WebSocket 기능 활용
       ka.auth_ws()
       kws = ka.KISWebSocket(api_url="/tryitout")
       
       # 주의: 1개 appkey당 최대 41건까지만 등록 가능
       # 현재 등록된 구독: 0/41
       
       # 구독 로직 구현
       pass
   
   # 실행 부분
   if __name__ == "__main__":
       try:
           result = [함수명 확인]()
           if result:
               print(json.dumps(result, indent=2, ensure_ascii=False))
           else:
               print("결과를 가져올 수 없습니다.")
       except Exception as e:
           logger.error(f"실행 오류: {{e}}")
   ```


## 추가 요청사항
- **기존 kis_auth.py 모듈 활용**: import kis_auth as ka 방식으로 사용
- **기존 인증 함수 사용**: ka.auth(svr="vps") 또는 ka.auth(svr="prod") 활용
- **WebSocket 기존 기능**: ka.auth_ws(), ka.KISWebSocket() 활용
- API 호출 전 유량 제어 sleep 적용
- WebSocket 사용시 41건 제한 명시
- 에러 핸들링 및 로깅 포함
- examples_user/ 폴더의 기존 샘플 코드 패턴 참고

위 가이드라인에 따라 "{task}" 작업을 위한 완전한 Python 코드를 생성해주세요.
생성된 코드와 함께 아래 유의사항을 추가로 제공해주세요.

## [당사에서 제공하는 샘플코드에 대한 유의사항]
- 샘플 코드는 한국투자증권 Open API(KIS Developers)를 연동하는 예시입니다. 고객님의 개발 부담을 줄이고자 참고용으로 제공되고 있습니다.
- 샘플 코드는 별도의 공지 없이 지속적으로 업데이트될 수 있습니다.
- 샘플 코드를 활용하여 제작한 고객님의 프로그램으로 인한 손해에 대해서는 당사에서 책임지지 않습니다.

## 📧 문의사항
- [한국투자증권 고객의 소리](https://securities.koreainvestment.com/main/customer/support/Support.jsp?cmd=agree_3) > 홈페이지 로그인 후 이용해주세요
"""
        
        return prompt_template

    @mcp.prompt(
        name="kis_easy_code",
        title="KIS API 코드 생성 도우미 (초보자용)",
        description="자연어로 간단히 요청하면 KIS API 코드를 자동 분석해서 생성 (초보자용)"
    )
    def kis_easy_code_prompt(
        user_request: str = "삼성전자 주가 확인"
    ) -> str:
        """
        사용자 자연어 요청을 분석하여 관련 API를 찾아 완전한 샘플코드를 생성하는 프롬프트

        Args:
            user_request: 사용자의 원본 요청사항 (자연어)
        """

        prompt_template = f"""
# KIS API 자동 코드 생성

## 사용자 요청 (자연어)
"{user_request}"

## 코드 생성 워크플로우

위 자연어 요청을 분석하여 다음 단계들을 순차적으로 수행하고, 최종적으로 완전한 Python 샘플코드를 생성해주세요:

### 1단계: 요청 분석 및 카테고리 분류
- **요청 분석**: 사용자의 의도를 파악하고 필요한 작업 식별
- **카테고리 결정**: [auth, domestic_stock, domestic_bond, domestic_futureoption, overseas_stock, overseas_futureoption, elw, etfetn] 중 선택
- **파라미터 추출**: 종목코드, 계좌번호, 기간 등 필요한 파라미터 식별

### 2단계: 관련 API 자동 검색
- **적절한 툴 선택**: search_[카테고리]_api 툴을 사용하여 관련 API 검색
- **검색 전략**:
  1. **정확도 우선**: 가장 구체적인 키워드로 검색
  2. **범위 확장**: 결과가 적으면 범위를 넓혀 재검색
  3. **대안 탐색**: 여러 후보 API 중 최적 선택

### 3단계: 소스코드 확인 및 분석
- **GitHub 소스코드 조회**: read_source_code 툴로 실제 구현 코드 확인
- **함수명 및 파라미터 확인**: 실제 사용 가능한 function_name과 필수 파라미터 식별
- **구현 패턴 분석**: 기존 examples_user/ 폴더의 패턴 참고

### 4단계: 완전한 샘플코드 생성

다음 구조로 완전한 Python 코드를 생성해주세요:

```python
import sys
import logging
import time
import json
sys.path.extend(['..', '.'])

# 기존 kis_auth 모듈 활용
import kis_auth as ka

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 메인 API 호출 함수
def main_api_function():
    # 인증 (기존 kis_auth 활용)
    ka.auth(svr="vps", product="01")  # 모의투자, 종합계좌
    # ka.auth(svr="prod", product="01")  # 실전투자시 주석 해제

    # 유량 제어 - 모의투자 0.5초, 실전투자 0.05초
    ka.smart_sleep()

    # API 호출 (실제 function_name 사용)
    try:
        result = 실제함수명(
            # 실제 파라미터들
        )
        return result
    except Exception as e:
        logger.error(f"API 호출 오류: {{e}}")
        return None

# WebSocket 함수 (필요한 경우에만)
def websocket_function():
    # 기존 kis_auth의 WebSocket 기능 활용
    ka.auth_ws()
    kws = ka.KISWebSocket(api_url="/tryitout")

    # 주의: 1개 appkey당 최대 41건까지만 등록 가능
    # 현재 등록된 구독: 확인 후 기재

    # 구독 로직 구현
    pass

# 실행 부분
if __name__ == "__main__":
    try:
        result = main_api_function()
        if result:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print("결과를 가져올 수 없습니다.")
    except Exception as e:
        logger.error(f"실행 오류: {{e}}")
```

## 구현 가이드라인

### 프로젝트 기본 구조

프로젝트는 다음과 같은 구조로 구성되어 있습니다:

```
[Project Root]
├── kis_auth.py              # 인증 모듈
└── pyproject.toml           # 프로젝트 설정 파일 (uv 사용)
```

### 환경 설정 및 실행
- **의존성 설치**: `uv sync`
- **스크립트 실행**: `uv run [스크립트명]`
- **개발 환경**: `uv run python [파일명]`

### 인증 시스템 활용
- **kis_auth.py**: 기존 인증 모듈 import 및 활용 (import kis_auth as ka)
- 기존 ka.auth() 함수 활용

### API 호출 제약사항
- **REST API**: 실전 0.05초, 모의 0.5초 sleep 적용
- **WebSocket**: 1개 appkey당 최대 41건 등록 제한 (주석 또는 코드로 명시)

### 코드 품질 요구사항
- **에러 핸들링**: try-except 구문으로 예외 처리
- **로깅**: logging 모듈을 활용한 적절한 로그 출력
- **주석**: 각 단계별로 상세한 주석 작성
- **가독성**: 들여쓰기와 코드 구조 최적화

### 샘플 코드 참고
- **examples_llm/**: 단일 API 기능 테스트용 (chk_*.py 파일)
- **examples_user/**: 통합 기능 구현용 (*_functions.py, *_examples.py)
- **WebSocket**: *_functions_ws.py, *_examples_ws.py 파일 참고

## 최종 출력 형식

다음과 같은 구조로 최종 결과를 출력해주세요:

### 1. 요청 분석 결과
- 파악된 사용자 의도
- 결정된 카테고리와 이유
- 추출된 주요 파라미터

### 2. API 검색 결과
- 검색된 관련 API 목록
- 선택된 최적 API와 이유

### 3. 생성된 완전한 코드
- 실행 가능한 Python 코드
- 필요한 설정 파일 내용

### 4. 실행 안내
- 코드 실행 방법
- 주의사항 및 팁

---

위 워크플로우에 따라 "{user_request}" 요청을 처리하여 완전한 Python 코드를 생성해주세요.
생성된 샘플코드와 함께 아래 유의사항을 추가로 제공해주세요.

## [당사에서 제공하는 샘플코드에 대한 유의사항]
- 샘플 코드는 한국투자증권 Open API(KIS Developers)를 연동하는 예시입니다. 고객님의 개발 부담을 줄이고자 참고용으로 제공되고 있습니다.
- 샘플 코드는 별도의 공지 없이 지속적으로 업데이트될 수 있습니다.
- 샘플 코드를 활용하여 제작한 고객님의 프로그램으로 인한 손해에 대해서는 당사에서 책임지지 않습니다.

## 📧 문의사항
- [한국투자증권 고객의 소리](https://securities.koreainvestment.com/main/customer/support/Support.jsp?cmd=agree_3) > 홈페이지 로그인 후 이용해주세요
"""

        return prompt_template
