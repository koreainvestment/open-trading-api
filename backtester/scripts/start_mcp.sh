#!/bin/bash
# KIS Backtest MCP Server 시작 스크립트
# 사용법: bash scripts/start_mcp.sh [PORT]
#
# 환경변수:
#   MCP_PORT  — 포트 (기본 3846)
#   MCP_HOST  — 바인드 주소 (기본 127.0.0.1)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
P2_DIR="$(dirname "$SCRIPT_DIR")"

PORT="${1:-${MCP_PORT:-3846}}"
HOST="${MCP_HOST:-127.0.0.1}"

echo "========================================"
echo " KIS Backtest MCP Server"
echo " transport : streamable-http"
echo " address   : http://${HOST}:${PORT}/mcp"
echo " health    : http://${HOST}:${PORT}/health"
echo "========================================"

cd "$P2_DIR"

# .env 로드 (있으면)
if [ -f ".env" ]; then
    set -a
    # shellcheck disable=SC1091
    source .env
    set +a
    echo "[.env] 환경변수 로드 완료"
fi

MCP_HOST="$HOST" MCP_PORT="$PORT" \
    uv run python -m kis_mcp.server
