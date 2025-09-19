# 중요 : MCP에 대한 내용을 완전히 숙지하신 뒤 사용해 주십시오. 
#       이 프로그램을 실행하여 발생한 모든 책임은 사용자 본인에게 있습니다.

# 한국투자증권 OPEN API MCP 서버 - Docker 설치 가이드

한국투자증권의 다양한 금융 API를 Docker를 통해 Claude Desktop에서 쉽게 사용할 수 있도록 하는 설치 가이드입니다.

## 🚀 주요 기능

### 지원하는 API 카테고리

| 카테고리 | 개수 | 주요 기능 |
|---------|------|----------|
| 국내주식 | 74개 | 현재가, 호가, 차트, 잔고, 주문, 순위분석, 시세분석, 종목정보, 실시간시세 등 |
| 해외주식 | 34개 | 미국/아시아 주식 시세, 잔고, 주문, 체결내역, 거래량순위, 권리종합 등 |
| 국내선물옵션 | 20개 | 선물옵션 시세, 호가, 차트, 잔고, 주문, 야간거래, 실시간체결 등 |
| 해외선물옵션 | 19개 | 해외선물 시세, 주문내역, 증거금, 체결추이, 옵션호가 등 |
| 국내채권 | 14개 | 채권 시세, 호가, 발행정보, 잔고조회, 주문체결내역 등 |
| ETF/ETN | 2개 | NAV 비교추이, 현재가 등 |
| ELW | 1개 | ELW 거래량순위 |

**전체 API 총합계: 166개**

### 핵심 특징
- 🐳 **Docker 컨테이너화**: 완전 격리된 환경에서 안전한 실행
- ⚡ **동적 코드 실행**: GitHub에서 실시간으로 API 코드를 다운로드하여 실행
- 🔧 **설정 기반**: JSON 파일로 API 설정 및 파라미터 관리
- 🛡️ **안전한 실행**: 격리된 임시 환경에서 코드 실행
- 🔍 **검증 기능**: API 상세 정보 조회로 파라미터 확인
- 🌍 **환경 지원**: 실전/모의 환경 구분 지원
- 🔐 **자동 설정**: 서버 시작 시 KIS 인증 설정 자동 생성
- 🖥️ **크로스 플랫폼**: Windows, macOS, Linux 모두 지원

## 📦 Docker 설치 및 설정

### 📋 Docker 설치

