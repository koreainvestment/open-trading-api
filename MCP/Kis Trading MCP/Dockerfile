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

# 의존성 레이어를 애플리케이션 소스와 분리해 Docker 캐시를 재사용한다.
COPY pyproject.toml Readme.md ./
RUN uv sync --no-install-project

# 애플리케이션 코드 복사 후 프로젝트 자체를 설치한다.
COPY . .
RUN uv sync

# 환경변수 설정
ENV ENV=live
ENV PYTHONPATH=/app
ENV MCP_TYPE=streamable-http
ENV MCP_HOST=0.0.0.0
ENV MCP_PORT=3000
ENV MCP_PATH=/mcp

# 포트 노출 (HTTP 서버용)
EXPOSE 3000

# KIS 자격증명과 계좌 정보는 이미지에 포함하지 않고 런타임에만 주입한다.

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
