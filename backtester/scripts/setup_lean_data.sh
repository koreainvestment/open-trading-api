#!/bin/bash
# P2 Lean 데이터 초기 설정 스크립트
#
# 사용법:
#   cd backtester
#   ./scripts/setup_lean_data.sh
#
# 이 스크립트는 Lean 백테스트에 필요한 환경을 설정합니다:
# - Docker 실행 확인
# - Lean Docker 이미지 pull
# - market-hours-database.json (거래소 운영 시간)
# - symbol-properties-database.csv (심볼 속성)
# - KRX 마스터파일 (KOSPI/KOSDAQ 종목)

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
WORKSPACE_DIR="$PROJECT_DIR/.lean-workspace"
DATA_DIR="$WORKSPACE_DIR/data"

# Lean 설정
LEAN_IMAGE="quantconnect/lean:latest"
LEAN_RAW_BASE="https://raw.githubusercontent.com/QuantConnect/Lean/master/Data"

echo "==================================="
echo "P2 Lean 환경 설정"
echo "==================================="
echo ""
echo "워크스페이스: $WORKSPACE_DIR"
echo ""

# Docker 실행 확인
echo "[1/7] Docker 확인 중..."
if ! command -v docker &> /dev/null; then
    echo "  ❌ Docker가 설치되지 않았습니다."
    echo "     https://www.docker.com/products/docker-desktop 에서 설치하세요."
    exit 1
fi

if ! docker info &> /dev/null; then
    echo "  ❌ Docker가 실행되지 않았습니다."
    echo "     Docker Desktop을 시작해주세요."
    exit 1
fi
echo "  ✅ Docker 실행 중"

# Lean 이미지 확인 및 Pull
echo "[2/7] Lean Docker 이미지 확인 중..."
if docker images -q "$LEAN_IMAGE" 2>/dev/null | grep -q .; then
    echo "  ✅ Lean 이미지 존재: $LEAN_IMAGE"
else
    echo "  📦 Lean 이미지 다운로드 중 (약 2-5GB, 몇 분 소요)..."
    docker pull "$LEAN_IMAGE"
    echo "  ✅ Lean 이미지 다운로드 완료"
fi

# 디렉토리 생성
echo "[3/7] 디렉토리 생성 중..."
mkdir -p "$DATA_DIR/market-hours"
mkdir -p "$DATA_DIR/symbol-properties"
mkdir -p "$DATA_DIR/equity/krx/daily"
mkdir -p "$DATA_DIR/equity/usa/daily"
mkdir -p "$DATA_DIR/forex/fxcm/daily"
mkdir -p "$WORKSPACE_DIR/projects"
mkdir -p "$WORKSPACE_DIR/results"

# market-hours-database.json 다운로드
echo "[4/7] market-hours-database.json 다운로드 중..."
MARKET_HOURS_FILE="$DATA_DIR/market-hours/market-hours-database.json"
if [ -f "$MARKET_HOURS_FILE" ]; then
    echo "  이미 존재: $MARKET_HOURS_FILE"
else
    curl -sL "$LEAN_RAW_BASE/market-hours/market-hours-database.json" -o "$MARKET_HOURS_FILE"
    echo "  다운로드 완료: $(du -h "$MARKET_HOURS_FILE" | cut -f1)"
fi

# symbol-properties-database.csv 다운로드
echo "[5/7] symbol-properties-database.csv 다운로드 중..."
SYMBOL_PROPS_FILE="$DATA_DIR/symbol-properties/symbol-properties-database.csv"
if [ -f "$SYMBOL_PROPS_FILE" ]; then
    echo "  이미 존재: $SYMBOL_PROPS_FILE"
else
    curl -sL "$LEAN_RAW_BASE/symbol-properties/symbol-properties-database.csv" -o "$SYMBOL_PROPS_FILE"
    echo "  다운로드 완료: $(du -h "$SYMBOL_PROPS_FILE" | cut -f1)"
fi

# lean.json 생성
echo "[6/7] lean.json 생성 중..."
LEAN_JSON="$WORKSPACE_DIR/lean.json"
cat > "$LEAN_JSON" << 'EOF'
{
  "data-folder": "./data",
  "results-destination-folder": "./results",
  "engine-type": "local"
}
EOF
echo "  생성 완료: $LEAN_JSON"

# KRX 마스터파일 다운로드 (KIS 공개 API)
echo "[7/7] KRX 마스터파일 다운로드 중..."
cd "$PROJECT_DIR"
if command -v python3 &> /dev/null; then
    python3 "$SCRIPT_DIR/download_master.py" 2>/dev/null || {
        echo "  Python 스크립트 실행 실패, uv 시도..."
        uv run python "$SCRIPT_DIR/download_master.py" 2>/dev/null || {
            echo "  ⚠️  마스터파일 다운로드 실패 (수동 실행 필요)"
            echo "     uv run python scripts/download_master.py"
        }
    }
else
    echo "  Python3이 없습니다. 수동으로 실행하세요:"
    echo "  uv run python scripts/download_master.py"
fi

echo ""
echo "==================================="
echo "설정 완료!"
echo "==================================="
echo ""
echo "데이터 구조:"
echo "  $DATA_DIR/"
echo "  ├── market-hours/"
echo "  │   └── market-hours-database.json"
echo "  ├── symbol-properties/"
echo "  │   └── symbol-properties-database.csv (+ KRX 종목)"
echo "  └── equity/krx/daily/"
echo "      └── (백테스트 시 KIS API로 자동 다운로드)"
echo ""
echo "다음 단계:"
echo "  1. API 서버 시작: cd backend && uv run uvicorn main:app --port 8002"
echo "  2. 프론트엔드 시작: cd frontend && npm run dev"
echo ""