#### 🚀 빠른 설치 (권장)
**공식 Docker Desktop을 사용하세요:**
- [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop/)
- [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/)  
- [Docker Engine for Linux](https://docs.docker.com/engine/install/)

#### 📋 OS별 간단 가이드

##### 🍎 **macOS**
```bash
# Homebrew 사용 (권장)
brew install --cask docker

# 또는 공식 인스톨러 다운로드
# https://www.docker.com/products/docker-desktop/
```

##### 🐧 **Linux (Ubuntu/Debian)**  
```bash
# 공식 스크립트 사용 (권장)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 사용자를 docker 그룹에 추가
sudo usermod -aG docker $USER
```

##### 🪟 **Windows**
**⚠️ Windows는 추가 설정이 필요합니다:**

1. **시스템 요구사항 확인**
   - Windows 10/11 Pro, Enterprise, Education
   - WSL2 또는 Hyper-V 지원

2. **Docker Desktop 설치**
   - [공식 사이트](https://www.docker.com/products/docker-desktop/)에서 다운로드
   - 설치 중 "Use WSL 2" 옵션 선택 권장

3. **설치 후 확인**
   ```cmd
   docker --version
   docker run hello-world
   ```

**Windows 상세 설치 가이드**: [Docker 공식 문서](https://docs.docker.com/desktop/install/windows-install/) 참조

### 요구사항
- Docker 20.10+
- 한국투자증권 OPEN API 계정

### 📋 설치 및 설정 단계

#### **1단계: 프로젝트 클론**
```bash
# 프로젝트 클론
git clone https://github.com/koreainvestment/open-trading-api.git
cd "open-trading-api/MCP/Kis Trading MCP"
```

#### **2단계: 한국투자증권 API 정보 준비**
한국투자증권 개발자 센터에서 발급받은 정보를 준비하세요:

**필수 정보:**
- App Key (실전용)
- App Secret (실전용)
- 계좌 정보들

**선택 정보:**
- App Key (모의용)
- App Secret (모의용)

#### **3단계: Docker 이미지 빌드**
```bash
# Docker 이미지 빌드
docker build -t kis-trade-mcp .

# 또는 태그와 함께 빌드
docker build -t kis-trade-mcp:latest .
```

#### **4단계: Docker 컨테이너 실행**

**기본 실행:**
```bash
docker run -d \
  --name kis-trade-mcp \
  -p 3000:3000 \
  -e KIS_APP_KEY="your_app_key" \
  -e KIS_APP_SECRET="your_app_secret" \
  -e KIS_PAPER_APP_KEY="your_paper_app_key" \
  -e KIS_PAPER_APP_SECRET="your_paper_app_secret" \
  -e KIS_HTS_ID="your_hts_id" \
  -e KIS_ACCT_STOCK="12345678" \
  -e KIS_ACCT_FUTURE="87654321" \
  -e KIS_PAPER_STOCK="11111111" \
  -e KIS_PAPER_FUTURE="22222222" \
  -e KIS_PROD_TYPE="01" \
  kis-trade-mcp
```

#### **5단계: 컨테이너 상태 확인**
```bash
# 컨테이너 상태 확인
docker ps

# 컨테이너 로그 확인
docker logs kis-trade-mcp

# 실시간 로그 확인
docker logs -f kis-trade-mcp

# HTTP 서버 접근 확인
curl http://localhost:3000/sse
```

#### **6단계: HTTP 서버 접근 확인**
컨테이너가 정상적으로 실행되면 HTTP 서버에 접근할 수 있습니다:

```bash
# 서버 상태 확인
curl http://localhost:3000/sse

# 또는 브라우저에서 접근
# http://localhost:3000/sse
```

### 🔗 Claude Desktop 연동 및 설정

#### 📝 Claude Desktop 설정
Claude Desktop 설정 파일에 MCP 서버를 등록하세요.

**설정 파일 위치:**
- **Linux/Mac**: `~/.claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

#### 🐧 Linux/Mac 설정
```json
{
  "mcpServers": {
    "kis-trade-mcp": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "http://localhost:3000/sse"]
    }
  }
}
```

#### 🪟 Windows 설정
```json
{
  "mcpServers": {
    "kis-trade-mcp": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "http://localhost:3000/sse"]
    }
  }
}
```

## 💬 사용법 및 질문 예시

### 기본 사용 패턴

1. **종목 검색**: 먼저 종목 코드를 찾습니다
2. **API 확인**: 사용할 API의 파라미터를 확인합니다  
3. **API 호출**: 필요한 파라미터와 함께 API를 호출합니다

### 질문 예시

**주식 시세 조회:**
- "삼성전자(005930) 현재가 시세 조회해줘"
- "애플(AAPL) 해외주식 현재 체결가 알려줘"
- "삼성전자 종목코드 찾아줘"

**잔고 및 계좌:**
- "국내주식 잔고 조회해줘"
- "해외주식 잔고 확인해줘"

**채권 및 기타:**
- "국고채 3년물 호가 정보 조회하는 방법"
- "KODEX 200 ETF(069500) NAV 비교추이 확인해줘"

**모의투자:**
- "모의투자로 삼성전자 현재가 조회해줘"
- "데모 환경에서 애플 주식 시세 알려줘"

## 🔧 컨테이너 관리

### 컨테이너 제어
```bash
# 컨테이너 시작
docker start kis-trade-mcp

# 컨테이너 중지
docker stop kis-trade-mcp

# 컨테이너 재시작
docker restart kis-trade-mcp

# 컨테이너 제거
docker stop kis-trade-mcp
docker rm kis-trade-mcp
```

### 컨테이너 내부 접근
```bash
# 컨테이너 내부 bash 실행
docker exec -it kis-trade-mcp /bin/bash

# 환경변수 확인
docker exec kis-trade-mcp env | grep KIS

# 로그 실시간 확인
docker logs -f kis-trade-mcp
```

## 💡 사용 팁

1. **환경변수 관리**: 민감한 정보는 환경변수로 안전하게 관리
2. **로그 모니터링**: `docker logs -f`로 실시간 로그 확인
3. **리소스 모니터링**: `docker stats`로 컨테이너 리소스 사용량 확인
4. **백업 전략**: 중요한 설정 파일은 정기적으로 백업
5. **보안 관리**: 컨테이너 내부에서만 민감한 정보 처리

## 📝 로깅 및 모니터링

### 로그 확인
```bash
# 전체 로그
docker logs kis-trade-mcp

# 최근 100줄
docker logs --tail 100 kis-trade-mcp

# 실시간 로그
docker logs -f kis-trade-mcp

# 특정 시간대 로그
docker logs --since "2024-01-01T00:00:00" kis-trade-mcp
```

### 성능 모니터링
```bash
# 컨테이너 리소스 사용량
docker stats kis-trade-mcp

