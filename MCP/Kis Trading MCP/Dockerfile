# Python 3.13 slim 이미지 사용
FROM python:3.13-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치를 위한 uv 설치
RUN pip install uv

# pyproject.toml 복사 (uv.lock이 없을 수 있으므로)
COPY pyproject.toml ./

# uv.lock이 있으면 복사, 없으면 의존성만 설치
COPY uv.lock* ./

# 의존성 설치 (uv.lock이 있으면 frozen, 없으면 일반 설치)
RUN if [ -f uv.lock ]; then uv sync --frozen; else uv sync; fi

# 애플리케이션 코드 복사
COPY . .

# 환경변수 설정
ENV ENV=live
ENV PYTHONPATH=/app

# 포트 노출 (HTTP 서버용)
EXPOSE 3000

# 환경변수 정의 (런타임에 설정됨)
ENV KIS_APP_KEY=""
ENV KIS_APP_SECRET=""
ENV KIS_PAPER_APP_KEY=""
ENV KIS_PAPER_APP_SECRET=""
ENV KIS_HTS_ID=""
ENV KIS_ACCT_STOCK=""
ENV KIS_ACCT_FUTURE=""
ENV KIS_PAPER_STOCK=""
ENV KIS_PAPER_FUTURE=""
ENV KIS_PROD_TYPE=""
ENV KIS_URL_REST=""
ENV KIS_URL_REST_PAPER=""
ENV KIS_URL_WS=""
ENV KIS_URL_WS_PAPER=""

# 시작 스크립트 생성
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
echo "Starting KIS Trade MCP Server..."\n\
echo "Environment: $ENV"\n\
\n\
# MCP 서버 시작 (HTTP 모드)\n\
exec uv run python server.py\n\
' > /app/start.sh && chmod +x /app/start.sh

# 시작 스크립트 실행
CMD ["/app/start.sh"]
