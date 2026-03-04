#!/bin/bash
# P2 Backtest System - Start Script
# Frontend: 3001, Backend: 8002

# Get absolute path of script directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=== P2 Backtest System ==="
echo "Frontend: http://localhost:3001"
echo "Backend:  http://localhost:8002"
echo ""

# Kill existing processes on these ports
lsof -ti:3001 | xargs kill -9 2>/dev/null
lsof -ti:8002 | xargs kill -9 2>/dev/null

# Check Lean data files
SYMBOL_PROPS="$SCRIPT_DIR/.lean-workspace/data/symbol-properties/symbol-properties-database.csv"
MARKET_HOURS="$SCRIPT_DIR/.lean-workspace/data/market-hours/market-hours-database.json"
if [ ! -f "$SYMBOL_PROPS" ] || [ ! -f "$MARKET_HOURS" ]; then
  echo "[Lean] 필수 데이터 파일 없음 → setup_lean_data.sh 실행..."
  bash "$SCRIPT_DIR/scripts/setup_lean_data.sh" || { echo "Lean 설정 실패. scripts/setup_lean_data.sh를 수동 실행하세요."; exit 1; }
fi

# Start backend
cd "$SCRIPT_DIR"
echo "[Backend] Starting on port 8002..."
uv run python -m uvicorn backend.main:app --host 0.0.0.0 --port 8002 --reload &
BACKEND_PID=$!

# Wait for backend
sleep 2

# Ensure frontend deps are installed
if [ ! -d "$SCRIPT_DIR/frontend/node_modules" ]; then
  echo "[Frontend] node_modules not found, running npm install..."
  (cd "$SCRIPT_DIR/frontend" && npm install) || { echo "npm install failed. Run: cd frontend && npm install"; exit 1; }
fi

# Start frontend
cd "$SCRIPT_DIR/frontend"
echo "[Frontend] Starting on port 3001..."
npm run dev &
FRONTEND_PID=$!

echo ""
echo "Press Ctrl+C to stop all services"

# Cleanup on exit
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT

wait