# 컨테이너 상세 정보
docker inspect kis-trade-mcp

# 프로세스 확인
docker exec kis-trade-mcp ps aux
```

## 🛠️ 문제 해결

### 일반적인 문제들

**1. 컨테이너가 시작되지 않는 경우**
```bash
# 로그 확인
docker logs kis-trade-mcp

# 환경변수 확인
docker exec kis-trade-mcp env | grep KIS
```

**2. 환경변수 누락**
```bash
# 컨테이너 재시작
docker restart kis-trade-mcp

# 환경변수 다시 설정하여 실행
docker run -d --name kis-trade-mcp -e KIS_APP_KEY="..." ...
```

**3. 메모리 부족**
```bash
# 메모리 사용량 확인
docker stats kis-trade-mcp

# 컨테이너 리소스 제한 설정
docker run -d --name kis-trade-mcp --memory="2g" --cpus="2" ...
```

**4. 네트워크 연결 문제**
```bash
# 포트 확인
docker port kis-trade-mcp

# 네트워크 연결 테스트
curl http://localhost:3000/sse
```

### 디버깅 명령어
```bash
# 컨테이너 내부 bash 접근
docker exec -it kis-trade-mcp /bin/bash

# Python 환경 확인
docker exec kis-trade-mcp uv run python -c "import sys; print(sys.path)"

# 의존성 확인
docker exec kis-trade-mcp uv pip list

# 네트워크 연결 확인
docker exec kis-trade-mcp ping github.com
```

## 🔒 보안 고려사항

- **컨테이너 격리**: 호스트 시스템과 완전히 분리된 환경에서 실행
- **환경변수 보안**: 민감한 정보는 환경변수로 전달, 코드에 하드코딩 금지
- **임시 파일 정리**: 각 API 호출 후 임시 파일 자동 삭제
- **네트워크 격리**: 필요한 경우 Docker 네트워크를 통한 추가 격리

## ⚠️ 제한사항 및 성능

### API 호출 제한
- 한국투자증권 API의 호출 제한을 준수해야 합니다
- 분당 호출 횟수 제한이 있을 수 있습니다
- 실전 환경에서는 더욱 신중한 사용이 필요합니다

### Docker 성능 고려사항
- **컨테이너 오버헤드**: Docker 컨테이너 실행으로 인한 약간의 성능 오버헤드
- **메모리 사용량**: SQLAlchemy와 pandas가 메모리를 많이 사용할 수 있음
- **네트워크 지연**: GitHub 다운로드 시 네트워크 지연 발생

### 다단계 타임아웃 설정
- 파일 다운로드: 30초 (GitHub 응답 대기)
- 코드 실행: 15초 (API 호출 및 결과 처리)
- 컨테이너 시작: 60초 (의존성 설치 및 초기화)

## 🔗 관련 링크

- [한국투자증권 개발자 센터](https://apiportal.koreainvestment.com/)
- [한국투자증권 OPEN API GitHub](https://github.com/koreainvestment/open-trading-api)
- [MCP (Model Context Protocol) 공식 문서](https://modelcontextprotocol.io/)
- [Docker 공식 문서](https://docs.docker.com/)

---

**주의**: 이 프로젝트는 한국투자증권 OPEN API를 사용합니다. 사용 전 반드시 [한국투자증권 개발자 센터](https://apiportal.koreainvestment.com/)에서 API 이용약관을 확인하시기 바랍니다.

## ⚠️ 투자 책임 고지

**본 MCP 서버는 한국투자증권 OPEN API를 활용한 도구일 뿐이며, 투자 조언이나 권유를 제공하지 않습니다.**

- 📈 **투자 결정 책임**: 모든 투자 결정과 그에 따른 손익은 전적으로 투자자 본인의 책임입니다
- 💰 **손실 위험**: 주식, 선물, 옵션 등 모든 금융상품 투자에는 원금 손실 위험이 있습니다
- 🔍 **정보 검증**: API를 통해 제공되는 정보의 정확성은 한국투자증권에 의존하며, 투자 전 반드시 정보를 검증하시기 바랍니다
- 🧠 **신중한 판단**: 충분한 조사와 신중한 판단 없이 투자하지 마시기 바랍니다
- 🎯 **모의투자 권장**: 실전 투자 전 반드시 모의투자를 통해 충분히 연습하시기 바랍니다

**투자는 본인의 판단과 책임 하에 이루어져야 하며, 본 도구 사용으로 인한 어떠한 손실에 대해서도 개발자는 책임지지 않습니다.**
